import os
import urllib.request
import pandas as pd

# Create directories
dirs = [
    'data/raw',
    'data/processed',
    'src/data',
    'src/visualization',
    'reports/figures'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)

# Download Advertising dataset
url = 'https://raw.githubusercontent.com/justmarkham/scikit-learn-videos/master/data/Advertising.csv'
dataset_path = 'data/raw/Advertising.csv'
urllib.request.urlretrieve(url, dataset_path)

print(f"Directories created and dataset downloaded to {dataset_path}")
