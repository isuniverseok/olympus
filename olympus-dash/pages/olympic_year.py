# pages/olympic_year.py
import dash
from dash import html, dcc, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd 
import os 

from data_loader import df, YEAR_OPTIONS_NO_ALL, get_default_value, DEFAULT_DROPDOWN_LABEL
import io
import base64
try:
    from wordcloud import WordCloud
    import matplotlib 
    from PIL import Image 
    WORDCLOUD_INSTALLED = True
except ImportError:
    WORDCLOUD_INSTALLED = False
    print("Word Cloud libraries not installed. Skipping word cloud generation.")
    class WordCloud:
        def __init__(self, **kwargs): pass
        def generate_from_frequencies(self, frequencies): return self
        def to_image(self): return None 

dash.register_page(__name__, name='Olympic Year')

# Placeholder for when image is not found or applicable
PLACEHOLDER_IMAGE = '/assets/imgs/olympic_logo.png' 
IMAGE_BASE_PATH = 'assets/imgs'


default_year = get_default_value(YEAR_OPTIONS_NO_ALL)


default_season = DEFAULT_DROPDOWN_LABEL

card_style = {
    "backgroundColor": "#ffffff",
    "border": "none",
    "borderRadius": "12px",
    "boxShadow": "0 4px 6px rgba(0,0,0,0.05)",
    "transition": "all 0.3s ease",
    "height": "100%",
    "overflow": "hidden"
}

card_hover_style = {
    "transform": "translateY(-5px)",
    "boxShadow": "0 8px 15px rgba(0,0,0,0.1)"
}

dashboard_style = {
    "width": "100%",
    "overflowX": "hidden",
    "paddingRight": "0px",
    "paddingLeft": "0px"
}

layout = html.Div([
    
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Olympic Year Analysis", 
                       className="display-3 fw-bold text-primary mb-4",
                       style={"textShadow": "2px 2px 4px rgba(255,255,255,0.8)"}),
                html.P("Explore detailed statistics and performance metrics for each Olympic year.", 
                      className="lead mb-5",
                      style={"fontSize": "1.4rem", "textShadow": "1px 1px 2px rgba(255,255,255,0.9)"})
            ], className="text-center py-4")
        ], width=12)
    ], className="mb-4"),

    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.P("Select a year and season to view comprehensive Olympic statistics, including medal tables, athlete participation, and event details.", 
                              className="lead text-muted mb-0")
                    ])
                ], style=card_style)
            ], width=12)
        ], className="mb-4"),

        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Select Year:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='olympic-year-year-dropdown',
                                    options=YEAR_OPTIONS_NO_ALL,
                                    value=default_year,
                                    clearable=False,
                                    style={
                                        'zIndex': '1000',
                                        'position': 'relative'
                                    }
                                )
                            ], width=12, md=6, lg=4, className="mb-3 mb-md-0"),

                            dbc.Col([
                                html.Label("Select Season:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id='olympic-year-season-dropdown',
                                    value=None,
                                    clearable=False,
                                    style={
                                        'zIndex': '1000',
                                        'position': 'relative'
                                    }
                                )
                            ], width=12, md=6, lg=4)
                        ], justify="center", className="g-3")
                    ], className="px-4 py-3")
                ], style={**card_style, 'zIndex': '100'}, className="mb-4")
            ], width=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Img(id='olympic-emblem-img', src=PLACEHOLDER_IMAGE, 
                                className="img-fluid", 
                                style={'max-height': '150px', 'display': 'block', 'margin': 'auto'})
                    ], className="d-flex align-items-center justify-content-center")
                ], style=card_style)
            ], width=12, md=3, className="mb-3"),
            
            dbc.Col(id='olympic-year-summary-col', width=12, md=6, className="mb-3"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Img(id='olympic-mascot-img', src=PLACEHOLDER_IMAGE, 
                                className="img-fluid", 
                                style={'max-height': '150px', 'display': 'block', 'margin': 'auto'})
                    ], className="d-flex align-items-center justify-content-center")
                ], style=card_style)
            ], width=12, md=3, className="mb-3"),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Form([
                                    dbc.RadioItems(
                                        options=[
                                            {"label": " 10 ", "value": 10},
                                            {"label": " 25 ", "value": 25},
                                            {"label": " 50 ", "value": 50},
                                        ],
                                        value=25,
                                        id="medal-table-page-size-selector",
                                        inline=True,
                                        className="bg-light p-2 rounded"
                                    ),
                                ],
                                id="page-size-selector-form-id",
                                style={'display': 'none'}
                                )
                            ], width="auto"),

                            dbc.Col([
                                dbc.Input(
                                    id="medal-table-search-input",
                                    placeholder="Search Country...",
                                    type="search",
                                    size="sm",
                                    className="border-primary"
                                ),
                            ],
                            id="medal-table-search-form",
                            style={'display': 'none', 'max-width': '300px'}
                            )
                        ], justify="between", align="center", className="mb-3"),

                        dbc.Spinner(
                            html.Div(id='olympic-year-details', 
                                   style={'maxHeight': '600px', 'overflowY': 'auto'})
                        ),
                    ], className="p-4")
                ], style=card_style)
            ], width=12)
        ]),

    ], className="px-3"),

    
    dcc.Store(id='medal-table-full-data-store'),
], id='olympic-year-page-container')


