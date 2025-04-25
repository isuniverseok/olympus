# pages/sport_profile.py
import dash
from dash import html, dcc, callback, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np # Import numpy for NaN handling if needed
# Updated import - include more options
from data_loader import df, SPORT_OPTIONS_NO_ALL, YEAR_OPTIONS, NOC_OPTIONS, get_default_value, DEFAULT_DROPDOWN_LABEL

# --- Icon Mapping Implementation (Using Emojis) ---
SPORT_ICONS = {
    "Athletics": "🏃",
    "Swimming": "🏊",
    "Gymnastics": "🤸",
    "Cycling": "🚴",
    "Archery": "🏹",
    "Fencing": "🤺",
    "Rowing": "🚣",
    "Sailing": "⛵",
    "Shooting": "🎯",
    "Weightlifting": "🏋️",
    "Boxing": "🥊",
    "Wrestling": "🤼",
    "Judo": "🥋",
    "Taekwondo": "🥋", # Same as Judo, could find alternative if needed
    "Basketball": "🏀",
    "Football": "⚽", # Soccer
    "Volleyball": "🏐",
    "Handball": "🤾",
    "Hockey": "🏒", # Field Hockey
    "Ice Hockey": "🏒",
    "Tennis": "🎾",
    "Table Tennis": "🏓",
    "Badminton": "🏸",
    "Equestrianism": "🐎", # Equestrian Sports
    "Canoeing": "🛶",
    "Diving": "🤽", # Closest, could represent diving platform
    "Water Polo": "🤽",
    "Art Competitions": "🎨", # Placeholder
    "Skiing": "⛷️",
    "Biathlon": "⛷️", # Combine Skiing/Shooting visually
    "Bobsleigh": "🛷",
    "Luge": "🛷",
    "Skating": "⛸️",
    "Figure Skating": "⛸️",
    "Speed Skating": "⛸️",
    "Short Track Speed Skating": "⛸️",
    "Curling": "🥌",
    "Snowboarding": "🏂",
    "Baseball": "⚾",
    "Cricket": "🏏",
    "Beach Volleyball": "🏐", # Same icon as Volleyball
    "Freestyle Skiing": "⛷️", # Grouping under Skiing icon
    "Golf": "⛳",
    "Motorboating": "🚤",
    "Polo": "🐎", # Same icon as Equestrianism
    "Rugby": "🏉", # Includes Rugby Sevens
    "Ski Jumping": "⛷️", # Grouping under Skiing icon
    "Triathlon": "🏅", # Using default medal - combination hard to represent
    "Tug Of War": "🏅", # Using default medal
    "Default": "🏅" # Medal as default
}

