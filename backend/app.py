import os
import sys
import json
import traceback
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure environment variables from project root .env are loaded before any services
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(env_path)

# Ensure backend directory is in sys.path so sibling modules load correctly under any WSGI runner
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import market_service
import genai_service

app = Flask(__name__)
CORS(app)

# ==========================================
# Load Models & Metadata
# ==========================================

print("Loading XGBoost model...")
model_path = os.path.join(os.path.dirname(__file__), '../models/saved_models/xgboost.joblib')
model = joblib.load(model_path)

print("Loading Store Metadata...")
store_path = os.path.join(os.path.dirname(__file__), '../data/raw/store.csv')
store_df = pd.read_csv(store_path)

print("Loading historical lags (latest available per store)...")
store_lags_path = os.path.join(os.path.dirname(__file__), '../data/processed/store_lags.csv')
if os.path.exists(store_lags_path):
    latest_lags = pd.read_csv(store_lags_path)
    print(f"Loaded {len(latest_lags)} store historical lag profiles from store_lags.csv.")
else:
    # Graceful fallback to test_fe.csv if store_lags.csv is missing
    test_fe_path = os.path.join(os.path.dirname(__file__), '../data/processed/test_fe.csv')
    test_df = pd.read_csv(test_fe_path)
    latest_lags = test_df.sort_values('Date').groupby('Store').last().reset_index()[['Store', 'Lag_1', 'Lag_7', 'RollingMean_7']]
    print(f"Fallback: Loaded {len(latest_lags)} store profiles from test_fe.csv.")

# Required features in exact order used during training
FEATURES = ['Store', 'DayOfWeek', 'Open', 'Promo', 'SchoolHoliday', 'CompetitionDistance', 
            'CompetitionOpenSinceMonth', 'CompetitionOpenSinceYear', 'Promo2', 'Promo2SinceWeek', 
            'Promo2SinceYear', 'Year', 'Month', 'Week', 'IsWeekend', 'Lag_1', 'Lag_7', 'RollingMean_7', 
            'StoreType_b', 'StoreType_c', 'StoreType_d', 'Assortment_b', 'Assortment_c', 
            'StateHoliday_EasterHoliday', 'StateHoliday_None', 'StateHoliday_PublicHoliday', 
            'PromoInterval_Jan,Apr,Jul,Oct', 'PromoInterval_Mar,Jun,Sept,Dec']

# ==========================================
# Static Asset & Frontend Serving
# ==========================================

@app.route('/', methods=['GET'])
def serve_index():
    """Serves the dashboard index.html when accessed via Flask root."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return send_from_directory(root_dir, 'index.html')

@app.route('/frontend/<path:filename>', methods=['GET'])
def serve_frontend(filename):
    """Serves CSS, JS, and image assets from the frontend directory."""
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    return send_from_directory(frontend_dir, filename)

@app.route('/reports/figures/<path:filename>', methods=['GET'])
def serve_figures(filename):
    """Serves generated report figures."""
    figures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../reports/figures'))
    return send_from_directory(figures_dir, filename)

# ==========================================
# Health & Monitoring Endpoints
# ==========================================

@app.route('/health', methods=['GET'])
def health():
    """Returns backend status, model loading state, and active store lag profile count."""
    return jsonify({
        'status': 'healthy',
        'service': 'BusinessMind Sales Prediction API',
        'model_loaded': model is not None,
        'model_algorithm': 'XGBoost Regressor',
        'stores_loaded': int(len(latest_lags)),
        'features_count': len(FEATURES),
        'environment': 'development' if app.debug else 'production'
    }), 200

@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Dynamically reads and returns verified model evaluation metrics."""
    metrics_path = os.path.join(os.path.dirname(__file__), '../reports/model_metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r', encoding='utf-8') as f:
                metrics_data = json.load(f)
            return jsonify({
                'status': 'success',
                'metrics': metrics_data
            }), 200
        except Exception as e:
            return jsonify({'error': f'Failed to parse metrics: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Metrics file not found.'}), 404

@app.route('/ai/health', methods=['GET'])
def ai_health():
    """Returns safe diagnostic information regarding AI Advisor status without exposing secrets."""
    return jsonify(genai_service.get_ai_health()), 200

