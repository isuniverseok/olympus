# pages/sport_profile.py
import dash
from dash import html, dcc, callback, Input, Output, State, MATCH, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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
    "Cycling": "Competitive racing using bicycles across disciplines like road racing, time trials, track cycling (velodrome), mountain biking, and BMX.",
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

        # --- Sport Description Area (Moved Here) ---
        dbc.Row([
            dbc.Col(id='sport-profile-description', width=12, lg=8) # Description Card will go here
        ], justify="center", className="mb-4"),

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
        ], className="align-items-stretch"),

        # --- Rules Area --- (Description removed from here)
        dbc.Row([
             dbc.Col(id='sport-profile-rules', width=12, lg=8) # Rules Card remains here
        ], justify="center", className="mb-4"),

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
     Input('sport-profile-season-radio', 'value')
)
def update_sport_visuals(selected_sport, selected_year, selected_noc, selected_gender, selected_event, selected_season):

    # --- Initializations ---
    event_options = [{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}]
    event_value = DEFAULT_EVENT_LABEL
    event_disabled = True
    layout_content = html.Div()

    # Get Icon (Emoji), Description, Rules
    icon_emoji = SPORT_ICONS.get(selected_sport, SPORT_ICONS["Default"]) 
    # Changed: Use html.Span for emoji, adjust styling as needed
    sport_icon_element = html.Span(icon_emoji, style={'fontSize': '2rem', 'marginLeft': '10px', "verticalAlign": "middle"})
    
    sport_desc_text = SPORT_DESCRIPTIONS.get(selected_sport, SPORT_DESCRIPTIONS["Default"])
    sport_desc_element = dbc.Card([dbc.CardHeader(f"About {selected_sport if selected_sport else 'the Sport'}", className="fw-bold"), dbc.CardBody(html.P(sport_desc_text, className="card-text"))], color="light", outline=True, className="shadow-sm h-100")
    
    sport_rules_text = SPORT_RULES.get(selected_sport, SPORT_RULES["Default"])
    sport_rules_element = dbc.Card([dbc.CardHeader("Rules Overview", className="fw-bold"), dbc.CardBody(html.P(sport_rules_text, className="card-text small"))], color="light", outline=True, className="shadow-sm h-100")

    # --- Handle No Sport Selected ---
    if not selected_sport:
        # Display default icon/desc/rules even if no sport selected yet
        return layout_content, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled

    # --- Update Event Dropdown based on Selected Sport & Season ---
    potential_events_df = df[df['Sport'] == selected_sport]
    if selected_season != "All":
        potential_events_df = potential_events_df[potential_events_df['Season'] == selected_season]

    if selected_sport and not potential_events_df.empty:
        sport_events = sorted(potential_events_df['Event'].unique())
        if sport_events:
            event_options = [{'label': DEFAULT_EVENT_LABEL, 'value': DEFAULT_EVENT_LABEL}] + [{'label': event, 'value': event} for event in sport_events]
            event_disabled = False
            # Ensure selected event is reset if it becomes invalid
            if selected_event not in sport_events and selected_event != DEFAULT_EVENT_LABEL:
                 event_value = DEFAULT_EVENT_LABEL 
            else:
                 event_value = selected_event
        else: 
             event_options = [{'label': "No events for this season", 'value': DEFAULT_EVENT_LABEL, 'disabled': True}]
             event_value = DEFAULT_EVENT_LABEL
             event_disabled = True

    if df.empty:
         no_data_alert = dbc.Alert("Data not loaded.", color="danger")
         return no_data_alert, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled

    # --- Filter data ---
    base_df = df[df['Sport'] == selected_sport]
    filter_title_parts = [selected_sport]
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
        if len(event_options) > 2: 
            filter_title_parts.append(f"- {selected_event}")

    filtered_df = base_df.copy()
    filter_title = " ".join(filter_title_parts)
    filters_applied = []
    if selected_season != "All": filters_applied.append(f"Season: {selected_season}")
    if selected_year != DEFAULT_DROPDOWN_LABEL: filters_applied.append(f"Year: {selected_year}")
    if selected_noc != DEFAULT_DROPDOWN_LABEL: filters_applied.append(f"NOC: {selected_noc}")
    if selected_gender != "All": filters_applied.append(f"Gender: {selected_gender}")
    if selected_event != DEFAULT_EVENT_LABEL and not event_disabled: filters_applied.append(f"Event: {selected_event}")
    filter_context_text = ", ".join(filters_applied) if filters_applied else "All data for sport"

    if filtered_df.empty:
         no_data_alert = dbc.Alert([
             html.Strong(f"No data found for: {selected_sport}"), html.Br(),
             f"with filters: {filter_context_text}. Try adjusting filters."
             ], color="warning")
         return no_data_alert, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled

    # --- Calculations ---
    medal_df = filtered_df[filtered_df['Medal'] != 'None'].copy()
    if not medal_df.empty:
        unique_event_medals_sport = medal_df.drop_duplicates(
             subset=['Year', 'Season', 'Event', 'Medal', 'region'])
    else:
        unique_event_medals_sport = pd.DataFrame(columns=medal_df.columns)

    # Top countries
    if not unique_event_medals_sport.empty:
        top_countries_medals = unique_event_medals_sport.groupby('region')['Medal'].count().nlargest(10).reset_index()
        fig_top_countries = px.bar(top_countries_medals, x='region', y='Medal', title=f"Top 10 Countries ({filter_title})", labels={'region':'Country', 'Medal':'Total Medals'}, template='plotly_white')
        fig_top_countries.update_layout(xaxis_title="", yaxis_title="Total Medals")
        top_countries_card = dbc.Card([dbc.CardHeader("Top Countries by Medal Count"), dbc.CardBody(dcc.Graph(figure=fig_top_countries))])
    else:
        top_countries_card = dbc.Alert("No medal data for Top Countries chart.", color="info")

    # Medals over time
    if not unique_event_medals_sport.empty:
        medals_over_time = unique_event_medals_sport.groupby('Year')['Medal'].count().reset_index()
        fig_medals_time = px.line(medals_over_time, x='Year', y='Medal', title=f"Medals Over Time ({filter_title})", markers=True, labels={'Year': 'Olympic Year', 'Medal': 'Total Medals'}, template='plotly_white')
        medals_time_card = dbc.Card([dbc.CardHeader("Medal Trends Over Time"), dbc.CardBody(dcc.Graph(figure=fig_medals_time))])
    else:
        medals_time_card = dbc.Alert("No medal data for Trends Over Time chart.", color="info")

    # Top athletes
    if not medal_df.empty:
        top_athletes = medal_df.groupby(['Name', 'NOC'])['Medal'].count().nlargest(10).reset_index()
        fig_top_athletes = px.bar(top_athletes, x='Name', y='Medal', color='NOC', title=f"Top 10 Athletes ({filter_title})", labels={'Name':'Athlete', 'Medal':'Total Medals', 'NOC': 'Country'}, template='plotly_white')
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

    return layout_content, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled