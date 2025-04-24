# pages/country_profile.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
# Updated import to use helpers from data_loader
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value

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
    if not selected_noc or df.empty:
        return html.P("Please select a country from the dropdown or wait for data to load.")

    # Filter data for the selected country
    country_df = df[df['NOC'] == selected_noc].copy()
    if country_df.empty:
        return html.P(f"No data found for {selected_noc}.")

    # --- Calculations ---
    # 1. Medals over Time
    medals_df = country_df[country_df['Medal'] != 'None']
    medals_time = medals_df.groupby(['Year', 'Medal']).size().unstack(fill_value=0).reset_index()

    # 2. Gender over Time
    gender_time = country_df.drop_duplicates(subset=['Year', 'Name', 'Gender'])\
                          .groupby(['Year', 'Gender']).size().unstack(fill_value=0).reset_index()

    # 3. Top Sports
    top_sports = medals_df['Sport'].value_counts().reset_index(name='Medal Count').head(10)

    # 4. Age Distribution
    age_data = country_df['Age'].dropna()

    # --- Generate Figures ---
    # Figure 1: Medals
    if not medals_time.empty:
        medal_columns = ['Gold', 'Silver', 'Bronze']
        for medal in medal_columns:
             if medal not in medals_time.columns: medals_time[medal] = 0 # Ensure columns exist
        medals_fig = px.bar(medals_time, x='Year', y=medal_columns,
                          title=f"Medals Won by {selected_noc} Over Time",
                          labels={'value': 'Medals', 'variable': 'Medal'},
                          color_discrete_map={'Gold': 'gold', 'Silver': 'silver', 'Bronze': '#cd7f32'})
        medals_fig.update_layout(xaxis_title='Year', yaxis_title='Number of Medals', legend_title_text='Medal', barmode='stack')
    else:
        medals_fig = go.Figure().update_layout(title=f"No Medal Data for {selected_noc}")

    # Figure 2: Gender
    if not gender_time.empty:
        gender_columns = ['M', 'F']
        for gender in gender_columns:
            if gender not in gender_time.columns: gender_time[gender] = 0 # Ensure M/F exist
        gender_fig = px.line(gender_time, x='Year', y=gender_columns,
                           title=f"Athlete Participation by Gender ({selected_noc})",
                           labels={'value': 'Athletes', 'variable': 'Gender'},
                           color_discrete_map={'M': 'royalblue', 'F': 'lightcoral'}, markers=True)
        gender_fig.update_layout(xaxis_title='Year', yaxis_title='Number of Unique Athletes', legend_title_text='Gender')
    else:
        gender_fig = go.Figure().update_layout(title=f"No Gender Data for {selected_noc}")


    # Figure 3: Top Sports
    if not top_sports.empty:
        sports_fig = px.bar(top_sports, x='Medal Count', y='Sport', orientation='h',
                           title=f"Top 10 Medal-Winning Sports ({selected_noc})")
        sports_fig.update_layout(xaxis_title='Total Medals Won', yaxis_title='Sport', yaxis={'categoryorder':'total ascending'})
    else:
         sports_fig = go.Figure().update_layout(title=f"No Medal Data (Top Sports) for {selected_noc}")


    # Figure 4: Age Distribution
    if not age_data.empty:
        age_fig = px.histogram(age_data, nbins=20, title=f"Age Distribution of Athletes ({selected_noc})")
        age_fig.update_layout(xaxis_title='Age', yaxis_title='Number of Athletes')
    else:
        age_fig = go.Figure().update_layout(title=f"No Age Data for {selected_noc}")

    # --- Assemble Layout for Output Div ---
    layout_content = dbc.Row([
        dbc.Col(dcc.Graph(figure=medals_fig), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(figure=gender_fig), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(figure=sports_fig), width=12, lg=6, className="mb-4"),
        dbc.Col(dcc.Graph(figure=age_fig), width=12, lg=6, className="mb-4"),
        # Add more charts or summary cards here in new Cols
    ])

    return layout_content