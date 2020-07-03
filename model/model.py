import torch.nn as nn
import numpy as np
import torch
import logging

class Feature_Embedding(nn.Module):
    def __init__(self, vocab_size, hidden_size):
        super(Feature_Embedding, self).__init__()
        self.type_embedding = nn.Embedding(4, hidden_size//2)
        self.projection = nn.Linear(7, hidden_size)
        self.function_embedding = nn.Embedding(vocab_size, hidden_size)
        self.function_encoder = nn.GRU(input_size = hidden_size, hidden_size = hidden_size, num_layers = 1, dropout = 0, batch_first = True)
        self.when_embedding = nn.Linear(vocab_size, hidden_size)
        self.related_pin_embedding = nn.Embedding(vocab_size, hidden_size//2)
        self.fusion = nn.Linear(hidden_size*4, hidden_size)
        self.dropout = nn.Dropout(p=0.2)

    def forward(self, operating_type, global_param, function, when, related_pin):
        type_embedding = self.type_embedding(operating_type)
        projection = self.projection(global_param)
        function_embedding = self.function_embedding(function)
        function_embedding, _ = self.function_encoder(function_embedding)
        when_embedding = self.when_embedding(when)
        related_pin_embedding = self.related_pin_embedding(related_pin)
        embedding = self.fusion(torch.cat((type_embedding, projection, function_embedding[:, -1], when_embedding, related_pin_embedding), dim=-1))
        embedding = self.dropout(embedding)
        return embedding

class Feature_Embedding_2(nn.Module):
    def __init__(self, vocab_size, hidden_size):
        super(Feature_Embedding_2, self).__init__()
        self.type_embedding = nn.Embedding(4, hidden_size//2)
        self.projection = nn.Linear(7, hidden_size)
        self.fusion = nn.Linear(hidden_size + hidden_size//2, hidden_size)
        self.dropout = nn.Dropout(p=0.2)

    def forward(self, operating_type, global_param, function, when, related_pin):
        type_embedding = self.type_embedding(operating_type)
        projection = self.projection(global_param)
        embedding = self.fusion(torch.cat((type_embedding, projection), dim=-1))
        embedding = self.dropout(embedding)
        return embedding


class FCModel(nn.Module):
    def __init__(self, vocab_size, hidden_size, use_function):
        super(FCModel, self).__init__()
        if use_function:
            self.embedding_layer = Feature_Embedding(vocab_size, hidden_size)
        else:
            self.embedding_layer = Feature_Embedding_2(vocab_size, hidden_size)
        self.prediction = nn.Sequential(
            nn.Linear(hidden_size, hidden_size//4),
            nn.ReLU(),
            nn.Linear(hidden_size//4, 1),
            # nn.ReLU()
        )
        self.loss = nn.L1Loss()
    def forward(self, ans, operating_type, global_param, function, when, related_pin):
        embedding = self.embedding_layer(operating_type, global_param, function, when, related_pin)
        pred = self.prediction(embedding)

        loss = torch.mean(torch.abs(pred-ans) / ans)

        return loss, pred

def build_model(cfg):
    logger = logging.getLogger('model')
    vocab_size = cfg['MODEL']['vocab_size']
    hidden_size = cfg['MODEL']['hidden_size']
    pad_length = cfg['MODEL']['pad_length']
    use_function = cfg['MODEL']['use_function']

    if cfg['MODEL']['type'] == 'NN':
        model = FCModel(vocab_size, hidden_size, use_function)
    elif cfg['MODEL']['type'] == 'LSTM':
        model = RNNModel(vocab_size, hidden_size)

    logger.info('Setup model {}.'.format(model.__class__.__name__))
    logger.info('Model structure:')
    logger.info(model)
    return model