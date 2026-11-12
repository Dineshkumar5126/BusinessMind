import pandas as pd
import numpy as np
import os
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure directories exist
os.makedirs('models/saved_models', exist_ok=True)
os.makedirs('reports/figures', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)

print("Loading feature-engineered datasets...")
train_df = pd.read_csv('data/processed/train_fe.csv')
test_df = pd.read_csv('data/processed/test_fe.csv')

# Separate features and target
# Exclude Date as it's a string/datetime and Sales as it's the target
target = 'Sales'
drop_cols = [target, 'Date']
features = [c for c in train_df.columns if c not in drop_cols]

X_train = train_df[features]
y_train = train_df[target]
X_test = test_df[features]
y_test = test_df[target]

print(f"Training features: {features}")
print(f"X_train shape: {X_train.shape}, X_test shape: {X_test.shape}")

# Dictionary to store results
results = {}

def evaluate_model(name, y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    results[name] = {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2
    }
    print(f"\n--- {name} ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2:   {r2:.4f}")
    return mae, rmse, r2

# 1. Linear Regression (Baseline)
print("\nTraining Linear Regression (Baseline)...")
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_preds = lr_model.predict(X_test)
evaluate_model('Linear Regression', y_test, lr_preds)
joblib.dump(lr_model, 'models/saved_models/linear_regression.joblib')

# 2. Random Forest Regressor
# Limit estimators/depth to ensure it completes within reasonable time on 800k rows
print("\nTraining Random Forest Regressor (this may take a few minutes)...")
rf_model = RandomForestRegressor(n_estimators=50, max_depth=15, n_jobs=-1, random_state=42)
rf_model.fit(X_train, y_train)
rf_preds = rf_model.predict(X_test)
evaluate_model('Random Forest', y_test, rf_preds)
joblib.dump(rf_model, 'models/saved_models/random_forest.joblib')

# 3. XGBoost Regressor
print("\nTraining XGBoost Regressor...")
xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=7, n_jobs=-1, random_state=42)
xgb_model.fit(X_train, y_train)
xgb_preds = xgb_model.predict(X_test)
evaluate_model('XGBoost', y_test, xgb_preds)
joblib.dump(xgb_model, 'models/saved_models/xgboost.joblib')

# Save predictions for further analysis if needed
test_df['Pred_LR'] = lr_preds
test_df['Pred_RF'] = rf_preds
test_df['Pred_XGB'] = xgb_preds
test_df.to_csv('data/processed/test_predictions.csv', index=False)

# Save metrics to JSON
with open('reports/model_metrics.json', 'w') as f:
    json.dump(results, f, indent=4)

print("\nGenerating evaluation visualizations...")
# 1. Model Comparison Bar Chart
metrics_df = pd.DataFrame(results).T.reset_index().rename(columns={'index': 'Model'})

fig, axes = plt.subplots(1, 3, figsize=(18, 5))
sns.barplot(data=metrics_df, x='Model', y='MAE', ax=axes[0], palette='viridis')
axes[0].set_title('Mean Absolute Error (Lower is Better)')
sns.barplot(data=metrics_df, x='Model', y='RMSE', ax=axes[1], palette='viridis')
axes[1].set_title('Root Mean Squared Error (Lower is Better)')
sns.barplot(data=metrics_df, x='Model', y='R2', ax=axes[2], palette='viridis')
axes[2].set_title('R-Squared (Higher is Better)')
plt.tight_layout()
plt.savefig('reports/figures/model_comparison.png')
plt.close()

# 2. Actual vs Predicted (using a sample to avoid overplotting, or aggregating by Date)
daily_actual = test_df.groupby('Date')['Sales'].sum()
daily_pred_xgb = test_df.groupby('Date')['Pred_XGB'].sum()

plt.figure(figsize=(14, 6))
plt.plot(pd.to_datetime(daily_actual.index), daily_actual.values, label='Actual Sales', marker='o')
plt.plot(pd.to_datetime(daily_pred_xgb.index), daily_pred_xgb.values, label='XGBoost Predicted', linestyle='--', marker='x')
plt.title('Daily Total Sales: Actual vs XGBoost Predicted (Test Set)')
plt.xlabel('Date')
plt.ylabel('Total Sales')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('reports/figures/actual_vs_predicted_xgb.png')
plt.close()

# 3. Residual Analysis for best model (assuming XGBoost is best)
residuals = y_test - xgb_preds
plt.figure(figsize=(10, 6))
sns.histplot(residuals, bins=50, kde=True)
plt.title('Residuals Distribution (XGBoost)')
plt.xlabel('Residual Error (Actual - Predicted)')
plt.tight_layout()
plt.savefig('reports/figures/residuals_xgb.png')
plt.close()

print("\nModel development and evaluation complete.")
