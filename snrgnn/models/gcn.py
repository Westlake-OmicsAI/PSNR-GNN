import torch
import torch.nn as nn
import torch.nn.functional as F
from dgl import DropEdge
from dgl.nn import GraphConv
import dgl
import DataProcess

class GCN(nn.Module):
    def __init__(self, nfeat:int, nhid:int, nclass:int, num_layers:int, activation:str, norm:list, drop:list, residual:str):
        super().__init__()
        self.num_layers = num_layers
        self.name = 'GCN_'+ residual
        self.hidden_list = []
        self.convs = nn.ModuleList()

        # Conv Layers
        self.convs.append(GraphConv(nfeat, nhid))
        for i in range(self.numLayers - 1):
            self.convs.append(GraphConv(nhid, nhid))
        self.out_fc = nn.Linear(nhid, nclass)
        self.data_process = DataProcess(num_layers, nfeat, nhid, nclass, residual, drop, norm, activation)
        self.reset_parameters()

    def reset_parameters(self):
        for conv in self.convs:
            conv.reset_parameters()
        self.out_fc.reset_parameters()

    def forward(self, graph, x):
        h = self.data_process.drop(graph, x)
        h = self.convs[0](graph, h)
        h = self.data_process.norm(h)
        h = self.data_process.activation(h)
        h = self.data_process.residual(h)
        self.hidden_list.append(h)
        
        for i in range(1, self.num_layers - 1):
            h = self.data_process.drop(graph, x)
            h = self.convs[i](graph, h)
            h = self.data_process.residual(self.hidden_list, h, i)
            h = self.data_process.norm(h)
            h = self.data_process.activation(h)
            self.hidden_list.append(h)

        h = self.out_fc(h)
        h = F.log_softmax(h, dim=1)
        return h

    