# Bus Ridership Forecasting Using Bidirectional GRU

## Overview
This project combines a deep learning framework for bus ridership forecasting with a management system to handle drivers and buses. The forecasting component uses a Bidirectional GRU (Bi‑GRU) model trained on a 28‑day historical lookback window to predict daily demand, helping improve scheduling, fleet allocation, and operational efficiency. The management system complements this by providing structured modules to manage bus and driver information, ensuring the solution is practical and applicable in real-world transit operations.

## Key Features
- **Bi‑GRU Forecasting Model**: Learns short-term fluctuations and weekly commuting patterns for accurate ridership prediction.
- **Data Preprocessing**: Cleaning, normalization, and construction of multivariate time series sequences for robust training.
- **Training & Optimization**: RMSprop optimizer, Huber loss, early stopping, and heuristics (Sunday clamping, Monday boosting) for improved accuracy.
- **Forecast Visualization**: Clear bar graph outputs comparing predicted ridership with historical data.
- **Management System**: Modules to manage drivers and buses, integrated with forecasting for operational efficiency.
- **Project Structure**:
  - `db_utils.py` – Database utilities
  - `bus_ops.py` – Bus management functions
  - `driver_ops.py` – Driver management functions
  - `prediction.py` – Forecasting model implementation
  - `app.py` – Main application logic
