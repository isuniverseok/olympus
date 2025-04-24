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

    # --- Calculations --- (Mostly remain the same, operate on final filtered_df)
    medal_df = filtered_df[filtered_df['Medal'] != 'None'].copy()

    # Key Sportsperson (Overall for sport, unaffected by filters)
    key_sportsperson_info = "N/A"
    sport_overall_df = df[(df['Sport'] == selected_sport) & (df['Medal'] != 'None')]
    if not sport_overall_df.empty:
        overall_medal_counts = sport_overall_df['Name'].value_counts()
        if not overall_medal_counts.empty:
            top_athlete = overall_medal_counts.idxmax()
            top_athlete_medals = overall_medal_counts.max()
            key_sportsperson_info = f"{top_athlete} ({top_athlete_medals} medals overall)"
        else:
            key_sportsperson_info = "No overall medal winners."

    # --- Plot Definitions --- (Plots now reflect all filters)
    plot_height = 350

    # 1. Top Countries Plot (Conditional)
    top_noc_fig = go.Figure().update_layout(title="Select 'All' NOCs", title_x=0.5, height=plot_height)
    if selected_noc == DEFAULT_DROPDOWN_LABEL:
        top_nocs_filtered = medal_df['NOC'].value_counts().reset_index(name='Medal Count').head(10)
        if not top_nocs_filtered.empty:
            top_noc_fig = px.bar(top_nocs_filtered, x='NOC', y='Medal Count', title=f"Top 10 Countries by Medals")
            top_noc_fig.update_layout(xaxis_title=None, yaxis_title='Medals Won', title_x=0.5, height=plot_height)
        else:
            top_noc_fig = go.Figure().update_layout(title="No Medal Data", title_x=0.5, height=plot_height)

    # 2. Participation Plot (Conditional)
    participation_fig = go.Figure().update_layout(title="Select 'All' Years", title_x=0.5, height=plot_height)
    if selected_year == DEFAULT_DROPDOWN_LABEL:
        # Need to group by year, considering other filters
        participation_by_year = filtered_df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Unique Athletes')
        if not participation_by_year.empty:
            participation_fig = px.line(participation_by_year, x='Year', y='Unique Athletes', markers=True, title="Athlete Participation Trend")
            participation_fig.update_layout(xaxis_title='Olympic Year', yaxis_title='Unique Athletes', title_x=0.5, height=plot_height)
        else:
            participation_fig = go.Figure().update_layout(title="No Participation Data", title_x=0.5, height=plot_height)

    # 3. Medal Breakdown Plot
    medal_counts = medal_df['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze']).fillna(0)
    medal_breakdown_fig = go.Figure().update_layout(title="No Medal Data", title_x=0.5, height=plot_height)
    if not medal_counts.empty and medal_counts.sum() > 0:
        medal_breakdown_fig = px.bar(medal_counts, x=medal_counts.index, y=medal_counts.values, title="Medal Distribution",
                                   color=medal_counts.index, color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#cd7f32'}, height=plot_height)
        medal_breakdown_fig.update_layout(showlegend=False, title_x=0.5, yaxis_title="Count", xaxis_title=None)

    # 4. Gender Distribution Plot
    gender_counts = filtered_df.drop_duplicates(subset=['Name'])['Gender'].value_counts()
    gender_fig = go.Figure().update_layout(title="No Gender Data", title_x=0.5, height=plot_height)
    # Only show pie if there's more than one gender in the filtered data
    if not gender_counts.empty and len(gender_counts) > 1:
        gender_fig = px.pie(gender_counts, values=gender_counts.values, names=gender_counts.index, title="Gender Distribution", hole=0.4, height=plot_height)
        gender_fig.update_traces(textposition='outside', textinfo='percent+label')
        gender_fig.update_layout(showlegend=False, title_x=0.5, margin=dict(t=60, b=20, l=20, r=20))
    elif not gender_counts.empty:
         # If only one gender, maybe just state it?
         single_gender = gender_counts.index[0]
         gender_fig.update_layout(title=f"Only {single_gender} Athletes Selected", title_x=0.5)


    # 5. Age Distribution Plot
    age_data = filtered_df['Age'].dropna()
    age_fig = go.Figure().update_layout(title="No Age Data Available", title_x=0.5, height=plot_height)
    if not age_data.empty:
        age_fig = px.histogram(age_data, nbins=20, title="Age Distribution", height=plot_height)
        age_fig.update_layout(title_x=0.5, yaxis_title="Count", xaxis_title="Age", bargap=0.1)

    # 6. Top Athletes List
    top_athletes_list = [html.Li("No medal winners found.")]
    if not medal_df.empty:
        athlete_medals_filtered = medal_df.groupby('Name')['Medal'].count().sort_values(ascending=False).head(5)
        if not athlete_medals_filtered.empty:
            top_athletes_list = [ html.Li([f"{name}: ", html.Strong(f"{count} medal{'s' if count > 1 else ''}")], className="mb-1") for name, count in athlete_medals_filtered.items() ]

    # 7. Physical Stats Cards
    desc_stats = filtered_df[['Age', 'Height', 'Weight']].describe().loc[['mean', 'min', 'max']]
    stats_cards = []
    physical_stats_available = False
    if not desc_stats.empty:
         for col in ['Age', 'Height', 'Weight']:
            if col in desc_stats.columns and not desc_stats.loc[['mean','min','max'], col].isnull().all():
                physical_stats_available = True
                stats_cards.append(
                    dbc.Col(html.Div([html.H6(col, className="text-muted small text-uppercase fw-bold"), html.P(f"Avg: {desc_stats.loc['mean', col]:.1f}" if pd.notna(desc_stats.loc['mean', col]) else "N/A", className="mb-0 small"), html.P(f"Min: {desc_stats.loc['min', col]:.1f}" if pd.notna(desc_stats.loc['min', col]) else "N/A", className="mb-0 small"), html.P(f"Max: {desc_stats.loc['max', col]:.1f}" if pd.notna(desc_stats.loc['max', col]) else "N/A", className="mb-0 small")], className="text-center p-2 border rounded shadow-sm"), width=12, md=4, className="mb-2"))

    # 8. Key Numbers
    num_events = filtered_df['Event'].nunique()
    num_athletes = filtered_df['Name'].nunique()

    # --- Assemble Visual Layout --- (Layout structure mostly the same)
    card_common_style = {"boxShadow": "0 2px 4px 0 rgba(0,0,0,0.1)", "border": "none", "borderRadius": "8px", "height": "100%"}
    plot_card_body_style = {"padding": "0.5rem"}

    layout_content = dbc.Container([
        # Row 1: Key Metrics & Top Performers
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H5("Selection Overview", className="card-title text-primary mb-3"), html.Small(f"Filters: {filter_context_text}", className="text-muted d-block mb-3"), html.P([html.I(className="bi bi-people-fill me-2"), html.Strong(f"Athletes in Selection: {num_athletes}")], className="mb-2"), html.P([html.I(className="bi bi-diagram-3-fill me-2"), html.Strong(f"Events in Selection: {num_events}")], className="mb-3"), html.Hr(className="my-3"), html.H6("Sport's Most Decorated:", className="text-muted small text-uppercase mb-2"), html.P([html.I(className="bi bi-person-check-fill me-2"), key_sportsperson_info], className="fw-bold")]), color="light", className="h-100 shadow-sm"), width=12, md=6, lg=4, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5(f"Top 5 Medal Winners", className="card-title text-primary mb-3"), html.Small(f"In current selection.", className="text-muted d-block mb-3"), html.Ul(top_athletes_list, className="list-unstyled ps-3 mt-3")]), className="h-100", style=card_common_style), width=12, md=6, lg=4, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5("Physical Stats", className="card-title text-primary mb-3 text-center"), html.Small("Avg, min, max in selection.", className="text-muted d-block mb-3 text-center"), dbc.Row(stats_cards, justify="center", className="g-3") if physical_stats_available else dbc.Alert("No physical stats data.", color="light", className="text-center small")]), className="h-100", style=card_common_style), width=12, lg=4, className="mb-4") if physical_stats_available else None,
        ], className="mb-4 align-items-stretch"),

        # Row 2: Distributions (Medals, Gender, Age)
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H5([html.I(className="bi bi-award-fill me-2"),"Medal Distribution"], className="card-title text-primary mb-3"), html.Small("Counts in selection.", className="text-muted d-block mb-2"), dcc.Graph(figure=medal_breakdown_fig, config={'displayModeBar': False})], style=plot_card_body_style), className="h-100", style=card_common_style), width=12, lg=4, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5([html.I(className="bi bi-gender-ambiguous me-2"), "Gender Distribution"], className="card-title text-primary mb-3"), html.Small("% unique athletes in selection.", className="text-muted d-block mb-2"), dcc.Graph(figure=gender_fig, config={'displayModeBar': False})], style=plot_card_body_style), className="h-100", style=card_common_style), width=12, lg=4, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody([html.H5([html.I(className="bi bi-graph-up me-2"),"Age Distribution"], className="card-title text-primary mb-3"), html.Small("Histogram of ages in selection.", className="text-muted d-block mb-2"), dcc.Graph(figure=age_fig, config={'displayModeBar': False})], style=plot_card_body_style), className="h-100", style=card_common_style), width=12, lg=4, className="mb-4"),
        ], className="mb-4 align-items-stretch"),

        # Row 3: Conditional Time Series / Country Plots
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([html.H5([html.I(className="bi bi-flag-fill me-2"),"Country Performance"], className="card-title text-primary mb-3"), html.Small("Top 10 medal countries (Requires 'All' NOCs).", className="text-muted d-block mb-2"), dcc.Graph(figure=top_noc_fig)], style=plot_card_body_style), className="h-100", style=card_common_style), width=12, lg=6, className="mb-4") if selected_noc == DEFAULT_DROPDOWN_LABEL else None,
            dbc.Col(dbc.Card(dbc.CardBody([html.H5([html.I(className="bi bi-calendar-event-fill me-2"),"Participation Over Time"], className="card-title text-primary mb-3"), html.Small("Unique athletes trend (Requires 'All' Years).", className="text-muted d-block mb-2"), dcc.Graph(figure=participation_fig)], style=plot_card_body_style), className="h-100", style=card_common_style), width=12, lg=6, className="mb-4") if selected_year == DEFAULT_DROPDOWN_LABEL else None,
        ], className="mb-4 align-items-stretch"),

    ], fluid=True)

    # Return layout, icon, description, rules, and event dropdown state
    return layout_content, sport_icon_element, sport_desc_element, sport_rules_element, event_options, event_value, event_disabled