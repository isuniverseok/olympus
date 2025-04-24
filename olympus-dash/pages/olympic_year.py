# pages/olympic_year.py
import dash
from dash import html, dcc, dash_table, callback, Input, Output # Added dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
# Updated import
from data_loader import df, YEAR_OPTIONS_NO_ALL, get_default_value

dash.register_page(__name__, name='Olympic Year')

# Use helper
default_year = get_default_value(YEAR_OPTIONS_NO_ALL)

layout = dbc.Container([
    html.H3("Olympic Year Summary"),
    html.Hr(),
      dbc.Row([
        dbc.Col([
            html.Label("Select Year:", className="fw-bold"),
            dcc.Dropdown(
                id='olympic-year-year-dropdown',
                options=YEAR_OPTIONS_NO_ALL, # Use options from data_loader
                value=default_year,
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ]),
     html.Hr(),
     # Placeholder Div for dynamic content based on year selection
    dbc.Spinner(
         html.Div(id='olympic-year-visuals')
    )
])


@callback(
    Output('olympic-year-visuals', 'children'),
    Input('olympic-year-year-dropdown', 'value')
)
def update_year_visuals(selected_year):
    if not selected_year or df.empty:
        return html.P("Please select an Olympic year or wait for data to load.")

    year_df = df[df['Year'] == selected_year].copy()
    if year_df.empty:
         return html.P(f"No data found for the year {selected_year}.")

    # --- Calculations & Components ---
    # 1. Basic Stats
    host_city = year_df['City'].iloc[0] if not year_df.empty else "N/A"
    num_countries = year_df['NOC'].nunique()
    num_athletes = year_df['Name'].nunique()
    num_sports = year_df['Sport'].nunique()
    num_events = year_df['Event'].nunique()

    summary_card = dbc.Card(dbc.CardBody([
        html.H4(f"{host_city} {int(selected_year)} Overview"), # Use int() for display
        dbc.Row([
             dbc.Col(f"Participating Nations (NOCs): {num_countries}", width=6),
             dbc.Col(f"Unique Athletes: {num_athletes}", width=6),
             dbc.Col(f"Sports: {num_sports}", width=6),
             dbc.Col(f"Events: {num_events}", width=6),
        ])
    ]), className="mb-4")

    # 2. Medal Table Calculation
    medals_df = year_df[year_df['Medal'] != 'None'].copy()
    if not medals_df.empty:
        # Pivot to get Gold, Silver, Bronze counts per NOC
        medal_counts = medals_df.groupby(['NOC', 'Medal']).size().unstack(fill_value=0)

        # Ensure Gold, Silver, Bronze columns exist
        for medal_type in ['Gold', 'Silver', 'Bronze']:
             if medal_type not in medal_counts.columns:
                 medal_counts[medal_type] = 0

        # Calculate Total
        medal_counts['Total'] = medal_counts[['Gold', 'Silver', 'Bronze']].sum(axis=1)

        # Sort by Gold, then Silver, then Bronze (Olympic standard), then Total as tie-breaker
        medal_table_df = medal_counts.sort_values(
            by=['Gold', 'Silver', 'Bronze', 'Total'],
            ascending=[False, False, False, False]
        ).reset_index()

        # Add Rank
        medal_table_df.insert(0, 'Rank', range(1, 1 + len(medal_table_df)))


        # Prepare for Dash DataTable
        medal_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in medal_table_df.columns],
            data=medal_table_df.head(20).to_dict('records'), # Show top 20 for brevity
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'fontWeight': 'bold', 'backgroundColor': 'rgb(230, 230, 230)'},
            sort_action='native', # Allow sorting
        )
        medal_table_component = dbc.Card([
            dbc.CardHeader("Top 20 Medal Table"),
            dbc.CardBody(medal_table)
        ], className="mb-4")

    else:
        medal_table_component = dbc.Alert("No medal data available for this year.", color="warning")


    # --- Assemble Layout ---
    layout_content = html.Div([
        summary_card,
        medal_table_component
        # Add more charts specific to the year here (e.g., distribution of medals across sports)
    ])

    return layout_content