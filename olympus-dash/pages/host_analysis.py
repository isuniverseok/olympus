# pages/host_analysis.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value

dash.register_page(__name__, name='Host Analysis')

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

# Function to get host country data
def get_host_data():
    host_data = []
    for year, (city, noc) in HOST_CITIES.items():
        # Get host year data
        host_year = df[df['Year'] == year]
        
        # Calculate unique medals using the same logic as in olympic_year.py
        # Handle host year medals
        host_year_medals = host_year[host_year['NOC'] == noc]
        host_medals_df = host_year_medals[host_year_medals['Medal'] != 'None'].copy()
        if not host_medals_df.empty:
            # Deduplicate medals by event (handles team events correctly)
            unique_host_medals = host_medals_df.drop_duplicates(
                subset=['Year', 'Season', 'Event', 'Medal']
            )
            host_medals = unique_host_medals['Medal'].value_counts()
        else:
            host_medals = pd.Series(0, index=['Gold', 'Silver', 'Bronze'])
        
        host_athletes = len(host_year[host_year['NOC'] == noc]['Name'].unique())
        
        # Get previous games data (if available)
        prev_year = year - 4 if year > 1896 else None
        prev_medals = None
        prev_athletes = None
        if prev_year:
            prev_year_data = df[df['Year'] == prev_year]
            
            # Previous medals with same deduplication logic
            prev_year_medals = prev_year_data[prev_year_data['NOC'] == noc]
            prev_medals_df = prev_year_medals[prev_year_data['Medal'] != 'None'].copy()
            if not prev_medals_df.empty:
                unique_prev_medals = prev_medals_df.drop_duplicates(
                    subset=['Year', 'Season', 'Event', 'Medal']
                )
                prev_medals = unique_prev_medals['Medal'].value_counts()
            else:
                prev_medals = pd.Series(0, index=['Gold', 'Silver', 'Bronze'])
                
            prev_athletes = len(prev_year_data[prev_year_data['NOC'] == noc]['Name'].unique())
        
        # Get next games data (if available)
        next_year = year + 4 if year < 2020 else None
        next_medals = None
        next_athletes = None
        if next_year:
            next_year_data = df[df['Year'] == next_year]
            
            # Next medals with same deduplication logic
            next_year_medals = next_year_data[next_year_data['NOC'] == noc]
            next_medals_df = next_year_medals[next_year_data['Medal'] != 'None'].copy()
            if not next_medals_df.empty:
                unique_next_medals = next_medals_df.drop_duplicates(
                    subset=['Year', 'Season', 'Event', 'Medal']
                )
                next_medals = unique_next_medals['Medal'].value_counts()
            else:
                next_medals = pd.Series(0, index=['Gold', 'Silver', 'Bronze'])
                
            next_athletes = len(next_year_data[next_year_data['NOC'] == noc]['Name'].unique())
        
        host_data.append({
            'Year': year,
            'City': city,
            'NOC': noc,
            'Host_Medals': host_medals.to_dict() if isinstance(host_medals, pd.Series) and not host_medals.empty else {'Gold': 0, 'Silver': 0, 'Bronze': 0},
            'Host_Athletes': host_athletes,
            'Prev_Medals': prev_medals.to_dict() if prev_medals is not None and isinstance(prev_medals, pd.Series) and not prev_medals.empty else {'Gold': 0, 'Silver': 0, 'Bronze': 0},
            'Prev_Athletes': prev_athletes,
            'Next_Medals': next_medals.to_dict() if next_medals is not None and isinstance(next_medals, pd.Series) and not next_medals.empty else {'Gold': 0, 'Silver': 0, 'Bronze': 0},
            'Next_Athletes': next_athletes
        })
    
    return pd.DataFrame(host_data)

# Create the layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Host Country Analysis", className="display-4 text-primary mb-4"),
                html.P("Explore the impact of hosting the Olympic Games on a country's performance and participation.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            html.P("This section analyzes the 'Home Field Advantage' by comparing host nations' performance during hosting years versus previous and subsequent games.", 
                  className="lead text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            html.Label("Select Host Country:", className="fw-bold"),
            dcc.Dropdown(
                id='host-country-dropdown',
                options=[{'label': f"{city} ({year}) - {noc}", 'value': noc} 
                        for year, (city, noc) in HOST_CITIES.items()],
                value='USA',  # Default to USA
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ]),
    html.Hr(),
    
    dbc.Spinner(
        html.Div(id='host-analysis-visuals')
    )
])

