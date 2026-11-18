# 📊 BusinessMind: Enterprise Retail Sales Prediction & Executive Analytics

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![XGBoost](https://img.shields.io/badge/Model-XGBoost%20Regressor-orange.svg)](https://xgboost.readthedocs.io/)
[![Deployment](https://img.shields.io/badge/Deploy-Render%20Ready-green.svg)](https://render.com/)

**BusinessMind** is an end-to-end Machine Learning web application designed to forecast daily retail store sales, simulate "What-If" business scenarios, and generate executive business insights with automated fallback synthesis.

Built for retail store managers, analysts, and enterprise planners, BusinessMind bridges the gap between raw statistical forecasting and managerial decision-making.

---

## 📑 Table of Contents
1. [Project Overview & Problem Statement](#-project-overview--problem-statement)
2. [Core Features](#-core-features)
3. [System Architecture](#-system-architecture)
4. [Dataset & Feature Engineering](#-dataset--feature-engineering)
5. [Model Benchmarks & Evaluation](#-model-benchmarks--evaluation)
6. [API Specification](#-api-specification)
7. [Installation & Local Setup](#-installation--local-setup)
8. [Production Deployment (Render)](#-production-deployment-render)
9. [Project Directory Structure](#-project-directory-structure)
10. [Methodology & Disclaimers](#-methodology--disclaimers)
11. [Limitations & Future Roadmap](#-limitations--future-roadmap)

---

## 🎯 Project Overview & Problem Statement

Retail store chains with hundreds of geographically dispersed locations face complex operational challenges:
- **Demand Volatility**: Sales vary drastically across promotional cycles, public holidays, school vacations, and day-of-week patterns.
- **Resource Misallocation**: Inaccurate demand estimation leads to over-staffing or under-stocking, inflating operational costs and eroding operating margins.
- **Decision Silos**: Traditional machine learning models deliver isolated numerical predictions without operational context or scenario simulation.

**BusinessMind** addresses these challenges by uniting:
1. **High-Accuracy Supervised ML**: An engineered XGBoost Regressor explaining ~90% of sales variance ($R^2 = 0.8999$).
2. **Interactive What-If Simulation**: Sensitivity comparison allowing managers to model promotional and calendar interventions before execution.
3. **Executive Business Summary Synthesis**: Structured managerial interpretation with a resilient zero-downtime heuristic fallback engine.
4. **Accessible Analytical UI**: Dual Light/Dark mode dashboard with comfortable contrast, typography, and clean information hierarchy.

---

## 🚀 Core Features

### 1. 🔮 Real-Time Sales Prediction Engine
- Generates store-specific daily sales revenue estimates using 28 verified features.
- Accounts for day-of-week seasonality, store type, assortment level, promotional status, calendar holidays, and historical lag trends.
- Automatically handles store closure heuristics (zero sales when closed).

### 2. ⚡ Smart What-If Sales Analysis
- **Side-by-Side Scenario Simulation**: Compare a **Baseline Scenario (A)** against a **Simulated Scenario (B)** for any target date.
- **Multi-Factor Sensitivity**: Adjust promotion status, public holidays, school holidays, and competitor proximity.
- **Delta Analysis**: Displays absolute dollar delta ($\pm\$X$) and percentage revenue lift ($\pm Y\%$) with a visual sensitivity bar.
- Evaluates operational changes as model-based scenario estimates without claiming unverified causal certainty.

### 3. 🧠 Executive Business Insights & Resilient Fallback
- Interprets forecast numbers into an executive 6-section business report:
  1. *Sales Forecast Summary*
  2. *Key Factors*
  3. *Business Interpretation*
  4. *Recommended Operational Actions*
  5. *Risks & Limitations*
  6. *Final Business Insight*
- **Enterprise-Grade Fallback**: If external generative APIs are unreachable, rate-limited, or unconfigured, an automated local heuristic engine instantly serves a structured managerial brief without downtime.

### 4. 📊 Model Diagnostics & Visual Comparison
- Interactive metrics table reading dynamic evaluation scores directly from the backend.
- Embedded diagnostic visualizations:
  - *Actual vs. Predicted Daily Sales (Chronological Test Set)*
  - *Model Comparison (MAE, RMSE, $R^2$ across Linear Regression, Random Forest, XGBoost)*
  - *XGBoost Residual Error Distribution (Gaussian validation)*

### 5. 🎨 Polished Dual-Theme Interface
- Warm off-white and sage green light theme by default for high readability.
- Professional charcoal/graphite dark mode accessible via a one-click header toggle.
- Theme selection persists across browser reloads via `localStorage`.
- White chart containers ensure all Matplotlib plots remain readable in both themes.

---

## 🏗 System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT / USER BROWSER                           │
│                                                                        │
│   Vanilla HTML5 + Modern CSS3 + Modular ES6 JavaScript                 │
│   ├── Dynamic API Base URL Resolution (Same-Origin / Remote)           │
│   ├── Real-Time Health Status Polling (GET /health)                    │
│   ├── Dynamic Evaluation Metrics Fetcher (GET /metrics)                │
│   ├── XGBoost Prediction Form & Business Summary Controller           │
│   ├── Smart What-If Scenario Comparison Engine                         │
│   └── Persistent Light / Dark Mode Theme Switcher                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP JSON Requests (CORS Enabled)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   BACKEND WEB SERVER (Flask / Gunicorn)                │
│                                                                        │
│   backend/app.py                                                       │
│   ├── Static Asset Delivery (/, /frontend/*, /reports/figures/*)       │
│   ├── GET /health ──────────────► System Status & Model Health         │
│   ├── GET /metrics ─────────────► reports/model_metrics.json           │
│   ├── POST /predict ────────────► XGBoost Pipeline (28 Features)       │
│   └── POST /insights ───────────► backend/genai_service.py             │
│                                   (External Synthesis + Fallback)      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       MODELS & DATA ASSETS                             │
│                                                                        │
│   ├── models/saved_models/xgboost.joblib (Trained Estimator, 893 KB)   │
│   ├── data/raw/store.csv (1,115 Store Metadata Records)                │
│   └── data/processed/store_lags.csv (Optimized Store Lag Profiles)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📈 Dataset & Feature Engineering

### Dataset Description
The machine learning pipeline is built on the real-world **Rossmann Store Sales** dataset, comprising historical daily sales across **1,115 retail pharmacy stores**:
- **Store Metadata**: Store type (`a`, `b`, `c`, `d`), assortment tier (`a`, `b`, `c`), competitor distance in meters, and promotion interval cycles.
- **Operating Context**: Customer open/closed status, school holidays, state holidays (`PublicHoliday`, `EasterHoliday`, `Christmas`).

### Feature Engineering & Leakage Prevention
To ensure rigorous time-series validity and eliminate lookahead bias:
1. **Chronological Sorting**: Data is sorted strictly by `Store` and `Date`.
2. **Past Information Only**: Historical sales signals are extracted strictly via shifted operations:
   - `Lag_1`: Previous day's sales (`shift(1)`).
   - `Lag_7`: Same-day sales from the prior week (`shift(7)`).
   - `RollingMean_7`: 7-day rolling sales average shifted by 1 day.
3. **Leakage Elimination**: The `Customers` feature was excluded from training because customer footfall is unknown at forecast time.
4. **Calendar Deconstruction**: Extracted `Year`, `Month`, `Week`, `DayOfWeek` (0=Mon, 6=Sun), and `IsWeekend`.
5. **One-Hot Encoding**: Dummy variables for store types, assortment tiers, holidays, and promo intervals.
6. **Chronological Train/Test Split**: The final 6 weeks of unseen chronological data (41,396 records) were reserved exclusively for evaluation.
7. **Cold-Start Optimization**: Extracted store-level lag values into [`data/processed/store_lags.csv`](data/processed/store_lags.csv) (39 KB), cutting startup memory overhead by 99% compared to parsing full raw test datasets.

---

## 🔬 Model Benchmarks & Evaluation

Three regression algorithms were trained and evaluated on the identical 6-week unseen chronological test split (41,396 records):

| Model Algorithm | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | $R^2$ Variance Explained | Selection Status |
| :--- | :---: | :---: | :---: | :---: |
| **Linear Regression (Baseline)** | \$1,071.20 | \$1,505.63 | 0.7553 | Baseline |
| **Random Forest Regressor** | **\$664.02** | \$973.96 | 0.8976 | Candidate (114 MB file) |
| **XGBoost Regressor** | \$670.96 | **\$963.28** | **0.8999** | **Selected Production Model** |

### Why XGBoost Was Selected:
- **Lowest RMSE (\$963.28)**: Penalizes large forecasting errors heavily, protecting retail managers from severe under-stocking.
- **Highest $R^2$ (0.8999)**: Explains ~90% of the variance across diverse store formats and holiday spikes.
- **Deployment Efficiency**: Model binary size is only **893 KB** (vs. 114 MB for Random Forest), enabling sub-millisecond inference and clean cloud deployment within standard container limits.

---

## 🔌 API Specification

### 1. `GET /health`
Returns backend health, model load state, and active store lag profile count.
```json
{
  "environment": "production",
  "features_count": 28,
  "model_algorithm": "XGBoost Regressor",
  "model_loaded": true,
  "service": "BusinessMind Sales Prediction API",
  "status": "healthy",
  "stores_loaded": 1115
}
```

### 2. `GET /metrics`
Dynamically reads validated evaluation benchmarks from `reports/model_metrics.json`.
```json
{
  "metrics": {
    "Linear Regression": { "MAE": 1071.20, "RMSE": 1505.63, "R2": 0.7553 },
    "Random Forest": { "MAE": 664.02, "RMSE": 973.96, "R2": 0.8976 },
    "XGBoost": { "MAE": 670.96, "RMSE": 963.28, "R2": 0.8999 }
  },
  "status": "success"
}
```

### 3. `POST /predict`
Generates a sales prediction for specified calendar and operating conditions.
- **Payload**:
  ```json
  {
    "store_id": 1,
    "date": "2015-07-20",
    "promo": 1,
    "state_holiday": "None",
    "school_holiday": 0,
    "competition_distance": 1270
  }
  ```
- **Response**:
  ```json
  {
    "status": "success",
    "prediction": 7824.51,
    "inputs": { ... }
  }
  ```

### 4. `POST /insights`
Generates managerial business interpretation with automated fallback.
- **Payload**:
  ```json
  {
    "store_id": 1,
    "date": "2015-07-20",
    "promo": 1,
    "state_holiday": "None",
    "school_holiday": 0,
    "prediction": 7824.51
  }
  ```
- **Response**:
  ```json
  {
    "insights": "<div class=\"ai-report-section\">...</div>",
    "status": "success"
  }
  ```

---

## 💻 Installation & Local Setup

### Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/BusinessMind.git
cd BusinessMind
```

### 2. Create and Activate Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template configuration file:
```bash
cp .env.example .env
```
Open `.env` in any text editor:
```env
# Optional: Add active keys for live external AI insights
# (If left as placeholders, system gracefully utilizes built-in fallbacks)
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-flash-lite-latest
GEMINI_FALLBACK_MODEL=gemini-3.6-flash
PORT=5000
FLASK_ENV=development
FLASK_DEBUG=1
```

### 5. Run the Application

#### Option A: Flask Development Server
```bash
python backend/app.py
```
Open **`http://localhost:5000`** in your browser.

#### Option B: Gunicorn Production Server (Linux/macOS)
```bash
gunicorn backend.app:app
```

---

## ☁️ Production Deployment (Render)

BusinessMind is architected for automated, single-service deployment on **[Render](https://render.com/)**.

### Step 1: Push Code to GitHub
Ensure `.env` is ignored by `.gitignore` and push your repository to GitHub:
```bash
git status
git add .
git commit -m "Prepare BusinessMind for production deployment"
git branch -M main
git remote add origin https://github.com/<your-username>/BusinessMind.git
git push -u origin main
```

### Step 2: Create a New Web Service on Render
1. Log into your Render Dashboard and click **New + > Web Service**.
2. Connect your GitHub repository (`BusinessMind`).
3. Set the following configuration settings:
   - **Environment**: `Python 3`
   - **Region**: Select closest region (e.g. Frankfurt, Oregon, Ohio)
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command**:
     ```bash
     gunicorn backend.app:app
     ```
   - **Plan**: `Free`

### Step 3: Configure Environment Variables in Render
In the **Environment** tab of your Render service, add:
- `PYTHON_VERSION` = `3.11.9`
- `FLASK_ENV` = `production`
- `FLASK_DEBUG` = `0`
- `GEMINI_MODEL` = `gemini-flash-lite-latest`
- `GEMINI_FALLBACK_MODEL` = `gemini-3.6-flash`
- `GEMINI_API_KEY` = *(Optional: your API key for live external synthesis)*

Render automatically binds to the `$PORT` variable and provisions an HTTPS URL (e.g. `https://businessmind.onrender.com`).

---

## 📁 Project Directory Structure

```
BusinessMind/
├── backend/
│   ├── __init__.py               # Package marker for WSGI runners
│   ├── app.py                    # Flask application, routing & asset serving
│   └── genai_service.py          # AI business insights & heuristic fallback
├── data/
│   ├── processed/
│   │   ├── store_lags.csv        # 39 KB pre-extracted store lag profiles
│   │   └── test_fe.csv           # 6.26 MB feature-engineered test set
│   └── raw/
│       └── store.csv             # Store metadata (Assortment, StoreType, etc.)
├── frontend/
│   ├── css/
│   │   └── style.css             # Dual light/dark theme, layout & cards
│   └── js/
│       └── main.js               # Client controller, What-If simulator, theme engine
├── models/
│   └── saved_models/
│       ├── linear_regression.joblib  # Baseline model binary (1 KB)
│       └── xgboost.joblib            # Selected production model binary (893 KB)
├── reports/
│   ├── figures/                  # Diagnostic plots (comparison, residuals, trends)
│   └── model_metrics.json        # Verified benchmark evaluation results
├── .env.example                  # Environment configuration template
├── .gitignore                    # Protection for secrets & files > 100 MB
├── index.html                    # Single-page application dashboard layout
├── README.md                     # Comprehensive project documentation
├── render.yaml                   # Infrastructure-as-code deployment blueprint
└── requirements.txt              # Production Python package manifest
```

---

## ⚖️ Methodology & Disclaimers

1. **Model-Based Scenario Estimations**:
   The **Smart What-If Sales Analysis** computes predictions strictly by passing modified feature vectors into the trained XGBoost model. It reflects the model's mathematical sensitivity to input variations and serves as a planning heuristic; it does not claim to establish verified causal mechanisms.
2. **Data Protection**:
   All API credentials and secret files are excluded from version control via `.gitignore`.

---

## 🔮 Limitations & Future Roadmap

- **Interactive Dynamic Plotting**: Future iterations can replace static Matplotlib figures with dynamic Plotly/Chart.js charts allowing store-level filtering.
- **Automated Weather Feeds**: Integrating localized historical and forecast weather APIs to refine demand estimation during extreme meteorological conditions.
- **Inventory Replenishment Recommendations**: Translating dollar revenue forecasts into SKU-level stocking recommendations.

---

## 👨‍💻 Capstone Information

- **Project**: BusinessMind — Retail Sales Prediction & Executive Analytics
- **Specialization**: B.Tech Computer Science & Engineering (AI & ML)
- **Primary Model**: XGBoost Regressor ($R^2 = 0.8999$, RMSE = \$963.28)
- **License**: MIT License
