# deep learning example found using AI
#import necessary libraries 
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data
from torch.utils.data import random_split
import torch.nn.functional as F

#sample dataset
# Assume we have a 10x2 input dataset
train = torch.tensor([[1,2],[3,4],[5,6],[7,8],[9,10]], dtype=torch.float)
test = torch.tensor([[11,12],[13,14],[15,16],[17,18],[19,20]], dtype=torch.float)

# Create a model
class Model(nn.Module):
  def __init__(self):
    super(Model, self).__init__()
    self.fc1 = nn.Linear(2, 5)
    self.fc2 = nn.Linear(5, 10)
    self.fc3 = nn.Linear(10, 1)

  def forward(self, x):
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = self.fc3(x)
    return x

# Create an instance of the model
model = Model()

# Choose an optimizer
optimizer = optim.Adam(model.parameters(), lr=0.001)

total = 0
correct = 0
# Train and test the model
for epoch in range(500):
  # Clear the gradients
  optimizer.zero_grad()
  
  # Forward pass
  output = model(train)
  
  # Calculate loss
  loss = (output - torch.sum(train)).pow(2).mean()

  # Backward pass
  loss.backward()
 
  # Update weights
  optimizer.step()

  # Start testing
  prediction =  model(test)

  null, prediction_label = torch.max(prediction.data, 0)
  null, actual_label = torch.max(test.data, 0)

  correct += (prediction_label == actual_label[0]).sum()
  total += 1

accuracy = correct/total
print(f"Accuracy: {accuracy}")

# Print the model's weights
for param in model.parameters():
  print(param)