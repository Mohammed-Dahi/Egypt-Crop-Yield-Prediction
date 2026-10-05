# 🌾 Egypt Crop Yield Prediction — End-to-End Project

Predict crop yield (kg/ha) in Egypt from FAOSTAT data, with a web app that runs instantly in the browser (no installation).

## Pipeline
1. **Data:** `train_data.csv` (3,502 rows) and `test_data.csv` (827 rows), 76 crops, 1964–2024.
2. **Features:** Item (crop) + Yield_Lag1 / Lag2 + Production_Lag1 + Area_Lag1 + Yield_RollingMean_3Y + Area_Growth_Lag1 + Production_Growth_Lag1.
3. **Baseline:** persistence (predict last year's yield).
4. **Models:** Linear Regression (One-Hot + StandardScaler) and Decision Tree (`max_depth` tuned on a chronological validation split, the latest 20% of years; best depth = 5).
5. **Test results:**

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Baseline | 929 | 2,672 | 0.973 |
| **Linear Regression** | 1,140 | **2,498** | 0.977 |
| Decision Tree (depth 5) | 1,361 | 2,695 | 0.973 |

   Linear Regression has the lowest RMSE, so it is the app's default. The baseline has the lowest MAE: for a typical crop-year, repeating last year's yield is already strong, and the model helps mainly on large jumps.
6. **Deployment:** both models were refit on train + test and exported to `model.json`; `crop_yield_app.html` computes predictions in the browser.

## Files
- `train_model.py` — training, evaluation, model export
- `model.json` — Linear Regression coefficients and decision tree
- `crop_yield_app.html` — the app

## Run
`pip install pandas scikit-learn`, then `python train_model.py` (CSV files next to it). Open the HTML file directly in a browser.

## Notes
- Rolling mean = average of the last 3 years (t-1, t-2, t-3).
- 2024 is the last year in the data, so 2024 area/production are unavailable; in "Forecast next year" mode the app assumes they equal the last known values.
- Results are predictive relationships, not causal effects.
