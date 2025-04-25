# pages/country_profile.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
# Updated import to use helpers from data_loader
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value
import pandas as pd
# NEW Import for Word Cloud
from wordcloud import WordCloud

dash.register_page(__name__, name='Country Profile')

# Country code to name and flag mapping
COUNTRY_MAPPING = {
    'AFG': ('Afghanistan', '🇦🇫'),
    'ALB': ('Albania', '🇦🇱'),
    'ALG': ('Algeria', '🇩🇿'),
    'AND': ('Andorra', '🇦🇩'),
    'ANG': ('Angola', '🇦🇴'),
    'ANT': ('Antigua and Barbuda', '🇦🇬'),
    'ARG': ('Argentina', '🇦🇷'),
    'ARM': ('Armenia', '🇦🇲'),
    'ARU': ('Aruba', '🇦🇼'),
    'ASA': ('American Samoa', '🇦🇸'),
    'AUS': ('Australia', '🇦🇺'),
    'AUT': ('Austria', '🇦🇹'),
    'AZE': ('Azerbaijan', '🇦🇿'),
    'BAH': ('Bahamas', '🇧🇸'),
    'BAN': ('Bangladesh', '🇧🇩'),
    'BAR': ('Barbados', '🇧🇧'),
    'BDI': ('Burundi', '🇧🇮'),
    'BEL': ('Belgium', '🇧🇪'),
    'BEN': ('Benin', '🇧🇯'),
    'BER': ('Bermuda', '🇧🇲'),
    'BHU': ('Bhutan', '🇧🇹'),
    'BIH': ('Bosnia and Herzegovina', '🇧🇦'),
    'BIZ': ('Belize', '🇧🇿'),
    'BLR': ('Belarus', '🇧🇾'),
    'BOL': ('Bolivia', '🇧🇴'),
    'BOT': ('Botswana', '🇧🇼'),
    'BRA': ('Brazil', '🇧🇷'),
    'BRN': ('Brunei', '🇧🇳'),
    'BRU': ('Brunei', '🇧🇳'),
    'BUL': ('Bulgaria', '🇧🇬'),
    'BUR': ('Burkina Faso', '🇧🇫'),
    'CAF': ('Central African Republic', '🇨🇫'),
    'CAM': ('Cambodia', '🇰🇭'),
    'CAN': ('Canada', '🇨🇦'),
    'CAY': ('Cayman Islands', '🇰🇾'),
    'CGO': ('Congo', '🇨🇬'),
    'CHA': ('Chad', '🇹🇩'),
    'CHI': ('Chile', '🇨🇱'),
    'CHN': ('China', '🇨🇳'),
    'CIV': ('Ivory Coast', '🇨🇮'),
    'CMR': ('Cameroon', '🇨🇲'),
    'COD': ('DR Congo', '🇨🇩'),
    'COK': ('Cook Islands', '🇨🇰'),
    'COL': ('Colombia', '🇨🇴'),
    'COM': ('Comoros', '🇰🇲'),
    'CPV': ('Cape Verde', '🇨🇻'),
    'CRC': ('Costa Rica', '🇨🇷'),
    'CRO': ('Croatia', '🇭🇷'),
    'CUB': ('Cuba', '🇨🇺'),
    'CYP': ('Cyprus', '🇨🇾'),
    'CZE': ('Czech Republic', '🇨🇿'),
    'DEN': ('Denmark', '🇩🇰'),
    'DJI': ('Djibouti', '🇩🇯'),
    'DMA': ('Dominica', '🇩🇲'),
    'DOM': ('Dominican Republic', '🇩🇴'),
    'ECU': ('Ecuador', '🇪🇨'),
    'EGY': ('Egypt', '🇪🇬'),
    'ERI': ('Eritrea', '🇪🇷'),
    'ESA': ('El Salvador', '🇸🇻'),
    'ESP': ('Spain', '🇪🇸'),
    'EST': ('Estonia', '🇪🇪'),
    'ETH': ('Ethiopia', '🇪🇹'),
    'FIJ': ('Fiji', '🇫🇯'),
    'FIN': ('Finland', '🇫🇮'),
    'FRA': ('France', '🇫🇷'),
    'FSM': ('Micronesia', '🇫🇲'),
    'GAB': ('Gabon', '🇬🇦'),
    'GAM': ('Gambia', '🇬🇲'),
    'GBR': ('Great Britain', '🇬🇧'),
    'GBS': ('Guinea-Bissau', '🇬🇼'),
    'GEO': ('Georgia', '🇬🇪'),
    'GEQ': ('Equatorial Guinea', '🇬🇶'),
    'GER': ('Germany', '🇩🇪'),
    'GHA': ('Ghana', '🇬🇭'),
    'GRE': ('Greece', '🇬🇷'),
    'GRN': ('Grenada', '🇬🇩'),
    'GUA': ('Guatemala', '🇬🇹'),
    'GUI': ('Guinea', '🇬🇳'),
    'GUM': ('Guam', '🇬🇺'),
    'GUY': ('Guyana', '🇬🇾'),
    'HAI': ('Haiti', '🇭🇹'),
    'HKG': ('Hong Kong', '🇭🇰'),
    'HON': ('Honduras', '🇭🇳'),
    'HUN': ('Hungary', '🇭🇺'),
    'INA': ('Indonesia', '🇮🇩'),
    'IND': ('India', '🇮🇳'),
    'IRI': ('Iran', '🇮🇷'),
    'IRL': ('Ireland', '🇮🇪'),
    'IRQ': ('Iraq', '🇮🇶'),
    'ISL': ('Iceland', '🇮🇸'),
    'ISR': ('Israel', '🇮🇱'),
    'ISV': ('US Virgin Islands', '🇻🇮'),
    'ITA': ('Italy', '🇮🇹'),
    'IVB': ('British Virgin Islands', '🇻🇬'),
    'JAM': ('Jamaica', '🇯🇲'),
    'JOR': ('Jordan', '🇯🇴'),
    'JPN': ('Japan', '🇯🇵'),
    'KAZ': ('Kazakhstan', '🇰🇿'),
    'KEN': ('Kenya', '🇰🇪'),
    'KGZ': ('Kyrgyzstan', '🇰🇬'),
    'KIR': ('Kiribati', '🇰🇮'),
    'KOR': ('South Korea', '🇰🇷'),
    'KOS': ('Kosovo', '🇽🇰'),
    'KSA': ('Saudi Arabia', '🇸🇦'),
    'KUW': ('Kuwait', '🇰🇼'),
    'LAO': ('Laos', '🇱🇦'),
    'LAT': ('Latvia', '🇱🇻'),
    'LBA': ('Libya', '🇱🇾'),
    'LBR': ('Liberia', '🇱🇷'),
    'LCA': ('Saint Lucia', '🇱🇨'),
    'LES': ('Lesotho', '🇱🇸'),
    'LIE': ('Liechtenstein', '🇱🇮'),
    'LTU': ('Lithuania', '🇱🇹'),
    'LUX': ('Luxembourg', '🇱🇺'),
    'MAD': ('Madagascar', '🇲🇬'),
    'MAR': ('Morocco', '🇲🇦'),
    'MAS': ('Malaysia', '🇲🇾'),
    'MAW': ('Malawi', '🇲🇼'),
    'MDA': ('Moldova', '🇲🇩'),
    'MDV': ('Maldives', '🇲🇻'),
    'MEX': ('Mexico', '🇲🇽'),
    'MHL': ('Marshall Islands', '🇲🇭'),
    'MKD': ('North Macedonia', '🇲🇰'),
    'MLI': ('Mali', '🇲🇱'),
    'MLT': ('Malta', '🇲🇹'),
    'MNG': ('Mongolia', '🇲🇳'),
    'MNE': ('Montenegro', '🇲🇪'),
    'MON': ('Monaco', '🇲🇨'),
    'MOZ': ('Mozambique', '🇲🇿'),
    'MRI': ('Mauritius', '🇲🇺'),
    'MTN': ('Mauritania', '🇲🇷'),
    'MYA': ('Myanmar', '🇲🇲'),
    'NAM': ('Namibia', '🇳🇦'),
    'NCA': ('Nicaragua', '🇳🇮'),
    'NED': ('Netherlands', '🇳🇱'),
    'NEP': ('Nepal', '🇳🇵'),
    'NGR': ('Nigeria', '🇳🇬'),
    'NIG': ('Niger', '🇳🇪'),
    'NOR': ('Norway', '🇳🇴'),
    'NRU': ('Nauru', '🇳🇷'),
    'NZL': ('New Zealand', '🇳🇿'),
    'OMA': ('Oman', '🇴🇲'),
    'PAK': ('Pakistan', '🇵🇰'),
    'PAN': ('Panama', '🇵🇦'),
    'PAR': ('Paraguay', '🇵🇾'),
    'PER': ('Peru', '🇵🇪'),
    'PHI': ('Philippines', '🇵🇭'),
    'PLE': ('Palestine', '🇵🇸'),
    'PLW': ('Palau', '🇵🇼'),
    'PNG': ('Papua New Guinea', '🇵🇬'),
    'POL': ('Poland', '🇵🇱'),
    'POR': ('Portugal', '🇵🇹'),
    'PRK': ('North Korea', '🇰🇵'),
    'PUR': ('Puerto Rico', '🇵🇷'),
    'QAT': ('Qatar', '🇶🇦'),
    'ROU': ('Romania', '🇷🇴'),
    'RSA': ('South Africa', '🇿🇦'),
    'RUS': ('Russia', '🇷🇺'),
    'RWA': ('Rwanda', '🇷🇼'),
    'SAM': ('Samoa', '🇼🇸'),
    'SEN': ('Senegal', '🇸🇳'),
    'SEY': ('Seychelles', '🇸🇨'),
    'SGP': ('Singapore', '🇸🇬'),
    'SKN': ('Saint Kitts and Nevis', '🇰🇳'),
    'SLE': ('Sierra Leone', '🇸🇱'),
    'SLO': ('Slovenia', '🇸🇮'),
    'SMR': ('San Marino', '🇸🇲'),
    'SOL': ('Solomon Islands', '🇸🇧'),
    'SOM': ('Somalia', '🇸🇴'),
    'SRB': ('Serbia', '🇷🇸'),
    'SRI': ('Sri Lanka', '🇱🇰'),
    'SSD': ('South Sudan', '🇸🇸'),
    'STP': ('São Tomé and Príncipe', '🇸🇹'),
    'SUD': ('Sudan', '🇸🇩'),
    'SUI': ('Switzerland', '🇨🇭'),
    'SUR': ('Suriname', '🇸🇷'),
    'SVK': ('Slovakia', '🇸🇰'),
    'SWE': ('Sweden', '🇸🇪'),
    'SWZ': ('Eswatini', '🇸🇿'),
    'SYR': ('Syria', '🇸🇾'),
    'TAN': ('Tanzania', '🇹🇿'),
    'TGA': ('Tonga', '🇹🇴'),
    'THA': ('Thailand', '🇹🇭'),
    'TJK': ('Tajikistan', '🇹🇯'),
    'TKM': ('Turkmenistan', '🇹🇲'),
    'TLS': ('Timor-Leste', '🇹🇱'),
    'TOG': ('Togo', '🇹🇬'),
    'TPE': ('Chinese Taipei', '🇹🇼'),
    'TTO': ('Trinidad and Tobago', '🇹🇹'),
    'TUN': ('Tunisia', '🇹🇳'),
    'TUR': ('Turkey', '🇹🇷'),
    'TUV': ('Tuvalu', '🇹🇻'),
    'UAE': ('United Arab Emirates', '🇦🇪'),
    'UGA': ('Uganda', '🇺🇬'),
    'UKR': ('Ukraine', '🇺🇦'),
    'URU': ('Uruguay', '🇺🇾'),
    'USA': ('United States', '🇺🇸'),
    'UZB': ('Uzbekistan', '🇺🇿'),
    'VAN': ('Vanuatu', '🇻🇺'),
    'VEN': ('Venezuela', '🇻🇪'),
    'VIE': ('Vietnam', '🇻🇳'),
    'VIN': ('Saint Vincent and the Grenadines', '🇻🇨'),
    'YEM': ('Yemen', '🇾🇪'),
    'ZAM': ('Zambia', '🇿🇲'),
    'ZIM': ('Zimbabwe', '🇿🇼')
}