@callback(
    Output('olympic-year-season-dropdown', 'options'),
    Output('olympic-year-season-dropdown', 'value'),
    Input('olympic-year-year-dropdown', 'value')
)
def update_season_options(selected_year):
    if not selected_year or df.empty:
        return [], None 

    available_seasons = df[df['Year'] == selected_year]['Season'].unique().tolist()

    dynamic_options = []
    if 'Summer' in available_seasons:
        dynamic_options.append({'label': 'Summer', 'value': 'Summer'})
    if 'Winter' in available_seasons:
        dynamic_options.append({'label': 'Winter', 'value': 'Winter'})

    new_season_value = None
    if 'Summer' in available_seasons:
        new_season_value = 'Summer'
    elif 'Winter' in available_seasons:
        new_season_value = 'Winter' # Default to Winter if only Winter is available
    # If neither, new_season_value remains None

    return dynamic_options, new_season_value

def get_image_path(image_type, city, year):
    print(f"[Debug] get_image_path called with: type={image_type}, city={city}, year={year}") # Debug
    if not city or pd.isna(city):
        print("[Debug] City is None or NaN") 
        return PLACEHOLDER_IMAGE
    city_slug = str(city).lower().replace(' ', '-').replace('_', '-')
    city_slug = city_slug.replace('st.-moritz', 'st_moritz')
    city_slug = city_slug.replace('salt-lake-city', 'salt_lake')
    city_slug = city_slug.replace('cortina-d\'ampezzo','cortina_d_ampezzo')
    city_slug = city_slug.replace('garmisch-partenkirchen','garmisch_p')
    city_slug = city_slug.replace('squaw-valley','squaw_valley')
    print(f"[Debug] Generated city_slug: {city_slug}") 

    filename = f"{city_slug}-{year}.png"
    relative_path = f"{IMAGE_BASE_PATH}/olympic_{image_type}/{filename}"
    print(f"[Debug] Checking relative_path: {relative_path}") 

    # Check relative to the app's assumed root directory
    full_path_to_check = relative_path
    print(f"[Debug] Checking existence of: {full_path_to_check}") 
    exists = os.path.exists(full_path_to_check)
    print(f"[Debug] os.path.exists result: {exists}") 
    
    if exists:
        print(f"[Debug] Image found! Returning path with leading slash: /{relative_path}") 
        return f"/{relative_path}" 
    else:
        print(f"[Debug] Image NOT found.") 
        return PLACEHOLDER_IMAGE

