# pages/country_profile.py
import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback, ClientsideFunction
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

# Modern card style with hover effects
card_style = {
    "backgroundColor": "#ffffff",
    "border": "1px solid #e0e0e0",
    "borderRadius": "10px",
    "boxShadow": "0 2px 4px rgba(0,0,0,0.05)",
    "transition": "all 0.3s ease",
    "height": "100%"
}

card_hover_style = {
    "transform": "translateY(-5px)",
    "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
}

# Layout with modern design
layout = dbc.Container([
    # Hero Section with Country Selection
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Country Performance Profile", className="display-4 text-primary mb-4"),
                html.P("Explore detailed Olympic performance metrics and statistics for countries across the globe.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),
    
    # Unified Country Selection and Header Section
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    # Country Selection
                    html.Div([
                        html.H5("Select Country", className="text-primary mb-3"),
            dcc.Dropdown(
                id='country-profile-noc-dropdown',
                options=custom_options,
                value=default_noc,
                clearable=False,
                            className="modern-dropdown mb-4"
                        ),
                    ], className="country-selector text-center"),
                    
                    # Country Info (only shown after selection)
                    html.Div(id='country-header-section', className="country-info text-center")
                ])
            ], className="country-card")
        ], width=12, lg=8, className="mx-auto")
    ], className="mb-5"),
    
    # Main Content Area with Spinner
    dbc.Spinner(
        html.Div(id='country-profile-visuals'),
        color="primary",
        type="grow",
        fullscreen=False,
        spinner_style={"width": "3rem", "height": "3rem"}
    ),
    
    # Hidden Stores
    dcc.Store(id='clicked-country', data=None, storage_type='session'),
    dcc.Input(id='top-n-sports-input', value=10, type='number', style={'display': 'none'})
], fluid=True, className="px-4 py-3")

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

