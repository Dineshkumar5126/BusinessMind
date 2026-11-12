import pandas as pd
import numpy as np
import datetime
import os

# Set seed for reproducibility
np.random.seed(42)

# Generate Dates for 2 years
start_date = datetime.date(2022, 1, 1)
end_date = datetime.date(2023, 12, 31)
date_range = pd.date_range(start_date, end_date)

# Store IDs and Categories
store_ids = ['S01', 'S02', 'S03']
categories = ['Electronics', 'Clothing', 'Home & Garden', 'Groceries']

data = []

# Generate realistic data
for d in date_range:
    for store in store_ids:
        for cat in categories:
            # Base sales vary by category and store
            base_sales = np.random.normal(500, 100) if cat == 'Groceries' else np.random.normal(200, 50)
            
            # Seasonality: Higher in December
            if d.month == 12:
                base_sales *= 1.5
                
            # Weekend effect
            if d.weekday() >= 5:
                base_sales *= 1.2
                
            # Promotions
            promo = np.random.choice([0, 1], p=[0.8, 0.2])
            if promo == 1:
                base_sales *= 1.3
                
            # Add some missing values randomly (approx 2% of the time) to satisfy preprocessing reqs
            sales_val = base_sales if np.random.random() > 0.02 else np.nan
            
            data.append({
                'Date': d,
                'Store_ID': store,
                'Category': cat,
                'Promotion': promo,
                'Marketing_Spend': np.random.uniform(50, 500) if promo == 1 else np.random.uniform(10, 100),
                'Sales_Revenue': sales_val
            })

df = pd.DataFrame(data)

# Add some duplicate rows to satisfy preprocessing reqs
duplicates = df.sample(n=10, random_state=42)
df = pd.concat([df, duplicates])

# Save to raw
os.makedirs('data/raw', exist_ok=True)
df.to_csv('data/raw/sales_data.csv', index=False)
print("Synthetic retail dataset created with dates, categories, and deliberate imperfections (missing/dupes).")