@callback(
    Output('olympic-year-summary-col', 'children'),
    Output('olympic-year-details', 'children'),
    Output('olympic-emblem-img', 'src'),
    Output('olympic-mascot-img', 'src'),
    Output('page-size-selector-form-id', 'style'),
    Output('medal-table-search-form', 'style'),
    Output('medal-table-full-data-store', 'data'),
    Output('olympic-year-page-container', 'style'),  
    Input('olympic-year-year-dropdown', 'value'),
    Input('olympic-year-season-dropdown', 'value'),
    Input('medal-table-page-size-selector', 'value')
)
def update_year_visuals(selected_year, selected_season, selected_page_size):
    print(f"\n[Debug] update_year_visuals triggered: year={selected_year}, season={selected_season}, page_size={selected_page_size}")
    summary_card_content = []
    details_content = []
    emblem_src = PLACEHOLDER_IMAGE
    mascot_src = PLACEHOLDER_IMAGE
    selector_style = {'display': 'none'}
    search_style = {'display': 'none'}
    full_medal_data_for_store = []
    page_background_style = {} 

    if not selected_year or df.empty:
        summary_card_content = [html.P("Please select an Olympic year...")]
        return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store, page_background_style

    year_df_all_seasons = df[df['Year'] == selected_year]
    available_seasons = year_df_all_seasons['Season'].unique().tolist()
    effective_season = None
    city_for_image = None
    if selected_season in available_seasons:
        effective_season = selected_season
    elif not selected_season and len(available_seasons) == 1:
         effective_season = available_seasons[0]
    elif not effective_season and available_seasons: 
         effective_season = available_seasons[0] 

    overlay_opacity = 0.7
    white_overlay = f'linear-gradient(rgba(255, 255, 255, {overlay_opacity}), rgba(255, 255, 255, {overlay_opacity}))'

    base_bg_style = {
        'background-position': 'center center',
        'background-repeat': 'no-repeat',
        'background-attachment': 'fixed',
        'transition': 'background 0.5s ease'
    }

    if effective_season == 'Summer':
        page_background_style = {
            **base_bg_style,
            'background-size': 'cover', 
            'background': f'{white_overlay}, url("/assets/imgs/summer_bg.jpg")',
        }
    elif effective_season == 'Winter':
        page_background_style = {
            **base_bg_style,
            'background-size': 'contain', 
            'background': f'{white_overlay}, url("/assets/imgs/winter_bg.png")',
        }

    if effective_season:
        season_df = year_df_all_seasons[year_df_all_seasons['Season'] == effective_season]
        if not season_df.empty:
            city_for_image = season_df['City'].mode()[0] if not season_df['City'].mode().empty else None
        if city_for_image:
            emblem_src = get_image_path('emblems', city_for_image, selected_year)
            mascot_src = get_image_path('mascots', city_for_image, selected_year)

    year_df_filtered = year_df_all_seasons
    if effective_season:
        year_df_filtered = year_df_all_seasons[year_df_all_seasons['Season'] == effective_season]
    year_df = year_df_filtered

    if year_df.empty:
        season_text = f" ({effective_season})" if effective_season else ""
        summary_card_content = [html.P(f"No data found for the year {selected_year}{season_text}.")]
        return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store, page_background_style

    host_city = year_df['City'].mode()[0] if not year_df.empty and not year_df['City'].mode().empty else "N/A"
    game_season_display = effective_season if effective_season else "All Seasons"

    num_countries = year_df['NOC'].nunique()
    num_athletes = year_df['Name'].nunique()
    num_sports = year_df['Sport'].nunique()
    num_events = year_df['Event'].nunique()

  
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

    medals_df = year_df[year_df['Medal'] != 'None'].copy()
    medal_table_component = None
    word_cloud_component = None 

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

        word_cloud_image_src = None
        if WORDCLOUD_INSTALLED and not medal_table_df.empty:
            try:
                medal_frequencies = medal_table_df.set_index('region')[['Total']].to_dict()['Total']

                if medal_frequencies:
                    wc = WordCloud(
                        background_color="white",
                        width=800,
                        height=400,
                        colormap='viridis', 
                        max_words=100, 
                        contour_width=1,
                        contour_color='steelblue'
                    ).generate_from_frequencies(medal_frequencies)

                    img_byte_arr = io.BytesIO()
                    wc_image = wc.to_image()
                    if wc_image: 
                        wc_image.save(img_byte_arr, format='PNG')
                        img_byte_arr.seek(0)
                        word_cloud_image_src = f"data:image/png;base64,{base64.b64encode(img_byte_arr.getvalue()).decode()}"
            except Exception as e:
                print(f"Error generating word cloud: {e}")
                word_cloud_image_src = None 

        if word_cloud_image_src:
            word_cloud_component = dbc.Card([
                dbc.CardHeader(html.H5("Medal Distribution Word Cloud", className="mb-0 fw-bold")),
                dbc.CardBody(
                    html.Img(src=word_cloud_image_src, style={'width': '100%', 'height': 'auto'})
                )
            ], color="light", className="shadow border-light mt-4") 
        
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

        
        details_content = [medal_table_component]
        if word_cloud_component:
            details_content.append(word_cloud_component)

        selector_style = {'display': 'flex', 'justify-content': 'end', 'margin-top': '0.5rem'}
        search_style = {'display': 'block', 'max-width': '300px'}
    else:
        details_content = [dbc.Alert("No medal data available for this selection.", color="warning", className="mb-4")]
        selector_style = {'display': 'none'}
        search_style = {'display': 'none'}
        full_medal_data_for_store = [] 

    if not details_content:
        details_content = [dbc.Alert("No specific details to display for this selection.", color="info", className="mb-4")]
        selector_style = {'display': 'none'}
        search_style = {'display': 'none'}

    return summary_card_content, details_content, emblem_src, mascot_src, selector_style, search_style, full_medal_data_for_store, page_background_style

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