# pages/prediction.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value

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
    2020: ('Tokyo', 'JPN')
}

# Function to prepare data for prediction
def prepare_prediction_data(noc, season):
    # Get historical data for the country
    country_data = df[df['NOC'] == noc].copy()
    
    # Filter by season
    if season == 'Summer':
        country_data = country_data[country_data['Year'] % 4 == 0]  # Summer Olympics are in years divisible by 4
    else:  # Winter
        country_data = country_data[country_data['Year'] % 4 == 2]  # Winter Olympics are in years divisible by 2 but not 4
    
    # Calculate yearly medal counts
    yearly_medals = country_data[country_data['Medal'] != 'None'].groupby(['Year', 'Event', 'Medal']).size().reset_index()
    yearly_medals = yearly_medals.groupby('Year')['Medal'].count().reset_index()
    yearly_medals.columns = ['Year', 'Medal_Count']
    
    # Calculate yearly athlete counts
    yearly_athletes = country_data.groupby('Year')['Name'].nunique().reset_index()
    yearly_athletes.columns = ['Year', 'Athlete_Count']
    
    # Calculate previous games performance
    yearly_medals['Previous_Medals'] = yearly_medals['Medal_Count'].shift(1)
    yearly_medals['Previous_Medals'] = yearly_medals['Previous_Medals'].fillna(0)
    
    # Calculate host status
    yearly_medals['Host_Status'] = yearly_medals['Year'].apply(
        lambda x: 1 if x in [year for year, (_, host_noc) in HOST_CITIES.items() if host_noc == noc] else 0
    )
    
    # Merge all features
    prediction_data = pd.merge(yearly_medals, yearly_athletes, on='Year', how='outer')
    prediction_data = prediction_data.fillna(0)
    
    return prediction_data