# --- Sport Descriptions ---
SPORT_DESCRIPTIONS = {
    "Athletics": "The foundation of the Olympics, including track events (running, hurdles), field events (jumping, throwing), and road events (marathons, race walks).",
    "Swimming": "Racing through water using various strokes (freestyle, breaststroke, backstroke, butterfly) over set distances in pools or open water.",
    "Gymnastics": "Showcasing strength, flexibility, balance, and coordination through artistic routines, rhythmic performances with apparatus, and trampoline acrobatics.",
    "Cycling": "Features various competitive disciplines using bicycles, including road racing, time trials, track cycling (velodrome), mountain biking, and BMX.",
    "Archery": "Testing precision and focus, archers shoot arrows at a target from a specified distance.",
    "Fencing": "A combat sport where two competitors duel using swords (foil, épée, or sabre), aiming to score points by hitting their opponent.",
    "Rowing": "Propelling a boat (shell) on water using oars. Events vary by boat size (single, double, quad, eight) and discipline (sculling, sweep).",
    "Sailing": "Navigating boats using wind power. Events involve racing around a course, categorized by boat class.",
    "Shooting": "A test of accuracy and control using firearms (pistols, rifles) or shotguns to hit stationary or moving targets.",
    "Weightlifting": "Athletes attempt a maximum-weight single lift of a barbell loaded with weight plates in two lifts: the Snatch and the Clean & Jerk.",
    "Boxing": "A combat sport where two opponents punch each other with gloved hands, aiming to score points or achieve a knockout within rounds.",
    "Wrestling": "A combat sport involving grappling techniques like clinch fighting, throws, takedowns, joint locks, and pins. Includes Freestyle and Greco-Roman styles.",
    "Judo": "Originating in Japan, Judo involves throwing or taking down an opponent to the ground, immobilizing them, or forcing submission with joint locks/chokes.",
    "Taekwondo": "A Korean martial art characterized by its emphasis on head-height kicks, jumping/spinning kicks, and fast kicking techniques.",
    "Basketball": "A team sport where two teams aim to score points by shooting a ball through a hoop elevated high above the ground.",
    "Football": "Known as soccer in some regions, two teams attempt to score by maneuvering the ball into the opposing team's goal, primarily using their feet.",
    "Volleyball": "Two teams score points by grounding a ball on the opposing team's court. Includes indoor and beach volleyball versions.",
    "Handball": "A team sport where two teams pass a ball using their hands, trying to throw it into the opponent's goal.",
    "Hockey": "Field hockey involves two teams using sticks to maneuver a ball into the opponent's goal on a grass or turf field.",
    "Ice Hockey": "A fast-paced contact team sport played on ice, using sticks to shoot a vulcanized rubber puck into the opponent's net.",
    "Tennis": "Players use rackets to strike a ball over a net into the opponent's court. Played individually (singles) or between two teams of two (doubles).",
    "Table Tennis": "Also known as ping-pong, players use small rackets to hit a lightweight ball back and forth across a table divided by a net.",
    "Badminton": "Players use rackets to hit a shuttlecock across a net. Points are scored by landing the shuttlecock in the opponent's half.",
    "Equestrianism": "Involves horse riding disciplines, including Dressage, Eventing, and Jumping.",
    "Canoeing": "Using a canoe or kayak to navigate water. Includes sprint and slalom disciplines.",
    "Diving": "Performing acrobatic dives into water from a springboard or platform.",
    "Water Polo": "A competitive team water sport where teams try to score goals by throwing the ball into the opposing team's goal.",
    "Art Competitions": "Formerly part of the Olympics, these involved medals awarded for works of art inspired by sport.",
    "Skiing": "Encompasses disciplines like Alpine (downhill, slalom), Cross-Country (distance), Freestyle (aerials, moguls), Nordic Combined, and Ski Jumping.",
    "Biathlon": "Combines cross-country skiing with rifle shooting.",
    "Bobsleigh": "Teams make timed runs down narrow, twisting, banked ice tracks in a gravity-powered sleigh.",
    "Luge": "Riders race down an ice track feet-first on a small sled.",
    "Skating": "General term, often referring to Ice Skating disciplines.",
    "Figure Skating": "Athletes perform jumps, spins, and other intricate moves on ice skates, judged on technical skill and artistic interpretation.",
    "Speed Skating": "Competitive ice skating focused on racing over set distances.",
    "Short Track Speed Skating": "Multiple skaters race on an oval ice track.",
    "Curling": "Players slide stones on a sheet of ice towards a target area (house), sweeping the ice to influence the stone's path.",
    "Snowboarding": "Involves riding a snowboard down a snow-covered slope. Disciplines include halfpipe, slopestyle, big air, and snowboard cross.",
    "Baseball": "A bat-and-ball game played between two teams who take turns batting and fielding. Points (runs) are scored by hitting the ball and advancing around bases.",
    "Cricket": "A bat-and-ball game played between two teams of eleven players on a field at the centre of which is a 22-yard (20-metre) pitch with a wicket at each end.",
    "Beach Volleyball": "A team sport played by two teams of two players on a sand court divided by a net, similar rules to indoor volleyball.",
    "Freestyle Skiing": "Skiing discipline incorporating aerial acrobatic jumps, mogul skiing (bumps), ski cross (racing), slopestyle (tricks on obstacles), and halfpipe.",
    "Golf": "Players use clubs to hit balls into a series of holes on a course in as few strokes as possible.",
    "Motorboating": "A former Olympic sport involving racing boats powered by motors.",
    "Polo": "A team sport played on horseback where the objective is to score goals against an opposing team by driving a small ball into the goal using a long-handled mallet.",
    "Rugby": "A contact team sport originating in England. Includes variations like Rugby Union (15 players) and Rugby Sevens (7 players), played at the Olympics.",
    "Ski Jumping": "Athletes ski down a steep take-off ramp (inrun), jump from the end, and aim to fly as far as possible before landing.",
    "Triathlon": "A multi-stage competition involving the completion of three continuous and sequential endurance disciplines: swimming, cycling, and running.",
    "Tug Of War": "A sport that directly pits two teams against each other in a test of strength: teams pull on opposite ends of a rope, with the goal being to bring the rope a certain distance.",
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

# --- Constants ---
PLOTLY_TEMPLATE = "plotly_white" # Hardcode light theme template
dash.register_page(__name__, name='Sport Profile', path_template='/sport/<sport_name>')
default_sport = get_default_value(SPORT_OPTIONS_NO_ALL)
DEFAULT_EVENT_LABEL = "All Events"
DEFAULT_COUNTRY_LABEL = "All Countries"

# Extract years for RangeSlider
all_years_list = [opt['value'] for opt in YEAR_OPTIONS if isinstance(opt['value'], (int, float))]
MIN_YEAR = min(all_years_list) if all_years_list else 1896
MAX_YEAR = max(all_years_list) if all_years_list else 2016
year_marks = {year: str(year) for year in range(MIN_YEAR, MAX_YEAR + 1, (MAX_YEAR - MIN_YEAR)//6 if (MAX_YEAR - MIN_YEAR)>0 else 10) }
if MIN_YEAR not in year_marks: year_marks[MIN_YEAR] = str(MIN_YEAR)
if MAX_YEAR not in year_marks: year_marks[MAX_YEAR] = str(MAX_YEAR)

# --- Layout Definition (Light Theme Only, No Placeholder) ---
def layout(sport_name=None):
    initial_sport = sport_name if sport_name else default_sport
    container_class = "pt-3 pb-5 bg-light text-dark" # Light theme base
    card_style = {"backgroundColor": "#ffffff", "border": "1px solid #dee2e6"}
    card_header_style = {"backgroundColor": "#e9ecef", "fontWeight": "600", "borderBottom": "1px solid #dee2e6"}
    plot_card_body_style = {"padding": "0.5rem"}
    olympic_colors = ["primary", "warning", "info", "success", "danger"]

    return dbc.Container(id='sport-profile-container', className=container_class, fluid=True, children=[
        # --- Title Row (No Theme Toggle) ---
        dbc.Row([
            dbc.Col(html.H3("Sport Performance Profile", className="text-primary d-inline-block me-3"), width='auto'),
            dbc.Col(id='sport-profile-main-icon', width='auto', className="d-flex align-items-center me-auto")
            # Theme switch removed
        ], align="center", className="mb-3"),

        dbc.Alert([
            html.H5("What is this page?", className="alert-heading"),
            html.P("Explore historical Olympic data...", className="mb-0")
            # Use default Bootstrap info alert style
            ], id='info-alert', color="info", className="shadow-sm mb-4 border border-info"),

        # --- Selected Sport Header Row ---
        dbc.Row([
            dbc.Col(id='selected-sport-header', width=12) # Populated by callback
        ], id='selected-sport-banner', justify="center", align="center", className="my-4 p-3 bg-light rounded shadow"),

        dbc.Row([dbc.Col([dcc.Dropdown(id='sport-profile-sport-dropdown', options=SPORT_OPTIONS_NO_ALL, value=initial_sport, clearable=False)], width=12, lg=6)], justify="center", className="mb-4"),

        # --- Filters Card ---
        dbc.Card(id='filter-card', children=[
            dbc.CardBody([
             html.H5("Filters", className="card-title text-primary mb-3"), # Primary color title
             dbc.Row([
                 dbc.Col([html.Label("Season:", className="fw-bold small d-block mb-2"), dbc.RadioItems(id="sport-profile-season-radio", options=["All", "Summer", "Winter"], value="All", inline=True)], width=12, md="auto", className="mb-3 filter-col"),
                 dbc.Col([html.Label("Gender:", className="fw-bold small d-block mb-2"), dbc.RadioItems(options=["All", "M", "F"], value="All", id="sport-profile-gender-radio", inline=True)], width=12, md="auto", className="mb-3 filter-col"),
                 dbc.Col([html.Label("Event:", className="fw-bold small"), dcc.Dropdown(id='sport-profile-event-dropdown', options=[{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}], value=DEFAULT_EVENT_LABEL, clearable=False, disabled=True, className="shadow-sm")], width=12, md=5, className="mb-3 filter-col", id='sport-profile-event-col'),
                 dbc.Col([html.Label("Year Range:", className="fw-bold small"), dcc.RangeSlider(id='sport-profile-year-slider', min=MIN_YEAR, max=MAX_YEAR, step=None, marks=year_marks, value=[MIN_YEAR, MAX_YEAR], tooltip={"placement": "bottom", "always_visible": False}, className="mt-3")], width=12, className="mb-3 filter-col")
             ], className="g-3 align-items-center")
            ])
        # Light theme card style
        ], className="mb-4 shadow bg-light border-secondary"),

        # --- Details Card (About/Rules) ---
        dbc.Row([dbc.Col(id='sport-profile-details-card', width=12, lg=10)], justify="center", className="mb-4"),

        # --- Visuals Area ---
        dbc.Spinner(html.Div([
            dbc.Row([
                # Use explicit header IDs for callback targeting
                dbc.Col(dbc.Card(children=[dbc.CardHeader("Current Selection", id="key-metrics-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[0]}"), dbc.CardBody(id="key-metrics-content")], style=card_style, className="h-100"), width=12, lg=4, className="mb-4"),
                dbc.Col(dbc.Card(children=[dbc.CardHeader("Top Athletes by Medal Count", id="top-athletes-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[1]}"), dbc.CardBody(id="top-athletes-graph-content", style=plot_card_body_style)], style=card_style, className="h-100"), width=12, lg=8, className="mb-4"),
            ], className="align-items-stretch g-4"),
            dbc.Row([
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Medal Counts", id="medal-breakdown-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[2]}"),
                    dbc.CardBody([
                        dcc.Dropdown(id={'type': 'dynamic-medal-filter', 'index': 0}, options=[{'label': DEFAULT_COUNTRY_LABEL, 'value': DEFAULT_COUNTRY_LABEL}], value=DEFAULT_COUNTRY_LABEL, placeholder="Filter by Country...", clearable=False, className="mb-3"),
                        html.Div(id='medal-breakdown-graph-content')
                    ], style=plot_card_body_style)
                ], style=card_style, className="h-100"), width=12, lg=4, className="mb-4"),
                dbc.Col(dbc.Card(children=[dbc.CardHeader("Gender Distribution", id="gender-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[3]}"), dbc.CardBody(id="gender-graph-content", style=plot_card_body_style)], style=card_style, className="h-100"), width=12, lg=4, className="mb-4"),
                dbc.Col(dbc.Card(children=[dbc.CardHeader("Age Distribution", id="age-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[4]}"), dbc.CardBody(id="age-graph-content", style=plot_card_body_style)], style=card_style, className="h-100"), width=12, lg=4, className="mb-4"),
            ], className="align-items-stretch g-4"),
            dbc.Row([
                dbc.Col(dbc.Card(children=[dbc.CardHeader("Top Countries by Medal Count", id="top-countries-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[0]}"), dbc.CardBody(id="top-countries-graph-content", style=plot_card_body_style)], style=card_style, className="h-100"), width=12, md=6, className="mb-4"),
                dbc.Col(dbc.Card(children=[dbc.CardHeader("Medal Trends Over Time", id="medals-time-header", style=card_header_style, className=f"fw-bold text-{olympic_colors[1]}"), dbc.CardBody(id="medals-time-graph-content", style=plot_card_body_style)], style=card_style, className="h-100"), width=12, md=6, className="mb-4"),
            ], className="align-items-stretch g-4"),
        ], id='sport-profile-visuals', className="mt-4"))
    ])

