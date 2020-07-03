import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
import logging
import os
import random
import torch.nn as nn
import math
import json
import matplotlib.pyplot as plt
import pickle


class Trainer:    
    def __init__(self, model, train_dataloader, test_dataloader, cfg, opt):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.cfg = cfg
        self.opt = opt
        self.n_epochs = self.cfg['TRAINER']['n_epochs']
        self.save_dir = self.cfg['SAVED']['output_dir']
        self.n_show_loss = self.cfg['TRAINER']['n_show_loss']
        self.train_dataloader = train_dataloader
        self.test_dataloader = test_dataloader
        self.batch_size = train_dataloader.batch_size
        self.device = self._prepare_gpu()
        self.tb_writer = SummaryWriter(log_dir=os.path.join(self.save_dir, 'tensorboard'))
        self.model = model
        self.pad_index = 0
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-4, 
                                          betas=(0.9, 0.999), weight_decay=0.01)        
        self.begin_epoch = 0
        self.all_log = []
        self._resume_checkpoint(opt.checkpoint)
                
    def train(self):
        opt = self.opt
        all_log = self.all_log
        self.model.to(self.device)

        best_score = 10
        for i in range(self.begin_epoch, self.begin_epoch + self.n_epochs):
            log = self._run_epoch(i, 'train')
            val_log = self._run_epoch(i, 'test')
            merged_log = {**log, **val_log}
            all_log.append(merged_log)
            if val_log['test_score'] < best_score:
                checkpoint = {
                    'log': all_log,
                    'state_dict': self.model.state_dict(),
                    'optimizer': self.optimizer.state_dict(),
                    'epoch': i,
                }
                check_path = os.path.join(self.save_dir, 'best.pth')
                torch.save(checkpoint, check_path)
                best_score = val_log['test_score']
            if (i + 1)%10 == 0 :
                checkpoint = {
                    'log': all_log,
                    'state_dict': self.model.state_dict(),
                    'optimizer': self.optimizer.state_dict(),
                    'epoch': i,
                }

                check_path = os.path.join(self.save_dir, 'checkpoint_' + str(i+1) + '.pth')
                torch.save(checkpoint, check_path)
                self.logger.info("SAVING CHECKPOINT: {}".format(check_path))

    def test(self):
        self.model.to(self.device)
        self._run_epoch(self.begin_epoch, 'test')

    def error_rate(self, gt, pred):
        return torch.sum(torch.abs(pred-gt) / gt, axis=0) / self.batch_size

    def _run_epoch(self, epoch, phase):
        self.logger.info('[Phase: {}, Epoch: {}]'.format(phase, epoch))
        if phase == 'train':
            self.model.train()
            dataloader = self.train_dataloader
        else:
            self.model.eval()
            dataloader = self.test_dataloader

        total_loss = 0
        total_score = 0
        for batch_idx, (ans, operating_type, global_params, function, when, related_pin) \
                                                    in enumerate(dataloader):
            ans = ans.to(self.device).unsqueeze(1)
            operating_type = operating_type.to(self.device)
            for i in range(len(global_params)):
                if i == 0:
                    global_param = global_params[i].unsqueeze(1)
                else:
                    global_param = torch.cat((global_param, global_params[i].unsqueeze(1)), dim=1)
            global_param = global_param.to(self.device)
            function = function.to(self.device)
            when = when.to(self.device).float()
            related_pin = related_pin.to(self.device)

            if phase == 'train':
                loss, pred = self.model(ans, operating_type, global_param, function, when, related_pin)
            else:
                loss, pred = self.model(ans, operating_type, global_param, function, when, related_pin)
            
            score = self.error_rate(ans.flatten(), pred.flatten()).item()
            total_score += score
            
            if phase == 'train':
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                total_loss += loss.item()
            else:
                total_loss += loss.item()
                
            if phase == 'train':
                if batch_idx % self.n_show_loss == 0:
                    out_info = '[%d/%d] total_loss: %.4f '%\
                            (batch_idx + 1, len(dataloader), loss.item())
                    out_info += 'Error_Rate %.4f'%(score)
                    self.logger.info(out_info)
            else:
                if batch_idx % self.n_show_loss == 0:
                    out_info = '[%d/%d] total_loss: %.4f '%\
                                (batch_idx + 1, len(dataloader), loss)
                    out_info += 'Error_Rate %.4f'%(score)
                    self.logger.info(out_info)
                
#         acc = (total_correct.float() / total_label.float()).item()
        log = self._log_epoch(epoch, total_loss/len(dataloader), total_score/len(dataloader),
                   phase, self.optimizer)
        return log
    
    def _log_epoch(self, epoch, total_loss, total_score, phase, optimizer):
        
        log = {
            'epoch': epoch,
            phase + '_loss': total_loss,
            phase + '_score': total_score,
        }
        self.tb_writer.add_scalar( phase + "/Loss", total_loss, epoch)
        self.tb_writer.add_scalar( phase + "/Error_Rate", total_score, epoch)
        self.tb_writer.add_scalar( phase + "/lr", optimizer.param_groups[0]['lr'], epoch)

        self.logger.info('[TOTAL] Loss: %.4f  Error_Rate: %.4f'%(total_loss, total_score))
        self.logger.debug("="*30)
        return log

    def _prepare_gpu(self):
        n_gpu = torch.cuda.device_count()
        device = torch.device('cuda:0' if n_gpu > 0 else 'cpu')
        torch.backends.cudnn.benchmark = False
        return device

    def _resume_checkpoint(self, path):
        if path == None: return
        try:
            checkpoint = torch.load(path)
            self.model.load_state_dict(checkpoint['state_dict']).to(self.device)

            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.begin_epoch = checkpoint['log'][-1]['epoch'] + 1
            self.all_log = checkpoint['log']
        except:
            self.logger.error('[Resume] Cannot load from checkpoint')

                                     
def build_trainer(cfg, opt, model, train_dataloader, test_dataloader):
    logger = logging.getLogger('Trainer')
    
    T = Trainer(model = model, train_dataloader=train_dataloader, test_dataloader=test_dataloader, cfg=cfg, opt=opt)
    logger.info('Setup trainer {}.'.format(T.__class__.__name__))
    return T