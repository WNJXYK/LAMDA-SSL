from LAMDA_SSL.Evaluation.Cluster.EvaluationCluster import EvaluationCluster
from sklearn.metrics import fowlkes_mallows_score
from LAMDA_SSL.utils import partial

class Fowlkes_Mallows_Score(EvaluationCluster):
    def __init__(self,sparse=False):
        # >> Parameter
        # >> - sparse: Whether to use sparse matrices for computation.
        super().__init__()
        self.score=partial(fowlkes_mallows_score,sparse=sparse)

    def scoring(self,y_true=None,clusters=None,X=None):
        return self.score(labels_true=y_true,labels_pred=clusters)