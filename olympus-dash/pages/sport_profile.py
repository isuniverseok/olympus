# pages/sport_profile.py
import dash
from dash import html, dcc, callback, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
# Updated import - include more options
from data_loader import df, SPORT_OPTIONS_NO_ALL, YEAR_OPTIONS, NOC_OPTIONS, get_default_value, DEFAULT_DROPDOWN_LABEL

# --- Icon Mapping Implementation (using Image URLs - REPLACE WITH REAL URLs FROM Icons8) ---
# You need to browse icons8.com/icons/set/olympic-sports and get the actual image link for each sport.
SPORT_ICONS = {
    "Athletics": "https://img.icons8.com/?size=50&id=10861&format=png", # Example URL for Athletics/Running
    "Swimming": "https://img.icons8.com/?size=50&id=12043&format=png", # Example URL for Swimming
    "Weightlifting": "https://img.icons8.com/?size=50&id=11953&format=png", # Example URL for Weightlifting
    "Gymnastics": "https://img.icons8.com/?size=50&id=11931&format=png", # Example URL for Gymnastics
    "Cycling": "https://img.icons8.com/?size=50&id=11886&format=png", # Example URL for Cycling
    "Archery": "https://img.icons8.com/?size=50&id=11879&format=png", # Example URL for Archery
    "Fencing": "https://img.icons8.com/?size=50&id=11927&format=png", # Example URL for Fencing
    "Rowing": "https://img.icons8.com/?size=50&id=11951&format=png", # Example URL for Rowing
    "Sailing": "https://img.icons8.com/?size=50&id=11948&format=png", # Example URL for Sailing
    "Shooting": "https://img.icons8.com/?size=50&id=11955&format=png", # Example URL for Shooting
    "Skiing": "https://img.icons8.com/?size=50&id=11946&format=png",
    "Ice Hockey": "https://img.icons8.com/?size=50&id=11926&format=png",
    "Default": "https://img.icons8.com/?size=50&id=85659&format=png" # Example for fallback/Olympic rings
}

# --- Sport Descriptions Placeholder ---
# TODO: Add brief, engaging descriptions for each sport.
SPORT_DESCRIPTIONS = {
    "Athletics": "Encompassing a variety of competitive running, jumping, throwing, and walking events, Athletics is a cornerstone of the Olympic Games.",
    "Swimming": "Competitive swimming involves navigating water using specific strokes. Events vary by distance, stroke type, and include individual and relay races.",
    "Weightlifting": "A test of strength where athletes attempt to lift the maximum possible weight on a barbell in two distinct movements: the snatch and the clean and jerk.",
    "Gymnastics": "Requires a combination of balance, strength, flexibility, agility, coordination, and endurance, showcased through artistic routines, rhythmic performances, or trampoline events.",
    "Cycling": "Features various competitive disciplines using bicycles, including road racing, track cycling, mountain biking, and BMX.",
    "Skiing": "Covers a variety of disciplines where athletes use skis to travel over snow, including Alpine, Cross-Country, Freestyle, and Ski Jumping.",
    "Ice Hockey": "A fast-paced team sport played on ice, where skaters use sticks to shoot a vulcanized rubber puck into their opponent's net.",
    "Default": "Explore detailed statistics, trends, and notable achievements for various Olympic sports."
}

# --- Sport Rules Placeholder ---
# TODO: Add *very brief* rule summaries or key aspects for each sport.
SPORT_RULES = {
    "Athletics": "Events include various track races (sprints, middle/long distance, hurdles, relays), field events (jumps like long jump, high jump; throws like shot put, discus, javelin), and combined events (decathlon, heptathlon).",
    "Swimming": "Races are contested using specific strokes (freestyle, backstroke, breaststroke, butterfly) over set distances in a pool. Starts, turns, and finishes must adhere to stroke-specific rules.",
    "Weightlifting": "Athletes compete in two lifts: the Snatch (barbell lifted from floor to overhead in one movement) and the Clean and Jerk (barbell lifted to shoulders, then overhead). Each athlete gets three attempts per lift.",
    "Gymnastics": "Artistic Gymnastics involves routines on apparatus like floor, vault, bars, beam. Rhythmic Gymnastics uses hoops, balls, clubs, ribbons. Trampoline involves acrobatic skills.",
    "Cycling": "Track Cycling has various sprint/endurance races in a velodrome. Road Cycling includes road races and time trials. Mountain Biking and BMX involve off-road courses/tracks.",
    "Skiing": "Disciplines vary widely. Alpine involves timed downhill runs through gates. Cross-Country focuses on endurance over long distances. Freestyle includes aerials, moguls, and slopestyle. Ski Jumping aims for the longest jump.",
    "Ice Hockey": "Teams of six players (including a goalie) try to score by shooting a puck into the opponent's net. Games consist of three periods. Penalties result in temporary player suspensions.",
    "Default": "Rules vary significantly depending on the selected sport and specific event."
}

