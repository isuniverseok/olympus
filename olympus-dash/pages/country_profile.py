# pages/country_profile.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
# Updated import to use helpers from data_loader
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value

dash.register_page(__name__, name='Country Profile')

# Use helper to get default value safely
default_noc = get_default_value(NOC_OPTIONS_NO_ALL)

layout = dbc.Container([
    html.H3("Country Performance Profile"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label("Select Country (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='country-profile-noc-dropdown',
                options=NOC_OPTIONS_NO_ALL, # Use options list from data_loader
                value=default_noc,
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ]),
    html.Hr(),

    # Visualization Area with Spinner
    dbc.Spinner(
        html.Div(id='country-profile-visuals') # Content will be loaded here by callback
    )
])

# Combined Callback for ALL country profile outputs
@callback(
    Output('country-profile-visuals', 'children'), # Output to the Div container
    Input('country-profile-noc-dropdown', 'value')
)
def update_country_visuals(selected_noc):
    if not selected_noc or df.empty:
        return html.P("Please select a country (NOC) from the dropdown or wait for data to load.")

    # Filter data for the selected country
    country_df = df[df['NOC'] == selected_noc].copy()
    if country_df.empty:
        return html.P(f"No data found for {selected_noc}.")

    # --- Calculations ---
    # 1. Medals over Time
    medals_df = country_df[country_df['Medal'] != 'None']
    medals_time = medals_df.groupby(['Year', 'Medal']).size().unstack(fill_value=0).reset_index()

    # 2. Gender over Time
    gender_time = country_df.drop_duplicates(subset=['Year', 'Name', 'Gender'])\
                          .groupby(['Year', 'Gender']).size().unstack(fill_value=0).reset_index()

    # 3. Top Sports
    top_sports = medals_df['Sport'].value_counts().reset_index(name='Medal Count').head(10)

    # 4. Age Distribution
    age_data = country_df['Age'].dropna()

    # --- Generate Figures ---
    # Figure 1: Medals
    if not medals_time.empty:
        medal_columns = ['Gold', 'Silver', 'Bronze']
        for medal in medal_columns:
             if medal not in medals_time.columns: medals_time[medal] = 0 # Ensure columns exist
        medals_fig = px.bar(medals_time, x='Year', y=medal_columns,
                          title=f"Medals Won by {selected_noc} Over Time",
                          labels={'value': 'Medals', 'variable': 'Medal'},
                          color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#cd7f32'})
        medals_fig.update_layout(xaxis_title='Year', yaxis_title='Number of Medals', legend_title_text='Medal', barmode='stack')
    else:
        medals_fig = go.Figure().update_layout(title=f"No Medal Data for {selected_noc}")

    # Figure 2: Gender
    if not gender_time.empty:
        gender_columns = ['M', 'F']
        for gender in gender_columns:
            if gender not in gender_time.columns: gender_time[gender] = 0 # Ensure M/F exist
        gender_fig = px.line(gender_time, x='Year', y=gender_columns,
                           title=f"Athlete Participation by Gender ({selected_noc})",
                           labels={'value': 'Athletes', 'variable': 'Gender'},
                           color_discrete_map={'M': 'royalblue', 'F': 'lightcoral'}, markers=True)
        gender_fig.update_layout(xaxis_title='Year', yaxis_title='Number of Unique Athletes', legend_title_text='Gender')
    else:
        gender_fig = go.Figure().update_layout(title=f"No Gender Data for {selected_noc}")


    # Figure 3: Top Sports
    if not top_sports.empty:
        sports_fig = px.bar(top_sports, x='Medal Count', y='Sport', orientation='h',
                           title=f"Top 10 Medal-Winning Sports ({selected_noc})")
        sports_fig.update_layout(xaxis_title='Total Medals Won', yaxis_title='Sport', yaxis={'categoryorder':'total ascending'})
    else:
         sports_fig = go.Figure().update_layout(title=f"No Medal Data (Top Sports) for {selected_noc}")


    # Figure 4: Age Distribution
    if not age_data.empty:
        age_fig = px.histogram(age_data, nbins=20, title=f"Age Distribution of Athletes ({selected_noc})")
        age_fig.update_layout(xaxis_title='Age', yaxis_title='Number of Athletes')
    else:
        age_fig = go.Figure().update_layout(title=f"No Age Data for {selected_noc}")

    # --- Assemble Layout for Output Div ---
    layout_content = dbc.Row([
        dbc.Col(dcc.Graph(figure=medals_fig), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(figure=gender_fig), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(figure=sports_fig), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(figure=age_fig), width=12, lg=6, className="mb-4"),
        # Add more charts or summary cards here in new Cols
    ])

    return layout_content