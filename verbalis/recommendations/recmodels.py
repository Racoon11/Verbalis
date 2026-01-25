import torch
import torch.nn as nn


class NCFUserEmb(nn.Module):
    def __init__(self, user_emb_dim, n_items,
                 embedding_dim=50, hidden_dims=[64, 32]):
        super().__init__()
        self.user_linear = nn.Linear(user_emb_dim, embedding_dim)
        self.item_embedding = nn.Embedding(n_items, embedding_dim)

        # MLP часть
        layers = []
        input_dim = embedding_dim * 2
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        layers.append(nn.Linear(input_dim, 1))
        self.mlp = nn.Sequential(*layers)

        # Инициализация весов
        self.user_linear.weight.data.uniform_(-0.1, 0.1)
        self.item_embedding.weight.data.uniform_(-0.1, 0.1)

    def forward(self, user_emb, item_ids):
        user_emb = self.user_linear(user_emb)
        item_emb = self.item_embedding(item_ids)
        x = torch.cat([user_emb, item_emb], dim=1)
        x = self.mlp(x)
        return x.squeeze()


class ContentBasedNeuralFilteringModel(nn.Module):
    def __init__(self, emb_dim, emb_linear_dim, hidden_dims=[64, 32]):
        super().__init__()
        self.user_linear = nn.Linear(emb_dim, emb_linear_dim)
        self.item_linear = nn.Linear(emb_dim, emb_linear_dim)

        # MLP часть
        layers = []
        input_dim = emb_linear_dim * 2
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            input_dim = hidden_dim
        layers.append(nn.Linear(input_dim, 1))
        self.mlp = nn.Sequential(*layers)

        # Инициализация весов
        self.user_linear.weight.data.uniform_(-0.1, 0.1)
        self.item_linear.weight.data.uniform_(-0.1, 0.1)

    def forward(self, user_emb, item_emb):
        user_emb = self.user_linear(user_emb)
        item_emb = self.item_linear(item_emb)
        x = torch.cat([user_emb, item_emb], dim=1)
        x = self.mlp(x)
        return x.squeeze()
