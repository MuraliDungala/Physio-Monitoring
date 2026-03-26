import pandas as pd
import os

kimore_path = r"e:\Physio-Monitoring\Physio-Monitoring\data\external\KIMORE\Kimore ex1"

X = pd.read_csv(os.path.join(kimore_path, 'Train_X.csv'), header=None)
Y = pd.read_csv(os.path.join(kimore_path, 'Train_Y.csv'), header=None)

print(f"Train_X shape: {X.shape}")
print(f"Train_Y shape: {Y.shape}")
print(f"First row of X (5 values): {X.iloc[0, :5].tolist()}")
print(f"First 5 values of Y: {Y.iloc[:5, 0].tolist()}")