# Function to get country display name for dropdown
def get_country_display(noc):
    if noc in COUNTRY_MAPPING:
        name, flag = COUNTRY_MAPPING[noc]
        return f"{name} - {noc} {flag}"
    return noc

# Create custom dropdown options with country name, NOC, and flag
custom_options = [
    {'label': get_country_display(opt['value']), 'value': opt['value']}
    for opt in NOC_OPTIONS_NO_ALL
]

# Use helper to get default value safely
default_noc = get_default_value(NOC_OPTIONS_NO_ALL)

layout = dbc.Container([
    html.H3("Country Performance Profile"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label("Select Country:", className="fw-bold"),
            dcc.Dropdown(
                id='country-profile-noc-dropdown',
                options=custom_options,
                value=default_noc,
                clearable=False,
            )
        ], width=12, md=6, lg=4)
    ]),
    html.Hr(),
    dbc.Spinner(html.Div(id='country-profile-visuals')),
    dcc.Store(id='clicked-country', data=None, storage_type='session'),
    dcc.Input(id='top-n-sports-input', value=10, type='number', style={'display': 'none'})
])

# Callback to update dropdown when country is selected from globe
@callback(
    Output('country-profile-noc-dropdown', 'value'),
    Input('clicked-country', 'data'),
    prevent_initial_call=True
)
def update_dropdown_from_globe(country):
    if country is None or country not in [opt['value'] for opt in NOC_OPTIONS_NO_ALL]:
        print(f"Invalid country code: {country}")  # Debug print
        raise PreventUpdate
    print(f"Updating dropdown to: {country}")  # Debug print
    return country

