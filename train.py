from loader import build_loader
from model import build_model
from trainer import build_trainer
from utils import ensure_dir
import logging, coloredlogs
import argparse
import yaml
import os
import torch

parser = argparse.ArgumentParser()
parser.add_argument('--cfg_path', type=str, default='config/default.yaml')
parser.add_argument('--checkpoint', type=str, default='saved/best.pth')
parser.add_argument('--eval_only', action='store_true', default=False)
opt = parser.parse_args()

with open(opt.cfg_path, 'r') as f:
    cfg = yaml.safe_load(f)


def env_setup(cfg):
    # handle dir for saving
    ensure_dir(cfg['SAVED']['output_dir'])

    # setting logger
    handlers = [logging.FileHandler(os.path.join(cfg['SAVED']['output_dir'],'output.log'),
                                    mode = 'w'), logging.StreamHandler()]
    logging.basicConfig(handlers = handlers, level=logging.INFO)
    logger = logging.getLogger('root')
    coloredlogs.install(logger = logger, fmt='%(asctime)s [%(name)s] %(levelname)s %(message)s')
    logger.info('Setup output directory - {}.'.format(cfg['SAVED']['output_dir']))

if __name__ == '__main__':
    # env setting
    env_setup(cfg)
    
    # dataloader setting
    TRAIN_D = build_loader(cfg, True)
    TEST_D = build_loader(cfg, False)
    
    # model setting
    model = build_model(cfg)
    
    if opt.eval_only:
        assert opt.checkpoint is not None, 'Please provide model ckpt for testing'
        checkpoint = torch.load(opt.checkpoint)
        model.load_state_dict(checkpoint['state_dict'])
        T = build_trainer(cfg=cfg, opt=opt, model=model, train_dataloader=TRAIN_D, test_dataloader=TEST_D)
        T.test()
    else:
        T = build_trainer(cfg=cfg, opt=opt, model=model, train_dataloader=TRAIN_D, test_dataloader=TEST_D)
        T.train()