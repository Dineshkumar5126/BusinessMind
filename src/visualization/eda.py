import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda(input_path, output_dir):
    print("Loading data for EDA...")
    df = pd.read_csv(input_path)
    df['Date'] = pd.to_datetime(df['Date'])
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Sales over time
    print("Generating Sales over Time plot...")
    plt.figure(figsize=(12, 6))
    daily_sales = df.groupby('Date')['Sales_Revenue'].sum().reset_index()
    sns.lineplot(data=daily_sales, x='Date', y='Sales_Revenue')
    plt.title('Total Daily Sales/Revenue Over Time')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sales_over_time.png'))
    plt.close()
    
    # 2. Sales by category
    print("Generating Sales by Category plot...")
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Category', y='Sales_Revenue')
    plt.title('Sales Distribution by Category')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sales_by_category.png'))
    plt.close()
    
    # 3. Sales distribution
    print("Generating Sales Distribution plot...")
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Sales_Revenue'], bins=50, kde=True)
    plt.title('Distribution of Sales Revenue')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'sales_distribution.png'))
    plt.close()
    
    # 4. Correlation matrix
    print("Generating Correlation Matrix plot...")
    plt.figure(figsize=(8, 6))
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Matrix of Numerical Features')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_matrix.png'))
    plt.close()
    
    print("EDA completed. Plots saved to", output_dir)

if __name__ == "__main__":
    run_eda('data/processed/sales_data_clean.csv', 'reports/figures/')
