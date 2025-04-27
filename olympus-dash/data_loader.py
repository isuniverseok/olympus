# data_loader.py
import pandas as pd
import os
from functools import lru_cache

# File paths
ATHLETE_EVENTS_FILENAME = 'athlete_events.csv'
NOC_REGIONS_FILENAME = 'noc_regions.csv'
DEFAULT_DROPDOWN_LABEL = "All"

@lru_cache()
def load_data():
    """Loads and processes Olympic data."""
    if not os.path.exists(ATHLETE_EVENTS_FILENAME):
        print(f"ERROR: Data file '{ATHLETE_EVENTS_FILENAME}' not found.")
        return pd.DataFrame(), {}
    if not os.path.exists(NOC_REGIONS_FILENAME):
        print(f"ERROR: Data file '{NOC_REGIONS_FILENAME}' not found.")
        return pd.DataFrame(), {}

    try:
        # Load data
        df = pd.read_csv(ATHLETE_EVENTS_FILENAME)
        noc_regions = pd.read_csv(NOC_REGIONS_FILENAME)
        
        # Merge datasets
        noc_map = noc_regions[['NOC', 'region']]
        df = df.merge(noc_map, on='NOC', how='left')
        df['region'] = df['region'].fillna('Unknown')

        # Clean data
        df.rename(columns={'Sex': 'Gender'}, inplace=True)
        df['Medal'] = df['Medal'].fillna('None')
        for col in ['Age', 'Height', 'Weight']:
            df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        df.dropna(subset=['Year'], inplace=True)

        # Create filter options
        years = sorted(df['Year'].dropna().unique().astype(int), reverse=True)
        sports = sorted(df['Sport'].dropna().unique().tolist())
        nocs = sorted(df['NOC'].dropna().unique().tolist())
        regions = sorted(df['region'].dropna().unique().tolist())

        filter_options = {
            'years': years,
            'sports': sports,
            'nocs': nocs,
            'regions': regions
        }

        return df, filter_options
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame(), {}

# Load data
df, FILTER_OPTIONS = load_data()

def create_dropdown_options(items_list, include_all=True, all_label=DEFAULT_DROPDOWN_LABEL):
    """Creates dropdown options."""
    if not isinstance(items_list, list):
        items_list = []

    options = [{'label': str(item), 'value': item} for item in items_list]
    if include_all:
        if not any(opt['value'] == all_label for opt in options):
             options.insert(0, {'label': all_label, 'value': all_label})
    return options

