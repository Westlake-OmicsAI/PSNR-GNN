import torch
import torch.nn as nn
import torch.nn.functional as F
from dgl.nn import GCN2Conv
import dgl
from .dataprocess import DataProcess

    
class GCNII(nn.Module):
    def __init__(self, nfeat:int, nhid:int, nclass:int, num_layers:int, activation:str, norm:list, drop:list, residual:str, num_node:int, args):
        super().__init__()
        self.residual = residual
        self.num_layers = num_layers
        self.name = 'GCNII_'+ residual
        self.hidden_list = []

        # Conv Layers
        self.convs = nn.ModuleList()
        self.in_fc = nn.Linear(nfeat, nhid)
        if self.residual not in ['snr']:
            self.convs.append(GCN2Conv(nhid, 1))
        else:
            self.convs.append(GCN2Conv(nfeat, 1))
        for i in range(self.num_layers - 1):
            self.convs.append(GCN2Conv(nhid, i+2))

        self.out_fc = nn.Linear(nhid, nclass)
        self.data_process = DataProcess(num_layers, nfeat, nhid, nclass, residual, drop, norm, activation, num_node, args)
        self.reset_parameters()

    def reset_parameters(self):
        for conv in self.convs:
            conv.reset_parameters()
        self.out_fc.reset_parameters()
        if self.residual not in ['snr']:
            self.in_fc.reset_parameters()

    def forward(self, graph, h):
        self.hidden_list = []
        if self.residual not in ['snr']:
            graph, h = self.data_process.drop(graph, h, self.training)
            h = self.in_fc(h)
            h = self.data_process.normalization(h)
            h = self.data_process.activation(h)
            self.hidden_list.append(h)

        graph, h = self.data_process.drop(graph, h, self.training)
        h = self.convs[0](graph, self.hidden_list[0], h)
        if self.residual not in ['snr']:
            h = self.data_process.residual(self.hidden_list, h, 0, graph)
        h = self.data_process.normalization(h)
        h = self.data_process.activation(h)
        self.hidden_list.append(h)

        for i in range(1, self.num_layers):
            graph, h = self.data_process.drop(graph, h, self.training)
            h = self.convs[i](graph, self.hidden_list[0], h)
            h = self.data_process.residual(self.hidden_list, h, i, graph)
            h = self.data_process.normalization(h)
            self.hidden_list.append(h)
  

        h = self.out_fc(h)
        h = F.log_softmax(h, dim=1)
        return h