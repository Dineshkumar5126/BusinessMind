import pandas as pd
import numpy as np
import os

def preprocess_data(input_path, output_path):
    print(f"Loading data from {input_path}...")
    df = pd.read_csv(input_path)
    
    print("\n--- Initial Data Info ---")
    print(df.info())
    
    print("\n--- Identifying Data Types ---")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    print(f"Numeric features: {numeric_cols}")
    print(f"Categorical features: {categorical_cols}")
    
    print("\n--- Handling Duplicates ---")
    duplicates = df.duplicated().sum()
    print(f"Found {duplicates} duplicate rows. Removing...")
    df = df.drop_duplicates()
    
    print("\n--- Handling Missing Values ---")
    missing = df.isnull().sum()
    print("Missing values before processing:")
    print(missing[missing > 0])
    
    # Fill missing Sales_Revenue with median of that store/category combination
    df['Sales_Revenue'] = df.groupby(['Store_ID', 'Category'])['Sales_Revenue'].transform(lambda x: x.fillna(x.median()))
    
    # Drop any remaining missing values if applicable
    df = df.dropna()
    print("Missing values handled.")
    
    print("\n--- Processing Dates ---")
    df['Date'] = pd.to_datetime(df['Date'])
    
    print("\n--- Data Quality Checks ---")
    if (df['Sales_Revenue'] < 0).any():
        print("Warning: Negative sales found!")
    else:
        print("Data quality check passed: No negative sales.")
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nPreprocessed data saved to {output_path}")
    print(f"Final shape: {df.shape}")

if __name__ == "__main__":
    preprocess_data('data/raw/sales_data.csv', 'data/processed/sales_data_clean.csv')
