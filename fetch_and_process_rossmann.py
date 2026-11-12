import pandas as pd
import urllib.request
import os

os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

print("Downloading Rossmann datasets...")
train_url = 'https://raw.githubusercontent.com/RPI-DATA/tutorials-intro/master/rossmann-store-sales/rossmann-store-sales/train.csv'
store_url = 'https://raw.githubusercontent.com/RPI-DATA/tutorials-intro/master/rossmann-store-sales/rossmann-store-sales/store.csv'

# Due to size, download locally
urllib.request.urlretrieve(train_url, 'data/raw/train.csv')
urllib.request.urlretrieve(store_url, 'data/raw/store.csv')

print("Loading data...")
train_df = pd.read_csv('data/raw/train.csv', low_memory=False)
store_df = pd.read_csv('data/raw/store.csv')

print("\n--- Data Overview ---")
print(f"Train rows: {len(train_df)}, columns: {len(train_df.columns)}")
print(f"Train columns: {list(train_df.columns)}")
print(f"Store rows: {len(store_df)}, columns: {len(store_df.columns)}")
print(f"Store columns: {list(store_df.columns)}")

print("\n--- Date Range ---")
train_df['Date'] = pd.to_datetime(train_df['Date'])
print(f"Min Date: {train_df['Date'].min()}, Max Date: {train_df['Date'].max()}")

print("\n--- Missing Values ---")
print("Train missing:")
print(train_df.isnull().sum()[train_df.isnull().sum() > 0])
print("Store missing:")
print(store_df.isnull().sum()[store_df.isnull().sum() > 0])

# Preprocessing
print("\n--- Preprocessing ---")
# Merge data
df = train_df.merge(store_df, on='Store', how='left')

# Drop stores that were closed (0 sales)
df = df[df['Open'] != 0]

# Preprocess missing values based on Rossmann dataset conventions
df['CompetitionDistance'] = df['CompetitionDistance'].fillna(df['CompetitionDistance'].max())
df['CompetitionOpenSinceMonth'] = df['CompetitionOpenSinceMonth'].fillna(0)
df['CompetitionOpenSinceYear'] = df['CompetitionOpenSinceYear'].fillna(0)
df['Promo2SinceWeek'] = df['Promo2SinceWeek'].fillna(0)
df['Promo2SinceYear'] = df['Promo2SinceYear'].fillna(0)
df['PromoInterval'] = df['PromoInterval'].fillna('')

df.to_csv('data/processed/rossmann_clean.csv', index=False)
print("Preprocessing complete. Saved to data/processed/rossmann_clean.csv")
print(f"Cleaned dataset rows: {len(df)}, columns: {len(df.columns)}")

