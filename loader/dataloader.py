import numpy as np
import logging
from torch.utils.data import DataLoader as DD
from torch.utils.data import Dataset
from torch.utils.data.dataloader import default_collate
from torch.utils.data.sampler import SubsetRandomSampler
import pandas as pd
import pickle

class CellDataset(Dataset):
    def __init__(self, fn):
        super(Dataset, self).__init__()
        with open(fn, 'rb') as file:
            self.dataframe = pickle.load(file)

    def __getitem__(self, index):
        data = self.dataframe.iloc[index]
        ans = data[1]
        operating_type = data[2]
        transition = data[3]
        capacitance = data[4]
        process = data[5].astype('float64')
        voltage = data[6]
        temperature = data[7].astype('float64')
        rise_capacitance = data[8]
        fall_capacitance = data[9]
        global_param = [transition, capacitance, process, voltage, temperature, rise_capacitance, fall_capacitance]
        function = data[10]
        when = data[11]
        related_pin = data[12]

        return ans, operating_type, global_param, function, when, related_pin

    def __len__(self):
        return len(self.dataframe)

class BaseDataLoader(DD):
    """
    Base class for all data loaders
    """
    def __init__(self, dataset, batch_size, shuffle, validation_split, num_workers, collate_fn=default_collate):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_split = validation_split
        self.shuffle = shuffle

        self.batch_idx = 0
        self.n_samples = len(dataset)

        self.sampler, self.valid_sampler = self._split_sampler(self.validation_split)

        self.init_kwargs = {
            'dataset': dataset,
            'batch_size': batch_size,
            'shuffle': self.shuffle,
            'collate_fn': collate_fn,
            'num_workers': num_workers
        }
        super(BaseDataLoader, self).__init__(sampler=self.sampler, **self.init_kwargs)

    def _split_sampler(self, split):
        if split == 0.0:
            return None, None

        idx_full = np.arange(self.n_samples)

        np.random.seed(0)
        np.random.shuffle(idx_full)
        len_valid = int(self.n_samples * split)
        
        valid_idx = idx_full[0:len_valid]
        train_idx = np.delete(idx_full, np.arange(0, len_valid))

        train_sampler = SubsetRandomSampler(train_idx)
        valid_sampler = SubsetRandomSampler(valid_idx)

        # turn off shuffle option which is mutually exclusive with sampler
        self.shuffle = False
        self.n_samples = len(train_idx)

        return train_sampler, valid_sampler

    def split_validation(self):
        if self.valid_sampler is None:
            return None
        else:
            return DD(sampler=self.valid_sampler, **self.init_kwargs)
        
class DataLoader(BaseDataLoader):
    def __init__(self, dataset, batch_size, shuffle, validation_split, num_workers = 0):
        collate_fn = default_collate
        super(DataLoader, self).__init__(dataset, batch_size, shuffle, validation_split, num_workers, collate_fn)
        
def build_loader(cfg, is_training):
    logger = logging.getLogger('dataloader')
    batch_size = cfg['DATALOADER']['batch_size']
    shuffle = cfg['DATALOADER']['shuffle']
    validation_split = cfg['DATALOADER']['val_split']
    num_workers = cfg['DATALOADER']['num_worker']
    if is_training:
        fn = 'data/train/' + cfg['DATA']['fn']
    else:
        fn = 'data/test/' + cfg['DATA']['fn']

    dataset = CellDataset(fn)
        
    logger.info('Setup dataset from [{}].'.format(fn))

    return DataLoader(dataset, batch_size, shuffle, validation_split, num_workers)