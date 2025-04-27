# data_loader.py
import pandas as pd
import os
from functools import lru_cache

# Define filenames with correct paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ATHLETE_EVENTS_FILENAME = os.path.join(BASE_DIR, 'athlete_events.csv')
NOC_REGIONS_FILENAME = os.path.join(BASE_DIR, 'noc_regions.csv')
DEFAULT_DROPDOWN_LABEL = "All"

@lru_cache() # Cache the loaded data
def load_data():
    """Loads, merges, and performs initial cleaning on the Olympic data."""
    # Check for essential files
    if not os.path.exists(ATHLETE_EVENTS_FILENAME):
        print(f"ERROR: Data file '{ATHLETE_EVENTS_FILENAME}' not found.")
        return pd.DataFrame(), {} # Return empty dataframe and empty filters
    if not os.path.exists(NOC_REGIONS_FILENAME):
        print(f"ERROR: Data file '{NOC_REGIONS_FILENAME}' not found.")
        # Decide if you want to proceed without region info or stop
        # For now, let's return empty to indicate a critical failure
        return pd.DataFrame(), {}

    try:
        # Load main athlete events data
        df = pd.read_csv(ATHLETE_EVENTS_FILENAME)
        print(f"Loaded {len(df)} rows from {ATHLETE_EVENTS_FILENAME}")

        # Load NOC regions data
        noc_regions = pd.read_csv(NOC_REGIONS_FILENAME)
        print(f"Loaded {len(noc_regions)} rows from {NOC_REGIONS_FILENAME}")

        # Select only necessary columns and merge
        noc_map = noc_regions[['NOC', 'region']]
        df = df.merge(noc_map, on='NOC', how='left') # Use left merge to keep all athletes

        # Handle potential missing regions after merge (if any NOC in athlete_events is not in noc_regions)
        df['region'] = df['region'].fillna('Unknown') # Or keep as NaN if preferred

        # Basic Cleaning
        df.rename(columns={'Sex': 'Gender'}, inplace=True)
        df['Medal'] = df['Medal'].fillna('None')
        for col in ['Age', 'Height', 'Weight']:
            # Use .loc to avoid SettingWithCopyWarning if df is a slice (though unlikely here)
            df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        df.dropna(subset=['Year'], inplace=True) # Essential rows must have Year

        print("Data loaded, merged, and cleaned.")

        # Pre-calculate filter options (now including region)
        years = sorted(df['Year'].dropna().unique().astype(int), reverse=True)
        sports = sorted(df['Sport'].dropna().unique().tolist())
        nocs = sorted(df['NOC'].dropna().unique().tolist())
        regions = sorted(df['region'].dropna().unique().tolist()) # Add region filter

        filter_options = {
            'years': years,
            'sports': sports,
            'nocs': nocs,
            'regions': regions # Include regions in options
        }

        return df, filter_options
    except Exception as e:
        print(f"Error loading or processing data: {e}")
        return pd.DataFrame(), {}

# Load data immediately when this module is imported
df, FILTER_OPTIONS = load_data()

# --- HELPER for Dropdown Options ---
# Helper to create dropdown options easily
def create_dropdown_options(items_list, include_all=True, all_label=DEFAULT_DROPDOWN_LABEL):
    """Creates list of dictionaries for Dash Dropdown options."""
    # Ensure items_list is valid
    if not isinstance(items_list, list):
        items_list = []

    options = [{'label': str(item), 'value': item} for item in items_list]
    if include_all:
        # Check if 'all_label' already exists as a value to prevent duplicates if an item is named "All"
        if not any(opt['value'] == all_label for opt in options):
             options.insert(0, {'label': all_label, 'value': all_label})
    return options

# Country flag emoji mapping for NOC codes
# This is a dictionary mapping NOC codes to their corresponding flag emojis
# Source for flag emojis: Unicode CLDR data
# Note: Not all NOCs may have a direct country flag correspondence
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
    'SYR': '🇸🇾', 'TAN': '🇹🇿', 'TGA': '��🇴', 'THA': '🇹🇭', 'TJK': '🇹🇯', 
    'TKM': '🇹🇲', 'TLS': '🇹🇱', 'TOG': '🇹🇬', 'TPE': '🇹🇼', 'TTO': '🇹🇹', 
    'TUN': '🇹🇳', 'TUR': '🇹🇷', 'TUV': '🇹🇻', 'UAE': '🇦🇪', 'UGA': '🇺🇬', 
    'UKR': '🇺🇦', 'URU': '🇺🇾', 'USA': '🇺🇸', 'UZB': '🇺🇿', 'VAN': '🇻🇺', 
    'VEN': '🇻🇪', 'VIE': '🇻🇳', 'VIN': '🇻🇨', 'YEM': '🇾🇪', 'ZAM': '🇿🇲', 
    'ZIM': '🇿🇼', 'ROT': '🏳️', 'UNK': '🏳️', 'IOA': '🏳️‍🌈',
    # Historical or special cases
    'EUN': '🏳️', 'TCH': '🇨🇿', 'FRG': '🇩🇪', 'GDR': '🇩🇪', 'YUG': '🇷🇸',
    'USSR': '🇷🇺', 'ANZ': '🇦🇺', 'BOH': '🇨🇿', 'WIF': '🇯🇲'
}

# Helper function to create enhanced NOC dropdown options with flags and country names
def create_noc_dropdown_options(nocs, include_all=True, all_label=DEFAULT_DROPDOWN_LABEL):
    """Creates dropdown options for NOCs with flag emojis and full country names."""
    # Ensure nocs list is valid
    if not isinstance(nocs, list):
        nocs = []
    
    # Create options with flag emoji and region name (from the loaded data)
    options = []
    for noc in nocs:
        flag_emoji = NOC_TO_FLAG_EMOJI.get(noc, '')  # Get flag emoji or empty string if not found
        
        # Find the country name from the loaded dataframe
        country_name = ''
        if not df.empty and 'NOC' in df.columns and 'region' in df.columns:
            country_matches = df[df['NOC'] == noc]['region'].unique()
            if len(country_matches) > 0:
                country_name = country_matches[0]
        
        # Format label with flag and country name
        if country_name:
            label = f"{flag_emoji} {noc} - {country_name}"
        else:
            label = f"{flag_emoji} {noc}"
            
        options.append({'label': label, 'value': noc})
    
    # Sort options by NOC code for consistency
    options = sorted(options, key=lambda x: x['value'])
    
    # Add "All" option if needed
    if include_all:
        if not any(opt['value'] == all_label for opt in options):
            options.insert(0, {'label': all_label, 'value': all_label})
    
    return options

# Create options for immediate use
YEAR_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('years', []), include_all=True)
SPORT_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('sports', []), include_all=True)
# Use enhanced function for NOC options
NOC_OPTIONS = create_noc_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=True)
REGION_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('regions', []), include_all=True) # Add region options

# Options without "All"
YEAR_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('years', []), include_all=False)
SPORT_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('sports', []), include_all=False)
# Use enhanced function for NOC options without "All"
NOC_OPTIONS_NO_ALL = create_noc_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=False)
REGION_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('regions', []), include_all=False) # Add region options (no all)

# Get default value for dropdowns requiring a specific item (not "All")
def get_default_value(options_list):
     return options_list[0]['value'] if options_list else None