# Function to train Decision Tree model
def train_prediction_model(data):
    # Prepare features
    X = data[['Year', 'Athlete_Count', 'Previous_Medals', 'Host_Status']].values
    y = data['Medal_Count'].values
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Decision Tree model
    model = DecisionTreeRegressor(
        max_depth=10,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42
    )
    
    # Fit model
    model.fit(X_train_scaled, y_train)
    
    # Calculate model performance
    y_pred = model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    # Get feature importance
    feature_importance = pd.DataFrame({
        'Feature': ['Year', 'Athlete Count', 'Previous Medals', 'Host Status'],
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    return model, scaler, rmse, r2, feature_importance

# Function to predict future medals
def predict_future_medals(model, scaler, last_year, last_athlete_count, last_medals, season, years_ahead=3):
    predictions = []
    current_year = last_year
    current_athlete_count = last_athlete_count
    current_medals = last_medals
    
    for _ in range(years_ahead):
        if season == 'Summer':
            current_year += 4
        else:  # Winter
            current_year += 4
        
        # Predict athlete count (simple linear projection)
        current_athlete_count = current_athlete_count * 1.05  # 5% growth assumption
        
        # Prepare features
        X_pred = scaler.transform([[
            current_year,
            current_athlete_count,
            current_medals,
            0  # Not hosting
        ]])
        
        # Make prediction
        pred_medals = model.predict(X_pred)[0]
        predictions.append({
            'Year': current_year,
            'Predicted_Medals': max(0, round(pred_medals)),
            'Predicted_Athletes': round(current_athlete_count)
        })
        
        # Update for next iteration
        current_medals = pred_medals
    
    return pd.DataFrame(predictions)

# Function to identify breakout sports
def identify_breakout_sports(noc, season):
    # Get recent data (last 3 Olympics)
    if season == 'Summer':
        recent_years = sorted([y for y in df['Year'].unique() if y % 4 == 0])[-3:]
    else:  # Winter
        recent_years = sorted([y for y in df['Year'].unique() if y % 4 == 2])[-3:]
    
    recent_data = df[(df['NOC'] == noc) & (df['Year'].isin(recent_years)) & (df['Medal'] != 'None')]
    
    # Calculate medal counts by sport
    sport_medals = recent_data.groupby('Sport')['Medal'].count().reset_index()
    sport_medals.columns = ['Sport', 'Medal_Count']
    
    # Calculate growth rate
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

# Function to test medal counting
def test_medal_counting(noc='USA', season='Summer'):
    # Get historical data for the country
    country_data = df[df['NOC'] == noc].copy()
    
    # Filter by season
    if season == 'Summer':
        country_data = country_data[country_data['Year'] % 4 == 0]  # Summer Olympics are in years divisible by 4
    else:  # Winter
        country_data = country_data[country_data['Year'] % 4 == 2]  # Winter Olympics are in years divisible by 2 but not 4
    
    # Calculate yearly medal counts
    yearly_medals = country_data[country_data['Medal'] != 'None'].groupby(['Year', 'Event', 'Medal']).size().reset_index()
    print("\nMedals by Year, Event, and Medal Type:")
    print(yearly_medals)
    
    yearly_medals = yearly_medals.groupby('Year')['Medal'].count().reset_index()
    yearly_medals.columns = ['Year', 'Medal_Count']
    print("\nTotal Medals by Year:")
    print(yearly_medals)

# Create the layout
layout = dbc.Container([
    # --- Hero Section ---
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Olympic Performance Prediction", className="display-4 text-primary mb-4"),
                html.P("Predict future Olympic performance using machine learning and historical data analysis.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

    # --- Description ---
    dbc.Row([
        dbc.Col([
            html.P("Use our advanced prediction models to forecast medal counts and identify potential breakout sports for selected countries.", 
                  className="lead text-muted mb-4")
        ], width=12)
    ]),
    
    # Country and Season Selection
    dbc.Row([
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
    
    # Prediction Results
    dbc.Spinner(
        html.Div(id='prediction-results')
    )
])

# Callback to update predictions
@callback(
    Output('prediction-results', 'children'),
    [Input('prediction-country-dropdown', 'value'),
     Input('prediction-season-radio', 'value')]
)
def update_predictions(selected_noc, selected_season):
    if not selected_noc:
        return html.P("Please select a country.")
    
    # Prepare data
    prediction_data = prepare_prediction_data(selected_noc, selected_season)
    if len(prediction_data) < 3:
        return html.P(f"Not enough historical data for {selected_noc} in {selected_season} Olympics to make predictions.")
    
    # Train model
    model, scaler, rmse, r2, feature_importance = train_prediction_model(prediction_data)
    
    # Make predictions
    last_year = prediction_data['Year'].max()
    last_athlete_count = prediction_data['Athlete_Count'].iloc[-1]
    last_medals = prediction_data['Medal_Count'].iloc[-1]
    future_predictions = predict_future_medals(model, scaler, last_year, last_athlete_count, last_medals, selected_season)
    
    # Identify breakout sports
    breakout_sports = identify_breakout_sports(selected_noc, selected_season)
    
    # Create visualizations
    # 1. Historical and Predicted Medals
    historical_fig = go.Figure()
    
    # Add historical data
    historical_fig.add_trace(go.Scatter(
        x=prediction_data['Year'],
        y=prediction_data['Medal_Count'],
        mode='lines+markers',
        name='Historical Medals',
        line=dict(color='royalblue')
    ))
    
    # Add predictions
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
    
    # 2. Feature Importance
    importance_fig = px.bar(
        feature_importance,
        x='Feature',
        y='Importance',
        title='Feature Importance in Decision Tree Model',
        color='Importance',
        color_continuous_scale='Viridis'
    )
    importance_fig.update_layout(xaxis_title='Feature', yaxis_title='Importance Score')
    
    # 3. Breakout Sports
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
    
    # Create summary cards
    summary_cards = [
        dbc.Card([
            dbc.CardHeader(f"{selected_season} Olympics Prediction Summary"),
            dbc.CardBody([
                html.P(f"Based on historical data from {prediction_data['Year'].min()} to {last_year}"),
                html.P(f"Last known medal count: {prediction_data['Medal_Count'].iloc[-1]}"),
                html.P(f"Last known athlete count: {last_athlete_count}"),
                html.Hr(),
                html.H5("Decision Tree Model Performance:"),
                html.P(f"RMSE: {rmse:.2f}"),
                html.P(f"R² Score: {r2:.2f}"),
                html.Hr(),
                html.H5("Predicted Medal Counts:"),
                *[html.P(f"{row['Year']}: {row['Predicted_Medals']} medals") 
                  for _, row in future_predictions.iterrows()]
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
            html.H4("Feature Importance", className="mb-3"),
            dcc.Graph(figure=importance_fig, className="chart-card animate-slide"),
            html.H4(f"{selected_season} Olympics Breakout Sports", className="mb-3"),
            dcc.Graph(figure=breakout_fig, className="chart-card animate-slide")
        ], width=12, lg=8),
        dbc.Col([
            html.H4(f"{selected_season} Olympics Analysis Summary", className="mb-3"),
            *summary_cards
        ], width=12, lg=4)
    ])

# Add this at the end of the file to run the test
if __name__ == "__main__":
    test_medal_counting()