import copy
from math import ceil
import torch
from Semi_sklearn.Base.SemiEstimator import SemiEstimator
from torch.utils.data.dataset import Dataset
from Semi_sklearn.Dataset.TrainDataset import TrainDataset
from abc import abstractmethod
from Semi_sklearn.Opitimizer.SemiOptimizer import SemiOptimizer
from Semi_sklearn.Scheduler.SemiScheduler import SemiScheduler
from Semi_sklearn.utils import EMA
from Semi_sklearn.utils import to_device
from torch.nn import Softmax
from Semi_sklearn.Data_loader.LabeledDataloader import LabeledDataLoader
from Semi_sklearn.Data_loader.UnlabeledDataloader import UnlabeledDataLoader
from Semi_sklearn.Data_loader.TrainDataloader import TrainDataLoader

class SemiDeepModelMixin(SemiEstimator):
    def __init__(self, train_dataset=None,
                 valid_dataset=None,
                 test_dataset=None,
                 train_dataloader=None,
                 labeled_dataloader=None,
                 unlabeled_dataloader=None,
                 valid_dataloader=None,
                 test_dataloader=None,
                 augmentation=None,
                 network=None,
                 epoch=1,
                 num_it_epoch=None,
                 num_it_total=None,
                 eval_epoch=None,
                 eval_it=None,
                 mu=None,
                 optimizer=None,
                 weight_decay=5e-4,
                 ema_decay=None,
                 scheduler=None,
                 device=None,
                 evaluation=None,
                 train_sampler=None,
                 labeled_sampler=None,
                 unlabeled_sampler=None,
                 train_batch_sampler=None,
                 labeled_batch_sampler=None,
                 unlabeled_batch_sampler=None,
                 valid_sampler=None,
                 valid_batch_sampler=None,
                 test_sampler=None,
                 test_batch_sampler=None,
                 parallel=None
                 ):
        self.train_dataset=train_dataset
        self.valid_dataset = valid_dataset if valid_dataset is not None else test_dataset
        self.test_dataset=test_dataset
        self.train_dataloader=train_dataloader
        self.labeled_dataloader=labeled_dataloader
        self.unlabeled_dataloader=unlabeled_dataloader
        self.valid_dataloader=valid_dataloader if valid_dataloader is not None else test_dataloader
        self.test_dataloader=test_dataloader
        self.augmentation=augmentation
        self.network=network
        self.epoch=epoch
        self.mu=mu
        self.optimizer=optimizer
        self.scheduler=scheduler
        self.device=device
        self.eval_epoch=eval_epoch
        self.eval_it=eval_it
        self.weight_decay=weight_decay
        self.ema_decay=ema_decay
        self.y_est=None
        self.y_true=None
        self.y_pred=None
        self.y_score=None
        self.num_it_epoch=num_it_epoch
        self.num_it_total=num_it_total
        self.evaluation=evaluation

        self.train_sampler=train_sampler
        self.train_batch_sampler=train_batch_sampler

        self.labeled_sampler=labeled_sampler
        self.unlabeled_sampler=unlabeled_sampler
        self.labeled_batch_sampler=labeled_batch_sampler
        self.unlabeled_batch_sampler = unlabeled_batch_sampler

        self.valid_sampler=valid_sampler if valid_sampler is not None else test_sampler
        self.valid_batch_sampler=valid_batch_sampler if valid_batch_sampler is not None else test_batch_sampler

        self.test_sampler=test_sampler
        self.test_batch_sampler=test_batch_sampler

        self.parallel=parallel
        self._optimizer=copy.deepcopy(self.optimizer)
        self._network=copy.deepcopy(self.network)
        self._scheduler=copy.deepcopy(self.scheduler)

        self._train_sampler=copy.deepcopy(self.train_sampler)
        self._labeled_sampler = copy.deepcopy(self.labeled_sampler)
        self._unlabeled_sampler = copy.deepcopy(self.unlabeled_sampler)
        self._valid_sampler = copy.deepcopy(self.valid_sampler)
        self._test_sampler=copy.deepcopy(self.test_sampler)

        self._train_batch_sampler=copy.deepcopy(self.train_batch_sampler)
        self._labeled_batch_sampler = copy.deepcopy(self.labeled_batch_sampler)
        self._unlabeled_batch_sampler = copy.deepcopy(self.unlabeled_batch_sampler)
        self._valid_batch_sampler=copy.deepcopy(self.valid_batch_sampler)
        self._test_batch_sampler=copy.deepcopy(self.test_batch_sampler)

        self._train_dataset=copy.deepcopy(self.train_dataset)
        self._valid_dataset = copy.deepcopy(self.valid_dataset)
        self._test_dataset=copy.deepcopy(self.test_dataset)

        self._train_dataloader=copy.deepcopy(self.train_dataloader)
        self._labeled_dataloader = copy.deepcopy(self.labeled_dataloader)
        self._unlabeled_dataloader = copy.deepcopy(self.unlabeled_dataloader)
        self._valid_dataloader=copy.deepcopy(self.valid_dataloader)
        self._test_dataloader = copy.deepcopy(self.test_dataloader)

        self._augmentation=copy.deepcopy(self.augmentation)
        self._evaluation=copy.deepcopy(self.evaluation)
        self._parallel=copy.deepcopy(self.parallel)

        self._epoch=0
        self.it_total=0
        self.loss=None
        self.weakly_augmentation=None
        self.strongly_augmentation=None
        self.normalization=None
        self.ema=None
        self._estimator_type=None
        self.init_model()
        self.init_epoch()
        self.init_ema()
        self.init_augmentation()

    def init_model(self):
        if self.device is not None and self.device is not 'cpu':
            torch.cuda.set_device(self.device)
        self._network=self._network.to(self.device)
        if self._parallel is not None:
            self._parallel=self._parallel.init_parallel(self._network)

    def init_augmentation(self):
        if self._augmentation is not None:
            if isinstance(self._augmentation, dict):
                self.weakly_augmentation = self._augmentation['augmentation'] \
                    if 'augmentation' in self._augmentation.keys() \
                    else self._augmentation['weakly_augmentation']
                if 'strongly_augmentation' in self._augmentation.keys():
                    self.strongly_augmentation = self._augmentation['strongly_augmentation']
            elif isinstance(self._augmentation, (list, tuple)):
                self.weakly_augmentation = self._augmentation[0]
                if len(self._augmentation) > 1:
                    self.strongly_augmentation = self._augmentation[1]
            else:
                self.weakly_augmentation = copy.deepcopy(self._augmentation)
            if self.strongly_augmentation is None:
                self.strongly_augmentation = copy.deepcopy(self.weakly_augmentation)

    def init_transform(self):
        if self.weakly_augmentation is not None:
            self._train_dataset.add_transform(self.weakly_augmentation,dim=1,x=0,y=0)
            self._train_dataset.add_unlabeled_transform(self.weakly_augmentation, dim=1, x=0, y=0)

    def init_ema(self):
        if self.ema_decay is not None:
            self.ema=EMA(model=self._network,decay=self.ema_decay)
            self.ema.register()
        else:
            self.ema=None

    def init_optimizer(self):
        if isinstance(self._optimizer,SemiOptimizer):
            no_decay = ['bias', 'bn']
            grouped_parameters = [
                {'params': [p for n, p in self._network.named_parameters() if not any(
                    nd in n for nd in no_decay)], 'weight_decay': self.weight_decay},
                {'params': [p for n, p in self._network.named_parameters() if any(
                    nd in n for nd in no_decay)], 'weight_decay': 0.0}
            ]
            self._optimizer=self._optimizer.init_optimizer(params=grouped_parameters)

    def init_scheduler(self):
        if isinstance(self._scheduler,SemiScheduler):
            self._scheduler=self._scheduler.init_scheduler(optimizer=self._optimizer)

    def init_epoch(self):
        if self.num_it_epoch is not None and self.epoch is not None:
            self.num_it_total=self.epoch*self.num_it_epoch
        if self.num_it_total is not None and self.epoch is not None:
            self.num_it_epoch=ceil(self.num_it_total/self.epoch)
        if self.num_it_total is not None and self.num_it_epoch is not None:
            self.epoch=ceil(self.num_it_total/self.num_it_epoch)

    def init_train_dataset(self,X=None,y=None,unlabeled_X=None):
        if isinstance(X,TrainDataset):
            self._train_dataset=X
        elif isinstance(X,Dataset) and y is None:
            self._train_dataset.init_dataset(labeled_dataset=X, unlabeled_dataset=unlabeled_X)
        else:
            self._train_dataset.init_dataset(labeled_X=X, labeled_y=y,unlabeled_X=unlabeled_X)

    def init_train_dataloader(self):
        # if self.
        if self._train_dataloader is not None:
            self._labeled_dataloader,self._unlabeled_dataloader=self._train_dataloader.init_dataloader(dataset=self._train_dataset,
                                                                                       sampler=self._train_sampler,
                                                                                       batch_sampler=self._train_batch_sampler,
                                                                                       mu=self.mu)
        else:
            self._train_dataloader=TrainDataLoader(labeled_dataloader=self._labeled_dataloader,unlabeled_dataloader=self._unlabeled_dataloader)
            self._train_sampler={'labeled':self._labeled_sampler,'unlabeled':self._unlabeled_sampler}
            self._train_batch_sampler={'labeled':self._labeled_batch_sampler,'unlabeled':self._unlabeled_batch_sampler}
            self._labeled_dataloader, self._unlabeled_dataloader = self._train_dataloader.init_dataloader(
                dataset=self._train_dataset,
                sampler=self._train_sampler,
                batch_sampler=self._train_batch_sampler,
                mu=self.mu)

    def init_pred_dataset(self, X=None,valid=False):
        if valid:
            if isinstance(X,Dataset):
                self._valid_dataset=X
            else:
                # print('init_pred_dataset')
                self._valid_dataset=self._valid_dataset.init_dataset(X=X)
        else:
            if isinstance(X,Dataset):
                self._test_dataset=X
            else:
                self._test_dataset=self._test_dataset.init_dataset(X=X)

    def init_pred_dataloader(self,valid=False):
        # print(self.valid_dataloader)
        if valid:
            # print('init_pred_dataloader')
            # print(self._valid_dataset)
            self._pred_dataloader=self._valid_dataloader.init_dataloader(self._valid_dataset,
                                                            sampler=self._valid_sampler,
                                                            batch_sampler=self._valid_batch_sampler)
        else:
            self._pred_dataloader=self._test_dataloader.init_dataloader(self._test_dataset,
                                                            sampler=self._test_sampler,
                                                            batch_sampler=self._test_batch_sampler)

        # print(self._pred_dataloader)
        # for i ,X,y in self._pred_dataloader:
        #     print(i,X,y)

    def fit(self,X=None,y=None,unlabeled_X=None,valid_X=None,valid_y=None):
        self.init_train_dataset(X,y,unlabeled_X)
        self.init_train_dataloader()
        self.start_fit()
        self.epoch_loop(valid_X,valid_y)
        self.end_fit()
        return self

    def epoch_loop(self,valid_X=None,valid_y=None):
        self.it_total = 0
        for self._epoch in range(self.epoch):
            self.it_epoch=0
            if self.it_total>=self.num_it_total:
                break
            self.start_epoch()
            self.train_batch_loop(valid_X,valid_y)
            self.end_epoch()
            if valid_X is not None and self.eval_epoch is not None and self._epoch % self.eval_epoch==0:
                self.evaluate(X=valid_X,y=valid_y,valid=True)

    def train_batch_loop(self,valid_X=None,valid_y=None):
        for (lb_idx, lb_X, lb_y), (ulb_idx, ulb_X, _) in zip(self._labeled_dataloader, self._unlabeled_dataloader):
            if self.it_epoch >= self.num_it_epoch or self.it_total >= self.num_it_total:
                break

            self.start_batch_train()

            lb_idx = to_device(lb_idx,self.device)

            lb_X = to_device(lb_X,self.device)
            lb_y = to_device(lb_y,self.device)
            ulb_idx = to_device(ulb_idx,self.device)
            ulb_X  = to_device(ulb_X,self.device)

            train_result = self.train(lb_X=lb_X, lb_y=lb_y, ulb_X=ulb_X, lb_idx=lb_idx, ulb_idx=ulb_idx)

            self.loss = self.get_loss(train_result)

            self.end_batch_train()

            self.it_total += 1
            self.it_epoch += 1
            print(self.it_total)

            if valid_X is not None and self.eval_it is not None and self.it_total % self.eval_it == 0:
                self.evaluate(X=valid_X, y=valid_y,valid=True)

    def pred_batch_loop(self):
        with torch.no_grad():
            for idx,X,_ in self._pred_dataloader:
                self.start_batch_test()

                idx=to_device(idx,self.device)
                X=to_device(X,self.device)

                _est=self.estimate(X=X,idx=idx)
                self.y_est=torch.cat((self.y_est,_est),0)

                self.end_batch_test()

    @torch.no_grad()
    def predict(self,X=None,valid=False):

        self.init_pred_dataset(X,valid)

        self.init_pred_dataloader(valid)

        self.start_predict()

        self.pred_batch_loop()

        self.end_predict()

        return self.y_pred

    @torch.no_grad()
    def evaluate(self,X,y=None,valid=False):

        if isinstance(X,Dataset) and y is None:
            y=getattr(X,'y')

        y_pred=self.predict(X,valid=valid).cpu()
        y_score=self.y_score.cpu()

        if self.evaluation is None:
            return None
        elif isinstance(self.evaluation,(list,tuple)):
            result=[]
            for eval in self.evaluation:
                result.append(eval.scoring(y,y_pred,y_score))
            return result
        elif isinstance(self.evaluation,dict):
            result={}
            for key,val in self.evaluation.items():
                result[key]=val.scoring(y,y_pred,y_score)
                print(key,' ',result[key])
            return result
        else:
            result=self.evaluation.scoring(y,y_pred,y_score)
            return result

    def start_fit(self, *args, **kwargs):
        self._network.zero_grad()
        self._network.train()

    def start_epoch(self, *args, **kwargs):
        pass

    def end_epoch(self, *args, **kwargs):
        pass

    def start_batch_train(self, *args, **kwargs):
        pass

    def end_batch_train(self, *args, **kwargs):
        self.loss.backward()
        self.optimize()

    def start_batch_test(self, *args, **kwargs):
        pass

    def end_batch_test(self, *args, **kwargs):
        pass

    def end_fit(self, *args, **kwargs):
        pass

    def start_predict(self, *args, **kwargs):
        self._network.eval()
        if self.ema is not None:
            self.ema.apply_shadow()
        self.y_est = torch.Tensor().to(self.device)

    def end_predict(self, *args, **kwargs):
        self.y_pred = self.get_predict_result(self.y_est)
        if self.ema is not None:
            self.ema.restore()
        self._network.train()

    def optimize(self,*args,**kwargs):
        self._optimizer.step()
        self._scheduler.step()
        if self.ema is not None:
            self.ema.update()
        self._network.zero_grad()

    @torch.no_grad()
    def estimate(self,X,idx=None,*args,**kwargs):
        outputs = self._network(X)
        return outputs

    @torch.no_grad()
    def get_predict_result(self,y_est,*args,**kwargs):
        if self._estimator_type=='classifier':
            self.y_score = Softmax(dim=-1)(y_est)
            max_probs, y_pred = torch.max(self.y_score, dim=-1)
            return y_pred
        else:
            self.y_score=y_est
            return y_est

    @abstractmethod
    def train(self,lb_X,lb_y,ulb_X,lb_idx=None,ulb_idx=None,*args,**kwargs):
        raise NotImplementedError

    @abstractmethod
    def get_loss(self,train_result,*args,**kwargs):
        raise NotImplementedError