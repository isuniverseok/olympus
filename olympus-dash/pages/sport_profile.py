# pages/sport_profile.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
# Updated import
from data_loader import df, SPORT_OPTIONS_NO_ALL, get_default_value

dash.register_page(__name__, name='Sport Profile')

# Use helper
default_sport = get_default_value(SPORT_OPTIONS_NO_ALL)

layout = dbc.Container([
    html.H3("Sport Performance Profile"),
    html.Hr(),
     dbc.Row([
        dbc.Col([
            html.Label("Select Sport:", className="fw-bold"),
            dcc.Dropdown(
                id='sport-profile-sport-dropdown',
                options=SPORT_OPTIONS_NO_ALL, # Use options from data_loader
                value=default_sport,
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ]),
    html.Hr(),
    dbc.Spinner(
        html.Div(id='sport-profile-visuals') # Placeholder for visuals
    )
])

@callback(
     Output('sport-profile-visuals', 'children'),
     Input('sport-profile-sport-dropdown', 'value')
)
def update_sport_visuals(selected_sport):
    if not selected_sport or df.empty:
        return html.P("Please select a sport from the dropdown or wait for data to load.")

    # Filter data for the selected sport
    sport_df = df[df['Sport'] == selected_sport].copy()
    if sport_df.empty:
         return html.P(f"No data found for {selected_sport}.")

    # --- Calculations ---
    # 1. Top Countries (by Medals)
    sport_medals_df = sport_df[sport_df['Medal'] != 'None']
    top_nocs = sport_medals_df['NOC'].value_counts().reset_index(name='Medal Count').head(15) # Top 15

    # 2. Participation over Time
    sport_athletes_time = sport_df.drop_duplicates(subset=['Year', 'Name'])\
                                .groupby('Year').size().reset_index(name='Unique Athletes')

    # --- Generate Figures ---
    # Figure 1: Top Countries
    if not top_nocs.empty:
        top_noc_fig = px.bar(top_nocs, x='NOC', y='Medal Count',
                            title=f"Top 15 Medal-Winning Countries (NOC) in {selected_sport}")
        top_noc_fig.update_layout(xaxis_title='Country (NOC)', yaxis_title='Medals Won')
    else:
        top_noc_fig = go.Figure().update_layout(title=f"No Medal Data for Top Countries in {selected_sport}")


    # Figure 2: Participation Trend
    if not sport_athletes_time.empty:
        participation_fig = px.line(sport_athletes_time, x='Year', y='Unique Athletes', markers=True,
                                   title=f"Unique Athlete Participation Trend in {selected_sport}")
        participation_fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Unique Athletes')
    else:
         participation_fig = go.Figure().update_layout(title=f"No Participation Data Found for {selected_sport}")

    # --- Assemble Layout ---
    layout_content = dbc.Row([
         dbc.Col(dcc.Graph(figure=top_noc_fig), width=12, lg=6, className="mb-4"),
         dbc.Col(dcc.Graph(figure=participation_fig), width=12, lg=6, className="mb-4"),
         # Add more sport-specific graphs here (e.g., events breakdown, age distribution for THIS sport)
    ])

    return layout_content