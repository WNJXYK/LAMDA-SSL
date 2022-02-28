from Semi_sklearn.Scheduler.LambdaLR import LambdaLR

class Linear_warmup(LambdaLR):
    def __init__(self,
                 num_training_steps,
                 num_warmup_steps=0,
                 start_factor=0,
                 end_factor=1,
                 last_epoch=-1):
        self.start_factor=start_factor
        self.end_factor=end_factor
        self.num_warmup_steps=num_warmup_steps
        self.num_training_steps=num_training_steps
        super().__init__(lr_lambda=self._lr_lambda,last_epoch=last_epoch)

    def _lr_lambda(self,current_step):
        if current_step > self.num_warmup_steps:
            return  self.start_factor+float(self.num_training_steps - current_step) \
                    / (self.num_training_steps - self.num_warmup_steps)*(self.end_factor-self.start_factor)
        return 1