dash.register_page(__name__, name='Sport Profile', path_template='/sport/<sport_name>') # Add path template if desired

# Use helper
default_sport = get_default_value(SPORT_OPTIONS_NO_ALL)
DEFAULT_EVENT_LABEL = "All Events" # Constant for the 'All Events' option

# --- Layout Definition ---
def layout(sport_name=None):
    initial_sport = sport_name if sport_name else default_sport

    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H3("Sport Performance Profile", className="text-primary"), width='auto'),
            # Icon column - styling adjusted
            dbc.Col(id='sport-profile-icon', width='auto', className="d-flex align-items-center")
        ], align="center", className="mb-3"),

        # --- What is Sport Profiling Explanation ---
        dbc.Alert([
            html.H5("What is this page?", className="alert-heading"),
            html.P("Explore historical Olympic data for a specific sport. Use the filters to refine your view by year, country, event, season, and gender.", className="mb-0")
            ], color="info", className="shadow-sm"),

        # --- Sport Selection ---
        dbc.Row([
             dbc.Col([
                html.Label("Select Sport:", className="fw-bold mb-1"),
                dcc.Dropdown(
                    id='sport-profile-sport-dropdown',
                    options=SPORT_OPTIONS_NO_ALL,
                    value=initial_sport,
                    clearable=False,
                    placeholder="Select a Sport...",
                    className="mb-3 shadow-sm"
                )
            ], width=12, lg=6)
        ], justify="center", className="my-4"), # Added vertical margin

        # --- Filters Row --- Includes Season, Event, Gender
         dbc.Row([
             # Season Filter
             dbc.Col([
                 html.Label("Season:", className="fw-bold small text-muted d-block mb-2"),
                 dbc.RadioItems(
                    options=[
                        {"label": "All", "value": "All"},
                        {"label": "Summer", "value": "Summer"},
                        {"label": "Winter", "value": "Winter"},
                    ],
                    value="All", # Default value
                    id="sport-profile-season-radio",
                    inline=True,
                    className="shadow-sm p-2 rounded bg-light me-3", # Added margin
                 )
             ], width=12, md="auto", className="mb-3 d-flex flex-column justify-content-center"), # Auto width
             # Year Filter
            dbc.Col([
                html.Label("Year:", className="fw-bold small text-muted"),
                dcc.Dropdown(id='sport-profile-year-dropdown', options=YEAR_OPTIONS, value=DEFAULT_DROPDOWN_LABEL, clearable=False, className="shadow-sm")
            ], width=12, sm=4, md=2, className="mb-3"),
            # NOC Filter
            dbc.Col([
                html.Label("Country (NOC):", className="fw-bold small text-muted"),
                dcc.Dropdown(id='sport-profile-noc-dropdown', options=NOC_OPTIONS, value=DEFAULT_DROPDOWN_LABEL, clearable=False, className="shadow-sm")
            ], width=12, sm=4, md=3, className="mb-3"),
             # Event Filter
             dbc.Col([
                 html.Label("Event:", className="fw-bold small text-muted"),
                 dcc.Dropdown(id='sport-profile-event-dropdown', options=[{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}], value=DEFAULT_EVENT_LABEL, clearable=False, disabled=True, className="shadow-sm")
             ], width=12, sm=4, md=3, className="mb-3", id='sport-profile-event-col'),
             # Gender Filter
            dbc.Col([
                 html.Label("Gender:", className="fw-bold small text-muted d-block mb-2"),
                 dbc.RadioItems(options=["All", "M", "F"], value="All", id="sport-profile-gender-radio", inline=True, className="shadow-sm p-2 rounded bg-light")
                 # Simpler options definition if labels match values
            ], width=12, md="auto", className="mb-3 d-flex flex-column justify-content-center")
        ], className="mb-4 align-items-end g-2"), # Use g-2 for gutters

        # --- Sport Description & Rules Area ---
        dbc.Row([
             dbc.Col(id='sport-profile-description', width=12, lg=6, className="mb-4"),
             dbc.Col(id='sport-profile-rules', width=12, lg=6, className="mb-4")
        ], className="align-items-stretch"),

        # --- Visuals Area ---
        dbc.Spinner(
            html.Div(id='sport-profile-visuals')
        )
    ], fluid=True, className="pt-3 pb-5") # Add bottom padding

