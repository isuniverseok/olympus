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
    html.H3("Olympic Year Summary"),
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
                # options=[], # Options are now dynamic
                value=default_season, # Default to "All"
                clearable=False,
                # placeholder="Select season..." # Optional placeholder
            )
        ], width=12, md=6, lg=4)
    ], className="mb-4"),

    html.Hr(),
    # Row for Images and Summary Card (Images added back)
    dbc.Row([
        # Column for Emblem Image
        dbc.Col([
            html.Div(html.Small("Emblem"), className="text-center text-muted"),
            html.Img(id='olympic-emblem-img', src=PLACEHOLDER_IMAGE, style={'max-height': '100px', 'max-width': '100%', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
        ], width=12, md=3, className="text-center mb-3"),
        # Column for Summary Card
        dbc.Col(id='olympic-year-summary-col', width=12, md=6),
        # Column for Mascot Image
        dbc.Col([
            html.Div(html.Small("Mascot"), className="text-center text-muted"),
            html.Img(id='olympic-mascot-img', src=PLACEHOLDER_IMAGE, style={'max-height': '100px', 'max-width': '100%', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
        ], width=12, md=3, className="text-center mb-3"),
    ], align="center", className="mb-4"),

    # Placeholder Div for Medal Table and other visuals
    dbc.Spinner(
        html.Div(id='olympic-year-details')
    )
])

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
    Input('olympic-year-year-dropdown', 'value'),
    Input('olympic-year-season-dropdown', 'value')
)
def update_year_visuals(selected_year, selected_season):
    print(f"\n[Debug] update_year_visuals triggered: year={selected_year}, season={selected_season}") # Debug
    summary_card_content = []
    details_content = []
    emblem_src = PLACEHOLDER_IMAGE
    mascot_src = PLACEHOLDER_IMAGE

    if not selected_year or df.empty:
        summary_card_content = [html.P("Please select an Olympic year...")]
        print("[Debug] No year selected or df empty, returning early.") # Debug
        return summary_card_content, details_content, emblem_src, mascot_src

    # --- Determine effective season and city for image lookup --- 
    year_df_all_seasons = df[df['Year'] == selected_year]
    available_seasons = year_df_all_seasons['Season'].unique().tolist()
    effective_season = None
    city_for_image = None
    print(f"[Debug] Available seasons for {selected_year}: {available_seasons}") # Debug

    if selected_season != DEFAULT_DROPDOWN_LABEL and selected_season in available_seasons:
        effective_season = selected_season
    elif selected_season == DEFAULT_DROPDOWN_LABEL and len(available_seasons) == 1:
        effective_season = available_seasons[0]
    print(f"[Debug] Determined effective_season: {effective_season}") # Debug
    
    if effective_season:
        season_df = year_df_all_seasons[year_df_all_seasons['Season'] == effective_season]
        if not season_df.empty:
            city_for_image = season_df['City'].mode()[0] if not season_df['City'].mode().empty else None
            print(f"[Debug] Found city_for_image: {city_for_image}") # Debug
        else:
             print(f"[Debug] season_df is empty for {selected_year} {effective_season}") # Debug
        
        if city_for_image:
            emblem_src = get_image_path('emblems', city_for_image, selected_year)
            mascot_src = get_image_path('mascots', city_for_image, selected_year)
            print(f"[Debug] Returned emblem_src: {emblem_src}") # Debug
            print(f"[Debug] Returned mascot_src: {mascot_src}") # Debug
        else:
            print("[Debug] No city found for image lookup.") # Debug
    else:
        print("[Debug] No effective season for image lookup.") # Debug
    
    # --- Filter data for stats and table ---
    year_df_filtered = year_df_all_seasons
    if effective_season:
        year_df_filtered = year_df_all_seasons[year_df_all_seasons['Season'] == effective_season]
    
    year_df = year_df_filtered

    if year_df.empty:
        season_text = f" ({selected_season})" if selected_season != DEFAULT_DROPDOWN_LABEL else ""
        summary_card_content = [html.P(f"No data found for the year {selected_year}{season_text}.")]
        return summary_card_content, details_content, emblem_src, mascot_src

    # --- Calculations & Components ---
    host_city = year_df['City'].mode()[0] if not year_df.empty and not year_df['City'].mode().empty else "N/A"
    game_season_display = effective_season if effective_season else "All Seasons"

    num_countries = year_df['NOC'].nunique()
    num_athletes = year_df['Name'].nunique()
    num_sports = year_df['Sport'].nunique()
    num_events = year_df['Event'].nunique()

    summary_card = dbc.Card(dbc.CardBody([
        html.H4(f"{host_city} {int(selected_year)} {game_season_display} Overview"),
        dbc.Row([
            dbc.Col(f"Participating Nations (NOCs): {num_countries}", width=6),
            dbc.Col(f"Unique Athletes: {num_athletes}", width=6),
            dbc.Col(f"Sports: {num_sports}", width=6),
            dbc.Col(f"Events: {num_events}", width=6),
        ])
    ]), className="mb-0")
    summary_card_content = [summary_card]

    # 2. Medal Table Calculation
    medals_df = year_df[year_df['Medal'] != 'None'].copy()
    if not medals_df.empty:
        # --- FIX: Deduplicate based on event medal per region --- 
        # Keep only one record for each unique Event-Medal combination per Region
        # for the filtered year/season to count team medals correctly.
        unique_event_medals = medals_df.drop_duplicates(
            subset=['Year', 'Season', 'Event', 'Medal', 'region']
        )
        # --- END FIX ---

        # Now group the deduplicated data
        medal_counts = unique_event_medals.groupby(['region', 'Medal']).size().unstack(fill_value=0)
        
        # Ensure Gold, Silver, Bronze columns exist (remains the same)
        for medal_type in ['Gold', 'Silver', 'Bronze']:
            if medal_type not in medal_counts.columns:
                medal_counts[medal_type] = 0
        medal_counts['Total'] = medal_counts[['Gold', 'Silver', 'Bronze']].sum(axis=1)
        medal_table_df = medal_counts.sort_values(
            by=['Gold', 'Silver', 'Bronze', 'Total'], ascending=[False, False, False, False]
        ).reset_index()
        medal_table_df.insert(0, 'Rank', range(1, 1 + len(medal_table_df)))
        medal_table = dash_table.DataTable(
            columns=[
                {"name": "Rank", "id": "Rank"}, {"name": "Country", "id": "region"},
                {"name": "Gold", "id": "Gold"}, {"name": "Silver", "id": "Silver"},
                {"name": "Bronze", "id": "Bronze"}, {"name": "Total", "id": "Total"}
            ],
            data=medal_table_df.head(20).to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '5px'},
            style_header={'fontWeight': 'bold', 'backgroundColor': 'rgb(230, 230, 230)'},
            sort_action='native',
        )
        medal_table_component = dbc.Card([
            dbc.CardHeader(f"Top 20 Medal Table ({game_season_display})"),
            dbc.CardBody(medal_table)
        ], className="mb-4")
        details_content = [medal_table_component]
    else:
        details_content = [dbc.Alert("No medal data available for this selection.", color="warning")]

    return summary_card_content, details_content, emblem_src, mascot_src