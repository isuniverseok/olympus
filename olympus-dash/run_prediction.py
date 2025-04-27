import sys
import os
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.prediction import (
    prepare_prediction_data,
    train_prediction_model,
    predict_future_medals,
    prepare_lstm_data,
    train_lstm_model,
    predict_future_medals_lstm
)
from data_loader import df

# Host cities and their NOCs
HOST_CITIES = {
    1896: ('Athens', 'GRE'),
    1900: ('Paris', 'FRA'),
    1904: ('St. Louis', 'USA'),
    1908: ('London', 'GBR'),
    1912: ('Stockholm', 'SWE'),
    1920: ('Antwerp', 'BEL'),
    1924: ('Paris', 'FRA'),
    1928: ('Amsterdam', 'NED'),
    1932: ('Los Angeles', 'USA'),
    1936: ('Berlin', 'GER'),
    1948: ('London', 'GBR'),
    1952: ('Helsinki', 'FIN'),
    1956: ('Melbourne', 'AUS'),
    1960: ('Rome', 'ITA'),
    1964: ('Tokyo', 'JPN'),
    1968: ('Mexico City', 'MEX'),
    1972: ('Munich', 'GER'),
    1976: ('Montreal', 'CAN'),
    1980: ('Moscow', 'RUS'),
    1984: ('Los Angeles', 'USA'),
    1988: ('Seoul', 'KOR'),
    1992: ('Barcelona', 'ESP'),
    1996: ('Atlanta', 'USA'),
    2000: ('Sydney', 'AUS'),
    2004: ('Athens', 'GRE'),
    2008: ('Beijing', 'CHN'),
    2012: ('London', 'GBR'),
    2016: ('Rio de Janeiro', 'BRA'),
    2020: ('Tokyo', 'JPN')
}

def main():
    # Set parameters
    noc = 'USA'
    season = 'Summer'
    years_ahead = 4  # Predict for 2020 and 2024
    
    print(f"\nPredicting for {noc} in {season} Olympics")
    
    # Run Decision Tree Model
    print("\n=== Decision Tree Model ===")
    prediction_data = prepare_prediction_data(noc, season)
    print(f"Prediction data shape: {prediction_data.shape}")
    
    print("Training model...")
    model, scaler, rmse, r2, feature_importance = train_prediction_model(prediction_data)
    
    last_year = prediction_data['Year'].max()
    last_athlete_count = prediction_data['Athlete_Count'].iloc[-1]
    last_medals = prediction_data['Medal_Count'].iloc[-1]
    print(f"Last known data - Year: {last_year}, Athletes: {last_athlete_count}, Medals: {last_medals}")
    
    print("Making predictions...")
    dt_predictions = predict_future_medals(model, scaler, last_year, last_athlete_count, last_medals, season, years_ahead)
    
    print("\nPredicted medals (Decision Tree):")
    print("----------------------------------------")
    for _, row in dt_predictions.iterrows():
        print(f"Year {row['Year']}: {row['Predicted_Medals']} medals (with {row['Predicted_Athletes']} athletes)")
    
    print("\nModel Performance:")
    print(f"RMSE: {rmse:.2f}")
    print("Feature Importance:")
    print(feature_importance)
    
    # Run LSTM Model
    print("\n=== LSTM Model ===")
    print("Preparing LSTM data...")
    X, y = prepare_lstm_data(noc, season)
    print(f"LSTM data shape - X: {X.shape}, y: {y.shape}")
    
    print("Training LSTM model...")
    lstm_model, lstm_scaler, lstm_rmse, lstm_r2, history = train_lstm_model(X, y)
    
    print("Making LSTM predictions...")
    last_sequence = X[-1]
    lstm_predictions = predict_future_medals_lstm(lstm_model, lstm_scaler, last_sequence, years_ahead)
    
    print("\nPredicted medals (LSTM):")
    print("----------------------------------------")
    for i, medals in enumerate(lstm_predictions):
        year = last_year + 4 * (i + 1)
        print(f"Year {year}: {medals} medals")
    
    print("\nLSTM Model Performance:")
    print(f"RMSE: {lstm_rmse:.2f}")
    print(f"R² Score: {lstm_r2:.2f}")
    
    # Compare predictions
    print("\n=== Model Comparison ===")
    print("Year\tDecision Tree\tLSTM\tDifference")
    print("----------------------------------------")
    for i in range(len(lstm_predictions)):
        year = last_year + 4 * (i + 1)
        dt_medals = dt_predictions.iloc[i]['Predicted_Medals']
        lstm_medals = lstm_predictions[i]
        diff = abs(dt_medals - lstm_medals)
        print(f"{year}\t{dt_medals}\t\t{lstm_medals}\t{diff}")

if __name__ == "__main__":
    main() 