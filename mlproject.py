# -*- coding: utf-8 -*-
"""97150237-ml-final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gRCvW7mooTikxdwc3TT0MPXaYpDE-hWP
"""

!gdown --id 1vX7xmAuLm21QrxnPLoKysU-uY_ciC81k

import numpy as np 
import pandas as pd
import torch
from torch import nn
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold 
from torch.optim import SparseAdam,Adam,Adagrad,SGD
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from sklearn import metrics

df = pd.read_csv('ratings.csv')

df.head(10)

df.drop('timestamp',axis=1)

users_num = df.userId.nunique()
movies_num = df.movieId.nunique()

df.shape

df.rating.value_counts()

train_df, test_df = train_test_split(df, test_size=0.2, random_state= 42)

class myDataset(Dataset):
 def __init__(self, users, movies, ratings):
        self.users = users
        self.movies = movies
        self.ratings = ratings 
 def __len__(self):
        return len(self.users)
 def __getitem__(self, item):
        user = self.users[item]
        movie = self.movie[item]
        rating = self.rating[item]  
        return {"users": torch.tensor (user-1, dtype = torch.long) , "movies": torch.tensor(movie-1, dtype = torch.long), "ratings": torch.tensor(rating, dtype = torch.float)}

class module(nn.Module):
    def __init__(self, n_user, n_movie, k):
        super().__init__()
        self.user_embeddings = nn.Embedding(n_user, k, sparse=True)
        self.item_embeddings = nn.Embedding(n_movie, k, sparse=True)
        self.out= nn.Linear(2*k , 1)
    def forward(self, users, movies,  ratings):
        user = self.user_factors(users)
        movie = self.user_factors(movies)
        output = torch.cat(user, movie, dim=1)
        output = self.out(output)
        return (user * movie).sum(axis=1)

batch_size = 32
train_loader = DataLoader(myDataset(train_df['userId'], train_df['movieId'], train_df['rating']), batch_size, shuffle=True)
test_loader =  DataLoader(myDataset(test_df['userId'], test_df['movieId'], test_df['rating']), batch_size, shuffle=True)
model = module(users_num, movies_num, 20)

optimizer = torch.optim.Adam(model.parameters(), lr = 1e-3)
#loss = nn.L1Loss()
loss = nn.MSELoss()
#loss = nn.BCELoss()

def train_network(model, train_loader, optimizer, criterion, num_epochs, train_dataset, test_loader, test_dataset):
  epoch_loss =[]
  epoch_accuracy = []
  test_loss =[]
  test_accuracy =[]
  for epoch in range(num_epochs):
    model.train()
    running_loss =0.0
    num_corrects =0.0
    for (x, labels) in train_loader:
      outputs = model(x)
      loss = criterion(outputs, labels)
      optimizer.zero_grad()
      loss.backward()
      optimizer.step()
      running_loss += loss.item()
      num_corrects += ((outputs>=0.5).float() == labels).float().sum()
    avg_loss = running_loss / len(train_loader)
    avg_acc = num_corrects / len(train_dataset)
    epoch_loss.append(avg_loss)
    epoch_accuracy.append(avg_acc)
    test_avgloss, test_avgacc = test(model, test_loader, criterion, test_dataset)
    test_loss.append(test_avgloss)
    test_accuracy.append(test_avgacc)
    print('Epoch{}/{}, train loss={:.3f}, train acc ={:.3f}, test loss = {:.3f}, test acc = {:.3f}'.format(epoch+1,num_epochs,
                                                                                                    avg_loss, avg_acc, test_avgloss,
                                                                                                  test_avgacc  ))
  return epoch_accuracy, epoch_loss, test_loss, test_accuracy

def test(model, test_laoder, criterion, test_dataset):
  model.eval()
  test_loss = 0.0
  num_corrects =0.0
  for (x, labels) in test_loader:
    outputs = model(x)
    loss = criterion(outputs, labels)
    test_loss += loss.item()
    num_corrects += ((outputs>=0.5).float() == labels).float().sum()
  avg_loss = test_loss / len(test_loader)
  avg_accuracy = num_corrects / len(test_dataset)
  return(avg_loss, avg_accuracy)

num_epochs = 20
train_acc, train_loss, test_loss, test_acc= train_network(model, train_loader, optimizer, criterion, num_epochs, train_df,
              test_loader, test_df)

