# pages/acknowledgement.py
import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc

dash.register_page(__name__, name='Acknowledgements')

layout = dbc.Container([
    html.H3("Acknowledgements"),
    html.Hr(),
    html.P("This project utilizes data primarily from the following source:"),
    # html.Ul([
    #    html.Li(dcc.Link("120 years of Olympic history: athletes and results on Kaggle", href="https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results", target="_blank")),
    # ]),
    html.P("We acknowledge the creators and curators of this dataset."),
    html.Hr(),
    html.H4("Technology Stack"),
     html.Ul([
         html.Li("Dash (Plotly)"),
         html.Li("Pandas"),
         html.Li("Dash Bootstrap Components"),
     ]),
     html.Hr(),
     html.H4("Project Team"),
     html.P("CS661 - Group 10 (List members here if desired)"),

])