# Combined Callback for ALL country profile outputs
@callback(
    Output('country-profile-visuals', 'children'),
    Input('country-profile-noc-dropdown', 'value'),
    Input('top-n-sports-input', 'value')
)
def update_country_visuals(selected_noc, n_sports):
    if not selected_noc:
        raise PreventUpdate

    # Validate n_sports input
    try:
        n = int(n_sports)
        if not (3 <= n <= 30): # Use same min/max as input component
            n = 10 # Fallback to default if out of range
    except (ValueError, TypeError):
        n = 10 # Fallback to default if invalid input

    country_name, country_flag = COUNTRY_MAPPING.get(selected_noc, (selected_noc, ''))
    country_df = df[df['NOC'] == selected_noc].copy()

    if country_df.empty:
        # Return minimal layout if no medals ever won
        first_appearance = country_df['Year'].min()
        last_appearance = country_df['Year'].max()
        num_olympics = country_df['Games'].nunique()
        layout_no_medals = html.Div([
            html.H4(f"{country_name} {country_flag} ({selected_noc})"),
            html.Hr(),
            dbc.Alert("This country has not won any medals.", color="info"),
            dbc.Row([dbc.Col(dbc.Card(dbc.CardBody([
                html.H5("Participation Summary", className="card-title"),
                html.P(f"Participated in {num_olympics} Olympics ({first_appearance} - {last_appearance})"),
            ])))])
        ])
        return layout_no_medals # Exit early if no medals

    # --- Calculations & Components ---
    medal_df = country_df[country_df['Medal'] != 'None'].copy()

    unique_event_medals_country = pd.DataFrame() # Initialize empty
    if not medal_df.empty:
        unique_event_medals_country = medal_df.drop_duplicates(
            subset=['Year', 'Season', 'Event', 'Medal']
        )
    # Note: We proceed even if unique_event_medals_country is empty, 
    # as the country might have participated without winning medals.

    # --- Medal & Participation Calculations --- 

    # 1. Overall Medal Counts
    total_medals = len(unique_event_medals_country)
    medal_counts = unique_event_medals_country['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze'], fill_value=0) if not unique_event_medals_country.empty else pd.Series(0, index=['Gold', 'Silver', 'Bronze'])

    # 2. Stacked Bar Chart - Medals Type Over Time
    fig_medals_type_time = go.Figure() # Default empty figure
    if not unique_event_medals_country.empty:
        medals_type_time = unique_event_medals_country.groupby(['Year', 'Medal']).size().reset_index(name='Count')
        medals_type_time['Medal'] = pd.Categorical(medals_type_time['Medal'], categories=["Bronze", "Silver", "Gold"], ordered=True)
        fig_medals_type_time = px.bar(medals_type_time, x='Year', y='Count', color='Medal',
                                        title='Medal Types Won Over Time',
                                        labels={'Count': 'Medals Won'},
                                        color_discrete_map={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'},
                                        template='plotly_white')
        fig_medals_type_time.update_layout(xaxis_title='Year', yaxis_title='Medals Won')
    else:
         fig_medals_type_time.update_layout(title="Medal Types Won Over Time", template='plotly_white', annotations=[dict(text="No Medals Won", showarrow=False)])

    # 3. Calculate Top N Sports Data (for Table)
    sport_table = dbc.Alert("No medal data for table.", color="info")
    medals_by_sport_all = pd.Series(dtype=float)
    if not unique_event_medals_country.empty:
        medals_by_sport_all = unique_event_medals_country['Sport'].value_counts()
        top_n_sports = medals_by_sport_all.nlargest(n)
        if not top_n_sports.empty:
            top_n_df = top_n_sports.reset_index()
            top_n_df.columns = ['Sport', 'Medal Count']
            sport_table = dbc.Table.from_dataframe(top_n_df, striped=True, bordered=True, hover=True, responsive=True, className="table-sm")

    # 4. NEW: Athlete Participation by Gender Over Time
    participation_gender_time = country_df.drop_duplicates(subset=['Year', 'Name']).groupby(['Year', 'Gender']).size().reset_index(name='Participants')
    fig_participation_gender = px.line(participation_gender_time, x='Year', y='Participants', color='Gender',
                                        title='Athlete Participation by Gender Over Time',
                                        labels={'Participants': 'Number of Athletes'},
                                        markers=True,
                                        template='plotly_white')
    fig_participation_gender.update_layout(xaxis_title='Year', yaxis_title='Number of Athletes')

    # 5. NEW: Medal Efficiency Over Time
    # Calculate unique athletes per year
    athletes_per_year = country_df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Athletes')
    # Calculate unique medals per year
    medals_per_year = unique_event_medals_country.groupby('Year').size().reset_index(name='Medals') if not unique_event_medals_country.empty else pd.DataFrame({'Year': [], 'Medals': []})
    # Merge and calculate efficiency
    efficiency_df = pd.merge(athletes_per_year, medals_per_year, on='Year', how='left').fillna(0)
    efficiency_df['Efficiency'] = efficiency_df.apply(lambda row: row['Medals'] / row['Athletes'] if row['Athletes'] > 0 else 0, axis=1)

    fig_medal_efficiency = px.line(efficiency_df, x='Year', y='Efficiency',
                                     title='Medal Efficiency Over Time (Medals per Athlete)',
                                     labels={'Efficiency': 'Medals per Athlete'},
                                     markers=True,
                                     template='plotly_white')
    fig_medal_efficiency.update_layout(xaxis_title='Year', yaxis_title='Medals per Athlete', yaxis_tickformat='.2f') # Format y-axis ticks

    # 6. Word Cloud for Top 20 Sports (calculation remains)
    fig_sport_wordcloud = go.Figure()
    if not medals_by_sport_all.empty:
        top_20_sports_dict = medals_by_sport_all.nlargest(20).to_dict()
        if top_20_sports_dict:
            wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis').generate_from_frequencies(top_20_sports_dict)
            fig_sport_wordcloud = px.imshow(wc.to_array(), title="Top Sports Word Cloud") # Title removed from figure, added to card header
            fig_sport_wordcloud.update_layout(
                # title_x=0.5, # Removed title
                xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0) # Remove margin around plot
            )
            fig_sport_wordcloud.update_xaxes(visible=False)
            fig_sport_wordcloud.update_yaxes(visible=False)
        else:
             fig_sport_wordcloud.update_layout(template='plotly_white', annotations=[dict(text="Not enough data for word cloud", showarrow=False)])
    else:
         fig_sport_wordcloud.update_layout(template='plotly_white', annotations=[dict(text="No Medals Won", showarrow=False)])

    # --- Athlete & Participation Calculations (Continued) ---
    # 7. Top Athletes (Using original medal_df if medals exist)
    athlete_list_items = [dbc.ListGroupItem("No medal winners")]
    if not medal_df.empty:
        top_athletes = medal_df['Name'].value_counts().nlargest(5).reset_index()
        top_athletes.columns=['Athlete', 'Medal Count']
        if not top_athletes.empty:
             athlete_list_items = [dbc.ListGroupItem(f"{row['Athlete']} ({row['Medal Count']} medals)") for index, row in top_athletes.iterrows()]

    # 8. First/Last Appearance & Medal
    first_appearance = country_df['Year'].min()
    last_appearance = country_df['Year'].max()
    first_medal_year = unique_event_medals_country['Year'].min() if not unique_event_medals_country.empty else "N/A"
    num_olympics = country_df['Games'].nunique()

    # --- Assemble Layout --- 
    layout_content = html.Div([
        html.H4(f"{country_name} {country_flag} ({selected_noc})"),
        html.Hr(),
        # Row 1: Info Cards
        dbc.Row([
             dbc.Col(dbc.Card(dbc.CardBody([
                html.H5("Overall Performance", className="card-title"),
                html.P(f"Total Unique Medals: {total_medals}"),
                dbc.Row([
                    dbc.Col(f"🥇 Gold: {medal_counts.get('Gold', 0)}"),
                    dbc.Col(f"🥈 Silver: {medal_counts.get('Silver', 0)}"),
                    dbc.Col(f"🥉 Bronze: {medal_counts.get('Bronze', 0)}")
                ], className="mb-2"),
                html.P(f"Participated in {num_olympics} Olympics ({first_appearance} - {last_appearance})"),
                html.P(f"First Medal Won: {first_medal_year}"),
            ])), width=12, md=4, className="mb-3"),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H5("Top Athletes (Most Medals)", className="card-title"),
                dbc.ListGroup(athlete_list_items, flush=True)
            ])), width=12, md=4, className="mb-3"),
            dbc.Col(width=12, md=4, className="mb-3") # Placeholder
        ]),
        # Row 2: Stacked Medals Chart (Full Width)
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_medals_type_time), width=12) # Changed width to 12
            # Removed column for bar chart
        ], className="mb-3"),
        # Row 3: Participation and Efficiency (same)
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_participation_gender), width=12, lg=6, className="mb-3"),
            dbc.Col(dcc.Graph(figure=fig_medal_efficiency), width=12, lg=6, className="mb-3")
        ]),
        # Row 4: Top N Sports Table and Word Cloud
        dbc.Row([
            # Column 1: Top N Sports Table with Input Control
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(f"Top {n} Sports by Medals"),
                    dbc.CardBody([
                        # --- Visible Input Control ---
                        dbc.Row([
                            dbc.Col(html.Label("Show Top:", className="fw-bold"), width="auto"),
                            dbc.Col(
                                dcc.Input(
                                    id='top-n-sports-input', # Same ID
                                    type='number', value=n, min=3, max=30, step=1,
                                    style={'width': '80px'}, debounce=True
                                ),
                                width="auto"
                            )
                        ], className="mb-3 align-items-center"),
                        sport_table
                    ])
                ]),
                width=12, lg=6, className="mb-3 mb-lg-0"
            ),
            # Column 2: Word Cloud (same)
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Top Sports Word Cloud (Max 20)"),
                    dbc.CardBody(dcc.Graph(figure=fig_sport_wordcloud, config={'displayModeBar': False}))
                ]),
                width=12, lg=6
            )
        ], className="mt-3")
    ])

    return layout_content