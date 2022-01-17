from Semi_sklearn.Dataset.LabledDataset import LabledDataset
from torchvision.datasets.vision import VisionDataset
from Semi_sklearn.utils import indexing

class LabledVisionDataset(LabledDataset,VisionDataset):
    def __init__(self,
                 root=None,
                 transforms=None,
                 transform=None,
                 target_transform=None
                 ):
        LabledDataset.__init__(self)
        VisionDataset.__init__(self,root=root,transforms=transforms,transform=transform,target_transform=target_transform)

    def __getitem__(self, i):

        X, y = self.X, self.y

        Xi = indexing(X, i, self.X_indexing_method)
        yi = indexing(y, i, self.y_indexing_method)
        # Xi = Image.fromarray(Xi)

        Xi, yi = self._transform(Xi, yi)
        if self.transform is not None:
            Xi=self.transform(Xi)
            # if isinstance(self.transform,(list,tuple)):
            #     trans_Xi=[trans(Xi) for trans in self.transform]
            # elif isinstance(self.transform,dict):
            #     trans_Xi={}
            #     for key,val in self.transform:
            #         trans_Xi[key]=val(Xi)
            # else:
            #     trans_Xi=self.transform(Xi)
            # Xi = trans_Xi

        if self.target_transform is not None:
            yi = self.target_transform(yi)

        return Xi, yi

    def __len__(self):
        return LabledDataset.__len__(self)

