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

def get_medal_counts():
    total_athletes = df.groupby('NOC').size().reset_index(name='total_athletes')
    
    medals_df = df[df['Medal'] != 'None'].copy()
    
    unique_event_medals = medals_df.drop_duplicates(
        subset=['Year', 'Season', 'Event', 'Medal', 'NOC']
    )
    
    medal_summary = unique_event_medals.groupby('NOC').apply(
        lambda x: f"Gold: {sum(x['Medal'] == 'Gold')}<br>"
                 f"Silver: {sum(x['Medal'] == 'Silver')}<br>"
                 f"Bronze: {sum(x['Medal'] == 'Bronze')}<br>"
                 f"Total Medals: {len(x)}"
    ).reset_index(name='Medal')
    
    medal_points = unique_event_medals.groupby('NOC').apply(
        lambda x: sum(x['Medal'].map({'Gold': 4, 'Silver': 2, 'Bronze': 1}))
    ).reset_index(name='total_points')
    
    medal_data = medal_summary.merge(medal_points, on='NOC', how='left')
    
    medal_data = medal_data.merge(total_athletes, on='NOC', how='right')
    medal_data['total_points'] = medal_data['total_points'].fillna(0)
    medal_data['total_athletes'] = medal_data['total_athletes'].fillna(0)
    
    medal_data['efficiency'] = medal_data['total_points'] / medal_data['total_athletes']
    medal_data['efficiency'] = medal_data['efficiency'].fillna(0)
    
    return medal_data

# Create the layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Global Olympic Analysis", className="display-4 text-primary mb-4"),
                html.P("Explore Olympic performance across the globe with our interactive 3D visualization.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

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

@callback(
    [Output('clicked-country', 'data'),
     Output('url', 'pathname')],
    Input('medal-globe', 'clickData')
)
def update_clicked_country(clickData):
    if clickData is None:
        raise PreventUpdate
    country = clickData['points'][0]['location']
    print(f"Selected country: {country}")  
    return country, '/country-profile'