# --- Callback Definition ---
@callback(
     Output('sport-profile-visuals', 'children'),
     Output('sport-profile-icon', 'children'),
     Output('sport-profile-description', 'children'),
     Output('sport-profile-rules', 'children'),
     Output('sport-profile-event-dropdown', 'options'),
     Output('sport-profile-event-dropdown', 'value'),
     Output('sport-profile-event-dropdown', 'disabled'),
     Input('sport-profile-sport-dropdown', 'value'),
     Input('sport-profile-year-dropdown', 'value'),
     Input('sport-profile-noc-dropdown', 'value'),
     Input('sport-profile-gender-radio', 'value'),
     Input('sport-profile-event-dropdown', 'value'),
     Input('sport-profile-season-radio', 'value') # Add Season input
)
def update_sport_visuals(selected_sport, selected_year, selected_noc, selected_gender, selected_event, selected_season):

    # --- Initializations ---
    event_options = [{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}]
    event_value = DEFAULT_EVENT_LABEL
    event_disabled = True
    layout_content = html.Div()

    # Get Icon, Description, Rules
    icon_url = SPORT_ICONS.get(selected_sport, SPORT_ICONS["Default"])
    sport_icon_element = html.Img(src=icon_url, height="35px", className="ms-2", style={"verticalAlign": "middle"})
    sport_desc_text = SPORT_DESCRIPTIONS.get(selected_sport, SPORT_DESCRIPTIONS["Default"])
    sport_desc_element = dbc.Card([dbc.CardHeader(f"About {selected_sport if selected_sport else 'the Sport'}", className="fw-bold"), dbc.CardBody(html.P(sport_desc_text, className="card-text"))], color="light", outline=True, className="shadow-sm h-100")
    sport_rules_text = SPORT_RULES.get(selected_sport, SPORT_RULES["Default"])
    sport_rules_element = dbc.Card([dbc.CardHeader("Rules Overview", className="fw-bold"), dbc.CardBody(html.P(sport_rules_text, className="card-text small"))], color="light", outline=True, className="shadow-sm h-100")

    # --- Handle No Sport Selected ---
    if not selected_sport:
        return layout_content, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled

    # --- Update Event Dropdown based on Selected Sport & Season ---
    # Events depend on both sport and potentially season
    potential_events_df = df[df['Sport'] == selected_sport]
    if selected_season != "All":
        potential_events_df = potential_events_df[potential_events_df['Season'] == selected_season]

    if selected_sport and not potential_events_df.empty:
        sport_events = sorted(potential_events_df['Event'].unique())
        if sport_events:
            event_options = [{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}] + [{'label': event, 'value': event} for event in sport_events]
            event_disabled = False
            if selected_event not in sport_events and selected_event != DEFAULT_EVENT_LABEL:
                 event_value = DEFAULT_EVENT_LABEL
            else:
                 event_value = selected_event
        else: # Sport selected, but no events found (maybe due to season filter)
             event_options = [{'label': "No events found for this season", 'value': DEFAULT_EVENT_LABEL, 'disabled': True}]
             event_value = DEFAULT_EVENT_LABEL
             event_disabled = True

    # --- Handle No Data Loaded ---
    if df.empty:
         no_data_alert = dbc.Alert("Data not loaded.", color="danger")
         return no_data_alert, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled

    # --- Filter data (Includes Season, Gender, Event) ---
    base_df = df[df['Sport'] == selected_sport]
    filter_title_parts = [selected_sport]

    # Apply filters sequentially
    if selected_season != "All":
        base_df = base_df[base_df['Season'] == selected_season]
        filter_title_parts.append(f"({selected_season})")
    if selected_year != DEFAULT_DROPDOWN_LABEL:
        base_df = base_df[base_df['Year'] == selected_year]
        filter_title_parts.append(f"in {selected_year}")
    if selected_noc != DEFAULT_DROPDOWN_LABEL:
        base_df = base_df[base_df['NOC'] == selected_noc]
        filter_title_parts.append(f"for {selected_noc}")
    if selected_gender != "All":
        base_df = base_df[base_df['Gender'] == selected_gender]
    if selected_event != DEFAULT_EVENT_LABEL and not event_disabled:
        base_df = base_df[base_df['Event'] == selected_event]
        # Only add event to title if it's specific (more than 1 possible event)
        if len(event_options) > 2: # More than just 'All Events' and 'No events found'
            filter_title_parts.append(f"- {selected_event}")

    filtered_df = base_df.copy() # Final filtered df
    filter_title = " ".join(filter_title_parts)
    # Create a more readable filter context string
    filters_applied = []
    if selected_season != "All": filters_applied.append(f"Season: {selected_season}")
    if selected_year != DEFAULT_DROPDOWN_LABEL: filters_applied.append(f"Year: {selected_year}")
    if selected_noc != DEFAULT_DROPDOWN_LABEL: filters_applied.append(f"NOC: {selected_noc}")
    if selected_gender != "All": filters_applied.append(f"Gender: {selected_gender}")
    if selected_event != DEFAULT_EVENT_LABEL and not event_disabled: filters_applied.append(f"Event: {selected_event}")
    filter_context_text = ", ".join(filters_applied) if filters_applied else "All data for sport"

    # --- Handle No Data After Filtering ---
    if filtered_df.empty:
         no_data_alert = dbc.Alert([
             html.Strong(f"No data found for: {selected_sport}"),
             html.Br(),
             f"with filters: {filter_context_text}. Try adjusting filters."
             ], color="warning")
         return no_data_alert, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled

    # --- Calculations --- (Operate on final filtered_df)
    medal_df = filtered_df[filtered_df['Medal'] != 'None'].copy()

    # --- FIX: Deduplicate event medals per region for accurate team counts ---
    if not medal_df.empty:
        unique_event_medals_sport = medal_df.drop_duplicates(
             subset=['Year', 'Season', 'Event', 'Medal', 'region'] # Use region here as well
        )
    else:
        unique_event_medals_sport = pd.DataFrame(columns=medal_df.columns) # Empty df if no medals
    # --- END FIX ---

    # Now use 'unique_event_medals_sport' for medal-related calculations
    # Example: Top medal-winning countries for this sport/filter
    if not unique_event_medals_sport.empty:
        top_countries_medals = unique_event_medals_sport.groupby('region')['Medal'].count().nlargest(10).reset_index()
        fig_top_countries = px.bar(top_countries_medals,
                                     x='region',
                                     y='Medal',
                                     title=f"Top 10 Countries by Medals ({filter_title})",
                                     labels={'region':'Country', 'Medal':'Total Medals'},
                                     template='plotly_white')
        fig_top_countries.update_layout(xaxis_title="", yaxis_title="Total Medals")
        top_countries_card = dbc.Card([dbc.CardHeader("Top Countries by Medal Count"), dbc.CardBody(dcc.Graph(figure=fig_top_countries))])
    else:
        top_countries_card = dbc.Alert("No medal data for Top Countries chart.", color="info")

    # Example: Medal distribution over time for this sport/filter
    if not unique_event_medals_sport.empty:
        medals_over_time = unique_event_medals_sport.groupby('Year')['Medal'].count().reset_index()
        fig_medals_time = px.line(medals_over_time, x='Year', y='Medal', title=f"Medals Over Time ({filter_title})", markers=True,
                                  labels={'Year': 'Olympic Year', 'Medal': 'Total Medals'},
                                  template='plotly_white')
        medals_time_card = dbc.Card([dbc.CardHeader("Medal Trends Over Time"), dbc.CardBody(dcc.Graph(figure=fig_medals_time))])
    else:
        medals_time_card = dbc.Alert("No medal data for Trends Over Time chart.", color="info")

    # Example: Top athletes by medals for this sport/filter
    # IMPORTANT: For athlete ranking, we SHOULD use the original medal_df (before deduplication)
    if not medal_df.empty:
        top_athletes = medal_df.groupby(['Name', 'NOC'])['Medal'].count().nlargest(10).reset_index()
        fig_top_athletes = px.bar(top_athletes,
                                  x='Name',
                                  y='Medal',
                                  color='NOC',
                                  title=f"Top 10 Athletes by Medals ({filter_title})",
                                  labels={'Name':'Athlete', 'Medal':'Total Medals', 'NOC': 'Country'},
                                  template='plotly_white')
        fig_top_athletes.update_layout(xaxis_title="", yaxis_title="Total Medals")
        top_athletes_card = dbc.Card([dbc.CardHeader("Top Athletes by Medal Count"), dbc.CardBody(dcc.Graph(figure=fig_top_athletes))])
    else:
        top_athletes_card = dbc.Alert("No medal data for Top Athletes chart.", color="info")


    # --- Assemble Final Layout ---
    layout_content = dbc.Row([
         dbc.Col([top_countries_card], width=12, md=6, className="mb-4"),
         dbc.Col([medals_time_card], width=12, md=6, className="mb-4"),
         dbc.Col([top_athletes_card], width=12, className="mb-4"),
    ])

    # Return all outputs
    return layout_content, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled