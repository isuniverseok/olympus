# data_loader.py
import pandas as pd
import os
from functools import lru_cache

DATA_FILENAME = 'athlete_events.csv'
DEFAULT_DROPDOWN_LABEL = "All"  # Re-add this definition here for clarity

@lru_cache() # Cache the loaded data
def load_data():
    """Loads and performs initial cleaning on the Olympic data."""
    if not os.path.exists(DATA_FILENAME):
        print(f"ERROR: Data file '{DATA_FILENAME}' not found.")
        return pd.DataFrame(), {} # Return empty dataframe and empty filters

    try:
        df = pd.read_csv(DATA_FILENAME)
        print(f"Loaded {len(df)} rows from {DATA_FILENAME}")

        # Basic Cleaning
        df.rename(columns={'Sex': 'Gender'}, inplace=True)
        df['Medal'] = df['Medal'].fillna('None') # Assign back
        for col in ['Age', 'Height', 'Weight']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce').astype('Int64')
        df.dropna(subset=['Year'], inplace=True) # Essential rows must have Year

        print("Data loaded and cleaned.")

        # Pre-calculate filter options
        years = sorted(df['Year'].dropna().unique().astype(int), reverse=True)
        sports = sorted(df['Sport'].dropna().unique().tolist())
        nocs = sorted(df['NOC'].dropna().unique().tolist())
        filter_options = {
            'years': years,
            'sports': sports,
            'nocs': nocs
        }

        return df, filter_options
    except Exception as e:
        print(f"Error loading or processing data: {e}")
        return pd.DataFrame(), {}

# Load data immediately when this module is imported
df, FILTER_OPTIONS = load_data()

# --- NEW HELPER ---
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

# Create options for immediate use if needed elsewhere
YEAR_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('years', []), include_all=True)
SPORT_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('sports', []), include_all=True)
NOC_OPTIONS = create_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=True)

# Options without "All" for specific selections
YEAR_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('years', []), include_all=False)
SPORT_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('sports', []), include_all=False)
NOC_OPTIONS_NO_ALL = create_dropdown_options(FILTER_OPTIONS.get('nocs', []), include_all=False)

# Get default value for dropdowns requiring a specific item (not "All")
def get_default_value(options_list):
     return options_list[0]['value'] if options_list else None