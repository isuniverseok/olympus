# pages/prediction.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

dash.register_page(__name__, name='Prediction')

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
    2020: ('Tokyo', 'JPN'),
    2024: ('Paris', 'FRA'),
    2028: ('Los Angeles', 'USA')
}

def prepare_prediction_data(noc, season):
    country_data = df[df['NOC'] == noc].copy()
    
    # Filter by season
    if season == 'Summer':
        country_data = country_data[country_data['Year'] % 4 == 0]  
    else:  
        country_data = country_data[country_data['Year'] % 4 == 2]  
    
     
    yearly_medals = country_data[country_data['Medal'] != 'None'].groupby(['Year', 'Event', 'Medal']).size().reset_index()
    yearly_medals = yearly_medals.groupby('Year')['Medal'].count().reset_index()
    yearly_medals.columns = ['Year', 'Medal_Count']
    
    yearly_athletes = country_data.groupby('Year')['Name'].nunique().reset_index()
    yearly_athletes.columns = ['Year', 'Athlete_Count']
    
    yearly_medals['Previous_Medals'] = yearly_medals['Medal_Count'].shift(1)
    yearly_medals['Previous_Medals'] = yearly_medals['Previous_Medals'].fillna(0)
    
    yearly_medals['Host_Status'] = yearly_medals['Year'].apply(
        lambda x: 1 if x in [year for year, (_, host_noc) in HOST_CITIES.items() if host_noc == noc] else 0
    )
    
    prediction_data = pd.merge(yearly_medals, yearly_athletes, on='Year', how='outer')
    prediction_data = prediction_data.fillna(0)
    
    return prediction_data

