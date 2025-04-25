# pages/globe.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from data_loader import df
import numpy as np
from dash.exceptions import PreventUpdate
from dash import dcc, html, callback, Input, Output, State, MATCH, ALL
from dash.dependencies import ClientsideFunction

dash.register_page(__name__, name='Globe View')

# Preprocess the medal data
def get_medal_counts():
    # Calculate total athletes per country
    total_athletes = df.groupby('NOC').size().reset_index(name='total_athletes')
    
    # Calculate medal points
    medal_points = df[df['Medal'] != 'None'].groupby('NOC').agg({
        'Medal': lambda x: (
            f"Gold: {sum(x == 'Gold')}<br>"
            f"Silver: {sum(x == 'Silver')}<br>"
            f"Bronze: {sum(x == 'Bronze')}<br>"
            f"Total Points: {sum(x == 'Gold') * 4 + sum(x == 'Silver') * 2 + sum(x == 'Bronze')}"
        )
    }).reset_index()
    
    # Calculate total points
    medal_points['total_points'] = df[df['Medal'] != 'None'].apply(
        lambda x: 4 if x['Medal'] == 'Gold' else (2 if x['Medal'] == 'Silver' else 1), axis=1
    ).groupby(df['NOC']).sum().values
    
    # Merge with total athletes
    medal_points = medal_points.merge(total_athletes, on='NOC', how='right')
    medal_points['total_points'] = medal_points['total_points'].fillna(0)
    medal_points['total_athletes'] = medal_points['total_athletes'].fillna(0)
    
    # Calculate efficiency
    medal_points['efficiency'] = medal_points['total_points'] / medal_points['total_athletes']
    medal_points['efficiency'] = medal_points['efficiency'].fillna(0)
    
    return medal_points

# Create the layout
layout = dbc.Container([
    # --- Hero Section ---
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Global Olympic Analysis", className="display-4 text-primary mb-4"),
                html.P("Explore Olympic performance across the globe with our interactive 3D visualization.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

    # --- Description ---
    dbc.Row([
        dbc.Col([
            html.P("Interact with the 3D globe to explore Olympic medal efficiency across countries. Click on a country to view its detailed profile.", 
                  className="lead text-muted mb-2"),
            html.P("Medal Efficiency = Total Points / Total Athletes (Gold=4, Silver=2, Bronze=1)", 
                  className="text-muted small mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='medal-globe',
                style={'height': '80vh'},  # Make the globe take up most of the viewport height
                config={'displayModeBar': True}
            ),
            # Hidden div to store the clicked country
            dcc.Store(id='clicked-country', data=None, storage_type='session'),
            # Hidden div for navigation
            dcc.Location(id='url', refresh=True)
        ])
    ])
])

@callback(
    Output('medal-globe', 'figure'),
    Input('medal-globe', 'id')  # Dummy input to initialize the callback
)
def update_globe(_):
    medal_data = get_medal_counts()
    
    # Create the choropleth trace
    fig = go.Figure(data=go.Choropleth(
        locations=medal_data['NOC'],
        z=medal_data['efficiency'],
        text=medal_data['Medal'],
        locationmode='ISO-3',
        colorscale='Viridis',
        colorbar_title="Medal Efficiency",
        hovertemplate="<b>%{location}</b><br><br>" +
                      "%{text}<br>" +
                      "Total Athletes: %{customdata[0]}<br>" +
                      "Efficiency Score: %{z:.3f}<br>" +
                      "<i>Click to view country profile</i><extra></extra>",
        customdata=medal_data[['total_athletes']].values
    ))

    # Update the layout to show a 3D globe
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='orthographic',
            landcolor='rgb(243, 243, 243)',
            oceancolor='rgb(204, 229, 255)',
            showocean=True,
            showcountries=True,
            countrycolor='rgb(204, 204, 204)',
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=800
    )

    # Add buttons for rotation
    fig.update_layout(
        updatemenus=[{
            'buttons': [
                {
                    'args': [{'geo.projection.rotation.lon': -100}],
                    'label': 'Americas',
                    'method': 'relayout'
                },
                {
                    'args': [{'geo.projection.rotation.lon': 20}],
                    'label': 'Europe/Africa',
                    'method': 'relayout'
                },
                {
                    'args': [{'geo.projection.rotation.lon': 100}],
                    'label': 'Asia/Pacific',
                    'method': 'relayout'
                }
            ],
            'direction': 'down',
            'showactive': True,
            'x': 0.1,
            'y': 0.9
        }]
    )

    return fig

# Callback to handle clicks and update the clicked country
@callback(
    [Output('clicked-country', 'data'),
     Output('url', 'pathname')],
    Input('medal-globe', 'clickData')
)
def update_clicked_country(clickData):
    if clickData is None:
        raise PreventUpdate
    country = clickData['points'][0]['location']
    print(f"Selected country: {country}")  # Debug print
    return country, '/country-profile'