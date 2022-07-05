import copy
from lamda_ssl.Base.InductiveEstimator import InductiveEstimator
from lamda_ssl.Base.DeepModelMixin import DeepModelMixin
from sklearn.base import ClassifierMixin
from collections import Counter
from lamda_ssl.utils import class_status
from lamda_ssl.Loss.Cross_Entropy import Cross_Entropy
from lamda_ssl.Loss.Semi_supervised_Loss import Semi_supervised_loss
import lamda_ssl.Config.FlexMatch as config
import torch

class FlexMatch(InductiveEstimator,DeepModelMixin,ClassifierMixin):
    def __init__(self,
                 threshold=config.threshold,
                 lambda_u=config.lambda_u,
                 T=config.T,
                 num_classes=config.num_classes,
                 threshold_warmup=config.threshold_warmup,
                 use_hard_labels=config.use_hard_labels,
                 use_DA=config.use_DA,
                 p_target=config.p_target,
                 mu=config.mu,
                 ema_decay=config.ema_decay,
                 weight_decay=config.weight_decay,
                 epoch=config.epoch,
                 num_it_epoch=config.num_it_epoch,
                 num_it_total=config.num_it_total,
                 eval_epoch=config.eval_epoch,
                 eval_it=config.eval_it,
                 device=config.device,
                 train_dataset=config.train_dataset,
                 labeled_dataset=config.labeled_dataset,
                 unlabeled_dataset=config.unlabeled_dataset,
                 valid_dataset=config.valid_dataset,
                 test_dataset=config.test_dataset,
                 train_dataloader=config.train_dataloader,
                 labeled_dataloader=config.labeled_dataloader,
                 unlabeled_dataloader=config.unlabeled_dataloader,
                 valid_dataloader=config.valid_dataloader,
                 test_dataloader=config.test_dataloader,
                 train_sampler=config.train_sampler,
                 train_batch_sampler=config.train_batch_sampler,
                 valid_sampler=config.valid_sampler,
                 valid_batch_sampler=config.valid_batch_sampler,
                 test_sampler=config.test_sampler,
                 test_batch_sampler=config.test_batch_sampler,
                 labeled_sampler=config.labeled_sampler,
                 unlabeled_sampler=config.unlabeled_sampler,
                 labeled_batch_sampler=config.labeled_batch_sampler,
                 unlabeled_batch_sampler=config.unlabeled_batch_sampler,
                 augmentation=config.augmentation,
                 network=config.network,
                 optimizer=config.optimizer,
                 scheduler=config.scheduler,
                 parallel=config.parallel,
                 evaluation=config.evaluation,
                 file=config.file,
                 verbose=config.verbose
                 ):
        DeepModelMixin.__init__(self,train_dataset=train_dataset,
                                    valid_dataset=valid_dataset,
                                    test_dataset=test_dataset,
                                    train_dataloader=train_dataloader,
                                    valid_dataloader=valid_dataloader,
                                    test_dataloader=test_dataloader,
                                    augmentation=augmentation,
                                    network=network,
                                    train_sampler=train_sampler,
                                    train_batch_sampler=train_batch_sampler,
                                    valid_sampler=valid_sampler,
                                    valid_batch_sampler=valid_batch_sampler,
                                    test_sampler=test_sampler,
                                    test_batch_sampler=test_batch_sampler,
                                    labeled_dataset=labeled_dataset,
                                    unlabeled_dataset=unlabeled_dataset,
                                    labeled_dataloader=labeled_dataloader,
                                    unlabeled_dataloader=unlabeled_dataloader,
                                    labeled_sampler=labeled_sampler,
                                    unlabeled_sampler=unlabeled_sampler,
                                    labeled_batch_sampler=labeled_batch_sampler,
                                    unlabeled_batch_sampler=unlabeled_batch_sampler,
                                    epoch=epoch,
                                    num_it_epoch=num_it_epoch,
                                    num_it_total=num_it_total,
                                    eval_epoch=eval_epoch,
                                    eval_it=eval_it,
                                    mu=mu,
                                    weight_decay=weight_decay,
                                    ema_decay=ema_decay,
                                    optimizer=optimizer,
                                    scheduler=scheduler,
                                    parallel=parallel,
                                    device=device,
                                    evaluation=evaluation,
                                    file=file,
                                    verbose=verbose
                                    )

        self.lambda_u=lambda_u
        self.threshold=threshold
        self.T=T
        self.num_classes=num_classes
        self.classwise_acc=None
        self.selected_label=None
        self.threshold_warmup=threshold_warmup
        self.use_hard_labels=use_hard_labels
        self.p_model=None
        self.p_target=p_target
        self.use_DA=use_DA
        self._estimator_type = ClassifierMixin._estimator_type

    def init_transform(self):
        self._train_dataset.add_unlabeled_transform(copy.deepcopy(self.train_dataset.unlabeled_transform),dim=0,x=1)
        self._train_dataset.add_transform(self.weakly_augmentation,dim=1,x=0,y=0)
        self._train_dataset.add_unlabeled_transform(self.weakly_augmentation,dim=1,x=0,y=0)
        self._train_dataset.add_unlabeled_transform(self.strongly_augmentation,dim=1,x=1,y=0)

    def start_fit(self):
        self.num_classes = self.num_classes if self.num_classes is not None else \
            class_status(self._train_dataset.labeled_dataset.y).num_classes
        if self.p_target is None:
            class_counts=torch.Tensor(class_status(self._train_dataset.labeled_dataset.y).class_counts).to(self.device)
            self.p_target = (class_counts / class_counts.sum(dim=-1, keepdim=True))
        else:
            self.p_target=self.p_target.to(self.device)
        self.selected_label = torch.ones((len(self._train_dataset.unlabeled_dataset),), dtype=torch.long ) * -1
        self.selected_label = self.selected_label.to(self.device)
        self.classwise_acc = torch.zeros((self.num_classes)).to(self.device)
        self._network.zero_grad()
        self._network.train()

    def train(self,lb_X,lb_y,ulb_X,lb_idx=None,ulb_idx=None,*args,**kwargs):
        w_lb_X=lb_X[0] if isinstance(lb_X,(tuple,list)) else lb_X
        w_ulb_X,s_ulb_X=ulb_X[0],ulb_X[1]
        num_lb = w_lb_X.shape[0]
        pseudo_counter = Counter(self.selected_label.tolist())
        if max(pseudo_counter.values()) < len(self._train_dataset.unlabeled_dataset):  # not all -1
            if self.threshold_warmup:
                for i in range(self.num_classes):
                    self.classwise_acc[i] = pseudo_counter[i] / max(pseudo_counter.values())
            else:
                wo_negative_one = copy.deepcopy(pseudo_counter)
                if -1 in wo_negative_one.keys():
                    wo_negative_one.pop(-1)
                for i in range(self.num_classes):
                    self.classwise_acc[i] = pseudo_counter[i] / max(wo_negative_one.values())

        inputs = torch.cat((w_lb_X, w_ulb_X, s_ulb_X))
        logits = self._network(inputs)
        logits_x_lb = logits[:num_lb]
        logits_x_ulb_w , logits_x_ulb_s = logits[num_lb:].chunk(2)
        logits_x_ulb_w = logits_x_ulb_w.detach()
        pseudo_label = torch.softmax(logits_x_ulb_w, dim=-1)
        if self.use_DA:
            if self.p_model == None:
                self.p_model = torch.mean(pseudo_label.detach(), dim=0)
            else:
                self.p_model = self.p_model * 0.999 + torch.mean(pseudo_label.detach(), dim=0) * 0.001
            pseudo_label = pseudo_label * self.p_target / self.p_model
            pseudo_label = (pseudo_label / pseudo_label.sum(dim=-1, keepdim=True))
        max_probs, max_idx = torch.max(pseudo_label, dim=-1)
        mask = max_probs.ge(self.threshold * (self.classwise_acc[max_idx] / (2. - self.classwise_acc[max_idx]))).float()
        select = max_probs.ge(self.threshold ).long()
        if ulb_idx[select == 1].nelement() != 0:
            self.selected_label[ulb_idx[select == 1]] = max_idx.long()[select == 1]
        if self.use_hard_labels is not True:
            pseudo_label = torch.softmax(logits_x_ulb_w / self.T, dim=-1)
        else:
            pseudo_label=max_idx

        result=(logits_x_lb,lb_y,logits_x_ulb_s,pseudo_label,mask)
        return result

    def get_loss(self,train_result,*args,**kwargs):
        logits_x_lb,lb_y,logits_x_ulb_s,pseudo_label,mask = train_result
        sup_loss=Cross_Entropy(reduction='mean')(logits=logits_x_lb,targets=lb_y)
        unsup_loss =(Cross_Entropy(reduction='none',use_hard_labels=self.use_hard_labels)(logits_x_ulb_s, pseudo_label) * mask).mean()
        loss = Semi_supervised_loss(self.lambda_u)(sup_loss ,unsup_loss)
        return loss

    def predict(self,X=None,valid=None):
        return DeepModelMixin.predict(self,X=X,valid=valid)

