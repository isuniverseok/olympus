# pages/country_profile.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
# Updated import to use helpers from data_loader
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value
import pandas as pd

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

    # Visualization Area with Spinner
    dbc.Spinner(
        html.Div(id='country-profile-visuals') # Content will be loaded here by callback
    ),
    
    # Hidden store to receive country from globe
    dcc.Store(id='clicked-country', data=None, storage_type='session')
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
    Output('country-profile-visuals', 'children'), # Output to the Div container
    Input('country-profile-noc-dropdown', 'value')
)
def update_country_visuals(selected_noc):
    if not selected_noc:
        raise PreventUpdate # Or return html.P("Please select a country.")

    # Get country name and flag
    country_name, country_flag = COUNTRY_MAPPING.get(selected_noc, (selected_noc, ''))

    # Filter data for the selected country
    country_df = df[df['NOC'] == selected_noc].copy()

    if country_df.empty:
        return html.Div([ # Return a list
            html.H4(f"{country_name} {country_flag} ({selected_noc})"),
            dbc.Alert(f"No data available for {country_name}.")
        ])

    # --- Calculations & Components --- 
    # Filter for medals
    medal_df = country_df[country_df['Medal'] != 'None'].copy()

    # --- FIX: Deduplicate event medals for accurate team counts ---
    if not medal_df.empty:
        unique_event_medals_country = medal_df.drop_duplicates(
            subset=['Year', 'Season', 'Event', 'Medal'] # Region/NOC not needed here
        )
    else:
        unique_event_medals_country = pd.DataFrame(columns=medal_df.columns) # Empty df if no medals
    # --- END FIX ---

    # --- Use deduplicated data for overall counts/trends --- 
    # 1. Overall Medal Counts (Using unique_event_medals_country)
    total_medals = len(unique_event_medals_country)
    medal_counts = unique_event_medals_country['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze'], fill_value=0)

    # 2. Medals Over Time (Using unique_event_medals_country)
    medals_over_time = unique_event_medals_country.groupby(['Year', 'Season'])['Medal'].count().unstack(fill_value=0).reset_index()
    fig_medals_time = go.Figure()
    if 'Summer' in medals_over_time.columns:
        fig_medals_time.add_trace(go.Scatter(x=medals_over_time['Year'], y=medals_over_time['Summer'], mode='lines+markers', name='Summer Medals'))
    if 'Winter' in medals_over_time.columns:
        fig_medals_time.add_trace(go.Scatter(x=medals_over_time['Year'], y=medals_over_time['Winter'], mode='lines+markers', name='Winter Medals'))
    fig_medals_time.update_layout(title='Medal Trend Over Time',
                                 xaxis_title='Year', yaxis_title='Medals Won',
                                 hovermode="x unified", template='plotly_white')

    # 3. Medals per Sport (Using unique_event_medals_country)
    medals_by_sport = unique_event_medals_country['Sport'].value_counts().nlargest(15).reset_index()
    medals_by_sport.columns=['Sport', 'Medal Count']
    fig_sport_medals = px.bar(medals_by_sport, x='Sport', y='Medal Count',
                              title='Top 15 Sports by Medals Won',
                              template='plotly_white')
    fig_sport_medals.update_layout(yaxis_title='Total Medals')

    # --- Use original medal_df for athlete-specific stats --- 
    # 4. Top Athletes (Using original medal_df)
    top_athletes = medal_df['Name'].value_counts().nlargest(5).reset_index()
    top_athletes.columns=['Athlete', 'Medal Count']
    athlete_list_items = [dbc.ListGroupItem(f"{row['Athlete']} ({row['Medal Count']} medals)") for index, row in top_athletes.iterrows()]

    # 5. First/Last Appearance & Medal (Using original country_df & unique_event_medals_country)
    first_appearance = country_df['Year'].min()
    last_appearance = country_df['Year'].max()
    first_medal_year = unique_event_medals_country['Year'].min() if not unique_event_medals_country.empty else "N/A"
    num_olympics = country_df['Games'].nunique()

    # --- Assemble Layout --- 
    layout_content = html.Div([
        html.H4(f"{country_name} {country_flag} ({selected_noc})"),
        html.Hr(),
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
            
            dbc.Col(width=12, md=4, className="mb-3") # Placeholder or for future use
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_medals_time), width=12, lg=6, className="mb-3"),
            dbc.Col(dcc.Graph(figure=fig_sport_medals), width=12, lg=6, className="mb-3")
        ])
    ])

    return layout_content