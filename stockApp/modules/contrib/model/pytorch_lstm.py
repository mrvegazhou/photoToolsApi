# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


from __future__ import division
from __future__ import print_function

import numpy as np
import pandas as pd
from typing import Text, Union
import copy
from stockApp.modules.common.file import get_or_create_path
from core.log.logger import get_module_logger

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader,Dataset
from torchvision import transforms
from torch.autograd import Variable

from .base import Model
from modules.dataHandler.dataset import DatasetH
from modules.dataHandler.dataset.handler import DataHandlerLP


class LSTM(Model):
    """LSTM Model

    Parameters
    ----------
input_size=8, hidden_size=32, num_layers=1, output_size=1, dropout=0, batch_first
    """

    def __init__(
        self,
        input_size=50,
        hidden_size=32,
        num_layers=2,
        output_size=1,
        dropout=0.0,
        batch_size=64,
        n_epochs=10,
        sequence_length=5,
        GPU=0,
        optimizer='adam',
        loss="mse",
        batch_first=True,
        seed=None,
    ):
        # Set logger.
        self.logger = get_module_logger("LSTM")
        self.logger.info("LSTM pytorch version...")

        # set hyper-parameters.
        self.input_size = input_size
        self.hidden_size = hidden_size
        # LSTM层数
        self.num_layers = num_layers
        self.dropout = dropout
        self.n_epochs = n_epochs
        self.output_size = output_size
        self.batch_size = batch_size
        self.device = torch.device("cuda:%d" % (GPU) if torch.cuda.is_available() and GPU >= 0 else "cpu")
        self.sequence_length = sequence_length
        self.batch_first = batch_first
        self.lr = 0.0001
        self.seed = seed
        self.loss = loss
        self.metric = ''

        if self.seed is not None:
            np.random.seed(self.seed)
            torch.manual_seed(self.seed)

        self.lstm_model = LSTMModel(input_size=self.input_size, hidden_size=self.hidden_size, num_layers=self.num_layers, output_size=1,
                     dropout=self.dropout, batch_first=self.batch_first)

        if optimizer.lower() == "adam":
            self.train_optimizer = optim.Adam(self.lstm_model.parameters(), lr=self.lr)
        elif optimizer.lower() == "gd":
            self.train_optimizer = optim.SGD(self.lstm_model.parameters(), lr=self.lr)
        else:
            raise NotImplementedError("optimizer {} is not supported!".format(optimizer))

        self.lstm_model.to(self.device)
        self.criterion = nn.MSELoss()  # 定义损失函数

    @property
    def use_gpu(self):
        return self.device != torch.device("cpu")

    class Mydataset(Dataset):
        def __init__(self, xx, yy, transform=None):
            self.x = xx
            self.y = yy
            self.tranform = transform

        def __getitem__(self, index):
            x1 = self.x[index]
            y1 = self.y[index]
            if self.tranform != None:
                return self.tranform(x1), y1
            return x1, y1

        def __len__(self):
            return len(self.x)

    @classmethod
    def getData(cls, df_train, df_valid, sequence_length, batch_size):
        df_train = df_train.fillna(0)
        df_valid = df_valid.fillna(0)

        # 构造X和Y
        # 根据前n天的数据，预测未来一天的收盘价(close)， 例如：根据1月1日、1月2日、1月3日、1月4日、1月5日的数据（每一天的数据包含8个特征），预测1月6日的收盘价。
        sequence = sequence_length
        train_x = []
        train_y = []
        for i in range(df_train.shape[0] - sequence):
            train_x.append(np.array(df_train['feature'].iloc[i:(i + sequence), :50].values, dtype=np.float32))
            train_y.append(np.array(df_train["label"].iloc[(i + sequence), 0], dtype=np.float32))

        test_x = []
        test_y = []
        for i in range(df_valid.shape[0] - sequence):
            test_x.append(np.array(df_valid['feature'].iloc[i:(i + sequence), ].values, dtype=np.float32))
            test_y.append(np.array(df_valid["label"].iloc[(i + sequence), 0], dtype=np.float32))

        # 构建batch
        train_loader = DataLoader(dataset=cls.Mydataset(train_x, train_y, transform=transforms.ToTensor()),
                                  batch_size=batch_size,
                                  shuffle=True)
        test_loader = DataLoader(dataset=cls.Mydataset(test_x, test_y), batch_size=batch_size, shuffle=True)
        return train_loader, test_loader

    def fit(
        self,
        dataset: DatasetH,
        evals_result=dict(),
        save_path=None,
    ):
        df_train, df_valid, df_test = dataset.prepare(
            ["train", "valid", "test"],
            col_set=["feature", "label"],
            data_key=DataHandlerLP.DK_L,
        )

        if df_train.empty or df_valid.empty:
            raise ValueError("Empty data from dataset, please check your dataset config.")

        train_loader, test_loader = self.getData(df_train, df_valid, self.sequence_length, self.batch_size)

        save_path = get_or_create_path(save_path)


        # train
        for step in range(self.n_epochs):
            self.logger.info("Epoch%d:", step)
            self.logger.info("training...")

            total_loss = 0
            for idx, (data, label) in enumerate(train_loader):
                if self.use_gpu:
                    data1 = data.squeeze(1).cuda()
                    pred = self.lstm_model(Variable(data1).cuda())
                    pred = pred[1, :, :]
                    label = label.unsqueeze(1).cuda()
                else:
                    data1 = data.squeeze(1)
                    pred = self.lstm_model(Variable(data1))
                    pred = pred[1, :, :]
                    label = label.unsqueeze(1)
                loss = self.criterion(pred, label)
                self.train_optimizer.zero_grad()
                loss.backward()
                self.train_optimizer.step()
                total_loss += loss.item()

            if step % 10 == 0:
                torch.save({'state_dict': self.lstm_model.state_dict()}, save_path)
                print('第%d epoch，保存模型' % step)
        torch.save({'state_dict': self.lstm_model.state_dict()}, save_path)

        if self.use_gpu:
            torch.cuda.empty_cache()

    def predict(self, dataset: DatasetH, segment: Union[Text, slice] = "test", save_path=None):
        x_test = dataset.prepare(segment, col_set="feature", data_key=DataHandlerLP.DK_I)
        model = self.lstm_model(input_size=self.input_size, hidden_size=self.hidden_size, num_layers=self.layers, output_size=1)
        model.to(self.device)
        save_path = get_or_create_path(save_path)
        checkpoint = torch.load(save_path)
        model.load_state_dict(checkpoint['state_dict'])
        preds = []
        labels = []
        train_loader, test_loader = self.getData(self.sequence_length, self.batch_size)
        for idx, (x, label) in enumerate(test_loader):
            if self.use_gpu:
                x = x.squeeze(1).cuda()  # batch_size,seq_len,input_size
            else:
                x = x.squeeze(1)
            pred = model(x)
            list = pred.data.squeeze(1).tolist()
            preds.extend(list[-1])
            labels.extend(label.tolist())
        print(preds, labels)


class LSTMModel(nn.Module):
    def __init__(
            self, input_size=8, hidden_size=32, num_layers=1, output_size=1, dropout=0, batch_first=True
    ):
        super(LSTMModel, self).__init__()
        # lstm的输入 #batch,seq_len, input_size
        self.hidden_size = hidden_size
        self.input_size = input_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.dropout = dropout
        self.batch_first = batch_first
        self.rnn = nn.LSTM(input_size=self.input_size, hidden_size=self.hidden_size, num_layers=self.num_layers,
                           batch_first=self.batch_first, dropout=self.dropout)
        self.linear = nn.Linear(self.hidden_size, self.output_size)

    def forward(self, x):
        out, (hidden, cell) = self.rnn(
            x)  # x.shape : batch, seq_len, hidden_size , hn.shape and cn.shape : num_layes * direction_numbers, batch, hidden_size
        # a, b, c = hidden.shape
        # out = self.linear(hidden.reshape(a * b, c))
        out = self.linear(hidden)
        return out
