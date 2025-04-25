# pages/olympic_year.py
import dash
from dash import html, dcc, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd # Import pandas
import os # Import os for path checking
# Updated import
from data_loader import df, YEAR_OPTIONS_NO_ALL, get_default_value, DEFAULT_DROPDOWN_LABEL

dash.register_page(__name__, name='Olympic Year')

# Placeholder for when image is not found or applicable
# Use the path to the generic olympic logo as the fallback
PLACEHOLDER_IMAGE = '/assets/imgs/olympic_logo.png' 
# Base path for images within the assets folder
IMAGE_BASE_PATH = 'assets/imgs'

# Use helper for default year
default_year = get_default_value(YEAR_OPTIONS_NO_ALL)

# Define default season value (options will be dynamic)
default_season = DEFAULT_DROPDOWN_LABEL

layout = dbc.Container([
    html.H3("Olympic Year Summary", className="mb-3"),
    html.Hr(),
    # Row for Filters
    dbc.Row([
        # Year Dropdown Column
        dbc.Col([
            html.Label("Select Year:", className="fw-bold"),
            dcc.Dropdown(
                id='olympic-year-year-dropdown',
                options=YEAR_OPTIONS_NO_ALL,
                value=default_year,
                clearable=False,
            )
        ], width=12, md=6, lg=4, className="mb-3 mb-md-0"),

        # Season Dropdown Column (options will be set by callback)
        dbc.Col([
            html.Label("Select Season:", className="fw-bold"),
            dcc.Dropdown(
                id='olympic-year-season-dropdown',
                value=default_season,
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ], className="mb-4"),

    # Row for Images and Summary Card
    dbc.Row([
        # Column for Emblem Image
        dbc.Col([
            html.Div(html.Small("Emblem"), className="text-center text-muted mb-1"),
            html.Img(id='olympic-emblem-img', src=PLACEHOLDER_IMAGE, className="img-fluid", style={'max-height': '100px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
        ], width=12, md=3, className="text-center mb-3"),
        # Column for Summary Card (output target)
        dbc.Col(id='olympic-year-summary-col', width=12, md=6, className="mb-3"),
        # Column for Mascot Image
        dbc.Col([
            html.Div(html.Small("Mascot"), className="text-center text-muted mb-1"),
            html.Img(id='olympic-mascot-img', src=PLACEHOLDER_IMAGE, className="img-fluid", style={'max-height': '100px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
        ], width=12, md=3, className="text-center mb-3"),
    ], align="center", className="mb-4 g-3"),

    html.Hr(),

    dcc.Store(id='medal-table-full-data-store'),

    # New Row for the main content (table + controls)
    dbc.Row([
        dbc.Col([ # Wrap everything in one column
            # Row to align search form to the right
            dbc.Row([
                dbc.Col([ # Column to contain the form
                    # Search Form (initially hidden)
                    dbc.Form([
                        dbc.Input(
                            id="medal-table-search-input",
                            placeholder="Search Country...",
                            type="search",
                            size="sm"
                        ),
                    ],
                    id="medal-table-search-form", # ID for the search form
                    className="mb-3", # Add some margin below search
                    style={'display': 'none', 'max-width': '300px'} # Hide initially, limit width
                    )
                ], width="auto") # Column takes auto width
            ], justify="end"), # Justify row content (the form col) to the end

            # Spinner for the table itself
            dbc.Spinner(
                html.Div(id='olympic-year-details') # Details (table) will be rendered here
            ),
            # Page Size Selector Form (initially hidden - REMAINS AFTER SPINNER)
            dbc.Form([\
                dbc.Label("Rows per page:", html_for="medal-table-page-size-selector", className="me-2"),
                dbc.RadioItems(\
                    options=[\
                        {"label": "10", "value": 10},\
                        {"label": "25", "value": 25},\
                        {"label": "50", "value": 50},\
                        {"label": "All", "value": 9999},\
                    ],\
                    value=25, # Default value
                    id="medal-table-page-size-selector", # ID used in Input
                    inline=True,\
                ),\
            ],
            id="page-size-selector-form-id", # ID for the form itself
            className="d-flex justify-content-end mt-1", # Adjusted margin
            style={'display': 'none'} # Hide initially
            )
        ], width=12) # Takes full width
    ], className="mt-4") # Add margin top

], fluid=True) # Use fluid container for better width usage

# -- NEW CALLBACK: Update Season Dropdown based on Year --
@callback(
    Output('olympic-year-season-dropdown', 'options'),
    Output('olympic-year-season-dropdown', 'value'),
    Input('olympic-year-year-dropdown', 'value')
)
def update_season_options(selected_year):
    if not selected_year or df.empty:
        # No year selected or data not loaded, return empty/default
        return [[{'label': DEFAULT_DROPDOWN_LABEL, 'value': DEFAULT_DROPDOWN_LABEL}] , DEFAULT_DROPDOWN_LABEL]

    # Find seasons available for the selected year
    available_seasons = df[df['Year'] == selected_year]['Season'].unique().tolist()

    # Create dynamic options
    dynamic_options = [{'label': DEFAULT_DROPDOWN_LABEL, 'value': DEFAULT_DROPDOWN_LABEL}]
    if 'Summer' in available_seasons:
        dynamic_options.append({'label': 'Summer', 'value': 'Summer'})
    if 'Winter' in available_seasons:
        dynamic_options.append({'label': 'Winter', 'value': 'Winter'})

    # Reset season value to "All" when year changes
    new_season_value = DEFAULT_DROPDOWN_LABEL

    return dynamic_options, new_season_value

# Function to generate image path and check existence
def get_image_path(image_type, city, year):
    print(f"[Debug] get_image_path called with: type={image_type}, city={city}, year={year}") # Debug
    if not city or pd.isna(city):
        print("[Debug] City is None or NaN") # Debug
        return PLACEHOLDER_IMAGE
    # Format city name: lowercase, replace spaces and underscores with hyphens
    city_slug = str(city).lower().replace(' ', '-').replace('_', '-')
    # Handle specific known cases like st. moritz or salt lake
    city_slug = city_slug.replace('st.-moritz', 'st_moritz')
    city_slug = city_slug.replace('salt-lake-city', 'salt_lake')
    city_slug = city_slug.replace('cortina-d\'ampezzo','cortina_d_ampezzo')
    city_slug = city_slug.replace('garmisch-partenkirchen','garmisch_p')
    city_slug = city_slug.replace('squaw-valley','squaw_valley')
    print(f"[Debug] Generated city_slug: {city_slug}") # Debug

    filename = f"{city_slug}-{year}.png"
    relative_path = f"{IMAGE_BASE_PATH}/olympic_{image_type}/{filename}"
    print(f"[Debug] Checking relative_path: {relative_path}") # Debug

    # Check relative to the app's assumed root directory
    full_path_to_check = relative_path
    print(f"[Debug] Checking existence of: {full_path_to_check}") # Debug
    exists = os.path.exists(full_path_to_check)
    print(f"[Debug] os.path.exists result: {exists}") # Debug
    
    if exists:
        print(f"[Debug] Image found! Returning path with leading slash: /{relative_path}") # Debug
        return f"/{relative_path}" # Return path with leading slash for browser
    else:
        # Fallback check (if needed, currently commented out)
        # ...
        print(f"[Debug] Image NOT found.") # Debug
        return PLACEHOLDER_IMAGE

# -- EXISTING CALLBACK: Update Visuals based on Year and Season --
@callback(
    Output('olympic-year-summary-col', 'children'),
    Output('olympic-year-details', 'children'),
    Output('olympic-emblem-img', 'src'),
    Output('olympic-mascot-img', 'src'),
    Output('page-size-selector-form-id', 'style'), # Output for page size form style
    Output('medal-table-search-form', 'style'), # Output for search form style
    Output('medal-table-full-data-store', 'data'), # Output to store
    Input('olympic-year-year-dropdown', 'value'),
    Input('olympic-year-season-dropdown', 'value'),
    Input('medal-table-page-size-selector', 'value') # Keep page size selector input
)
def update_year_visuals(selected_year, selected_season, selected_page_size): # Keep page size argument
    print(f"\n[Debug] update_year_visuals triggered: year={selected_year}, season={selected_season}, page_size={selected_page_size}") # Debug
    summary_card_content = []
    details_content = []
    emblem_src = PLACEHOLDER_IMAGE
    mascot_src = PLACEHOLDER_IMAGE
    selector_style = {'display': 'none'} # Default to hidden
    search_style = {'display': 'none'} # Default search to hidden
    full_medal_data_for_store = [] # Initialize store data

    if not selected_year or df.empty:
        summary_card_content = [html.P("Please select an Olympic year...")]
        print("[Debug] No year selected or df empty, returning early.") # Debug
        # Ensure all outputs get a default value
        return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store

    # --- Determine effective season and city for image lookup ---
    year_df_all_seasons = df[df['Year'] == selected_year]
    available_seasons = year_df_all_seasons['Season'].unique().tolist()
    effective_season = None
    city_for_image = None
    if selected_season != DEFAULT_DROPDOWN_LABEL and selected_season in available_seasons:
        effective_season = selected_season
    elif selected_season == DEFAULT_DROPDOWN_LABEL and len(available_seasons) == 1:
        effective_season = available_seasons[0]

    if effective_season:
        season_df = year_df_all_seasons[year_df_all_seasons['Season'] == effective_season]
        if not season_df.empty:
            city_for_image = season_df['City'].mode()[0] if not season_df['City'].mode().empty else None
        if city_for_image:
            emblem_src = get_image_path('emblems', city_for_image, selected_year)
            mascot_src = get_image_path('mascots', city_for_image, selected_year)

    # --- Filter data for stats and table ---
    year_df_filtered = year_df_all_seasons
    if effective_season:
        year_df_filtered = year_df_all_seasons[year_df_all_seasons['Season'] == effective_season]
    year_df = year_df_filtered

    if year_df.empty:
        season_text = f" ({selected_season})" if selected_season != DEFAULT_DROPDOWN_LABEL else ""
        summary_card_content = [html.P(f"No data found for the year {selected_year}{season_text}.")]
        # Ensure all outputs get a default value
        return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store

    # --- Calculations & Components ---
    host_city = year_df['City'].mode()[0] if not year_df.empty and not year_df['City'].mode().empty else "N/A"
    game_season_display = effective_season if effective_season else "All Seasons"
    num_countries = year_df['NOC'].nunique()
    num_athletes = year_df['Name'].nunique()
    num_sports = year_df['Sport'].nunique()
    num_events = year_df['Event'].nunique()

    summary_card = dbc.Card(dbc.CardBody([
        html.H4(f"{host_city} {int(selected_year)} {game_season_display} Overview", className="card-title"),
        dbc.Row([
            dbc.Col(f"Participating Nations (NOCs): {num_countries}", width=12, sm=6, className="mb-2"),
            dbc.Col(f"Unique Athletes: {num_athletes}", width=12, sm=6, className="mb-2"),
            dbc.Col(f"Sports: {num_sports}", width=12, sm=6, className="mb-2"),
            dbc.Col(f"Events: {num_events}", width=12, sm=6, className="mb-2"),
        ])
    ]), color="light", className="shadow-sm h-100")
    summary_card_content = [summary_card]

    # 2. Medal Table Calculation
    medals_df = year_df[year_df['Medal'] != 'None'].copy()
    medal_table_component = None

    if not medals_df.empty:
        unique_event_medals = medals_df.drop_duplicates(
            subset=['Year', 'Season', 'Event', 'Medal', 'region']
        )
        medal_counts = unique_event_medals.groupby(['region', 'Medal']).size().unstack(fill_value=0)
        for medal_type in ['Gold', 'Silver', 'Bronze']:
            if medal_type not in medal_counts.columns:
                medal_counts[medal_type] = 0
        medal_counts['Total'] = medal_counts[['Gold', 'Silver', 'Bronze']].sum(axis=1)
        medal_table_df = medal_counts.sort_values(
            by=['Gold', 'Silver', 'Bronze', 'Total'], ascending=[False, False, False, False]
        ).reset_index()
        medal_table_df.insert(0, 'Rank', range(1, 1 + len(medal_table_df)))
        full_medal_data_for_store = medal_table_df.to_dict('records') # Prepare data for store

        # Determine actual page size
        actual_page_size = selected_page_size
        if selected_page_size == 9999:
            actual_page_size = len(medal_table_df)

        medal_table = dash_table.DataTable(
            id='medal-data-table',
            columns=[
                {"name": "Rank", "id": "Rank"}, {"name": "Country", "id": "region"},
                {"name": "🥇 Gold", "id": "Gold"}, {"name": "🥈 Silver", "id": "Silver"},
                {"name": "🥉 Bronze", "id": "Bronze"}, {"name": "Total", "id": "Total"}
            ],
            data=full_medal_data_for_store,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '8px'},
            style_header={
                'fontWeight': 'bold',
                'backgroundColor': 'rgb(220, 220, 220)',
                'borderBottom': '1px solid black'
             },
            sort_action='native',
            page_size=actual_page_size,
            style_data_conditional=[
                {'if': {'row_index': 'odd'},
                 'backgroundColor': 'rgb(248, 248, 248)'}
            ],
        )
        medal_table_component = dbc.Card([
            # Simplified Card Header - only title
            dbc.CardHeader(
                 html.H5(f"Medal Table ({game_season_display})", className="mb-0")
            ),
            dbc.CardBody(medal_table)
        ], color="light", className="shadow-sm")

        # Set details content to just the table
        details_content = [medal_table_component]
        # Make the selectors visible
        selector_style = {'display': 'flex', 'justify-content': 'end', 'margin-top': '0.5rem'} # Adjusted margin 
        search_style = {'display': 'block', 'max-width': '300px'} # Show search

    else:
        # If no medal data, set alert and keep selectors hidden
        details_content = [dbc.Alert("No medal data available for this selection.", color="warning", className="mb-4")]
        selector_style = {'display': 'none'}
        search_style = {'display': 'none'}
        full_medal_data_for_store = [] # Ensure store is empty if no medals

    # Final check for content
    if not details_content:
        details_content = [dbc.Alert("No specific details to display for this selection.", color="info", className="mb-4")]
        selector_style = {'display': 'none'}
        search_style = {'display': 'none'}

    # Return all outputs
    return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store

# New callback for filtering
@callback(
    Output('medal-data-table', 'data'),
    Input('medal-table-search-input', 'value'),
    State('medal-table-full-data-store', 'data')
)
def update_filtered_table_data(search_value, full_data):
    if not search_value or not full_data:
        return full_data if full_data else []

    search_lower = search_value.lower()
    filtered_data = [
        row for row in full_data
        if 'region' in row and search_lower in str(row['region']).lower()
    ]
    return filtered_data