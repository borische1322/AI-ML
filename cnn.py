# -*- coding: utf-8 -*-
"""Copy of Untitled3.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xZ58wTYEShdLgyzi7KNRp3OjvTAXZH9u
"""

from google.colab import drive
drive.mount('/content/drive')

import os
import cv2
import numpy as np
from tqdm import tqdm

REBUILD_DATA = False

class DogsVSCats():
  IMG_SIZE = 50
  CATS = "drive/MyDrive/CNN tut/PetImages/Cat"
  DOGS = "drive/MyDrive/CNN tut/PetImages/Dog"
  LABELS = {CATS: 0, DOGS: 1}

  training_data = []
  catcount = 0;
  dogcount = 0;

  def make_training_data(self):
    for label in self.LABELS:
      print(label)
      for f in tqdm(os.listdir(label)):
        try:
          path = os.path.join(label, f)
          img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
          img = cv2.resize(img, (self.IMG_SIZE, self.IMG_SIZE))
          self.training_data.append([np.array(img), np.eye(2)[self.LABELS[label]]]) #make an identity matrix and get one row as a one hot vector

          if label == self.CATS:
            self.catcount += 1
          elif label == self.DOGS:
            self.dogcount += 1
        except Exception as e:
          pass

    np.random.shuffle(self.training_data)
    np.save("training_data.npy", self.training_data)
    print("Cats: ", self.catcount)
    print("Dogs: ", self.dogcount)


if REBUILD_DATA:
  dogsvscats = DogsVSCats()
  dogsvscats.make_training_data()

training_data = np.load("drive/MyDrive/CNN tut/training_data.npy", allow_pickle=True)
print(len(training_data))

import matplotlib.pyplot as plt

plt.imshow(training_data[1][0], cmap="gray")
plt.show()
print(training_data[1][1])

"""# **CNN**"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class Net(nn.Module):
  def __init__(self):
    super().__init__()
    self.conv1 = nn.Conv2d(1, 16, 2)
    self.conv2 = nn.Conv2d(16, 32, 2)
    self.conv3 = nn.Conv2d(32, 64, 1)

    x = torch.randn(7,19).view(-1, 1, 7, 19)
    self._to_linear = None
    self.convs(x)


    self.fc1 = nn.Linear(self._to_linear , 512)
    self.fc2 = nn.Linear(512, 19)

  def convs(self, x):
    x = F.max_pool2d(F.relu(self.conv1(x)), (2,2))
    x = F.max_pool2d(F.relu(self.conv2(x)), (2,2))
    x = F.relu(self.conv3(x))

    #print(x[0].shape)

    if self._to_linear is None:
      self._to_linear = x[0].shape[0]*x[0].shape[1]*x[0].shape[2]
    return x

  def forward(self, x):
    x = self.convs(x)
    x = x.view(-1, self._to_linear)
    x = F.relu(self.fc1(x))
    x = self.fc2(x)
    return F.softmax(x, dim=1)


net = Net()

import torch.optim as optim

optimizer = optim.Adam(net.parameters(), lr= 0.001)
loss_function = nn.MSELoss()

#X = torch.Tensor(np.array([i[0] for i in training_data])).view(-1, 50, 50)
X = torch.Tensor(np.load("drive/MyDrive/CNN tut/datanpy/anish/gestureOverallX.npy")).view(-1,7,19)
#y = torch.Tensor(np.array([i[1] for i in training_data]))
y = torch.Tensor(np.load("drive/MyDrive/CNN tut/datanpy/anish/gestureOverallY.npy"))

iden = np.eye(19)

y = torch.Tensor(np.array([iden[int(i)] for i in y]))

VAL_PCT = 0.1
val_size = int(len(X) * VAL_PCT)
print(val_size)

train_X = X[: -val_size]
train_y = y[: -val_size]

test_X = X[-val_size:]
test_y = y[-val_size:]

print(train_X.view(-1, 1,7,19)[0])
print(test_y)

BATCH_SIZE = 100
EPOCHS = 10

for epoch in range(EPOCHS):
  for i in tqdm(range(0, len(train_X), BATCH_SIZE)):
    #print(i, i+BATCH_SIZE)
    batch_X = train_X[i:i+BATCH_SIZE].view(-1, 1,7,19)
    batch_y = train_y[i:i+BATCH_SIZE].view(-1, 19)

    net.zero_grad() #could also use optimizer.zero_grad() since in this case is the same
    outputs = net(batch_X)
    loss = loss_function(outputs, batch_y)
    loss.backward()
    optimizer.step()

print(loss)

correct = 0
total = 0

with torch.no_grad():
  for i in tqdm(range(len(X))):
    real_class = torch.argmax(y[i])
    net_out = net(X[i].view(-1, 1, 7, 19))
    predicted_class = torch.argmax(net_out)
    if predicted_class == real_class:
      correct += 1
    total += 1

print("Accuracy:", round(correct/total, 3))