# pages/landing.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from data_loader import df, FILTER_OPTIONS
import pandas as pd

dash.register_page(__name__, path='/', name='Home')

# Card styling
card_style = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e0e0e0",
    "borderRadius": "10px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
    "transition": "all 0.3s ease",
    "height": "100%"
}

card_hover_style = {
    "transform": "translateY(-5px)",
    "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
}

def create_stat_card(title, value, icon, className=""):
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.I(className=f"bi bi-{icon} display-4 text-primary mb-3"),
                html.H4(title, className="card-title text-muted"),
                html.H2(f"{value:,}" if isinstance(value, (int, float)) else value, 
                       className="card-text text-center display-6")
            ], className="text-center")
        ])
    ], className=f"stat-card {className}", style=card_style)

# Layout
layout = dbc.Container([
    # Hero Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(src="/assets/imgs/olympic_logo.png", className="mb-4", style={"height": "100px"}),
                html.H1("Olympus Insight", className="display-3 fw-bold text-primary mb-4"),
                html.P("Explore Olympic data through interactive visualizations and insights.", 
                      className="lead mb-5")
            ], className="text-center py-5")
        ], width=12)
    ], className="mb-4"),

    # Stats
    dbc.Row([
        dbc.Col(create_stat_card("Total Athletes", len(df['Name'].unique()), "people-fill"), width=12, md=4, className="mb-4"),
        dbc.Col(create_stat_card("Total Countries", len(df['NOC'].unique()), "globe"), width=12, md=4, className="mb-4"),
        dbc.Col(create_stat_card("Total Sports", len(df['Sport'].unique()), "trophy-fill"), width=12, md=4, className="mb-4")
    ], className="mb-5"),

    # Main content
    dbc.Row([
        # Athlete Trend Chart
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Athlete Participation Trends", className="text-primary"),
                dbc.CardBody([
                    dcc.Graph(id='athlete-trend-chart', config={'displayModeBar': False})
                ])
            ], className="chart-card animate-slide", style=card_style)
        ], width=12, lg=8, className="mb-4"),
        
        # Dataset Summary
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Dataset Overview", className="text-primary"),
                dbc.CardBody([
                    html.Div([
                        html.I(className="bi bi-calendar-range display-4 text-primary mb-3"),
                        html.H5("Years Covered", className="text-muted"),
                        html.P(f"{FILTER_OPTIONS.get('years', [None])[-1]} - {FILTER_OPTIONS.get('years', [None])[0]}", 
                              className="lead")
                    ], className="text-center mb-4"),
                    html.Div([
                        html.I(className="bi bi-info-circle display-4 text-primary mb-3"),
                        html.H5("About the Data", className="text-muted"),
                        html.P("Explore detailed analysis through our interactive navigation menu.", 
                              className="lead")
                    ], className="text-center")
                ])
            ], className="info-card animate-slide", style=card_style)
        ], width=12, lg=4, className="mb-4")
    ])
], fluid=True, className="px-4 py-3")

# Athlete trend chart callback
@callback(
    Output('athlete-trend-chart', 'figure'),
    Input('athlete-trend-chart', 'id')
)
def update_athlete_trend(_):
    if df.empty:
        return go.Figure().update_layout(
            template="plotly_white",
            title="Data not loaded",
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
    
    # Separate Summer and Winter data
    summer_df = df[df['Season'] == 'Summer']
    winter_df = df[df['Season'] == 'Winter']
    
    # Calculate athletes per year
    summer_athletes = summer_df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Athletes')
    summer_athletes['Season'] = 'Summer'
    
    winter_athletes = winter_df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Athletes')
    winter_athletes['Season'] = 'Winter'
    
    # Combine data
    combined_df = pd.concat([summer_athletes, winter_athletes])
    
    # Create trend lines
    fig = px.line(
        combined_df,
        x='Year',
        y='Athletes',
        color='Season',
        title='Athlete Participation by Olympic Season',
        markers=True,
        template="plotly_white",
        color_discrete_map={'Summer': '#FF7F0E', 'Winter': '#1F77B4'}
    )
    
    fig.update_layout(
        xaxis_title='Olympic Year',
        yaxis_title='Number of Athletes',
        title_x=0.5,
        hovermode='x unified',
        legend_title='Season',
        margin=dict(t=30, b=30, l=30, r=30)
    )
    
    return fig