# Callback to update visualizations
@callback(
    Output('host-analysis-visuals', 'children'),
    Input('host-country-dropdown', 'value')
)
def update_host_analysis(selected_noc):
    if not selected_noc:
        return dbc.Alert("Please select a host country.", color="info", className="m-3")
    
    try:
        # Get host years for selected country
        host_years = [year for year, (_, noc) in HOST_CITIES.items() if noc == selected_noc]
        if not host_years:
            return dbc.Alert(f"No hosting data found for {selected_noc}.", color="warning", className="m-3")
        
        # Get host data
        host_data = get_host_data()
        if host_data.empty:
            return dbc.Alert("No data available for analysis.", color="warning", className="m-3")
        
        # Create visualizations for each host year
        visualizations = []
        summary_cards = []
        
        for year in host_years:
            city = HOST_CITIES[year][0]
            
            # Get data for this host year
            year_data = host_data[host_data['Year'] == year]
            if year_data.empty:
                continue
                
            year_data = year_data.iloc[0]
            
            # Create medal comparison figure
            medal_fig = go.Figure()
            
            # Calculate relevant years for hover text
            host_display_year = year
            prev_display_year = year - 4 if year > 1896 else None
            next_display_year = year + 4 if year < 2020 else None
            
            # Add previous games data first
            if prev_display_year:
                medal_fig.add_trace(go.Bar(
                    name='Previous Games',
                    x=['Gold', 'Silver', 'Bronze'],
                    y=[year_data['Prev_Medals'].get('Gold', 0),
                       year_data['Prev_Medals'].get('Silver', 0),
                       year_data['Prev_Medals'].get('Bronze', 0)],
                    marker_color=['gold', 'silver', '#cd7f32'],
                    opacity=0.7,
                    marker_pattern_shape="/",
                    customdata=[prev_display_year] * 3,
                    hovertemplate=f"<b>Previous Games ({prev_display_year})</b><br>" +
                                  "Medal: %{x}<br>" +
                                  "Count: %{y}<extra></extra>"
                ))
            
            # Add host year data second (solid)
            medal_fig.add_trace(go.Bar(
                name='Host Year',
                x=['Gold', 'Silver', 'Bronze'],
                y=[year_data['Host_Medals'].get('Gold', 0),
                   year_data['Host_Medals'].get('Silver', 0),
                   year_data['Host_Medals'].get('Bronze', 0)],
                marker_color=['gold', 'silver', '#cd7f32'],
                customdata=[host_display_year] * 3,
                hovertemplate=f"<b>Host Year ({host_display_year})</b><br>" +
                              "Medal: %{x}<br>" +
                              "Count: %{y}<extra></extra>"
            ))

            # Add next games data third
            if next_display_year:
                medal_fig.add_trace(go.Bar(
                    name='Next Games',
                    x=['Gold', 'Silver', 'Bronze'],
                    y=[year_data['Next_Medals'].get('Gold', 0),
                       year_data['Next_Medals'].get('Silver', 0),
                       year_data['Next_Medals'].get('Bronze', 0)],
                    marker_color=['gold', 'silver', '#cd7f32'],
                    opacity=0.7,
                    marker_pattern_shape=".",
                    customdata=[next_display_year] * 3,
                    hovertemplate=f"<b>Next Games ({next_display_year})</b><br>" +
                                  "Medal: %{x}<br>" +
                                  "Count: %{y}<extra></extra>"
                ))
            
            medal_fig.update_layout(
                title=f"Medal Comparison for {selected_noc} at {city} {year}",
                barmode='group',
                xaxis_title='Medal Type',
                yaxis_title='Number of Medals',
                showlegend=True,
                template="plotly_white"
            )
            
            # Create athlete participation figure
            athlete_fig = go.Figure()
            
            # Add previous games data first
            if prev_display_year:
                athlete_fig.add_trace(go.Bar(
                    name='Previous Games',
                    x=['Athletes'],
                    y=[year_data['Prev_Athletes']],
                    marker_color='royalblue',
                    opacity=0.7,
                    marker_pattern_shape="/",
                    customdata=[prev_display_year],
                    hovertemplate=f"<b>Previous Games ({prev_display_year})</b><br>" +
                                  "Athletes: %{y}<extra></extra>"
                ))
            
            # Add host year data second (solid)
            athlete_fig.add_trace(go.Bar(
                name='Host Year',
                x=['Athletes'],
                y=[year_data['Host_Athletes']],
                marker_color='royalblue',
                customdata=[host_display_year],
                hovertemplate=f"<b>Host Year ({host_display_year})</b><br>" +
                              "Athletes: %{y}<extra></extra>"
            ))
            
            # Add next games data third
            if next_display_year:
                athlete_fig.add_trace(go.Bar(
                    name='Next Games',
                    x=['Athletes'],
                    y=[year_data['Next_Athletes']],
                    marker_color='royalblue',
                    opacity=0.7,
                    marker_pattern_shape=".",
                    customdata=[next_display_year],
                    hovertemplate=f"<b>Next Games ({next_display_year})</b><br>" +
                                  "Athletes: %{y}<extra></extra>"
                ))
            
            athlete_fig.update_layout(
                title=f"Athlete Participation for {selected_noc} at {city} {year}",
                barmode='group',
                xaxis_title='',
                yaxis_title='Number of Athletes',
                showlegend=True,
                xaxis_showticklabels=False,
                template="plotly_white"
            )
            
            visualizations.extend([
                dbc.Col(dcc.Graph(figure=medal_fig), width=12, className="mb-4"),
                dbc.Col(dcc.Graph(figure=athlete_fig), width=12, className="mb-4")
            ])
            
            # Calculate statistics for summary card
            host_total = sum(year_data['Host_Medals'].values())
            prev_total = sum(year_data['Prev_Medals'].values())
            next_total = sum(year_data['Next_Medals'].values())
            
            # Calculate improvements
            prev_improvement = ((host_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
            next_improvement = ((host_total - next_total) / next_total * 100) if next_total > 0 else 0
            
            # Calculate athlete changes
            prev_athlete_change = ((year_data['Host_Athletes'] - year_data['Prev_Athletes']) / year_data['Prev_Athletes'] * 100) if year_data['Prev_Athletes'] and year_data['Prev_Athletes'] > 0 else 0
            next_athlete_change = ((year_data['Host_Athletes'] - year_data['Next_Athletes']) / year_data['Next_Athletes'] * 100) if year_data['Next_Athletes'] and year_data['Next_Athletes'] > 0 else 0
            
            # Calculate efficiency
            host_efficiency = host_total / year_data['Host_Athletes'] if year_data['Host_Athletes'] > 0 else 0
            prev_efficiency = prev_total / year_data['Prev_Athletes'] if year_data['Prev_Athletes'] and year_data['Prev_Athletes'] > 0 else 0
            next_efficiency = next_total / year_data['Next_Athletes'] if year_data['Next_Athletes'] and year_data['Next_Athletes'] > 0 else 0
            
            summary_cards.append(
                dbc.Card([
                    dbc.CardHeader(f"{city} {year}"),
                    dbc.CardBody([
                        html.H5("Medal Statistics", className="mb-3"),
                        html.P(f"Total Medals: {host_total}"),
                        html.P(f"vs Previous Games: {prev_improvement:.1f}% change" if prev_total > 0 else "No previous games data"),
                        html.P(f"vs Next Games: {next_improvement:.1f}% change" if next_total > 0 else "No next games data"),
                        html.Hr(),
                        html.H5("Athlete Statistics", className="mb-3"),
                        html.P(f"Total Athletes: {year_data['Host_Athletes']}"),
                        html.P(f"vs Previous Games: {prev_athlete_change:.1f}% change" if year_data['Prev_Athletes'] and year_data['Prev_Athletes'] > 0 else "No previous games data"),
                        html.P(f"vs Next Games: {next_athlete_change:.1f}% change" if year_data['Next_Athletes'] and year_data['Next_Athletes'] > 0 else "No next games data"),
                        html.Hr(),
                        html.H5("Efficiency Statistics", className="mb-3"),
                        html.P(f"Medals per Athlete: {host_efficiency:.2f}"),
                        html.P(f"vs Previous Games: {((host_efficiency - prev_efficiency) / prev_efficiency * 100):.1f}% change" if prev_efficiency > 0 else "No previous games data"),
                        html.P(f"vs Next Games: {((host_efficiency - next_efficiency) / next_efficiency * 100):.1f}% change" if next_efficiency > 0 else "No next games data")
                    ])
                ], className="performance-card animate-slide mb-3")
            )
        
        if not visualizations:
            return dbc.Alert("No visualization data available for the selected country.", color="warning", className="m-3")
        
        return dbc.Row([
            dbc.Col([
                html.H4("Medal and Athlete Comparisons", className="mb-3"),
                *visualizations
            ], width=12, lg=8),
            dbc.Col([
                html.H4("Summary Statistics", className="mb-3"),
                *summary_cards
            ], width=12, lg=4)
        ])
        
    except Exception as e:
        print(f"Error in host analysis callback: {str(e)}")
        return dbc.Alert(f"An error occurred while processing the data: {str(e)}", color="danger", className="m-3")