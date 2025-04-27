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
# Imports for Word Cloud
import io
import base64
try:
    from wordcloud import WordCloud
    import matplotlib # Often needed implicitly by wordcloud
    from PIL import Image # Needed for image conversion
    WORDCLOUD_INSTALLED = True
except ImportError:
    WORDCLOUD_INSTALLED = False
    print("Word Cloud libraries not installed. Skipping word cloud generation.")
    # Define dummy WordCloud class if not installed to avoid NameError later
    class WordCloud:
        def __init__(self, **kwargs): pass
        def generate_from_frequencies(self, frequencies): return self
        def to_image(self): return None # Or return a placeholder PIL image if needed

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
    html.H3("Olympic Year Summary", className="mb-3 display-5 text-center fw-bold"),
    html.Hr(className="my-4"),
    # Row for Filters - CENTERED
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

        # Season Dropdown Column
        dbc.Col([
            html.Label("Select Season:", className="fw-bold"),
            dcc.Dropdown(
                id='olympic-year-season-dropdown',
                value=None,
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ], className="mb-4", justify="center"),

    # Row for Images and Summary Card
    dbc.Row([
        # Column for Emblem Image
        dbc.Col([
            html.Img(id='olympic-emblem-img', src=PLACEHOLDER_IMAGE, className="img-fluid", style={'max-height': '150px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
        ], width=12, md=3, className="text-center mb-3 d-flex flex-column justify-content-center"),
        # Column for Summary Card (output target)
        dbc.Col(id='olympic-year-summary-col', width=12, md=6, className="mb-3"),
        # Column for Mascot Image
        dbc.Col([
            html.Img(id='olympic-mascot-img', src=PLACEHOLDER_IMAGE, className="img-fluid", style={'max-height': '150px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'})
        ], width=12, md=3, className="text-center mb-3 d-flex flex-column justify-content-center"),
    ], align="stretch", className="mb-4 g-3"),

    html.Hr(className="my-4"),

    dcc.Store(id='medal-table-full-data-store'),

    # New Row for the main content (table + controls)
    dbc.Row([
        dbc.Col([ # Wrap everything in one column
            # Row to hold Search and Page Size controls
            dbc.Row([
                # Column for Page Size Selector (Left)
                dbc.Col([
                    dbc.Form([\
                        dbc.RadioItems(\
                            options=[\
                                {"label": "10", "value": 10},\
                                {"label": "25", "value": 25},\
                                {"label": "50", "value": 50},\
                            ],\
                            value=25, # Default value
                            id="medal-table-page-size-selector", # ID used in Input
                            inline=True,\
                        ),\
                    ],
                    id="page-size-selector-form-id", # ID for the form itself
                    style={'display': 'none'} # Hide initially
                    )
                ], width="auto"), # Auto width for left col

                # Column for Search Input (Right)
                dbc.Col([
                    dbc.Input(
                        id="medal-table-search-input",
                        placeholder="Search Country...",
                        type="search",
                        size="sm"
                    ),
                ],
                id="medal-table-search-form", # ID for the search form
                style={'display': 'none', 'max-width': '300px'} # Hide initially, limit width
                )
            
            ], justify="between", align="center", className="mb-3"), # Space controls out, add bottom margin

            # Spinner for the table itself
            dbc.Spinner(
                html.Div(id='olympic-year-details') # Details (table + word cloud) will be rendered here
            ),
            
        ], width=12) # Takes full width
    ], className="mt-4") # Add margin top

], fluid=True, id='olympic-year-page-container', className="pt-4")

# -- NEW CALLBACK: Update Season Dropdown based on Year --
@callback(
    Output('olympic-year-season-dropdown', 'options'),
    Output('olympic-year-season-dropdown', 'value'),
    Input('olympic-year-year-dropdown', 'value')
)
def update_season_options(selected_year):
    if not selected_year or df.empty:
        # No year selected or data not loaded, return empty/default
        return [], None # Return empty options and None value

    # Find seasons available for the selected year
    available_seasons = df[df['Year'] == selected_year]['Season'].unique().tolist()

    # Create dynamic options (WITHOUT "All")
    dynamic_options = []
    if 'Summer' in available_seasons:
        dynamic_options.append({'label': 'Summer', 'value': 'Summer'})
    if 'Winter' in available_seasons:
        dynamic_options.append({'label': 'Winter', 'value': 'Winter'})

    # Set default value based on availability
    new_season_value = None
    if 'Summer' in available_seasons:
        new_season_value = 'Summer' # Default to Summer if available
    elif 'Winter' in available_seasons:
        new_season_value = 'Winter' # Default to Winter if only Winter is available
    # If neither, new_season_value remains None

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
    Output('page-size-selector-form-id', 'style'),
    Output('medal-table-search-form', 'style'),
    Output('medal-table-full-data-store', 'data'),
    Output('olympic-year-page-container', 'style'), # Add output for page style
    Input('olympic-year-year-dropdown', 'value'),
    Input('olympic-year-season-dropdown', 'value'),
    Input('medal-table-page-size-selector', 'value')
)
def update_year_visuals(selected_year, selected_season, selected_page_size):
    print(f"\n[Debug] update_year_visuals triggered: year={selected_year}, season={selected_season}, page_size={selected_page_size}")
    # Initialize outputs
    summary_card_content = []
    details_content = []
    emblem_src = PLACEHOLDER_IMAGE
    mascot_src = PLACEHOLDER_IMAGE
    selector_style = {'display': 'none'}
    search_style = {'display': 'none'}
    full_medal_data_for_store = []
    page_background_style = {} # Default empty style

    if not selected_year or df.empty:
        summary_card_content = [html.P("Please select an Olympic year...")]
        # Ensure all outputs get a default value
        return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store, page_background_style

    # --- Determine effective season and city for image lookup ---
    year_df_all_seasons = df[df['Year'] == selected_year]
    available_seasons = year_df_all_seasons['Season'].unique().tolist()
    effective_season = None
    city_for_image = None
    # Determine effective season based on dropdown selection AND availability for the year
    if selected_season in available_seasons:
        effective_season = selected_season
    # (Handle case where selected_season might be None initially or if year changes before season updates)
    elif not selected_season and len(available_seasons) == 1:
         effective_season = available_seasons[0]
    # Add a fallback if selection invalid somehow, maybe default to first available?
    elif not effective_season and available_seasons: 
         effective_season = available_seasons[0] # Fallback logic

    # Determine background IMAGE with opacity overlay based on effective_season
    overlay_opacity = 0.7
    white_overlay = f'linear-gradient(rgba(255, 255, 255, {overlay_opacity}), rgba(255, 255, 255, {overlay_opacity}))'

    # Base style properties (common)
    base_bg_style = {
        'background-position': 'center center',
        'background-repeat': 'no-repeat',
        'background-attachment': 'fixed',
        'transition': 'background 0.5s ease'
    }

    if effective_season == 'Summer':
        page_background_style = {
            **base_bg_style,
            'background-size': 'cover', # Keep cover for summer
            'background': f'{white_overlay}, url("/assets/imgs/summer_bg.jpg")',
        }
    elif effective_season == 'Winter':
        page_background_style = {
            **base_bg_style,
            'background-size': 'contain', # Change to contain for winter
            'background': f'{white_overlay}, url("/assets/imgs/winter_bg.png")',
        }
    # else: page_background_style remains {} (default background)

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
        season_text = f" ({effective_season})" if effective_season else ""
        summary_card_content = [html.P(f"No data found for the year {selected_year}{season_text}.")]
        # Ensure all outputs get a default value, including background
        return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store, page_background_style

    # --- Calculations & Components ---
    host_city = year_df['City'].mode()[0] if not year_df.empty and not year_df['City'].mode().empty else "N/A"
    game_season_display = effective_season if effective_season else "All Seasons"

    # Calculate base stats
    num_countries = year_df['NOC'].nunique()
    # Calculate total unique athletes
    num_athletes = year_df['Name'].nunique()
    num_sports = year_df['Sport'].nunique()
    num_events = year_df['Event'].nunique()

    # REMOVED: Gender breakdown calculation

    # Reverted Summary Card Content (4 stats)
    summary_card = dbc.Card(dbc.CardBody([
        html.H4(f"{host_city} {int(selected_year)} {game_season_display} Overview", className="card-title text-center mb-4"),
        dbc.Row([
            # Stat 1: Nations
            dbc.Col([
                html.Div("🌍", style={'fontSize': '1.5rem'}),
                html.H5(f"{num_countries}", className="mt-1 mb-0"),
                html.Small("Nations", className="text-muted")
            ], width=6, lg=3, className="text-center mb-3 mb-lg-0"), # Back to lg=3
            # Stat 2: Athletes
            dbc.Col([
                html.Div("🏃", style={'fontSize': '1.5rem'}),
                html.H5(f"{num_athletes}", className="mt-1 mb-0"),
                html.Small("Athletes", className="text-muted")
            ], width=6, lg=3, className="text-center mb-3 mb-lg-0"),
            # Stat 3: Sports
            dbc.Col([
                html.Div("🏅", style={'fontSize': '1.5rem'}),
                html.H5(f"{num_sports}", className="mt-1 mb-0"),
                html.Small("Sports", className="text-muted")
            ], width=6, lg=3, className="text-center mb-3 mb-lg-0"),
            # Stat 4: Events
            dbc.Col([
                html.Div("🏆", style={'fontSize': '1.5rem'}),
                html.H5(f"{num_events}", className="mt-1 mb-0"),
                html.Small("Events", className="text-muted")
            ], width=6, lg=3, className="text-center mb-3 mb-lg-0"),
        ], justify="center") # Center the columns in the row
    ]), color="light", className="shadow border-light h-100")
    summary_card_content = [summary_card]

    # 2. Medal Table Calculation
    medals_df = year_df[year_df['Medal'] != 'None'].copy()
    medal_table_component = None
    word_cloud_component = None # Initialize word cloud component

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

        # --- Word Cloud Generation ---
        word_cloud_image_src = None
        if WORDCLOUD_INSTALLED and not medal_table_df.empty:
            try:
                # Create frequency dictionary: {Country: Total Medals}
                medal_frequencies = medal_table_df.set_index('region')[['Total']].to_dict()['Total']

                if medal_frequencies:
                    wc = WordCloud(
                        background_color="white",
                        width=800,
                        height=400,
                        colormap='viridis', # Example colormap
                        max_words=100, # Limit number of words
                        contour_width=1,
                        contour_color='steelblue'
                    ).generate_from_frequencies(medal_frequencies)

                    # Convert to image bytes
                    img_byte_arr = io.BytesIO()
                    wc_image = wc.to_image() # Get PIL image
                    if wc_image: 
                        wc_image.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)
                        # Encode as base64
                        word_cloud_image_src = f"data:image/png;base64,{base64.b64encode(img_byte_arr.getvalue()).decode()}"
            except Exception as e:
                print(f"Error generating word cloud: {e}")
                word_cloud_image_src = None # Ensure it's None on error

        if word_cloud_image_src:
            word_cloud_component = dbc.Card([
                dbc.CardHeader(html.H5("Medal Distribution Word Cloud", className="mb-0 fw-bold")),
                dbc.CardBody(
                    html.Img(src=word_cloud_image_src, style={'width': '100%', 'height': 'auto'})
                )
            ], color="light", className="shadow border-light mt-4") # Add margin top
        # --- End Word Cloud --- 
        
        # Determine actual page size
        actual_page_size = selected_page_size

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
            dbc.CardHeader(
                 html.H5(f"Medal Table ({game_season_display})", className="mb-0 fw-bold")
            ),
            dbc.CardBody(medal_table)
        ], color="light", className="shadow border-light")

        # Set details content - Add word cloud if available
        details_content = [medal_table_component]
        if word_cloud_component:
            details_content.append(word_cloud_component)

        # Make the selectors visible
        selector_style = {'display': 'flex', 'justify-content': 'end', 'margin-top': '0.5rem'}
        search_style = {'display': 'block', 'max-width': '300px'}
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

    # Return all outputs including the updated background style
    return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store, page_background_style

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