# Update the main callback to trigger animation reset
@callback(
    [Output('country-profile-visuals', 'children'),
     Output('country-header-section', 'children'),
     Output('country-profile-visuals', 'className')],  # Add className output
    [Input('country-profile-noc-dropdown', 'value'),
     Input('top-n-sports-input', 'value')]
)
def update_country_visuals(selected_noc, n_sports):
    if not selected_noc:
        return (
            dbc.Alert("Please select a country.", color="info", className="m-3"),
            None,
            "trigger-animation"
        )

    try:
        # Filter data for selected country
        country_df = df[df['NOC'] == selected_noc].copy()
        if country_df.empty:
            return (
                dbc.Alert(f"No data found for {selected_noc}.", color="warning", className="m-3"),
                None,
                "trigger-animation"
            )

        # Create header content
        header_content = html.Div([
            html.H3(f"Country Profile: {selected_noc}", className="text-primary"),
            html.P(f"Analyzing Olympic performance from {country_df['Year'].min()} to {country_df['Year'].max()}", 
                  className="text-muted")
        ])

        # Handle case where country has no medals
        if country_df[country_df['Medal'] != 'None'].empty:
            first_appearance = country_df['Year'].min()
            last_appearance = country_df['Year'].max()
            num_olympics = country_df['Games'].nunique()
            layout_no_medals = html.Div([
                # No Medals Alert with modern styling
                dbc.Row([
                    dbc.Col([
                        dbc.Alert([
                            html.H4("No Medals Won", className="alert-heading"),
                            html.P("This country has participated in the Olympics but has not won any medals yet.", className="mb-0")
                        ], color="info", className="shadow-sm")
                    ], width=12, className="mb-4")
                ]),
                
                # Participation Summary Card
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Participation Summary", className="card-title text-primary"),
                                html.Div([
                                    html.P([
                                        html.I(className="bi bi-calendar-event me-2"),
                                        f"Participated in {num_olympics} Olympics"
                                    ], className="mb-2"),
                                    html.P([
                                        html.I(className="bi bi-clock-history me-2"),
                                        f"First Appearance: {first_appearance}"
                                    ], className="mb-2"),
                                    html.P([
                                        html.I(className="bi bi-clock me-2"),
                                        f"Last Appearance: {last_appearance}"
                                    ])
                                ])
                            ])
                        ], className="performance-card animate-slide")
                    ], width=12)
                ])
            ])
            return layout_no_medals, header_content, "trigger-animation"

        # --- Calculations & Components --- 
        medal_df = country_df[country_df['Medal'] != 'None'].copy()

        unique_event_medals_country = pd.DataFrame()
        if not medal_df.empty:
            unique_event_medals_country = medal_df.drop_duplicates(
                    subset=['Year', 'Season', 'Event', 'Medal']
            )

        # --- Medal & Participation Calculations --- 
        total_medals = len(unique_event_medals_country)
        medal_counts = unique_event_medals_country['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze'], fill_value=0) if not unique_event_medals_country.empty else pd.Series(0, index=['Gold', 'Silver', 'Bronze'])

        # --- Create Modern Layout ---
        layout_content = html.Div([
            # Overall Performance Cards
            dbc.Row([
                # Total Medals Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Total Medals", className="card-title text-primary"),
                            html.H2(f"{total_medals}", className="display-4 text-center mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.Span("🥇", className="h3"),
                                        html.H4(f"{medal_counts.get('Gold', 0)}", className="mb-0")
                                    ], className="text-center")
                                ], width=4),
                                dbc.Col([
                                    html.Div([
                                        html.Span("🥈", className="h3"),
                                        html.H4(f"{medal_counts.get('Silver', 0)}", className="mb-0")
                                    ], className="text-center")
                                ], width=4),
                                dbc.Col([
                                    html.Div([
                                        html.Span("🥉", className="h3"),
                                        html.H4(f"{medal_counts.get('Bronze', 0)}", className="mb-0")
                                    ], className="text-center")
                                ], width=4)
                            ])
                        ])
                    ], className="performance-card animate-slide", style=card_style)
                ], width=12, md=4, className="mb-4"),
                
                # Participation Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Olympic Participation", className="card-title text-primary"),
                            html.Div([
                                html.P([
                                    html.I(className="bi bi-calendar-event me-2"),
                                    f"Participated in {country_df['Games'].nunique()} Olympics"
                                ], className="mb-2"),
                                html.P([
                                    html.I(className="bi bi-clock-history me-2"),
                                    f"First Appearance: {country_df['Year'].min()}"
                                ], className="mb-2"),
                                html.P([
                                    html.I(className="bi bi-trophy me-2"),
                                    f"First Medal: {unique_event_medals_country['Year'].min() if not unique_event_medals_country.empty else 'N/A'}"
                                ])
                            ])
                        ])
                    ], className="performance-card animate-slide", style=card_style)
                ], width=12, md=4, className="mb-4"),
                
                # Top Athletes Card
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Top Athletes", className="card-title text-primary"),
                            dbc.ListGroup([
                                dbc.ListGroupItem(f"{row['Athlete']} ({row['Medal Count']} medals)", className="border-0")
                                for index, row in medal_df['Name'].value_counts().nlargest(5).reset_index().rename(columns={'Name': 'Athlete', 'count': 'Medal Count'}).iterrows()
                            ], flush=True)
                        ])
                    ], className="performance-card animate-slide", style=card_style)
                ], width=12, md=4, className="mb-4")
            ]),
            
            # Charts Section
            dbc.Row([
                # Medals Over Time Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Medal Types Won Over Time", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=px.bar(
                                    unique_event_medals_country.groupby(['Year', 'Medal']).size().reset_index(name='Count'),
                                    x='Year',
                                    y='Count',
                                    color='Medal',
                                    title=None,
                                    color_discrete_map={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'},
                                    template='plotly_white'
                                ).update_layout(
                                    xaxis_title='Year',
                                    yaxis_title='Medals Won',
                                    showlegend=True,
                                    legend_title='Medal Type'
                                ),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card animate-slide", style=card_style)
                ], width=12, className="mb-4")
            ]),
            
            # Participation and Efficiency Charts
        dbc.Row([
                # Gender Participation Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Athlete Participation by Gender", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=px.line(
                                    country_df.drop_duplicates(subset=['Year', 'Name']).groupby(['Year', 'Gender']).size().reset_index(name='Participants'),
                                    x='Year',
                                    y='Participants',
                                    color='Gender',
                                    markers=True,
                                    template='plotly_white'
                                ).update_layout(
                                    xaxis_title='Year',
                                    yaxis_title='Number of Athletes',
                                    showlegend=True,
                                    legend_title='Gender'
                                ),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card animate-slide", style=card_style)
                ], width=12, md=6, className="mb-4"),
                
                # Medal Efficiency Chart
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Medal Efficiency Over Time", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=px.line(
                                    pd.merge(
                                        country_df.drop_duplicates(subset=['Year', 'Name']).groupby('Year').size().reset_index(name='Athletes'),
                                        unique_event_medals_country.groupby('Year').size().reset_index(name='Medals'),
                                        on='Year',
                                        how='left'
                                    ).fillna(0).assign(
                                        Efficiency=lambda x: x['Medals'] / x['Athletes']
                                    ),
                                    x='Year',
                                    y='Efficiency',
                                    markers=True,
                                    template='plotly_white'
                                ).update_layout(
                                    xaxis_title='Year',
                                    yaxis_title='Medals per Athlete',
                                    yaxis_tickformat='.2f'
                                ),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="chart-card animate-slide", style=card_style)
                ], width=12, md=6, className="mb-4")
            ]),
            
            # Sports Analysis Section
        dbc.Row([
                # Top Sports Table
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.H5(f"Top {n_sports} Sports by Medals", className="d-inline-block mb-0"),
                                dcc.Input(
                                    id='top-n-sports-input',
                                    type='number',
                                    value=n_sports,
                                    min=3,
                                    max=30,
                                    step=1,
                                    style={'width': '80px', 'marginLeft': '10px'},
                                    debounce=True
                                )
                            ], className="d-flex align-items-center")
                        ], className="bg-primary text-white"),
                        dbc.CardBody([
                            dbc.Table.from_dataframe(
                                unique_event_medals_country['Sport'].value_counts().nlargest(n_sports).reset_index().rename(columns={'Sport': 'Sport', 'count': 'Medal Count'}),
                                striped=True,
                                bordered=True,
                                hover=True,
                                responsive=True,
                                className="table-sm"
                            )
                        ])
                    ], className="analysis-card animate-slide", style=card_style)
                ], width=12, lg=6, className="mb-4"),
                
                # Sports Word Cloud
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Top Sports Word Cloud", className="bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(
                                figure=px.imshow(
                                    WordCloud(
                                        width=800,
                                        height=400,
                                        background_color='white',
                                        colormap='viridis'
                                    ).generate_from_frequencies(
                                        unique_event_medals_country['Sport'].value_counts().nlargest(20).to_dict()
                                    ).to_array(),
                                    title=None
                                ).update_layout(
                                    xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                                    yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                                    plot_bgcolor='rgba(0,0,0,0)',
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    margin=dict(l=0, r=0, t=0, b=0)
                                ),
                                config={'displayModeBar': False}
                            )
                        ])
                    ], className="analysis-card animate-slide", style=card_style)
                ], width=12, lg=6, className="mb-4")
            ])
        ])

        return layout_content, header_content, "trigger-animation"

    except Exception as e:
        print(f"Error in country profile callback: {str(e)}")
        return (
            dbc.Alert(f"An error occurred while processing the data: {str(e)}", color="danger", className="m-3"),
            None,
            "trigger-animation"
        )