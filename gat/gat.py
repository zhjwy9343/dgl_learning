"""
Graph Attention Networks in DGL using SPMV optimization.
References
----------
Paper: https://arxiv.org/abs/1710.10903
Author's code: https://github.com/PetarV-/GAT
Pytorch implementation: https://github.com/Diego999/pyGAT
"""



import torch
import torch.nn as nn
import dgl.function as fn
from dgl.nn import GATConv 
# TODO can the differenft conv layers be applied on every type of Graphs (such as Hetro + directional ? )
# GATConv can be applied on homogeneous graph and unidirectional bipartite graph. If the layer is to be applied to a unidirectional bipartite graph


class GAT(nn.Module):
    def __init__(self,
                 g,
                 num_layers,
                 in_dim,
                 num_hidden,
                 num_classes,
                 heads,
                 activation,
                 feat_drop,
                 attn_drop,
                 negative_slope,
                 residual):
        super(GAT, self).__init__()
        self.g = g
        self.num_layers = num_layers
        self.gat_layers = nn.ModuleList()
        self.activation = activation
        # input projection (no residual)
        self.gat_layers.append(GATConv(
            in_dim, num_hidden, heads[0],
            feat_drop, attn_drop, negative_slope, False, self.activation))
        # hidden layers
        for l in range(1, num_layers):
            # due to multi-head, the in_dim = num_hidden * num_heads
            self.gat_layers.append(GATConv(
                num_hidden * heads[l-1], num_hidden, heads[l],
                feat_drop, attn_drop, negative_slope, residual, self.activation))
        # output projection
        self.gat_layers.append(GATConv(
            num_hidden * heads[-2], num_classes, heads[-1],
            feat_drop, attn_drop, negative_slope, residual, None)) # last layer no self.activation

    def forward(self, inputs):
        h = inputs
        for l in range(self.num_layers):
            t = self.gat_layers[l](self.g, h)
            h = t.flatten(1) # flatten(1) 将输入扁平化但保留batch_size,假设第一维是batch。 
            # TODO flatten(1) 1不指定就是start dim
        # output projection
        logits = self.gat_layers[-1](self.g, h).mean(1)
        return logits