# Country flag emojis
NOC_TO_FLAG_EMOJI = {
    'AFG': '🇦🇫', 'ALB': '🇦🇱', 'ALG': '🇩🇿', 'AND': '🇦🇩', 'ANG': '🇦🇴', 
    'ANT': '🇦🇬', 'ARG': '🇦🇷', 'ARM': '🇦🇲', 'ARU': '🇦🇼', 'ASA': '🇦🇸', 
    'AUS': '🇦🇺', 'AUT': '🇦🇹', 'AZE': '🇦🇿', 'BAH': '🇧🇸', 'BAN': '🇧🇩', 
    'BAR': '🇧🇧', 'BDI': '🇧🇮', 'BEL': '🇧🇪', 'BEN': '🇧🇯', 'BER': '🇧🇲', 
    'BHU': '🇧🇹', 'BIH': '🇧🇦', 'BIZ': '🇧🇿', 'BLR': '🇧🇾', 'BOL': '🇧🇴', 
    'BOT': '🇧🇼', 'BRA': '🇧🇷', 'BRN': '🇧🇳', 'BRU': '🇧🇮', 'BUL': '🇧🇬', 
    'BUR': '🇧🇫', 'CAF': '🇨🇫', 'CAM': '🇰🇭', 'CAN': '🇨🇦', 'CAY': '🇰🇾', 
    'CGO': '🇨🇩', 'CHA': '🇹🇩', 'CHI': '🇨🇱', 'CHN': '🇨🇳', 'CIV': '🇨🇮', 
    'CMR': '🇨🇲', 'COD': '🇨🇩', 'COK': '🇨🇰', 'COL': '🇨🇴', 'COM': '🇰🇲', 
    'CPV': '🇨🇻', 'CRC': '🇨🇷', 'CRO': '🇭🇷', 'CUB': '🇨🇺', 'CYP': '🇨🇾', 
    'CZE': '🇨🇿', 'DEN': '🇩🇰', 'DJI': '🇩🇯', 'DMA': '🇩🇲', 'DOM': '🇩🇴', 
    'ECU': '🇪🇨', 'EGY': '🇪🇬', 'ERI': '🇪🇷', 'ESA': '🇸🇻', 'ESP': '🇪🇸', 
    'EST': '🇪🇪', 'ETH': '🇪🇹', 'FIJ': '🇫🇯', 'FIN': '🇫🇮', 'FRA': '🇫🇷', 
    'FSM': '🇫🇲', 'GAB': '🇬🇦', 'GAM': '🇬🇲', 'GBR': '🇬🇧', 'GBS': '🇬🇼', 
    'GEO': '🇬🇪', 'GEQ': '🇬🇶', 'GER': '🇩🇪', 'GHA': '🇬🇭', 'GRE': '🇬🇷', 
    'GRN': '🇬🇩', 'GUA': '🇬🇹', 'GUI': '🇬🇳', 'GUM': '🇬🇺', 'GUY': '🇬🇾', 
    'HAI': '🇭🇹', 'HKG': '🇭🇰', 'HON': '🇭🇳', 'HUN': '🇭🇺', 'INA': '🇮🇩', 
    'IND': '🇮🇳', 'IRI': '🇮🇷', 'IRL': '🇮🇪', 'IRQ': '🇮🇶', 'ISL': '🇮🇸', 
    'ISR': '🇮🇱', 'ISV': '🇻🇮', 'ITA': '🇮🇹', 'IVB': '🇻🇬', 'JAM': '🇯🇲', 
    'JOR': '🇯🇴', 'JPN': '🇯🇵', 'KAZ': '🇰🇿', 'KEN': '🇰🇪', 'KGZ': '🇰🇬', 
    'KIR': '🇰🇮', 'KOR': '🇰🇷', 'KOS': '🇽🇰', 'KSA': '🇸🇦', 'KUW': '🇰🇼', 
    'LAO': '🇱🇦', 'LAT': '🇱🇻', 'LBA': '🇱🇾', 'LBN': '🇱🇧', 'LBR': '🇱🇷', 
    'LCA': '🇱🇨', 'LES': '🇱🇸', 'LIE': '🇱🇮', 'LTU': '🇱🇹', 'LUX': '🇱🇺', 
    'MAD': '🇲🇬', 'MAR': '🇲🇦', 'MAS': '🇲🇾', 'MAW': '🇲🇼', 'MDA': '🇲🇩', 
    'MDV': '🇲🇻', 'MEX': '🇲🇽', 'MGL': '🇲🇳', 'MHL': '🇲🇭', 'MKD': '🇲🇰', 
    'MLI': '🇲🇱', 'MLT': '🇲🇹', 'MNE': '🇲🇪', 'MON': '🇲🇨', 'MOZ': '🇲🇿', 
    'MRI': '🇲🇺', 'MTN': '🇲🇷', 'MYA': '🇲🇲', 'NAM': '🇳🇦', 'NCA': '🇳🇮', 
    'NED': '🇳🇱', 'NEP': '🇳🇵', 'NGR': '🇳🇬', 'NIG': '🇳🇪', 'NOR': '🇳🇴', 
    'NRU': '🇳🇷', 'NZL': '🇳🇿', 'OMA': '🇴🇲', 'PAK': '🇵🇰', 'PAN': '🇵🇦', 
    'PAR': '🇵🇾', 'PER': '🇵🇪', 'PHI': '🇵🇭', 'PLE': '🇵🇸', 'PLW': '🇵🇼', 
    'PNG': '🇵🇬', 'POL': '🇵🇱', 'POR': '🇵🇹', 'PRK': '🇰🇵', 'PUR': '🇵🇷', 
    'QAT': '🇶🇦', 'ROU': '🇷🇴', 'RSA': '🇿🇦', 'RUS': '🇷🇺', 'RWA': '🇷🇼', 
    'SAM': '🇼🇸', 'SEN': '🇸🇳', 'SEY': '🇸🇨', 'SIN': '🇸🇬', 'SKN': '🇰🇳', 
    'SLE': '🇸🇱', 'SLO': '🇸🇮', 'SMR': '🇸🇲', 'SOL': '🇸🇧', 'SOM': '🇸🇴', 
    'SRB': '🇷🇸', 'SRI': '🇱🇰', 'SSD': '🇸🇸', 'STP': '🇸🇹', 'SUD': '🇸🇩', 
    'SUI': '🇨🇭', 'SUR': '🇸🇷', 'SVK': '🇸🇰', 'SWE': '🇸🇪', 'SWZ': '🇸🇿', 
    'SYR': '🇸🇾', 'TAN': '🇹🇿', 'TGA': '🇹🇴', 'THA': '🇹🇭', 'TJK': '🇹🇯', 
    'TKM': '🇹🇲', 'TLS': '🇹🇱', 'TOG': '🇹🇬', 'TPE': '🇹🇼', 'TTO': '🇹🇹', 
    'TUN': '🇹🇳', 'TUR': '🇹🇷', 'TUV': '🇹🇻', 'UAE': '🇦🇪', 'UGA': '🇺🇬', 
    'UKR': '🇺🇦', 'URU': '🇺🇾', 'USA': '🇺🇸', 'UZB': '🇺🇿', 'VAN': '🇻🇺', 
    'VEN': '🇻🇪', 'VIE': '🇻🇳', 'VIN': '🇻🇨', 'YEM': '🇾🇪', 'ZAM': '🇿🇲', 
    'ZIM': '🇿🇼', 'ROT': '🏳️', 'UNK': '🏳️', 'IOA': '🏳️‍🌈',
    # Historical cases
    'EUN': '🏳️', 'TCH': '🇨🇿', 'FRG': '🇩🇪', 'GDR': '🇩🇪', 'YUG': '🇷🇸',
    'USSR': '🇷🇺', 'ANZ': '🇦🇺', 'BOH': '🇨🇿', 'WIF': '🇯🇲'
}

