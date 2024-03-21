import torch
import torch.nn as nn
import torch.nn.functional as F
from dgl.nn import GATConv
import dgl
import DataProcess 


class GAT(nn.module):
    def __init__(self, nfeat:int, nhid:int, nclass:int, num_layers:int, num_heads, activation:str, norm:list, drop:list, residual:str):
        super().__init__()
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.name = 'GAT_'+ residual
        self.hidden_list = []

        # Conv Layers
        self.convs = nn.ModuleList()
        self.convs.append(GATConv(nfeat, nhid, num_heads = self.num_heads))
        for i in range(self.numLayers - 1):
            self.convs.append(GATConv(nhid, nhid, num_heads = self.num_heads))

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
        h = torch.mean(h,dim=1)
        h = self.data_process.norm(h)
        h = self.data_process.activation(h)
        self.hidden_list.append(h)
        
        for i in range(1, self.num_layers - 1):
            h = self.data_process.drop(graph, x)
            h = self.convs[i](graph, h)
            h = torch.mean(h,dim=1)
            h = self.data_process.residual(self.hidden_list, h, i)
            h = self.data_process.norm(h)
            h = self.data_process.activation(h)
            self.hidden_list.append(h)

        h = self.out_fc(h)
        h = F.log_softmax(h, dim=1)
        return h