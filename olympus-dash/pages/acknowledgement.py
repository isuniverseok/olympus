# pages/acknowledgement.py
import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc

dash.register_page(__name__, name='Acknowledgement')

layout = dbc.Container([
    dbc.Card(
        dbc.CardBody([
            html.H2("Acknowledgements", className="text-primary mb-4"),
            html.Hr(),
            
            # Data Sources Section
            html.H4("Data Sources", className="mt-4"),
            html.P("This project utilizes data primarily from the following sources:"),
            html.Ul([
                html.Li([
                    html.A("120 years of Olympic history: athletes and results", 
                          href="https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results",
                          target="_blank",
                          className="text-decoration-none"),
                    " on Kaggle"
                ]),
                html.Li([
                    html.A("International Olympic Committee (IOC) Official Website",
                          href="https://olympics.com/",
                          target="_blank",
                          className="text-decoration-none")
                ]),
            ], className="mb-4"),
            
            # Technology Stack Section
            html.H4("Technology Stack", className="mt-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Frontend", className="card-title"),
                            html.Ul([
                                html.Li("Dash (Plotly)"),
                                html.Li("Dash Bootstrap Components"),
                                html.Li("HTML/CSS"),
                            ])
                        ]),
                        className="h-100"
                    )
                ], width=12, md=4, className="mb-3"),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Backend", className="card-title"),
                            html.Ul([
                                html.Li("Python"),
                                html.Li("Pandas"),
                                html.Li("NumPy"),
                            ])
                        ]),
                        className="h-100"
                    )
                ], width=12, md=4, className="mb-3"),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Data Visualization", className="card-title"),
                            html.Ul([
                                html.Li("Plotly"),
                                html.Li("Mapbox"),
                                html.Li("D3.js"),
                            ])
                        ]),
                        className="h-100"
                    )
                ], width=12, md=4, className="mb-3"),
            ], className="mb-4"),
            
            # Project Team Section
            html.H4("Project Team", className="mt-4"),
            html.P("CS661 - Big Data Visual Analytics", className="mb-2"),
            html.P("Group 10:", className="mb-3"),
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Team Members", className="card-title"),
                            html.Ul([
                                html.Li("Manoj Gattani"),
                                html.Li("Sai Kiran"),
                                html.Li("Sai Teja"),
                                html.Li("Sai Charan"),
                            ])
                        ])
                    )
                ], width=12, md=6),
            ]),
            
            # Footer
            html.Hr(className="mt-4"),
            html.P(
                "Created with ❤️ at University of Illinois Chicago",
                className="text-center text-muted mt-4"
            ),
        ]),
        className="shadow-sm"
    ),
], fluid=True, className="py-4")