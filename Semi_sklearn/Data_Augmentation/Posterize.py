from Semi_sklearn.Data_Augmentation.Augmentation import Augmentation
import torchvision.transforms.functional as F
class Posterize(Augmentation):
    def __init__(self, v):
        super().__init__()
        v = int(v)
        self.v = max(1, v)

    def transform(self,X):
        if X is not None:
            X=F.posterize(X, self.v)
            return X
        else:
            raise ValueError('No data to augment')