def train_prediction_model(data):
    X = data[['Year', 'Athlete_Count', 'Previous_Medals', 'Host_Status']].values
    y = data['Medal_Count'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = DecisionTreeRegressor(
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42
    )
    
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    feature_importance = pd.DataFrame({
        'Feature': ['Year', 'Athlete Count', 'Previous Medals', 'Host Status'],
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    return model, scaler, rmse, r2, feature_importance

def predict_future_medals(model, scaler, last_year, last_athlete_count, last_medals, noc, season, years_ahead=1):
    predictions = []
    current_year = last_year
    current_athlete_count = last_athlete_count
    current_medals = last_medals
    
    historical_medals = [last_medals]
    if len(historical_medals) > 0:
        avg_medals = np.mean(historical_medals)
    else:
        avg_medals = last_medals
    
    if current_year < 2020:
        next_year = 2020
        host_status = 1 if next_year in HOST_CITIES and HOST_CITIES[next_year][1] == noc else 0
        
        X_pred = scaler.transform([[
            next_year,
            current_athlete_count * 1.05,  
            current_medals,
            host_status
        ]])
        
        pred_medals = model.predict(X_pred)[0]
        
        if host_status == 1:
            if noc in ['USA', 'CHN', 'GBR', 'RUS']:  
                pred_medals = pred_medals * 1.25  
            else:
                pred_medals = pred_medals * 1.15  
        
        predictions.append({
            'Year': next_year,
            'Predicted_Medals': max(0, round(pred_medals)),
            'Predicted_Athletes': round(current_athlete_count * 1.05),
            'Host_Status': host_status
        })
        
        growth_rate = (pred_medals - last_medals) / last_medals if last_medals > 0 else 0
        
        for year in [2024, 2028]:
            host_status = 1 if year in HOST_CITIES and HOST_CITIES[year][1] == noc else 0
            base_pred = pred_medals * (1 + growth_rate)
            
            if host_status == 1:
                if noc in ['USA', 'CHN', 'GBR', 'RUS']:
                    base_pred = base_pred * 1.25
                else:
                    base_pred = base_pred * 1.15
            
            predictions.append({
                'Year': year,
                'Predicted_Medals': max(0, round(base_pred)),
                'Predicted_Athletes': round(current_athlete_count * (1.05 ** ((year - 2020) // 4 + 1))),
                'Host_Status': host_status
            })
    
    return pd.DataFrame(predictions)

def identify_breakout_sports(noc, season):
    if season == 'Summer':
        recent_years = sorted([y for y in df['Year'].unique() if y % 4 == 0])[-3:]
    else:  
        recent_years = sorted([y for y in df['Year'].unique() if y % 4 == 2])[-3:]
    
    recent_data = df[(df['NOC'] == noc) & (df['Year'].isin(recent_years)) & (df['Medal'] != 'None')]
    
    sport_medals = recent_data.groupby('Sport')['Medal'].count().reset_index()
    sport_medals.columns = ['Sport', 'Medal_Count']
    
    sport_growth = []
    for sport in sport_medals['Sport']:
        sport_data = recent_data[recent_data['Sport'] == sport]
        if len(sport_data) >= 2:
            first_year = sport_data['Year'].min()
            last_year = sport_data['Year'].max()
            first_medals = len(sport_data[sport_data['Year'] == first_year])
            last_medals = len(sport_data[sport_data['Year'] == last_year])
            growth_rate = ((last_medals - first_medals) / first_medals * 100) if first_medals > 0 else float('inf')
            sport_growth.append({
                'Sport': sport,
                'Growth_Rate': growth_rate,
                'Total_Medals': len(sport_data)
            })
    
    return pd.DataFrame(sport_growth)

def get_top_sports(noc, season, year):
    country_data = df[(df['NOC'] == noc) & (df['Year'] == year)].copy()
    
    if season == 'Summer':
        country_data = country_data[country_data['Year'] % 4 == 0]
    else:
        country_data = country_data[country_data['Year'] % 4 == 2]
    
    medal_data = country_data[country_data['Medal'] != 'None']
    
    sport_medals = medal_data.groupby('Sport')['Event'].nunique().reset_index()
    sport_medals.columns = ['Sport', 'Medal_Count']
    
    top_sports = sport_medals.nlargest(3, 'Medal_Count')['Sport'].tolist()
    
    while len(top_sports) < 3:
        top_sports.append('None')
    
    return top_sports

def prepare_lstm_data(noc, season, sequence_length=3):
    """Prepare data for LSTM model including top sports."""
    
    country_data = df[df['NOC'] == noc].copy()
    
    if season == 'Summer':
        country_data = country_data[country_data['Year'] % 4 == 0]
    else:
        country_data = country_data[country_data['Year'] % 4 == 2]
    
    years = sorted(country_data['Year'].unique())
    
    medal_counts = []
    for year in years:
        year_data = country_data[country_data['Year'] == year]
        medal_count = len(year_data[year_data['Medal'] != 'None'].groupby('Event').size())
        medal_counts.append(medal_count)
    
    weights = np.linspace(0.5, 1.5, len(medal_counts))  
    avg_medals = np.average(medal_counts, weights=weights) if medal_counts else 0
    std_medals = np.sqrt(np.average((medal_counts - avg_medals)**2, weights=weights)) if len(medal_counts) > 1 else 0
    max_medals = max(medal_counts) if medal_counts else 0
    min_medals = min(medal_counts) if medal_counts else 0
    
    X, y, sample_weights = [], [], []
    for i in range(len(years) - sequence_length):
        sequence = []
        for j in range(sequence_length):
            year = years[i + j]
            year_data = country_data[country_data['Year'] == year]
            
            medal_count = len(year_data[year_data['Medal'] != 'None'].groupby('Event').size())
            
            athlete_count = year_data['Name'].nunique()
            
            host_status = 1 if year in [year for year, (_, host_noc) in HOST_CITIES.items() if host_noc == noc] else 0
            
            top_sports = get_top_sports(noc, season, year)
            
            if j > 0:
                prev_year = years[i + j - 1]
                prev_year_data = country_data[country_data['Year'] == prev_year]
                prev_medal_count = len(prev_year_data[prev_year_data['Medal'] != 'None'].groupby('Event').size())
                momentum = medal_count - prev_medal_count
            else:
                momentum = 0
            
            if j >= 2:
                recent_counts = [len(country_data[country_data['Year'] == years[i + k]][country_data['Medal'] != 'None'].groupby('Event').size()) 
                               for k in range(j-2, j+1)]
                weights = [0.2, 0.3, 0.5]  
                trend = np.average(recent_counts, weights=weights)
            else:
                trend = medal_count
            
            performance_ratio = medal_count / avg_medals if avg_medals > 0 else 1
            
            features = [
                year,
                medal_count,
                athlete_count,
                host_status,
                momentum,
                trend,
                performance_ratio,
                avg_medals,
                std_medals,
                max_medals,
                min_medals
            ]
            
            for sport in ['Athletics', 'Swimming', 'Gymnastics']:  
                features.append(1 if sport in top_sports else 0)
            
            sequence.append(features)
        
        X.append(sequence)
        next_year = years[i + sequence_length]
        next_year_data = country_data[country_data['Year'] == next_year]
        next_year_medals = len(next_year_data[next_year_data['Medal'] != 'None'].groupby('Event').size())
        y.append(next_year_medals)
        
        weight = 1.0 + (i / len(years))  
        sample_weights.append(weight)
    
    return np.array(X), np.array(y), np.array(sample_weights)

def train_lstm_model(X, y, sample_weights):
    """Train LSTM model for medal prediction."""
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
    
    y_scaler = MinMaxScaler()
    y_scaled = y_scaler.fit_transform(y.reshape(-1, 1))
    
    train_size = int(len(X) * 0.8)
    X_train, X_test = X_scaled[:train_size], X_scaled[train_size:]
    y_train, y_test = y_scaled[:train_size], y_scaled[train_size:]
    weights_train = sample_weights[:train_size]
    
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(X.shape[1], X.shape[2])),
        Dropout(0.2),
        LSTM(32, return_sequences=True),
        Dropout(0.2),
        LSTM(16),
        Dropout(0.2),
        Dense(8, activation='relu'),
        Dense(1, activation='linear')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )
    
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=20,
        restore_best_weights=True
    )
    
    history = model.fit(
        X_train, y_train,
        sample_weight=weights_train,
        epochs=200,
        batch_size=32,
        validation_split=0.1,
        callbacks=[early_stopping],
        verbose=0
    )
    
    y_pred_scaled = model.predict(X_test)
    y_pred = y_scaler.inverse_transform(y_pred_scaled)
    y_test_original = y_scaler.inverse_transform(y_test)
    
    rmse = np.sqrt(mean_squared_error(y_test_original, y_pred))
    r2 = r2_score(y_test_original, y_pred)
    
    return model, (scaler, y_scaler), rmse, r2, history

def predict_future_medals_lstm(model, scalers, last_sequence, noc, years_ahead=1):
    """Make predictions using LSTM model."""
    predictions = []
    current_sequence = last_sequence.copy()
    scaler, y_scaler = scalers
    
    last_known_medals = current_sequence[-1][1]  
    last_known_year = current_sequence[-1][0]
    
    if last_known_year < 2020:
        scaled_sequence = scaler.transform(current_sequence.reshape(-1, current_sequence.shape[-1])).reshape(current_sequence.shape)
        pred_scaled = model.predict(scaled_sequence[np.newaxis, ...])[0][0]
        pred_2020 = y_scaler.inverse_transform([[pred_scaled]])[0][0]
        
        is_host_2020 = 1 if 2020 in HOST_CITIES and HOST_CITIES[2020][1] == noc else 0
        if is_host_2020:
            if noc in ['USA', 'CHN', 'GBR', 'RUS']:
                pred_2020 = pred_2020 * 1.25
            else:
                pred_2020 = pred_2020 * 1.15
        
        predictions.append(max(0, round(pred_2020)))
        
        last_3_years_medals = [seq[1] for seq in current_sequence[-3:]]
        avg_last_3 = np.mean(last_3_years_medals)
        max_last_3 = max(last_3_years_medals)
        min_last_3 = min(last_3_years_medals)
        
        performance_range = max_last_3 - min_last_3
        
        for year in [2024, 2028]:
            is_host = 1 if year in HOST_CITIES and HOST_CITIES[year][1] == noc else 0
            
            recent_trend = (last_3_years_medals[-1] - last_3_years_medals[0]) / len(last_3_years_medals)
            trend_weight = min(max(0.5 + recent_trend / performance_range, 0.3), 0.7)
            
            base_pred = (trend_weight * max_last_3) + ((1 - trend_weight) * avg_last_3)
            
            if is_host:
                if noc in ['USA', 'CHN', 'GBR', 'RUS']:
                    base_pred = base_pred * 1.25
                else:
                    base_pred = base_pred * 1.15
            
            base_pred = max(min(base_pred, max_last_3 * 1.2), min_last_3 * 0.8)
            
            predictions.append(max(0, round(base_pred)))
    
    return predictions


layout = dbc.Container([
   
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Olympic Performance Prediction", className="display-4 text-primary mb-4"),
                html.P("Predict future Olympic performance using machine learning and historical data analysis.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.P("Use our advanced prediction models to forecast medal counts and identify potential breakout sports for selected countries.", 
                  className="lead text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select Model:", className="fw-bold"),
            dcc.RadioItems(
                id='prediction-model-radio',
                options=[
                    {'label': 'Decision Tree', 'value': 'decision_tree'},
                    {'label': 'LSTM', 'value': 'lstm'}
                ],
                value='decision_tree',
                inline=True,
                className="mt-2"
            )
        ], width=12, md=6, lg=4),
        dbc.Col([
            html.Label("Select Country:", className="fw-bold"),
            dcc.Dropdown(
                id='prediction-country-dropdown',
                options=NOC_OPTIONS_NO_ALL,
                value=get_default_value(NOC_OPTIONS_NO_ALL),
                clearable=False,
            )
        ], width=12, md=6, lg=4),
        dbc.Col([
            html.Label("Select Season:", className="fw-bold"),
            dcc.RadioItems(
                id='prediction-season-radio',
                options=[
                    {'label': 'Summer Olympics', 'value': 'Summer'},
                    {'label': 'Winter Olympics', 'value': 'Winter'}
                ],
                value='Summer',
                inline=True,
                className="mt-2"
            )
        ], width=12, md=6, lg=4)
    ]),
    html.Hr(),
    
    dbc.Spinner(
        html.Div(id='prediction-results')
    )
])


