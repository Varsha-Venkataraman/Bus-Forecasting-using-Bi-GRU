import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, GRU, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import RMSprop

# ----------------------------
# Load bus series
# ----------------------------
def load_bus_series(filepath, bus_id):
    df = pd.read_csv(filepath, parse_dates=['Date'], dayfirst=True)
    df = df.sort_values('Date').reset_index(drop=True)

    if bus_id not in df.columns:
        raise ValueError(f"Bus ID '{bus_id}' not found in CSV columns: {df.columns.tolist()}")

    raw_series = df[['Date', bus_id]].copy()
    raw_series[bus_id] = raw_series[bus_id].fillna(0)
    raw_series['Weekday'] = raw_series['Date'].dt.weekday

    return raw_series

# ----------------------------
# Scale series with one-hot weekday
# ----------------------------
def scale_series(series, bus_id):
    scaler = MinMaxScaler()
    scaled_count = scaler.fit_transform(series[[bus_id]])
    weekday_encoded = pd.get_dummies(series['Weekday'], prefix='wd').values
    scaled = np.hstack([weekday_encoded, scaled_count])
    return scaled, scaler

# ----------------------------
# Create sequences
# ----------------------------
def create_sequences(scaled_data, lookback=28):
    X, y = [], []
    for i in range(len(scaled_data) - lookback):
        X.append(scaled_data[i:i+lookback])
        y.append(scaled_data[i+lookback][-1])  # Only passenger count
    return np.array(X), np.array(y)

# ----------------------------
# Build GRU model
# ----------------------------
def build_gru(lookback=28, input_dim=8):
    model = Sequential()
    model.add(Input(shape=(lookback, input_dim)))
    model.add(Bidirectional(GRU(64, return_sequences=True)))
    model.add(Dropout(0.2))
    model.add(GRU(32))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer=RMSprop(learning_rate=0.001), loss='mae')
    return model

# ----------------------------
# Train model
# ----------------------------
def train_model(model, X_train, y_train, epochs=50, batch_size=8):
    early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    history = model.fit(
        X_train, y_train,
        validation_split=0.3,
        epochs=epochs,
        batch_size=batch_size,
        callbacks=[early_stop],
        verbose=1
    )
    return history

# ----------------------------
# Forecast
# ----------------------------
def forecast(model, last_sequence, scaler, days=7, start_weekday=0):
    predictions = []
    seq = last_sequence.copy()
    weekday_template = np.eye(7)

    for i in range(days):
        weekday_vector = weekday_template[start_weekday % 7]
        pred_scaled = model.predict(seq.reshape(1, seq.shape[0], seq.shape[1]), verbose=0)[0][0]
        pred = scaler.inverse_transform([[pred_scaled]])[0][0]

        # Optional clamp for Sunday
        if start_weekday % 7 == 6:
            pred = 0

        print(f"📅 Forecast Day {i+1} → Weekday {start_weekday % 7} → Predicted: {round(pred, 2)}")

        next_step = np.append(weekday_vector, pred_scaled).reshape(1, -1)
        seq = np.vstack([seq[1:], next_step])
        start_weekday += 1
        predictions.append(max(0, pred))
    return predictions

# ----------------------------
# Evaluation (safe MAPE)
# ----------------------------
def evaluate_model(model, X_test, y_test, scaler):
    y_pred_scaled = model.predict(X_test, verbose=0)
    y_pred = scaler.inverse_transform(y_pred_scaled)[:, 0]
    y_true = scaler.inverse_transform(y_test.reshape(-1, 1))[:, 0]

    rmse = np.sqrt(np.mean((y_pred - y_true) ** 2))
    mae = np.mean(np.abs(y_pred - y_true))
    mask = y_true > 1e-5
    mape = np.mean(np.abs((y_pred[mask] - y_true[mask]) / y_true[mask])) * 100
    accuracy = 100 - mape

    print(f"\n✅ Accuracy: {accuracy:.2f}%")
    print(f"📊 RMSE: {rmse:.2f}")
    print(f"📊 MAE: {mae:.2f}")
    print(f"📊 MAPE: {mape:.2f}%")

    return {'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'Accuracy': accuracy}

# ----------------------------
# Plot historical + predicted
# ----------------------------
def plot_historical_predicted(historical, preds, bus_id, weekdays, dates, forecast_start_date):
    dates = pd.to_datetime(dates)
    forecast_dates = [forecast_start_date + pd.Timedelta(days=i) for i in range(len(preds))]
    all_data = historical + preds
    all_dates = dates.tolist() + forecast_dates
    labels = [date.strftime('%d-%b') for date in all_dates]
    colors = ['skyblue'] * len(historical) + ['orange'] * len(preds)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(range(len(all_data)), all_data, color=colors)

    for i in range(len(historical)):
        if weekdays[i] == 5:
            ax.bar(i, historical[i], color='lightcoral')
    for i in range(len(preds)):
        if forecast_dates[i].weekday() == 5:
            ax.bar(len(historical) + i, preds[i], color='red')

    tick_spacing = max(1, len(all_data) // 15)
    ax.set_xticks(range(0, len(all_data), tick_spacing))
    ax.set_xticklabels([labels[i] for i in range(0, len(all_data), tick_spacing)], rotation=30, ha='right')

    ax.set_ylabel("Number of Passengers")
    ax.set_title(f"Bus {bus_id} Demand Forecast")
    plt.tight_layout()

    return fig

# ----------------------------
# Main run
# ----------------------------
def run_bus_prediction(bus_id, filepath='bus_data.csv', lookback=28, forecast_days=7):
    raw_series = load_bus_series(filepath, bus_id)

    historical_values = raw_series[bus_id].tolist()
    weekdays = raw_series['Weekday'].tolist()
    dates = raw_series['Date'].tolist()
    forecast_start_date = raw_series['Date'].iloc[-1] + pd.Timedelta(days=1)
    start_weekday = (raw_series['Weekday'].iloc[-1] + 1) % 7

    scaled, scaler = scale_series(raw_series, bus_id)
    X, y = create_sequences(scaled, lookback)
    input_dim = X.shape[2]

    model = build_gru(lookback, input_dim)
    train_model(model, X, y, epochs=50, batch_size=8)

    last_seq = X[-1]
    preds = forecast(model, last_seq, scaler, days=forecast_days, start_weekday=start_weekday)

    fig = plot_historical_predicted(historical_values, preds, bus_id, weekdays, dates, forecast_start_date)
    evaluate_model(model, X, y, scaler)

    return preds, fig

"""
# ----------------------------
# Run Test predictions
# ----------------------------
if __name__ == "__main__":
    open('final_predictions.csv', 'w').close()
    for bus_id in ['5']:
        print(f"\n🔄 Running prediction for Bus ID: {bus_id}")
        run_bus_prediction(bus_id=bus_id, filepath='bus_data.csv')
"""
