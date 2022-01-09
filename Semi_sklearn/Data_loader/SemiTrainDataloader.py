from torch.utils.data.dataloader import DataLoader
from Semi_sklearn.Dataset.SemiTrainDataset import SemiTrainDataset
def SemiTrainDataLoader(DataLoader):
    def __init__(self,
                 batch_size= 1,
                 shuffle = False, sampler = None,
                 batch_sampler=None, Iterable = None,
                 num_workers = 0, collate_fn = None,
                 pin_memory = False, drop_last = True,
                 timeout = 0, worker_init_fn = None,
                 multiprocessing_context=None, generator=None,
                 *, prefetch_factor = 2,
                 persistent_workers= False,
                 batch_size_adjust=False):
        self.batch_size=batch_size
        if isinstance(self.batch_size,list):
            self.labled_batch_size,self.unlabled_batch_size=self.batch_size[0],self.batch_size[1]
        elif isinstance(self.batch_size,dict):
            self.labled_batch_size, self.unlabled_batch_size = self.batch_size['labled'], self.batch_size['unlabled']
        else:
            self.labled_batch_size, self.unlabled_batch_size=self.batch_size, self.batch_size

        self.shuffle=shuffle
        if isinstance(self.shuffle,list):
            self.labled_shuffle,self.unlabled_shuffle=self.shuffle[0],self.shuffle[1]
        elif isinstance(self.shuffle,dict):
            self.labled_shuffle,self.unlabled_shuffle = self.shuffle['labled'], self.shuffle['unlabled']
        else:
            self.labled_shuffle,self.unlabled_shuffle=self.shuffle, self.shuffle

        self.sampler=sampler
        if isinstance(self.sampler,list):
            self.labled_sampler,self.unlabled_sampler=self.sampler[0],self.sampler[1]
        elif isinstance(self.sampler,dict):
            self.labled_sampler,self.unlabled_sampler = self.sampler['labled'], self.sampler['unlabled']
        else:
            self.labled_sampler,self.unlabled_sampler=self.sampler, self.sampler

        self.batch_sampler=batch_sampler
        if isinstance(self.batch_sampler,list):
            self.labled_batch_sampler,self.unlabled_batch_sampler=self.batch_sampler[0],self.batch_sampler[1]
        elif isinstance(self.batch_sampler,dict):
            self.labled_batch_sampler,self.unlabled_batch_sampler = self.batch_sampler['labled'], self.batch_sampler['unlabled']
        else:
            self.labled_batch_sampler,self.unlabled_batch_sampler=self.batch_sampler, self.batch_sampler

        self.num_workers=num_workers
        if isinstance(self.num_workers,list):
            self.labled_num_workers,self.unlabled_num_workers=self.num_workers[0],self.num_workers[1]
        elif isinstance(self.num_workers,dict):
            self.labled_num_workers,self.unlabled_num_workers = self.num_workers['labled'], self.num_workers['unlabled']
        else:
            self.labled_num_workers,self.unlabled_num_workers=self.num_workers, self.num_workers

        self.collate_fn=collate_fn
        if isinstance(self.collate_fn,list):
            self.labled_collate_fn,self.unlabled_collate_fn=self.collate_fn[0],self.collate_fn[1]
        elif isinstance(self.collate_fn,dict):
            self.labled_collate_fn,self.unlabled_collate_fn= self.collate_fn['labled'], self.collate_fn['unlabled']
        else:
            self.labled_collate_fn,self.unlabled_collate_fn=self.collate_fn, self.collate_fn

        self.pin_memory=pin_memory
        if isinstance(self.pin_memory,list):
            self.labled_pin_memory,self.unlabled_pin_memory=self.pin_memory[0],self.pin_memory[1]
        elif isinstance(self.pin_memory,dict):
            self.labled_pin_memory,self.unlabled_pin_memory = self.pin_memory['labled'], self.pin_memory['unlabled']
        else:
            self.labled_pin_memory,self.unlabled_pin_memory=self.pin_memory, self.pin_memory

        self.drop_last=drop_last
        if isinstance(self.drop_last,list):
            self.labled_drop_last,self.unlabled_drop_last=self.drop_last[0],self.drop_last[1]
        elif isinstance(self.drop_last,dict):
            self.labled_drop_last,self.unlabled_drop_last = self.drop_last['labled'], self.drop_last['unlabled']
        else:
            self.labled_drop_last,self.unlabled_drop_last=self.drop_last, self.drop_last

        self.timeout=timeout
        if isinstance(self.timeout,list):
            self.labled_timeout,self.unlabled_timeout=self.timeout[0],self.timeout[1]
        elif isinstance(self.timeout,dict):
            self.labled_timeout,self.unlabled_timeout = self.timeout['labled'], self.timeout['unlabled']
        else:
            self.labled_timeout,self.unlabled_timeout=self.timeout, self.timeout

        self.worker_init_fn=worker_init_fn
        if isinstance(self.worker_init_fn,list):
            self.labled_worker_init_fn,self.unlabled_worker_init_fn=self.worker_init_fn[0],self.worker_init_fn[1]
        elif isinstance(self.worker_init_fn,dict):
            self.labled_worker_init_fn,self.unlabled_worker_init_fn = self.worker_init_fn['labled'], self.worker_init_fn['unlabled']
        else:
            self.labled_worker_init_fn,self.unlabled_worker_init_fn=self.worker_init_fn, self.worker_init_fn

        self.multiprocessing_context=multiprocessing_context
        if isinstance(self.multiprocessing_context,list):
            self.labled_multiprocessing_context,self.unlabled_multiprocessing_context=self.multiprocessing_context[0],self.multiprocessing_context[1]
        elif isinstance(self.multiprocessing_context,dict):
            self.labled_multiprocessing_context,self.unlabled_multiprocessing_context = self.multiprocessing_context['labled'], self.multiprocessing_context['unlabled']
        else:
            self.labled_multiprocessing_context,self.unlabled_multiprocessing_context=self.multiprocessing_context, self.multiprocessing_context

        self.generator=generator
        if isinstance(self.generator,list):
            self.labled_generator,self.unlabled_generator=self.generator[0],self.generator[1]
        elif isinstance(self.generator,dict):
            self.labled_generator,self.unlabled_generator = self.generator['labled'], self.generator['unlabled']
        else:
            self.labled_generator,self.unlabled_generator=self.generator, self.generator

        self.prefetch_factor=prefetch_factor
        if isinstance(self.prefetch_factor,list):
            self.labled_prefetch_factor,self.unlabled_prefetch_factor=self.prefetch_factor[0],self.prefetch_factor[1]
        elif isinstance(self.prefetch_factor,dict):
            self.labled_prefetch_factor,self.unlabled_prefetch_factor = self.prefetch_factor['labled'], self.prefetch_factor['unlabled']
        else:
            self.labled_prefetch_factor,self.unlabled_prefetch_factor=self.prefetch_factor, self.prefetch_factor

        self.persistent_workers=persistent_workers
        if isinstance(self.persistent_workers,list):
            self.labled_persistent_workers,self.unlabled_persistent_workers=self.persistent_workers[0],self.persistent_workers[1]
        elif isinstance(self.persistent_workers,dict):
            self.labled_persistent_workers,self.unlabled_persistent_workers = self.persistent_workers['labled'], self.persistent_workers['unlabled']
        else:
            self.labled_persistent_workers,self.unlabled_persistent_workers=self.persistent_workers, self.persistent_workers

        self.dataset=None
        self.labled_dataset=None
        self.unlabled_dataset=None
        self.labled_dataloader=None
        self.unlabled_dataloader=None
        self.len_labled=None
        self.len_unlabled=None
        self.batch_size_adjust=batch_size_adjust

    def get_dataloader(self,dataset=None,labled_dataset=None,unlabled_dataset=None,semitrain_class=SemiTrainDataset,mu=None):
        if dataset is not None:
            self.dataset=dataset
            self.labled_dataset=self.dataset.get_dataset(labled=True)
            self.unlabled_dataset = self.undataset.get_dataset(labled=False)
        elif labled_dataset is not None and unlabled_dataset is not None:
            self.labled_dataset=labled_dataset
            self.unlabled_dataset=unlabled_dataset
            self.dataset=semitrain_class()
            self.dataset.init_dataset(labled_dataset=self.labled_dataset,unlabled_dataset=self.unlabled_dataset)
        else:
            raise ValueError('No dataset')
        self.len_labled=self.dataset.__len__(labled=True)
        self.len_unlabled=self.dataset.__len__(labled=False)
        if self.batch_size_adjust:
            if self.len_labled < self.len_unlabled:
                self.unlabled_batch_size=self.labled_batch_size*(self.len_unlabled//self.len_labled)
            else:
                self.labled_batch_size = self.unlabled_batch_size * (self.len_labled//self.len_unlabled)
        if mu is not None:
            self.unlabled_batch_size=mu*self.labled_batch_size
        self.labled_dataloader=DataLoader(dataset=self.labled_dataset,
                            batch_size=self.labled_batch_size,
                            shuffle = self.labled_shuffle,
                            sampler = self.labled_sampler,
                            batch_sampler = self.labled_batch_sampler,
                            num_workers = self.labled_num_workers,
                            collate_fn = self.labled_collate_fn,
                            pin_memory = self.labled_pin_memory,
                            drop_last = self.labled_drop_last,
                            timeout = self.labled_timeout,
                            worker_init_fn = self.labled_worker_init_fn,
                            multiprocessing_context = self.labled_multiprocessing_context,
                            generator = self.labled_generator,
                            prefetch_factor = self.labled_prefetch_factor,
                            persistent_workers = self.labled_persistent_workers)
        self.unlabled_dataloader=DataLoader(dataset=self.unlabled_dataset,
                            batch_size=self.unlabled_batch_size,
                            shuffle = self.unlabled_shuffle,
                            sampler = self.unlabled_sampler,
                            batch_sampler = self.unlabled_batch_sampler,
                            num_workers = self.unlabled_num_workers,
                            collate_fn = self.unlabled_collate_fn,
                            pin_memory = self.unlabled_pin_memory,
                            drop_last = self.unlabled_drop_last,
                            timeout = self.unlabled_timeout,
                            worker_init_fn = self.unlabled_worker_init_fn,
                            multiprocessing_context = self.unlabled_multiprocessing_context,
                            generator = self.unlabled_generator,
                            prefetch_factor = self.unlabled_prefetch_factor,
                            persistent_workers = self.unlabled_persistent_workers)
        return self.labled_dataloader,self.unlabled_dataloader