# --- Callback Definition (Simplified Outputs - 15 total) ---
@callback(
     # --- Content Areas (7) ---
     Output('key-metrics-content', 'children'),           # Enhanced content
     Output('top-athletes-graph-content', 'children'),
     Output('medal-breakdown-graph-content', 'children'),
     Output('gender-graph-content', 'children'),
     Output('age-graph-content', 'children'),
     Output('top-countries-graph-content', 'children'),
     Output('medals-time-graph-content', 'children'),
     # --- Page Elements (3) ---
     Output('sport-profile-main-icon', 'children'),
     Output('selected-sport-header', 'children'),
     Output('sport-profile-details-card', 'children'),
     # --- Event Dropdown (3) ---
     Output('sport-profile-event-dropdown', 'options'),
     Output('sport-profile-event-dropdown', 'value'),
     Output('sport-profile-event-dropdown', 'disabled'),
     # --- Medal Country Filter (2) ---
     Output({'type': 'dynamic-medal-filter', 'index': 0}, 'options'),
     Output({'type': 'dynamic-medal-filter', 'index': 0}, 'value'),
     # --- Inputs (No Theme Input) ---
     Input('sport-profile-sport-dropdown', 'value'),
     Input('sport-profile-year-slider', 'value'),
     Input('sport-profile-gender-radio', 'value'),
     Input('sport-profile-event-dropdown', 'value'),
     Input('sport-profile-season-radio', 'value'),
     Input({'type': 'dynamic-medal-filter', 'index': 0}, 'value'),
     prevent_initial_call=True
)
def update_sport_visuals(selected_sport, selected_year_range, selected_gender, selected_event, selected_season, medal_country_value):
    # --- Theme Settings (Hardcoded Light) ---
    plotly_template = "plotly_white"
    text_color_class = "text-dark"
    muted_text_class = "text-muted"
    card_style = {"backgroundColor": "#ffffff", "border": "1px solid #dee2e6"}
    primary_color = "primary"
    olympic_colors = ["primary", "warning", "info", "success", "danger"]
    default_alert_color = "secondary"
    no_data_alert_class = "text-dark"

    # --- Initializations ---
    default_alert = dbc.Alert("Select filters to view data", color=default_alert_color, className="m-3")
    key_metrics_content = dbc.ListGroup([
        dbc.ListGroupItem(html.Div([html.I(className="bi bi-filter me-2"), "Filters applied: None"], className="d-flex align-items-center small"))
    ], flush=True, className="border-0") # Initial empty state
    top_athletes_content = default_alert
    medal_breakdown_content = default_alert
    gender_content = default_alert
    age_content = default_alert
    top_countries_content = default_alert
    medals_time_content = default_alert
    event_options = [{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}]
    event_value = DEFAULT_EVENT_LABEL
    event_disabled = True
    details_card_content = html.Div()
    selected_sport_header_content = None
    main_icon_emoji = SPORT_ICONS["Default"]
    medal_country_options = [{'label': DEFAULT_COUNTRY_LABEL, 'value': DEFAULT_COUNTRY_LABEL}]

    # --- Process Selected Sport ---
    if selected_sport:
         main_icon_emoji = SPORT_ICONS.get(selected_sport, SPORT_ICONS["Default"])
         sport_desc_text = SPORT_DESCRIPTIONS.get(selected_sport, "")
         sport_rules_text = SPORT_RULES.get(selected_sport, "")
         selected_sport_header_content = html.Div([
             html.Span(main_icon_emoji, style={'fontSize': '3rem', 'marginRight': '15px', "verticalAlign": "middle"}),
             html.H4(selected_sport, className=f"text-{primary_color} d-inline-block align-middle")
         ])
         # Light theme styling for details card
         details_card_content = dbc.Card([
             dbc.CardHeader(f"About {selected_sport}", className=f"fw-bold text-{olympic_colors[0]}", style={"backgroundColor": "#e9ecef", "borderBottom": "1px solid #dee2e6"}),
             dbc.CardBody([
                 html.P(sport_desc_text, className=f"card-text mb-4 {text_color_class}"),
                 html.H6("Rules Overview", className=f"text-{olympic_colors[1]}"),
                 html.P(sport_rules_text, className=f"card-text small fst-italic {muted_text_class}")
             ], className=text_color_class)
         ], style=card_style, className="shadow-sm")

    main_icon_element = html.Span(main_icon_emoji, style={'fontSize': '1.5rem', 'marginLeft': '10px', "verticalAlign": "middle"})

    # --- Create default return tuple structure (15 items) ---
    num_outputs = 15
    return_values = [None] * num_outputs
    return_values[0:7] = [key_metrics_content, top_athletes_content, medal_breakdown_content, gender_content, age_content, top_countries_content, medals_time_content]
    return_values[7:10] = [main_icon_element, selected_sport_header_content, details_card_content]
    return_values[10:13] = [event_options, event_value, event_disabled]
    return_values[13:15] = [medal_country_options, medal_country_value]

    # --- Handle No Sport Selected ---
    if not selected_sport:
        return_values[8] = None
        return_values[9] = html.Div()
        return tuple(return_values)

    # --- Event Dropdown & Data Loading Checks ---
    event_value = selected_event
    if not df.empty:
        potential_events_df = df[(df['Sport'] == selected_sport) & (df['Year'] >= selected_year_range[0]) & (df['Year'] <= selected_year_range[1])]
        if selected_season != "All": potential_events_df = potential_events_df[potential_events_df['Season'] == selected_season]
        sport_events = sorted(potential_events_df['Event'].unique()) if not potential_events_df.empty else []
        if sport_events:
            event_options = [{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}] + [{'label': ev, 'value': ev} for ev in sport_events]
            event_disabled = False
            if event_value != DEFAULT_EVENT_LABEL and event_value not in sport_events:
                event_value = DEFAULT_EVENT_LABEL # Reset if invalid
        else:
            event_options = [{'label': "No events for filters", 'value': DEFAULT_EVENT_LABEL, 'disabled': True}]
            event_value = DEFAULT_EVENT_LABEL
            event_disabled = True
    else:
        event_options = [{'label': "Data not loaded", 'value': DEFAULT_EVENT_LABEL, 'disabled': True}]
        event_value = DEFAULT_EVENT_LABEL
        event_disabled = True
        no_data_alert = dbc.Alert("Data not loaded.", color="danger", className="m-3")
        return_values[0:7] = [no_data_alert] * 7
        return_values[10:13] = [event_options, event_value, event_disabled]
        return tuple(return_values)

    # --- Try Filtering and Calculations ---
    try:
        # --- Filter Data ---
        base_df = df[(df['Sport'] == selected_sport) & (df['Year'] >= selected_year_range[0]) & (df['Year'] <= selected_year_range[1])]
        if selected_season != "All": base_df = base_df[base_df['Season'] == selected_season]
        if selected_gender != "All": base_df = base_df[base_df['Gender'] == selected_gender]
        if event_value != DEFAULT_EVENT_LABEL and not event_disabled: base_df = base_df[base_df['Event'] == event_value]
        filtered_df = base_df.copy()

        # --- Filter Context Text ---
        filters_applied = [f"Years: {selected_year_range[0]}-{selected_year_range[1]}"]
        if selected_season != "All": filters_applied.append(f"S: {selected_season}")
        if selected_gender != "All": filters_applied.append(f"G: {selected_gender}")
        if event_value != DEFAULT_EVENT_LABEL and not event_disabled: filters_applied.append(f"E: {event_value[:25] + ('...' if len(event_value)>25 else '')}")
        filter_context_text = ", ".join(filters_applied) if len(filters_applied)>1 else "All Data in Range"

        # --- Update Medal Country Filter Options ---
        medal_df = filtered_df[filtered_df['Medal'] != 'None'].copy()
        current_medal_value = medal_country_value
        if not medal_df.empty and 'NOC' in medal_df.columns:
            nocs_with_medals = sorted(medal_df['NOC'].unique())
            if nocs_with_medals:
                medal_country_options = [{'label': DEFAULT_COUNTRY_LABEL, 'value': DEFAULT_COUNTRY_LABEL}] + [{'label': noc, 'value': noc} for noc in nocs_with_medals]
                if current_medal_value != DEFAULT_COUNTRY_LABEL and current_medal_value not in nocs_with_medals:
                    current_medal_value = DEFAULT_COUNTRY_LABEL
            else:
                medal_country_options = [{'label': "No Medal Winners", 'value': DEFAULT_COUNTRY_LABEL, 'disabled': True}]
                current_medal_value = DEFAULT_COUNTRY_LABEL
        else:
            # Handle case where filtered_df might be empty but we still need default options
            medal_country_options = [{'label': "No Medal Data", 'value': DEFAULT_COUNTRY_LABEL, 'disabled': True}]
            current_medal_value = DEFAULT_COUNTRY_LABEL
        medal_country_value = current_medal_value
        return_values[13] = medal_country_options
        return_values[14] = medal_country_value

        # --- Handle No Data After Filtering ---
        if filtered_df.empty:
            no_data_alert = dbc.Alert([ html.Strong(f"No data for: {selected_sport}"), html.Br(), f"Filters: {filter_context_text}."], color="warning", className=f"{no_data_alert_class} m-3")
            return_values[0:7] = [no_data_alert] * 7
            return_values[10:13] = [event_options, event_value, event_disabled]
            return tuple(return_values)

        # --- Main Calculations & Plot Generation --- #
        plot_height = 350
        no_data_msg = dbc.Alert("No Data for Selection", color=default_alert_color, className="m-3")
        if 'region' not in medal_df.columns and 'NOC' in medal_df.columns: medal_df['region'] = medal_df['NOC']

        # --- Build Enhanced Key Metrics Content --- #
        num_athletes_count = filtered_df['Name'].nunique()
        num_events_count = filtered_df['Event'].nunique()
        mean_height = filtered_df['Height'].mean()
        min_height = filtered_df['Height'].min()
        max_height = filtered_df['Height'].max()
        mean_weight = filtered_df['Weight'].mean()
        min_weight = filtered_df['Weight'].min()
        max_weight = filtered_df['Weight'].max()

        height_stats_str = f"{min_height:.1f} / {mean_height:.1f} / {max_height:.1f} cm" if pd.notna(mean_height) else "N/A"
        weight_stats_str = f"{min_weight:.1f} / {mean_weight:.1f} / {max_weight:.1f} kg" if pd.notna(mean_weight) else "N/A"

        # Get top athletes from medal_df
        top_athletes_list_items = [dbc.ListGroupItem("N/A", className="p-1 small border-0")]
        if not medal_df.empty:
            top_athletes_names = medal_df.groupby('Name')['Medal'].count().nlargest(3).reset_index()
            if not top_athletes_names.empty:
                 top_athletes_list_items = [
                     dbc.ListGroupItem(f"{row['Name']} ({row['Medal']} medals)", className="p-1 small border-0")
                     for index, row in top_athletes_names.iterrows()
                 ]

        key_metrics_content = dbc.ListGroup([
            dbc.ListGroupItem([html.I(className="bi bi-filter me-2"), html.Strong("Filters: "), html.Span(filter_context_text, className="small")], className="d-flex align-items-center border-0"),
            dbc.ListGroupItem([html.I(className="bi bi-people-fill me-2"), html.Strong(f"Athletes in Selection: {num_athletes_count}")], className="d-flex align-items-center border-0"),
            dbc.ListGroupItem([html.I(className="bi bi-diagram-3-fill me-2"), html.Strong(f"Events in Selection: {num_events_count}")], className="d-flex align-items-center border-0"),
            dbc.ListGroupItem([html.I(className="bi bi-rulers me-2"), html.Strong("Height (Min/Avg/Max): "), html.Span(height_stats_str, className="ms-auto")], className="d-flex justify-content-between align-items-center small border-0"),
            dbc.ListGroupItem([html.I(className="bi bi-universal-access me-2"), html.Strong("Weight (Min/Avg/Max): "), html.Span(weight_stats_str, className="ms-auto")], className="d-flex justify-content-between align-items-center small border-0"),
            dbc.ListGroupItem([html.I(className="bi bi-trophy-fill me-2"), html.Strong("Most Decorated:"), dbc.ListGroup(top_athletes_list_items, flush=True, className="ms-2 border-0")], className="d-flex flex-column small border-0 pt-2")
        ], flush=True, className="border-0") # Flush to remove outer borders, border-0 for items

        # --- Plot Generation (Light Theme) --- #
        # Top Athletes
        top_athletes_content = no_data_msg
        athlete_country_col = 'NOC'
        if not medal_df.empty and 'Name' in medal_df.columns and athlete_country_col in medal_df.columns:
            top_athletes = medal_df.groupby(['Name', athlete_country_col])['Medal'].count().nlargest(10).reset_index()
            if not top_athletes.empty:
                fig_ath = px.bar(top_athletes, x='Name', y='Medal', color=athlete_country_col, title=None, labels={'Name':'Athlete', 'Medal':'Total Medals', athlete_country_col: 'Country'}, template=plotly_template, height=plot_height, hover_name='Name')
                fig_ath.update_layout(xaxis_title="", yaxis_title="Total Medals", title=None, showlegend=False, margin=dict(t=10, b=10))
                top_athletes_content = dcc.Graph(figure=fig_ath, config={'displayModeBar': False})

        # Medal Breakdown Content
        medal_breakdown_content = no_data_msg
        medal_df_for_dist = medal_df.copy()
        if medal_country_value != DEFAULT_COUNTRY_LABEL and 'NOC' in medal_df_for_dist.columns:
             medal_df_for_dist = medal_df_for_dist[medal_df_for_dist['NOC'] == medal_country_value]
        medal_counts = medal_df_for_dist['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze']).fillna(0)
        if not medal_counts.empty and medal_counts.sum() > 0:
            fig_med = px.bar(medal_counts, x=medal_counts.index, y=medal_counts.values, title=None, color=medal_counts.index, color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#cd7f32'}, height=plot_height, template=plotly_template)
            fig_med.update_layout(showlegend=False, title=None, yaxis_title="Count", xaxis_title=None, margin=dict(t=10, b=10))
            medal_breakdown_content = dcc.Graph(figure=fig_med, config={'displayModeBar': False})

        # Gender Distribution Content
        gender_content = no_data_msg
        gender_counts = filtered_df.drop_duplicates(subset=['Name'])['Gender'].value_counts()
        if selected_gender == "All" and not gender_counts.empty and len(gender_counts) > 1:
             fig_gen = px.pie(gender_counts, values=gender_counts.values, names=gender_counts.index, title=None, hole=0.4, height=plot_height, template=plotly_template)
             fig_gen.update_traces(textposition='outside', textinfo='percent+label')
             fig_gen.update_layout(showlegend=False, title=None, margin=dict(t=10, b=20, l=20, r=20))
             gender_content = dcc.Graph(figure=fig_gen, config={'displayModeBar': False})
        elif not gender_counts.empty:
             single_gender = gender_counts.index[0] if len(gender_counts) == 1 else selected_gender
             gender_content = dbc.Alert(f"Displaying only {single_gender} athletes based on filter.", color=default_alert_color, className="m-3")

        # Age Distribution Content
        age_content = no_data_msg
        age_data = filtered_df['Age'].dropna()
        if not age_data.empty:
            fig_age = px.histogram(age_data, nbins=20, title=None, height=plot_height, template=plotly_template)
            fig_age.update_layout(title=None, yaxis_title="Count", xaxis_title="Age", bargap=0.1, margin=dict(t=10, b=10))
            age_content = dcc.Graph(figure=fig_age, config={'displayModeBar': False})

        # Top Countries Content
        top_countries_content = no_data_msg
        country_col = 'region' if 'region' in medal_df.columns else 'NOC'
        if country_col in medal_df.columns and not medal_df.empty:
            top_countries_medals = medal_df.groupby(country_col)['Medal'].count().nlargest(10).reset_index()
            if not top_countries_medals.empty:
                fig_cntry = px.bar(top_countries_medals, x=country_col, y='Medal', title=None, labels={country_col:'Country', 'Medal':'Medals'}, template=plotly_template, height=plot_height, hover_name=country_col)
                fig_cntry.update_layout(xaxis_title="", yaxis_title="Total Medals", title=None, margin=dict(t=10, b=10))
                top_countries_content = dcc.Graph(figure=fig_cntry, config={'displayModeBar': False})

        # Medals Over Time Content
        medals_time_content = no_data_msg
        if not medal_df.empty and 'Year' in medal_df.columns:
             medals_over_time = medal_df.groupby('Year')['Medal'].count().reset_index()
             medals_over_time = medals_over_time[ (medals_over_time['Year'] >= selected_year_range[0]) & (medals_over_time['Year'] <= selected_year_range[1]) ]
             if not medals_over_time.empty and len(medals_over_time['Year'].unique()) > 1:
                 fig_time = px.line(medals_over_time, x='Year', y='Medal', title=None, markers=True, labels={'Year': 'Olympic Year', 'Medal': 'Total Medals'}, template=plotly_template, height=plot_height, hover_name='Year')
                 fig_time.update_layout(title=None, margin=dict(t=10, b=10))
                 medals_time_content = dcc.Graph(figure=fig_time, config={'displayModeBar': False})
             elif not medals_over_time.empty:
                 medals_time_content = dbc.Alert("Need data for multiple years to show trend.", color=default_alert_color, className="m-3")

        # --- Assign final calculated values to return tuple --- #
        return_values[0:7] = [key_metrics_content, top_athletes_content, medal_breakdown_content, gender_content, age_content, top_countries_content, medals_time_content]
        return_values[7:10] = [main_icon_element, selected_sport_header_content, details_card_content]
        return_values[10:13] = [event_options, event_value, event_disabled]
        # Medal options/value already assigned
        return tuple(return_values)

    except Exception as e:
        print(f"Error during callback execution: {e}")
        error_alert = dbc.Alert(f"An error occurred processing the data: {e}", color="danger", className="m-3")
        return_values[0:7] = [error_alert] * 7
        return tuple(return_values)