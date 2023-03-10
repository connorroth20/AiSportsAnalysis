import torch.nn as nn
import pandas as pd
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.utils.data import Dataset

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
class cbbDataset(Dataset):
    
    def __init__(self, split='train', shuffle=True):
        path = '../cbb.csv'
        data = pd.read_csv(path, header=None)
        data.columns = ['TEAM','CONF','G','W','ADJOE','ADJDE','BARTHAG','EFG_O','EFG_D','TOR','TORD','ORB','DRB','FTR','FTRD','2P_O','2P_D','3P_O','3P_D','ADJ_T','WAB','POSTSEASON','SEED', 'YEAR']
        #We only want to analyze the teams in the tournament
        data = data.loc[data['SEED'].notnull()]
        #Get just the columns that we want
        X = data.loc[:, ['ADJOE','ADJDE','BARTHAG','EFG_O','TOR','ADJ_T']].values
        #Strip off the headers
        X=X[1:]

        X = X.astype(float)

        #Scale the input data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        #Separate into data sets
        X_train, X_test= train_test_split(X_scaled, test_size = 0.2, random_state = 0, shuffle = True)

        # print(X_train)
        # print(y_train)
        if split == 'train':
            self.x_data = X_train
            print('Training dataset loaded')
        elif split == 'test':
            self.x_data = X_test
            print('Test dataset loaded')
        else:
            self.x_data = np.concatenate((X_train,X_test),axis=0)

    def __getitem__(self, i):
        return torch.tensor(self.x_data[i]).float().to(device)

    def __len__(self):
        return len(self.x_data)

    @staticmethod
    def test(model, test_dl):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        accuracy = None
        total = 0
        correct = 0
        for (X) in test_dl:
            X = X.to(device)
            Y = X[0].to(device)
            prediction = model(X)
            prediction_label = prediction.data[0]
            print(f"prediction_label: {prediction_label}")
            print(f"x.data: {Y.data}")
            print(f"check: {(prediction_label == Y.data).sum()}")
            correct += (prediction_label == Y.data).sum()
            total += 1
        accuracy = correct / total
        return accuracy

    @staticmethod
    def train(model, lr, momentum, num_epochs, train_dl, test_dl):
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=momentum)
        loss_fn = nn.MSELoss(reduction='mean')

        for epoch in range(1, num_epochs + 1):
            for X in train_dl:
                opt.zero_grad()
                X = X.to(device)
                Y = X[0].to(device)
                guess = model(X)
                loss = loss_fn(guess, Y)
                loss.backward()
                opt.step()
            test_accuracy = cbbDataset.test(model, test_dl)
            print(f"Test accuracy at epoch {epoch}: {test_accuracy:.4f}")

class cbb_linear_model(nn.Module):
    def __init__(self):
        super().__init__()
        self.relu = nn.ReLU()
        self.fc1 = nn.Linear(in_features = 6, out_features = 32, bias=True)
        self.fc2 = nn.Linear(in_features = 32, out_features = 64, bias=True)
        self.fc3 = nn.Linear(in_features = 64, out_features = 32, bias=True)
        self.fc4 = nn.Linear(in_features = 32, out_features = 6, bias=True)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x

lr = 0.01
momentum = 0.2
num_epochs = 1

dataset_train = cbbDataset(split='train')
dataset_test = cbbDataset(split='test')

model = cbb_linear_model()
model = model.to(device)
cbbDataset.train(model, lr, momentum, num_epochs, dataset_train, dataset_test)
test_accuracy = cbbDataset.test(model, dataset_test)
print(f"Final test accuracy: {test_accuracy:.4f}")