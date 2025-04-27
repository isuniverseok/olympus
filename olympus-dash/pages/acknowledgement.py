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
                    " on Kaggle (Main source for athlete events, NOCs)."
                ]),
                html.Li("Human Development Index (HDI) Data"),
                html.Li("Olympic Host City Data"),
                html.Li("Emblem and Mascot Data"),
            ], className="mb-4"),
            
            # Technology Stack Section
            html.H4("Technology Stack", className="mt-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Core Framework", className="card-title"),
                            html.Ul([
                                html.Li("Python"),
                                html.Li("Dash (Plotly)"),
                                html.Li("Dash Bootstrap Components (Flatly Theme)"),
                                html.Li("HTML/CSS"),
                            ])
                        ]),
                        className="h-100"
                    )
                ], width=12, md=4, className="mb-3"),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody([
                            html.H5("Data Handling & Analysis", className="card-title"),
                            html.Ul([
                                html.Li("Pandas"),
                                html.Li("NumPy"),
                                html.Li("Scikit-learn"),
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
                                html.Li("Matplotlib"),
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
                                html.Li("Abhishek Choudhary"),
                                html.Li("Arnesh Dadhich"),
                                html.Li("Nirmal Prajapati"),
                                html.Li("Rajat Gattani"),
                                html.Li("Utkarsh Agarwal"),
                                html.Li("Vipul Chanchalani"),
                                html.Li("Vishal Himmatsinghka"),
                                html.Li("Yash Verma"),
                            ])
                        ])
                    )
                ], width=12, md=6),
            ]),
            
            # Footer
            html.Hr(className="mt-4"),
            html.P(
                "Created with ❤️ at IIT Kanpur",
                className="text-center text-muted mt-4"
            ),
        ]),
        className="shadow-sm"
    ),
], fluid=True, className="py-4")