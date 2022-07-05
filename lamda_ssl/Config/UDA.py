from lamda_ssl.Transform.RandomHorizontalFlip import RandomHorizontalFlip
from lamda_ssl.Transform.RandomCrop import RandomCrop
from lamda_ssl.Transform.RandAugment import RandAugment
from lamda_ssl.Transform.Cutout import Cutout
from lamda_ssl.Opitimizer.SGD import SGD
from lamda_ssl.Scheduler.CosineAnnealingLR import CosineAnnealingLR
from lamda_ssl.Network.WideResNet import WideResNet
from lamda_ssl.Dataloader.UnlabeledDataloader import UnlabeledDataLoader
from lamda_ssl.Dataloader.LabeledDataloader import LabeledDataLoader
from lamda_ssl.Sampler.RandomSampler import RandomSampler
from lamda_ssl.Sampler.SequentialSampler import SequentialSampler
from sklearn.pipeline import Pipeline
from lamda_ssl.Evaluation.Classification.Accuracy import Accuracy
from lamda_ssl.Evaluation.Classification.Top_k_Accuracy import Top_k_Accurary
from lamda_ssl.Evaluation.Classification.Precision import Precision
from lamda_ssl.Evaluation.Classification.Recall import Recall
from lamda_ssl.Evaluation.Classification.F1 import F1
from lamda_ssl.Evaluation.Classification.AUC import AUC
from lamda_ssl.Evaluation.Classification.Confusion_Matrix import Confusion_Matrix
from lamda_ssl.Dataset.LabeledDataset import LabeledDataset
from lamda_ssl.Dataset.UnlabeledDataset import UnlabeledDataset
from lamda_ssl.Transform.Normalization import Normalization
from lamda_ssl.Transform.ImageToTensor import ImageToTensor
from lamda_ssl.Transform.ToImage import ToImage

mean = [0.4914, 0.4822, 0.4465]
std = [0.2471, 0.2435, 0.2616]

pre_transform = ToImage()
transforms = None
target_transform = None
transform = Pipeline([('ToTensor', ImageToTensor()),
                    ('Normalization', Normalization(mean=mean, std=std))
                    ])
unlabeled_transform = Pipeline([('ToTensor', ImageToTensor()),
                                ('Normalization', Normalization(mean=mean, std=std))
                                ])
test_transform = Pipeline([('ToTensor', ImageToTensor()),
                                ('Normalization', Normalization(mean=mean, std=std))
                                ])
valid_transform = Pipeline([('ToTensor', ImageToTensor()),
                                 ('Normalization', Normalization(mean=mean, std=std))
                                 ])

train_dataset=None
labeled_dataset=LabeledDataset(pre_transform=pre_transform,transforms=transforms,
                               transform=transform,target_transform=target_transform)

unlabeled_dataset=UnlabeledDataset(pre_transform=pre_transform,transform=unlabeled_transform)

valid_dataset=UnlabeledDataset(pre_transform=pre_transform,transform=valid_transform)

test_dataset=UnlabeledDataset(pre_transform=pre_transform,transform=test_transform)

# Batch sampler
train_batch_sampler=None
labeled_batch_sampler=None
unlabeled_batch_sampler=None
valid_batch_sampler=None
test_batch_sampler=None

# sampler
train_sampler=None
labeled_sampler=RandomSampler(replacement=True,num_samples=64*(2**20))
unlabeled_sampler=RandomSampler(replacement=True)
valid_sampler=SequentialSampler()
test_sampler=SequentialSampler()

#dataloader
train_dataloader=None
labeled_dataloader=LabeledDataLoader(batch_size=64,num_workers=0,drop_last=True)
unlabeled_dataloader=UnlabeledDataLoader(num_workers=0,drop_last=True)
valid_dataloader=UnlabeledDataLoader(batch_size=64,num_workers=0,drop_last=False)
test_dataloader=UnlabeledDataLoader(batch_size=64,num_workers=0,drop_last=False)

# network
network=WideResNet(num_classes=10,depth=28,widen_factor=2,drop_rate=0)

# optimizer
optimizer=SGD(lr=0.03,momentum=0.9,nesterov=True)

# scheduler
scheduler=CosineAnnealingLR(eta_min=0,T_max=2**20)

# augmentation
weakly_augmentation=Pipeline([('RandomHorizontalFlip',RandomHorizontalFlip()),
                              ('RandomCrop',RandomCrop(padding=0.125,padding_mode='reflect')),
                              ])

strongly_augmentation=Pipeline([('RandomHorizontalFlip',RandomHorizontalFlip()),
                              ('RandomCrop',RandomCrop(padding=0.125,padding_mode='reflect')),
                              ('RandAugment',RandAugment(n=2,m=10,num_bins=10)),
                              ('Cutout',Cutout(v=0.5,fill=(127, 127, 127))),
                              ])
augmentation={
    'weakly_augmentation':weakly_augmentation,
    'strongly_augmentation':strongly_augmentation
}

# evalutation
evaluation={
    'accuracy':Accuracy(),
    'top_5_accuracy':Top_k_Accurary(k=5),
    'precision':Precision(average='macro'),
    'Recall':Recall(average='macro'),
    'F1':F1(average='macro'),
    'AUC':AUC(multi_class='ovo'),
    'Confusion_matrix':Confusion_Matrix(normalize='true')
}

# model
weight_decay=5e-4
ema_decay=0.999
epoch=1
num_it_total=2**20
num_it_epoch=2**20
eval_epoch=None
eval_it=None
device='cpu'

parallel=None
file=None
verbose=False

threshold=0.8
lambda_u=1.0
T=0.4
mu=7
tsa_schedule=None
num_classes=None