import pandas as pd
import numpy as np
import os

print("Loading preprocessed Rossmann dataset...")
df = pd.read_csv('data/processed/rossmann_clean.csv', low_memory=False)

# Sort chronologically (Crucial for time-series and preventing leakage)
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values(by=['Store', 'Date']).reset_index(drop=True)

print("Extracting calendar features...")
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Week'] = df['Date'].dt.isocalendar().week.astype(int)
df['DayOfWeek'] = df['Date'].dt.dayofweek # 0=Monday, 6=Sunday
df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)

# In Rossmann data, DayOfWeek is already given (1=Mon, 7=Sun). Let's just use the extracted one to be standard.

print("Creating lag and rolling sales features (past information only)...")
# Calculate lag and rolling features grouped by Store
# Must be sorted by Date within each Store, which we already did
df['Lag_1'] = df.groupby('Store')['Sales'].shift(1)
df['Lag_7'] = df.groupby('Store')['Sales'].shift(7)
df['RollingMean_7'] = df.groupby('Store')['Sales'].shift(1).rolling(window=7, min_periods=1).mean()

print("Handling categorical variables...")
# StateHoliday contains string '0' and int 0. Clean it up:
df['StateHoliday'] = df['StateHoliday'].astype(str).replace({'0': 'None', 0: 'None', 'a': 'PublicHoliday', 'b': 'EasterHoliday', 'c': 'Christmas'})
df['StoreType'] = df['StoreType'].astype(str)
df['Assortment'] = df['Assortment'].astype(str)

# Label Encoding for tree-based models (we'll just use dummy encoding to be safe and compatible with linear baseline later if needed, 
# or just LabelEncoder. For simplicity in pandas, let's use Label Encoding for high cardinality (Store) 
# and One-Hot Encoding for low cardinality.
# Store is already an integer.
df = pd.get_dummies(df, columns=['StoreType', 'Assortment', 'StateHoliday', 'PromoInterval'], drop_first=True)

print("Handling missing values created by lags...")
# Drop rows with NaN from lags (first 7 days for each store)
df = df.dropna(subset=['Lag_7', 'RollingMean_7'])

# Drop Customers as it is a future information leakage (we don't know it beforehand)
if 'Customers' in df.columns:
    df = df.drop(columns=['Customers'])

print("Creating chronological train/test split...")
# Let's use the last 6 weeks of data as the test set
max_date = df['Date'].max()
split_date = max_date - pd.Timedelta(weeks=6)

train_df = df[df['Date'] < split_date]
test_df = df[df['Date'] >= split_date]

# Save datasets
train_path = 'data/processed/train_fe.csv'
test_path = 'data/processed/test_fe.csv'
train_df.to_csv(train_path, index=False)
test_df.to_csv(test_path, index=False)

print("\n=== Feature Engineering Verification Report ===")
print(f"Total rows after removing NAs: {len(df)}")
print(f"Total columns: {len(df.columns)}")
print(f"Target Variable: 'Sales'")
print(f"Feature Names: {list(df.columns)}")
print(f"Train date range: {train_df['Date'].min().date()} to {train_df['Date'].max().date()}")
print(f"Test date range: {test_df['Date'].min().date()} to {test_df['Date'].max().date()}")
print(f"Train rows: {len(train_df)}, Test rows: {len(test_df)}")
print("Verification: Data sorted chronologically by Store and Date. Lags computed via shift(1), ensuring NO future information (data leakage) is used.")
