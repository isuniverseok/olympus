import sys
import os
import numpy as np
import pandas as pd
from pages.prediction import prepare_lstm_data, train_lstm_model, predict_future_medals_lstm

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    # Set parameters
    noc = 'USA'
    season = 'Summer'
    sequence_length = 3
    
    print(f"Preparing LSTM data for {noc} in {season} Olympics...")
    X, y = prepare_lstm_data(noc, season, sequence_length)
    print(f"Data shape: X={X.shape}, y={y.shape}")
    
    print("Training LSTM model...")
    model, scaler, rmse, r2, history = train_lstm_model(X, y)
    print(f"Model trained with RMSE: {rmse:.2f}, R²: {r2:.2f}")
    
    # Get last sequence for prediction
    last_sequence = X[-1]
    
    # Make predictions
    print("\nMaking predictions...")
    predictions = predict_future_medals_lstm(model, scaler, last_sequence, years_ahead=4)
    
    # Print results
    print(f"\nPredicted medals for {noc} in {season} Olympics:")
    print("----------------------------------------")
    years = [2016 + 4 * (i + 1) for i in range(len(predictions))]
    for year, medals in zip(years, predictions):
        print(f"Year {year}: {medals} medals")

if __name__ == "__main__":
    main() 