# ==========================================
# Core ML Prediction Endpoint
# ==========================================

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # 1. Input Validation
        try:
            store_id = int(data.get('store_id', 1))
            if store_id < 1 or store_id > 1115:
                return jsonify({'error': f'Store ID {store_id} is out of valid range (1 to 1,115).'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid store_id provided. Must be an integer between 1 and 1,115.'}), 400

        date_str = str(data.get('date', '2015-07-20')).strip()
        try:
            date_obj = pd.to_datetime(date_str)
        except Exception:
            return jsonify({'error': f"Invalid date '{date_str}'. Expected valid date format (YYYY-MM-DD)."}), 400

        try:
            promo = 1 if str(data.get('promo', 1)).strip() in ['1', 'true', 'True'] else 0
        except Exception:
            promo = 0

        try:
            school_holiday = 1 if str(data.get('school_holiday', 0)).strip() in ['1', 'true', 'True'] else 0
        except Exception:
            school_holiday = 0

        state_holiday = str(data.get('state_holiday', 'None')).strip()
        if state_holiday not in ['None', 'PublicHoliday', 'EasterHoliday', 'Christmas']:
            state_holiday = 'None'

        # 2. Calendar Features
        year = date_obj.year
        month = date_obj.month
        week = date_obj.isocalendar().week
        day_of_week = date_obj.dayofweek
        is_weekend = 1 if day_of_week >= 5 else 0
        is_open = 0 if state_holiday != 'None' and day_of_week == 6 else 1  # Standard retail operating heuristic

        # 3. Store Metadata Features
        store_info = store_df[store_df['Store'] == store_id]
        if store_info.empty:
            return jsonify({'error': f'Store ID {store_id} not found.'}), 400
        store_info = store_info.iloc[0]

        if 'competition_distance' in data and data.get('competition_distance') is not None and str(data.get('competition_distance')).strip() != '':
            try:
                comp_dist = float(data['competition_distance'])
            except (ValueError, TypeError):
                comp_dist = store_info['CompetitionDistance'] if not pd.isna(store_info['CompetitionDistance']) else store_df['CompetitionDistance'].max()
        else:
            comp_dist = store_info['CompetitionDistance'] if not pd.isna(store_info['CompetitionDistance']) else store_df['CompetitionDistance'].max()
        comp_month = store_info['CompetitionOpenSinceMonth'] if not pd.isna(store_info['CompetitionOpenSinceMonth']) else 0
        comp_year = store_info['CompetitionOpenSinceYear'] if not pd.isna(store_info['CompetitionOpenSinceYear']) else 0
        promo2 = store_info['Promo2']
        promo2_week = store_info['Promo2SinceWeek'] if not pd.isna(store_info['Promo2SinceWeek']) else 0
        promo2_year = store_info['Promo2SinceYear'] if not pd.isna(store_info['Promo2SinceYear']) else 0
        promo_interval = store_info['PromoInterval'] if not pd.isna(store_info['PromoInterval']) else ''
        
        # 3. Lags
        lags = latest_lags[latest_lags['Store'] == store_id]
        if not lags.empty:
            lag1 = lags['Lag_1'].values[0]
            lag7 = lags['Lag_7'].values[0]
            roll7 = lags['RollingMean_7'].values[0]
        else:
            # Fallback if store not in lag set
            lag1, lag7, roll7 = 5000, 5000, 5000 

        # 4. Construct Row Dictionary with exact feature order
        row = {f: 0 for f in FEATURES}
        row['Store'] = store_id
        row['DayOfWeek'] = day_of_week
        row['Open'] = is_open
        row['Promo'] = promo
        row['SchoolHoliday'] = school_holiday
        row['CompetitionDistance'] = comp_dist
        row['CompetitionOpenSinceMonth'] = comp_month
        row['CompetitionOpenSinceYear'] = comp_year
        row['Promo2'] = promo2
        row['Promo2SinceWeek'] = promo2_week
        row['Promo2SinceYear'] = promo2_year
        row['Year'] = year
        row['Month'] = month
        row['Week'] = week
        row['IsWeekend'] = is_weekend
        row['Lag_1'] = lag1
        row['Lag_7'] = lag7
        row['RollingMean_7'] = roll7

        # Categoricals (One-Hot Encoded)
        store_type = store_info['StoreType']
        if f'StoreType_{store_type}' in row: row[f'StoreType_{store_type}'] = 1
        
        assort = store_info['Assortment']
        if f'Assortment_{assort}' in row: row[f'Assortment_{assort}'] = 1

        if f'StateHoliday_{state_holiday}' in row: row[f'StateHoliday_{state_holiday}'] = 1
        elif state_holiday == 'None' and 'StateHoliday_None' in row: row['StateHoliday_None'] = 1

        if promo_interval == 'Jan,Apr,Jul,Oct': row['PromoInterval_Jan,Apr,Jul,Oct'] = 1
        elif promo_interval == 'Mar,Jun,Sept,Dec': row['PromoInterval_Mar,Jun,Sept,Dec'] = 1

        # Predict
        input_df = pd.DataFrame([row])
        # Ensure column order matches training features exactly
        input_df = input_df[FEATURES]
        
        prediction = model.predict(input_df)[0]
        
        # Ensure we don't predict negative sales or sales when closed
        if is_open == 0:
            prediction = 0
        prediction = max(0, float(prediction))

        return jsonify({
            'status': 'success',
            'prediction': round(prediction, 2),
            'inputs': data
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# ==========================================
# Market Intelligence Endpoints
# ==========================================

@app.route('/market/competitor', methods=['POST'])
def market_competitor():
    data = request.json
    if not data or not data.get('competitor_name'):
        return jsonify({'error': 'Missing competitor_name in request'}), 400
        
    result, status_code = market_service.get_competitor_analysis(data['competitor_name'])
    return jsonify(result), status_code

@app.route('/market/keyword', methods=['POST'])
def market_keyword():
    data = request.json
    if not data or not data.get('topic'):
        return jsonify({'error': 'Missing topic in request'}), 400
        
    result, status_code = market_service.get_keyword_search(data['topic'])
    return jsonify(result), status_code

@app.route('/market/trend', methods=['POST'])
def market_trend():
    data = request.json
    if not data or not data.get('industry'):
        return jsonify({'error': 'Missing industry in request'}), 400
        
    result, status_code = market_service.get_trend_discovery(data['industry'])
    return jsonify(result), status_code

# ==========================================
# GenAI Insight Endpoint
# ==========================================

@app.route('/insights', methods=['POST'])
def generate_insights():
    data = request.json
    if not data or ('prediction' not in data and 'predicted_sales' not in data):
        return jsonify({'error': 'Missing prediction data in request'}), 400
        
    result, status_code = genai_service.generate_insights(data)
    return jsonify(result), status_code

# ==========================================
# Application Entry Point
# ==========================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1' or os.environ.get('FLASK_ENV') == 'development'
    print(f"Starting BusinessMind ML API on port {port} (debug={debug_mode})...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
