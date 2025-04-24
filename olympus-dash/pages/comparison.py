# pages/comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from data_loader import df, FILTER_OPTIONS, create_dropdown_options

dash.register_page(__name__, name='Country Comparison')

default_noc1 = FILTER_OPTIONS['nocs'][0] if FILTER_OPTIONS.get('nocs') else None
default_noc2 = FILTER_OPTIONS['nocs'][1] if len(FILTER_OPTIONS.get('nocs', [])) > 1 else None


layout = dbc.Container([
    html.H3("Compare Two Countries"),
    html.Hr(),
     dbc.Row([
        dbc.Col([
            html.Label("Select Country 1 (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='comparison-noc1-dropdown',
                options=create_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=False),
                value=default_noc1,
                clearable=False,
            )
        ], width=6, lg=4),
         dbc.Col([
            html.Label("Select Country 2 (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='comparison-noc2-dropdown',
                options=create_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=False),
                value=default_noc2,
                clearable=False,
            )
        ], width=6, lg=4),
    ]),
     html.Hr(),
     html.P("This page will compare the selected countries on metrics like:"),
     html.Ul([
         html.Li("Overall medal counts head-to-head over time."),
         html.Li("Performance comparison in specific sports where both compete."),
         html.Li("Comparative timelines."),
     ]),
    dbc.Alert("Comparison charts coming soon!", color="info"),
    # Placeholder for Comparison components/callbacks
])