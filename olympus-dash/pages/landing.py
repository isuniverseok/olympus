# pages/landing.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go # Import go for empty figure handling
from data_loader import df, FILTER_OPTIONS # Import data

dash.register_page(__name__, path='/', name='Home') # Register page, path '/' is root

# Define Layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Welcome to Olympus Insight!"),
            html.P("Your portal to exploring over a century of Olympic Games data."),
            html.Hr(),
        ], width=12)
    ]),

    # --- NEW: Overview Chart ---
    dbc.Row([
        dbc.Col(
            dbc.Card([
                 dbc.CardHeader("Overall Athlete Participation Trend"),
                 dbc.CardBody(dcc.Graph(id='athlete-trend-chart', figure={})) # Placeholder
            ]), width=12, className="mb-4")
    ]),
    # --- End New ---

    dbc.Row([
        dbc.Col([
            html.H4("Explore the Data:"),
            html.P("Use the navigation bar above to explore different analyses:"),
            html.Ul([
                html.Li(dcc.Link("Country Profiling", href="/country-profile")), # Use dcc.Link
                html.Li(dcc.Link("Sport Profiling", href="/sport-profile")),
                html.Li(dcc.Link("Olympic Year Analysis", href="/olympic-year")),
                html.Li(dcc.Link("Host Analysis", href="/host-analysis")),
                html.Li(dcc.Link("Country Comparison", href="/comparison")),
                # ... Add links for other pages if desired
                html.Li("More Analysis & Acknowledgements available in navbar.")
            ]),
             html.Hr(),
             html.H4("Dataset Summary"),
             html.P(f"Years Covered: {FILTER_OPTIONS.get('years', [None])[-1]} - {FILTER_OPTIONS.get('years', [None])[0]}" if FILTER_OPTIONS.get('years') else "N/A"),
             html.P(f"Total Nations (NOCs): {len(FILTER_OPTIONS.get('nocs', []))}" if FILTER_OPTIONS.get('nocs') else "N/A"),
             html.P(f"Total Sports: {len(FILTER_OPTIONS.get('sports', []))}" if FILTER_OPTIONS.get('sports') else "N/A"),
             html.P(f"Total Athlete Entries: {len(df):,}" if not df.empty else "N/A"),
        ], width=12)
    ])
])

# --- NEW: Callback for the trend chart ---
@callback(
    Output('athlete-trend-chart', 'figure'),
    Input('athlete-trend-chart', 'id') # Use a dummy input to trigger on load
)
def update_athlete_trend(_): # Argument name doesn't matter for dummy input
    if df.empty:
        return go.Figure().update_layout(
            title="Data not loaded", xaxis={'visible': False}, yaxis={'visible': False}
        )

    # Calculate unique athletes per year
    athletes_per_year = df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Unique Athletes')

    fig = px.line(athletes_per_year,
                  x='Year',
                  y='Unique Athletes',
                  title='Trend of Unique Athlete Participation Over Time',
                  markers=True)
    fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Unique Athletes')
    return fig