def create_noc_dropdown_options(nocs, include_all=True, all_label=DEFAULT_DROPDOWN_LABEL):
    """Creates NOC dropdown options with flags."""
    if not isinstance(nocs, list):
        nocs = []
    
    options = []
    for noc in nocs:
        flag_emoji = NOC_TO_FLAG_EMOJI.get(noc, '')
        
        country_name = ''
        if not df.empty and 'NOC' in df.columns and 'region' in df.columns:
            country_matches = df[df['NOC'] == noc]['region'].unique()
            if len(country_matches) > 0:
                country_name = country_matches[0]
        
        if country_name:
            label = f"{flag_emoji} {noc} - {country_name}"
        else:
            label = f"{flag_emoji} {noc}"
            
        options.append({'label': label, 'value': noc})
    
    options = sorted(options, key=lambda x: x['value'])
    
    if include_all:
        if not any(opt['value'] == all_label for opt in options):
            options.insert(0, {'label': all_label, 'value': all_label})
    
    return options

# Create dropdown options
YEAR_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('years', []), include_all=True)
SPORT_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('sports', []), include_all=True)
NOC_OPTIONS = create_noc_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=True)
REGION_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('regions', []), include_all=True)

# Options without "All"
YEAR_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('years', []), include_all=False)
SPORT_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('sports', []), include_all=False)
NOC_OPTIONS_NO_ALL = create_noc_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=False)
REGION_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('regions', []), include_all=False)

def get_default_value(options_list):
     return options_list[0]['value'] if options_list else None