@callback(
    Output('prediction-results', 'children'),
    [Input('prediction-country-dropdown', 'value'),
     Input('prediction-season-radio', 'value'),
     Input('prediction-model-radio', 'value')]
)
def update_predictions(selected_noc, selected_season, selected_model):
    if not selected_noc:
        return html.P("Please select a country.")
    
    prediction_data = prepare_prediction_data(selected_noc, selected_season)
    if len(prediction_data) < 3:
        return html.P(f"Not enough historical data for {selected_noc} in {selected_season} Olympics to make predictions.")
    
    if selected_model == 'decision_tree':
        all_predictions = []
        current_data = prediction_data.copy()
        
        model, scaler, rmse, r2, feature_importance = train_prediction_model(current_data)
        
        last_year = current_data['Year'].max()
        last_athlete_count = current_data['Athlete_Count'].iloc[-1]
        last_medals = current_data['Medal_Count'].iloc[-1]
        
        future_predictions = predict_future_medals(
            model=model,
            scaler=scaler,
            last_year=last_year,
            last_athlete_count=last_athlete_count,
            last_medals=last_medals,
            noc=selected_noc,
            season=selected_season
        )
        
        historical_fig = go.Figure()
        historical_fig.add_trace(go.Scatter(
            x=prediction_data['Year'],
            y=prediction_data['Medal_Count'],
            mode='lines+markers',
            name='Historical Medals',
            line=dict(color='royalblue')
        ))
        historical_fig.add_trace(go.Scatter(
            x=future_predictions['Year'],
            y=future_predictions['Predicted_Medals'],
            mode='lines+markers',
            name='Predicted Medals',
            line=dict(color='red', dash='dash')
        ))
        historical_fig.update_layout(
            title=f"Historical and Predicted Medal Count for {selected_noc} in {selected_season} Olympics",
            xaxis_title='Year',
            yaxis_title='Number of Medals',
            showlegend=True
        )
        
        importance_fig = px.bar(
            feature_importance,
            x='Feature',
            y='Importance',
            title='Feature Importance in Decision Tree Model',
            color='Importance',
            color_continuous_scale='Viridis'
        )
        importance_fig.update_layout(xaxis_title='Feature', yaxis_title='Importance Score')
        
        model_summary = [
            html.H5("Decision Tree Model Performance:"),
            html.P(f"RMSE: {rmse:.2f}"),
            html.P(f"R² Score: {r2:.2f}")
        ]
        
    else:  # LSTM model
        all_predictions = []
        current_sequence = prepare_lstm_data(selected_noc, selected_season)[0][-1]
        
        X, y, sample_weights = prepare_lstm_data(selected_noc, selected_season)
        model, scalers, rmse, r2, history = train_lstm_model(X, y, sample_weights)
        
        next_prediction = predict_future_medals_lstm(model, scalers, current_sequence, selected_noc)
        
        historical_fig = go.Figure()
        historical_fig.add_trace(go.Scatter(
            x=prediction_data['Year'],
            y=prediction_data['Medal_Count'],
            mode='lines+markers',
            name='Historical Medals',
            line=dict(color='royalblue')
        ))
        historical_fig.add_trace(go.Scatter(
            x=[2020, 2024, 2028],
            y=next_prediction,
            mode='lines+markers',
            name='Predicted Medals',
            line=dict(color='red', dash='dash')
        ))
        historical_fig.update_layout(
            title=f"Historical and Predicted Medal Count for {selected_noc} in {selected_season} Olympics",
            xaxis_title='Year',
            yaxis_title='Number of Medals',
            showlegend=True
        )
        
        importance_fig = go.Figure()
        importance_fig.add_trace(go.Scatter(
            y=history.history['loss'],
            name='Training Loss',
            mode='lines'
        ))
        importance_fig.add_trace(go.Scatter(
            y=history.history['val_loss'],
            name='Validation Loss',
            mode='lines'
        ))
        importance_fig.update_layout(
            title='LSTM Model Training History',
            xaxis_title='Epoch',
            yaxis_title='Loss',
            showlegend=True
        )
        
        model_summary = [
            html.H5("LSTM Model Performance:"),
            html.P(f"RMSE: {rmse:.2f}"),
            html.P(f"R² Score: {r2:.2f}")
        ]
    
    breakout_sports = identify_breakout_sports(selected_noc, selected_season)
    
    if not breakout_sports.empty:
        breakout_sports = breakout_sports.sort_values('Growth_Rate', ascending=False).head(5)
        breakout_fig = px.bar(
            breakout_sports,
            x='Sport',
            y='Growth_Rate',
            title=f"Top 5 Breakout Sports for {selected_noc} in {selected_season} Olympics",
            labels={'Growth_Rate': 'Growth Rate (%)', 'Sport': 'Sport'},
            color='Total_Medals',
            color_continuous_scale='Viridis'
        )
        breakout_fig.update_layout(xaxis_title='Sport', yaxis_title='Growth Rate (%)')
    else:
        breakout_fig = go.Figure().update_layout(
            title=f"No breakout sports data available for {selected_noc} in {selected_season} Olympics"
        )
    
    summary_cards = [
        dbc.Card([
            dbc.CardHeader(f"{selected_season} Olympics Prediction Summary"),
            dbc.CardBody([
                html.P(f"Based on historical data from {prediction_data['Year'].min()} to {prediction_data['Year'].max()}"),
                html.P(f"Last known medal count: {prediction_data['Medal_Count'].iloc[-1]}"),
                html.P(f"Last known athlete count: {prediction_data['Athlete_Count'].iloc[-1]}"),
                html.Hr(),
                *model_summary,
                html.Hr(),
                html.H5("Predicted Medal Counts:"),
                *[html.P(f"{prediction_data['Year'].max() + 4 * (i+1)}: {medals} medals") 
                  for i, medals in enumerate(future_predictions['Predicted_Medals'] if selected_model == 'decision_tree' else next_prediction)]
            ])
        ], className="performance-card animate-slide mb-3"),
        
        dbc.Card([
            dbc.CardHeader(f"{selected_season} Olympics Breakout Sports Analysis"),
            dbc.CardBody([
                html.P("Top 5 sports showing the highest growth in medal count:"),
                *[html.P(f"{row['Sport']}: {row['Growth_Rate']:.1f}% growth ({row['Total_Medals']} total medals)") 
                  for _, row in breakout_sports.iterrows()]
            ])
        ], className="analysis-card animate-slide mb-3")
    ]
    
    return dbc.Row([
        dbc.Col([
            html.H4(f"{selected_season} Olympics Medal Predictions", className="mb-3"),
            dcc.Graph(figure=historical_fig, className="chart-card animate-slide"),
            html.H4("Model Analysis", className="mb-3"),
            dcc.Graph(figure=importance_fig, className="chart-card animate-slide"),
            html.H4(f"{selected_season} Olympics Breakout Sports", className="mb-3"),
            dcc.Graph(figure=breakout_fig, className="chart-card animate-slide")
        ], width=12, lg=8),
        dbc.Col([
            html.H4(f"{selected_season} Olympics Analysis Summary", className="mb-3"),
            *summary_cards
        ], width=12, lg=4)
    ])