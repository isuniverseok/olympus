# pages/landing.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go # Import go for empty figure handling
from data_loader import df, FILTER_OPTIONS # Import data

dash.register_page(__name__, path='/', name='Home') # Register page, path '/' is root

# --- Helper function for Stat Cards (Optional but good practice) ---
def create_stat_card(title, value, className=""):
    return dbc.Card([
        dbc.CardHeader(title),
        dbc.CardBody([html.H4(f"{value:,}" if isinstance(value, (int, float)) else value, className="card-title text-center")])
    ], className=f"text-center {className}") # Center text in card

# Define Layout
layout = dbc.Container([
    # --- Hero Section ---
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Olympus Insight", className="display-4 text-primary mb-4"),
                html.P("Explore the rich history of the Olympic Games through interactive visualizations and detailed analyses.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

    # --- NEW: Olympic Logo Row ---
    dbc.Row([
        dbc.Col(
            html.Img(
                id="landing-logo-img",
                src="https://upload.wikimedia.org/wikipedia/commons/5/5c/Olympic_rings_without_rims.svg",
                style={'height': '80px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'} # Set height and center
            ),
            width=12
        )
    ], className="mb-4"), # Add margin below logo
    # --- End Logo Row ---

    # Welcome Message Row
    dbc.Row([
        dbc.Col([
            html.H2("Explore Olympic History with Olympus Insight!", className="text-center"), # Center title
            html.P("Dive into detailed analyses of athletes, countries, sports, and hosting trends across more than a century of the Olympic Games.", className="text-center"), # Center paragraph
            # html.Hr(), # Removing Hr as logo provides visual separation
        ], width=12)
    ], className="mb-4"),

    # --- NEW: Key Statistics Row ---
    dbc.Row([
        dbc.Col(create_stat_card("Total Nations (NOCs)", len(FILTER_OPTIONS.get('nocs', [])) if FILTER_OPTIONS.get('nocs') else "N/A"), width=12, lg=4, className="mb-4 mb-lg-0"), # Full width on small, 1/3 on large
        dbc.Col(create_stat_card("Total Sports", len(FILTER_OPTIONS.get('sports', [])) if FILTER_OPTIONS.get('sports') else "N/A"), width=12, lg=4, className="mb-4 mb-lg-0"),
        dbc.Col(create_stat_card("Total Athlete Entries", len(df) if not df.empty else "N/A"), width=12, lg=4),
    ], className="mb-4"),
    # --- End New Stats Row ---

    # --- MODIFIED: Overview Charts Row (Side-by-Side) ---
    dbc.Row([
        # Athlete Trend Chart
        dbc.Col(
            dbc.Card([
                 dbc.CardHeader("Athlete Participation Trend"),
                 dbc.CardBody(dcc.Loading(
                     type="default",
                     children=dcc.Graph(id='athlete-trend-chart', figure={})
                 ))
            ], className="chart-card animate-slide"),
            width=12, md=6, # Full width on small, half on medium+
            className="mb-4 mb-md-0" # Margin bottom on small, none on medium+
        ),
        # Country Trend Chart
        dbc.Col(
            dbc.Card([
                 dbc.CardHeader("Country Participation Trend"),
                 dbc.CardBody(dcc.Loading(
                     type="default",
                     children=dcc.Graph(id='country-trend-chart', figure={})
                 ))
            ], className="chart-card animate-slide"),
            width=12, md=6 # Full width on small, half on medium+
        )
    ], className="mb-4"),
    # --- End Modified Charts Row ---

    # Explore and Summary Row
    dbc.Row([
        # Explore Data Card
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Explore the Data"),
                dbc.CardBody([
                    html.Ul([
                        html.Li([
                            dcc.Link("Country Profiling", href="/country-profile"),
                            html.Small(" - View detailed medal counts and participation history for individual countries.", className="text-muted d-block")
                        ]),
                        html.Li([
                            dcc.Link("Sport Profiling", href="/sport-profile"),
                            html.Small(" - Analyze trends, top athletes, and participating nations within specific sports.", className="text-muted d-block")
                        ]),
                        html.Li([
                            dcc.Link("Olympic Year Analysis", href="/olympic-year"),
                            html.Small(" - Explore details and highlights of specific Olympic Games years.", className="text-muted d-block")
                        ]),
                        html.Li([
                            dcc.Link("Host Analysis", href="/host-analysis"),
                            html.Small(" - Examine medal distribution and participation based on host cities/countries.", className="text-muted d-block")
                        ]),
                        html.Li([
                            dcc.Link("Country Comparison", href="/comparison"),
                            html.Small(" - Compare medal tallies and participation metrics between selected countries.", className="text-muted d-block")
                        ]),
                    ], style={'list-style-type': 'none', 'padding-left': 0}),
                    html.P("More analysis options are available in the main navigation bar.", className="mt-3")
                ])
            ], className="analysis-card animate-slide"),
            width=6 # Takes half the width
        ),
        # Dataset Summary Card
        dbc.Col(
             dbc.Card([
                 dbc.CardHeader("Dataset Summary"),
                 dbc.CardBody([
                     html.P(f"Years Covered: {FILTER_OPTIONS.get('years', [None])[-1]} - {FILTER_OPTIONS.get('years', [None])[0]}" if FILTER_OPTIONS.get('years') else "N/A"),
                     html.P("Detailed analysis available via navigation.") # Added placeholder text
                 ])
             ], className="analysis-card animate-slide"),
             width=6 # Takes half the width
        )
    ])
], fluid=True) # Keep container fluid

# --- Callback for the athlete trend chart (unchanged) ---
@callback(
    Output('athlete-trend-chart', 'figure'),
    Input('athlete-trend-chart', 'id')
)
def update_athlete_trend(_):
    if df.empty:
        return go.Figure().update_layout(template="plotly_white", title="Data not loaded", xaxis={'visible': False}, yaxis={'visible': False})
    athletes_per_year = df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Unique Athletes')
    fig = px.line(athletes_per_year, x='Year', y='Unique Athletes', title='Unique Athletes Over Time', markers=True, template="plotly_white") # Added template
    fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Number of Unique Athletes', title_x=0.5) # Center title
    return fig

# --- NEW Callback for the country trend chart ---
@callback(
    Output('country-trend-chart', 'figure'),
    Input('country-trend-chart', 'id') # Dummy input
)
def update_country_trend(_):
    if df.empty:
        return go.Figure().update_layout(template="plotly_white", title="Data not loaded", xaxis={'visible': False}, yaxis={'visible': False})

    # Calculate unique countries (NOCs) per year
    countries_per_year = df.drop_duplicates(subset=['Year', 'NOC']).groupby('Year')['NOC'].nunique().reset_index(name='Unique Countries')

    # Create figure using go.Figure instead of px.line
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=countries_per_year['Year'],
        y=countries_per_year['Unique Countries'],
        mode='lines+markers',
        name='Unique Countries'
    ))
    
    fig.update_layout(
        title='Unique Countries Over Time',
        xaxis_title='Olympic Year',
        yaxis_title='Number of Unique Countries',
        title_x=0.5,  # Center title
        template="plotly_white"
    )
    return fig