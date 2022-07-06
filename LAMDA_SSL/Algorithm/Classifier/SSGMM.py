import copy
from LAMDA_SSL.Base.InductiveEstimator import InductiveEstimator
from sklearn.base import ClassifierMixin
import numpy as np
from torch.utils.data.dataset import Dataset
from LAMDA_SSL.utils import class_status
import LAMDA_SSL.Config.SSGMM as config

class SSGMM(InductiveEstimator,ClassifierMixin):
    def __init__(self,tolerance=config.tolerance, max_iterations=config.max_iterations, num_classes=config.num_classes,
                 evaluation=config.evaluation,verbose=config.verbose,file=config.file):
        # >> Parameter
        # >> - num_classes: The number of classes.
        # >> - tolerance: Tolerance for iterative convergence.
        # >> - max_iterations: The maximum number of iterations.
        self.num_classes=num_classes
        self.tolerance=tolerance
        self.max_iterations=max_iterations
        self.evaluation = evaluation
        self.verbose = verbose
        self.file = file
        self.y_pred=None
        self.y_score=None
        self._estimator_type = ClassifierMixin._estimator_type

    def normfun(self,x, mu, sigma):

        k = len(x)

        dis = np.expand_dims(x - mu, axis=0)

        pdf = np.exp(-0.5 * dis.dot(np.linalg.inv(sigma)).dot(dis.T)) / np.sqrt(
            ((2 * np.pi) ** k) * np.linalg.det(sigma))

        return pdf

    def fit(self,X,y,unlabeled_X):
        self.num_classes = self.num_classes if self.num_classes is not None else \
            class_status(y).num_classes
        L=len(X)
        U=len(unlabeled_X)
        m=L+U
        labele_set={}

        for _ in range(self.num_classes):
            labele_set[_]=set()
        for _ in range(L):
            labele_set[y[_]].add(_)
        self.mu=[]
        self.alpha=[]

        self.gamma=np.empty((U,self.num_classes))
        self.alpha = np.random.rand(self.num_classes)
        self.alpha = self.alpha / self.alpha.sum()
        self.mu = np.random.rand(self.num_classes, X.shape[1])
        self.sigma = np.empty((self.num_classes, X.shape[1], X.shape[1]))
        for i in range(self.num_classes):
            self.sigma[i] = np.eye(X.shape[1])

        for _ in range(self.max_iterations):
            # E Step
            pre=copy.copy(self.alpha)

            for j in range(U):
                _sum=0
                for i in range(self.num_classes):
                    _sum+=self.alpha[i]*self.normfun(unlabeled_X[j],self.mu[i],self.sigma[i])
                for i in range(self.num_classes):
                    self.gamma[j][i]=self.alpha[i]*self.normfun(unlabeled_X[j],self.mu[i],self.sigma[i])/_sum
                    # print(self.gamma[j][i])


            # M step
            for i in range(self.num_classes):
                _sum_mu=0
                _sum_sigma=np.zeros((X.shape[1],X.shape[1]))
                _norm=0
                _norm+=len(labele_set[i])

                for j in labele_set[i]:
                    _sum_mu+=X[j]
                for j in range(U):
                    _sum_mu+=self.gamma[j][i]*unlabeled_X[j]
                    _norm+=self.gamma[j][i]

                self.mu[i]=_sum_mu/_norm

                self.alpha[i]=_norm/m


                for j in labele_set[i]:
                    _sum_sigma+=np.outer(X[j]-self.mu[i],X[j]-self.mu[i])

                for j in range(U):
                    _sum_sigma += self.gamma[j][i]*np.outer(unlabeled_X[j] - self.mu[i], unlabeled_X[j] - self.mu[i])
                self.sigma[i]=_sum_sigma/_norm

            isOptimal = True
            for i in range(self.num_classes):
                if abs((self.alpha[i] - pre[i])/pre[i])>self.tolerance:
                    isOptimal=False

            if isOptimal:
                break

        return self

    def predict_proba(self,X):
        y_proba=np.empty((len(X),self.num_classes))
        for i in range(len(X)):
            _sum=0
            for j in range(self.num_classes):
                _sum+=self.normfun(X[i],self.mu[j],self.sigma[j])
            for j in range(self.num_classes):
                y_proba[i][j]=self.normfun(X[i],self.mu[j],self.sigma[j])/_sum
        return y_proba

    def predict(self,X):
        y_proba=self.predict_proba(X)
        y_pred=np.argmax(y_proba, axis=1)
        return y_pred

    def evaluate(self,X,y=None):

        if isinstance(X,Dataset) and y is None:
            y=getattr(X,'y')

        self.y_score = self.predict_proba(X)
        self.y_pred=self.predict(X)


        if self.evaluation is None:
            return None
        elif isinstance(self.evaluation,(list,tuple)):
            result=[]
            for eval in self.evaluation:
                score=eval.scoring(y,self.y_pred,self.y_score)
                if self.verbose:
                    print(score, file=self.file)
                result.append(score)
            self.result = result
            return result
        elif isinstance(self.evaluation,dict):
            result={}
            for key,val in self.evaluation.items():

                result[key]=val.scoring(y,self.y_pred,self.y_score)

                if self.verbose:
                    print(key,' ',result[key],file=self.file)
                self.result = result
            return result
        else:
            result=self.evaluation.scoring(y,self.y_pred,self.y_score)
            if self.verbose:
                print(result, file=self.file)
            self.result=result
            return result



