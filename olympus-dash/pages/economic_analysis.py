import dash
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_loader import df as olympic_df, FILTER_OPTIONS, create_dropdown_options

# Register the page
dash.register_page(__name__, name='Economic Factors (HDI)')

# --- Data Loading and Processing ---

@dash.callback(
    Output('hdi-data-store', 'data'),
    Input('hdi-data-store', 'data') # Trigger on load
)
def load_and_process_hdi_data(_):
    """Loads and processes the HDI.csv data."""
    try:
        # Correct path: relative to the app.py execution directory (olympus-dash)
        hdi_file_path = 'HDI.csv'
        hdi_raw_df = pd.read_csv(hdi_file_path)

        # Clean column names (remove leading/trailing spaces if any)
        hdi_raw_df.columns = hdi_raw_df.columns.str.strip()

        # Melt the dataframe to long format
        id_vars = ['HDI Rank', 'Country']
        value_vars = [col for col in hdi_raw_df.columns if col.isdigit()] # Select only year columns

        if not value_vars:
            print("ERROR: No year columns found in HDI data.")
            return []

        hdi_long_df = pd.melt(hdi_raw_df,
                              id_vars=id_vars,
                              value_vars=value_vars,
                              var_name='Year',
                              value_name='HDI')

        # Clean data: Convert Year to numeric, HDI to numeric (replace '..' with NaN)
        hdi_long_df['Year'] = pd.to_numeric(hdi_long_df['Year'], errors='coerce').astype('Int64')
        hdi_long_df['HDI'] = pd.to_numeric(hdi_long_df['HDI'], errors='coerce')

        # Drop rows where HDI or Year is NaN after conversion
        hdi_long_df.dropna(subset=['Year', 'HDI'], inplace=True)

        print(f"Successfully loaded and processed HDI data. Shape: {hdi_long_df.shape}")
        return hdi_long_df.to_dict('records')

    except FileNotFoundError:
        print(f"ERROR: HDI data file '{hdi_file_path}' not found. Make sure it is in the olympus-dash directory.")
        return []
    except Exception as e:
        print(f"Error loading or processing HDI data: {e}")
        return []

# --- Country Name Mapping ---
REGION_TO_HDI_COUNTRY_MAPPING = {
    "USA": "United States",
    "Russia": "Russian Federation",
    "UK": "United Kingdom",
    "Great Britain": "United Kingdom",
    "South Korea": "Korea (Republic of)",
    "North Korea": "Korea (Democratic People's Rep. of)",
    "Germany": "Germany",
    "West Germany": "Germany",
    "East Germany": "Germany",
    "Soviet Union": "Russian Federation",
    "Czechoslovakia": "Czechia",
    "Yugoslavia": "Serbia",
    "Bolivia": "Bolivia (Plurinational State of)",
    "Iran": "Iran (Islamic Republic of)",
    "Moldova": "Moldova (Republic of)",
    "Syria": "Syrian Arab Republic",
    "Tanzania": "Tanzania (United Republic of)",
    "Venezuela": "Venezuela (Bolivarian Republic of)",
    "Vietnam": "Viet Nam",
    "Palestine": "Palestine, State of",
    "Republic of Congo": "Congo",
    "Democratic Republic of the Congo": "Congo (Democratic Republic of the)",
    "Eswatini": "Eswatini (Kingdom of)",
    "Czech Republic": "Czechia", # Added mapping
    "Ivory Coast": "Côte d'Ivoire", # Added mapping
    # Add more mappings as differences are found
}

# --- Analysis and Plotting Functions ---

def merge_olympic_hdi(olympic_data, hdi_data, year=None):
    """Merges Olympic medal data with HDI data for a specific year or latest available."""
    if not hdi_data:
        return pd.DataFrame()

    hdi_df = pd.DataFrame(hdi_data)
    if not isinstance(olympic_data, pd.DataFrame):
        print("Warning: olympic_data is not a DataFrame.")
        return pd.DataFrame()
        
    medals_df = olympic_data[olympic_data['Medal'] != 'None'].copy()

    # ** Correct Medal Counting Logic **
    medals_df['medal_event_key'] = (
        medals_df['Year'].astype(str) + '_' +
        medals_df['Season'].astype(str) + '_' +
        medals_df['Event'].astype(str) + '_' +
        medals_df['Medal'].astype(str)
    )
    unique_medals_df = medals_df.drop_duplicates(subset=['medal_event_key', 'region'])
    medal_counts_by_region_year = unique_medals_df.groupby(['Year', 'region'], observed=False).size().reset_index(name='MedalCount')

    # Prepare HDI data with mapped region
    hdi_df['region_mapped'] = hdi_df['Country'].map(REGION_TO_HDI_COUNTRY_MAPPING).fillna(hdi_df['Country']) 

    if year:
        target_year = int(year)
        available_hdi_years = sorted([y for y in hdi_df['Year'].unique() if pd.notna(y)])
        if not available_hdi_years:
             print("Warning: No valid years found in HDI data.")
             return pd.DataFrame()

        valid_years = [y for y in available_hdi_years if y <= target_year]
        closest_hdi_year = max(valid_years) if valid_years else min(available_hdi_years)
        
        hdi_year_df = hdi_df[hdi_df['Year'] == closest_hdi_year][['region_mapped', 'HDI']].drop_duplicates(subset=['region_mapped'])
        medals_year_df = medal_counts_by_region_year[medal_counts_by_region_year['Year'] == target_year]
        print(f"Using HDI data from year {closest_hdi_year} for Olympic year {target_year}")
        
        merged_df = pd.merge(
            medals_year_df,
            hdi_year_df,
            left_on='region',
            right_on='region_mapped',
            how='left'
        )

    else: # Aggregate all years
        latest_hdi = hdi_df.loc[hdi_df.groupby('region_mapped')['Year'].idxmax()][['region_mapped', 'HDI']]
        max_year = hdi_df['Year'].max()
        print(f"Using latest available HDI data (up to {max_year}) mapped to region")

        total_medals_all_years = medal_counts_by_region_year.groupby('region', observed=False)['MedalCount'].sum().reset_index()
        merged_df = pd.merge(
            total_medals_all_years, 
            latest_hdi,
            left_on='region',
            right_on='region_mapped',
            how='left'
        )

    # Create HDI Categories
    merged_df['HDI_Category'] = pd.cut(
        merged_df['HDI'],
        bins=[0, 0.55, 0.7, 0.8, 1.0],
        labels=['Low HDI (<0.55)', 'Medium HDI (0.55-0.7)', 'High HDI (0.7-0.8)', 'Very High HDI (>0.8)'],
    )

    return merged_df.dropna(subset=['HDI']) 


# Plotting functions use the aggregated merged_df from above
def create_hdi_medal_correlation_scatter(merged_df, year=None):
    """Creates scatter plot of HDI vs Medal Count."""
    if merged_df.empty:
        return go.Figure().update_layout(title="No data for HDI vs Medals", template='plotly_dark')

    title = f"HDI vs. Total Olympic Medal Count ({year})" if year else "HDI vs. Total Olympic Medal Count (All Years Merged with Latest HDI)"
    color_col = 'HDI_Category' if 'HDI_Category' in merged_df.columns else None
    category_orders_dict = {"HDI_Category": ['Low HDI (<0.55)', 'Medium HDI (0.55-0.7)', 'High HDI (0.7-0.8)', 'Very High HDI (>0.8)']} if color_col else None

    fig = px.scatter(
        merged_df, 
        x='HDI',
        y='MedalCount',
        color=color_col,
        size='MedalCount',
        hover_name='region', 
        title=title,
        labels={'HDI': 'Human Development Index (HDI)', 'MedalCount': 'Total Medal Count', 'region': 'Country/Region'},
        category_orders=category_orders_dict
    )
    fig.update_layout(template='plotly_dark', height=600)
    return fig

# This function now needs the *original* olympic_df and hdi_data to perform sport-specific filtering *before* aggregation
def create_hdi_sport_performance_bar(olympic_data, hdi_data, sport_filter=None, year=None):
    """Creates bar chart showing medal counts IN A SPECIFIC SPORT grouped by HDI category."""
    if not hdi_data:
        return go.Figure().update_layout(title="HDI data not loaded", template='plotly_dark')

    hdi_df = pd.DataFrame(hdi_data)
    medals_df = olympic_data[olympic_data['Medal'] != 'None'].copy()
    
    # Prepare HDI data with mapped region
    hdi_df['region_mapped'] = hdi_df['Country'].map(REGION_TO_HDI_COUNTRY_MAPPING).fillna(hdi_df['Country']) 

    # --- Get relevant HDI data (closest year or latest) --- 
    if year:
        target_year = int(year)
        available_hdi_years = sorted([y for y in hdi_df['Year'].unique() if pd.notna(y)])
        if not available_hdi_years:
            return go.Figure().update_layout(title="No valid years in HDI data", template='plotly_dark')
        valid_years = [y for y in available_hdi_years if y <= target_year]
        closest_hdi_year = max(valid_years) if valid_years else min(available_hdi_years)
        hdi_year_df = hdi_df[hdi_df['Year'] == closest_hdi_year][['region_mapped', 'HDI']].drop_duplicates(subset=['region_mapped'])
        medals_df = medals_df[medals_df['Year'] == target_year] # Filter medals by year too
        title_year_suffix = f"in {target_year}"
    else:
        latest_hdi = hdi_df.loc[hdi_df.groupby('region_mapped')['Year'].idxmax()][['region_mapped', 'HDI']]
        hdi_year_df = latest_hdi
        title_year_suffix = "(All Years Merged)"

    # --- Filter Medals by Sport (if applicable) --- 
    if sport_filter and sport_filter != "All":
        sport_medals_df = medals_df[medals_df['Sport'] == sport_filter].copy()
        title = f"Medal Distribution by HDI Category for {sport_filter} {title_year_suffix}"
    else:
        sport_medals_df = medals_df.copy()
        title = f"Overall Medal Distribution by HDI Category {title_year_suffix}"

    # --- Count Unique Medals for the filtered DataFrame --- 
    if sport_medals_df.empty:
         return go.Figure().update_layout(title=f"No medals found for {sport_filter or 'selected criteria'} {title_year_suffix}", template='plotly_dark')
         
    sport_medals_df['medal_event_key'] = (
        sport_medals_df['Year'].astype(str) + '_' +
        sport_medals_df['Season'].astype(str) + '_' +
        sport_medals_df['Event'].astype(str) + '_' +
        sport_medals_df['Medal'].astype(str)
    )
    unique_sport_medals_df = sport_medals_df.drop_duplicates(subset=['medal_event_key', 'region'])

    # --- Merge Unique Sport Medals with HDI --- 
    merged_sport_df = pd.merge(
        unique_sport_medals_df,
        hdi_year_df,
        left_on='region',
        right_on='region_mapped',
        how='left'
    ).dropna(subset=['HDI'])
    
    if merged_sport_df.empty:
         return go.Figure().update_layout(title=f"No medals found for {sport_filter or 'selected criteria'} {title_year_suffix} with HDI data", template='plotly_dark')

    # --- Create HDI Categories and Aggregate --- 
    merged_sport_df['HDI_Category'] = pd.cut(
        merged_sport_df['HDI'],
        bins=[0, 0.55, 0.7, 0.8, 1.0],
        labels=['Low HDI (<0.55)', 'Medium HDI (0.55-0.7)', 'High HDI (0.7-0.8)', 'Very High HDI (>0.8)'],
    )

    if 'HDI_Category' not in merged_sport_df.columns or merged_sport_df['HDI_Category'].isnull().all():
         return go.Figure().update_layout(title="Could not assign HDI Categories", template='plotly_dark')

    sport_hdi_summary = merged_sport_df.groupby('HDI_Category', observed=False).size().reset_index(name='MedalCount')

    # --- Create Bar Chart --- 
    fig = px.bar(
        sport_hdi_summary,
        x='HDI_Category',
        y='MedalCount',
        color='HDI_Category',
        title=title,
        labels={'HDI_Category': 'HDI Category', 'MedalCount': 'Total Medal Count'},
        category_orders={'HDI_Category': ['Low HDI (<0.55)', 'Medium HDI (0.55-0.7)', 'High HDI (0.7-0.8)', 'Very High HDI (>0.8)']}
    )
    fig.update_layout(template='plotly_dark', height=500, xaxis_title="HDI Category", yaxis_title="Number of Medals")
    return fig


def generate_hdi_insights(merged_df, sport=None, year=None):
    """Generates textual insights based on the HDI analysis."""
    # merged_df here is the one aggregated for the scatter plot (country-level summary)
    if merged_df.empty:
        return html.P("Insufficient data to generate insights.")

    insights = []
    year_text = f"in {year}" if year else "across Olympics (latest HDI)"
    sport_text = f"for {sport}" if sport and sport != "All" else "across all sports"

    insights.append(html.H4(f"HDI Impact Insights {year_text} {sport_text}"))

    # Overall Correlation - Use the already aggregated merged_df
    if len(merged_df) > 1 and merged_df['HDI'].nunique() > 1 and merged_df['MedalCount'].nunique() > 1:
        try:
             corr = merged_df['HDI'].corr(merged_df['MedalCount'])
             insights.append(html.P([
                 f"Overall correlation between Country/Region HDI and Total Medal Count: ", 
                 html.Strong(f"{corr:.2f}")
             ]))
             # Add explanation for the correlation value
             explanation = ""
             if abs(corr) >= 0.7:
                 explanation = "This indicates a strong linear relationship. "
             elif abs(corr) >= 0.4:
                 explanation = "This indicates a moderate linear relationship. "
             elif abs(corr) >= 0.1:
                 explanation = "This indicates a weak linear relationship. "
             else:
                 explanation = "This indicates little to no linear relationship. "
             
             if corr > 0:
                 explanation += "As HDI increases, the total medal count tends to increase as well."
             elif corr < 0:
                 explanation += "As HDI increases, the total medal count tends to decrease."
             
             insights.append(html.Small([
                 "Correlation measures the linear association between two variables (from -1 to +1). ",
                 "A value closer to +1 suggests a stronger positive association, while a value closer to -1 suggests a stronger negative association. ",
                 "A value near 0 suggests a weak linear association. "
             ], className="text-muted d-block mb-2"))
             insights.append(html.P(explanation))
             insights.append(html.P([
                 "This suggests that factors associated with higher human development (like better healthcare, education, and living standards) may contribute to a nation's ability to achieve Olympic success, potentially through better funding, facilities, and athlete support systems. ",
                 html.Em("Note: Correlation does not imply causation.")
             ]))

        except Exception as e:
            print(f"Could not calculate correlation: {e}")
            insights.append(html.P("Could not calculate overall HDI-Medal correlation."))

    # Distribution by HDI Category (based on total medals)
    if 'HDI_Category' in merged_df.columns:
        # Sum medals per category from the aggregated df
        category_medal_sum = merged_df.groupby('HDI_Category', observed=False)['MedalCount'].sum()
        if category_medal_sum.sum() > 0:
            category_counts = (category_medal_sum / category_medal_sum.sum()).sort_index()
            insights.append(html.H5("Total Medal Distribution by HDI Category:"))
            insights.append(html.Ul([
                html.Li(f"{category}: {count:.1%}") for category, count in category_counts.items()
            ]))
        else:
             insights.append(html.P("No medals found to calculate distribution by HDI category."))
             
    # Simplified insight - mentioning that the bar chart shows sport-specific distribution if a sport is selected.
    if sport and sport != "All":
        insights.append(html.P(f"The bar chart above shows the distribution of medals specifically for {sport} across HDI categories."))

    return html.Div(insights)


# --- Layout Definition ---
layout = dbc.Container(fluid=True, children=[
    dcc.Store(id='hdi-data-store'), # To store processed HDI data

    dbc.Row([
        dbc.Col([
            html.H1("Economic Factors (HDI) & Olympic Performance", className="mb-4"),
            html.P(
                "Explore the relationship between Human Development Index (HDI) and Olympic medal performance.",
                className="lead"
            )
        ])
    ]),

    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Analysis Filters"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Select Olympic Year:"),
                            dcc.Dropdown(
                                id="hdi-year-dropdown",
                                options=create_dropdown_options(
                                    sorted(olympic_df['Year'].dropna().unique().astype(int), reverse=True),
                                    include_all=True, all_label="All Years (Latest HDI)"
                                ),
                                value="All", # Default to All
                                clearable=False,
                                # Removed inline style, rely on assets/economic_analysis.css
                            )
                        ], md=6),
                        dbc.Col([
                            html.Label("Select Sport:"),
                            dcc.Dropdown(
                                id="hdi-sport-dropdown",
                                options=create_dropdown_options(
                                    sorted(olympic_df['Sport'].dropna().unique().tolist()),
                                    include_all=True, all_label="All Sports"
                                ),
                                value="All", # Default to All Sports
                                clearable=False,
                                # Removed inline style, rely on assets/economic_analysis.css
                            )
                        ], md=6),
                    ]),
                ])
            ], className="mb-4")
        ])
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("HDI vs. Total Medal Count"),
            dbc.CardBody(dcc.Graph(id="hdi-medal-scatter-chart"))
        ]), md=12, className="mb-4")
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Medal Distribution by HDI Category"),
            dbc.CardBody(dcc.Graph(id="hdi-sport-bar-chart"))
        ]), md=12, className="mb-4"),
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Key Insights"),
            dbc.CardBody(html.Div(id="hdi-insights"))
        ]), md=12, className="mt-4")
    ])
])

# --- Callbacks ---

@callback(
    [Output("hdi-medal-scatter-chart", "figure"),
     Output("hdi-sport-bar-chart", "figure"),
     Output("hdi-insights", "children")],
    [Input("hdi-year-dropdown", "value"),
     Input("hdi-sport-dropdown", "value"),
     Input("hdi-data-store", "data")]
)
def update_hdi_analysis(year_value, sport_value, hdi_data):
    if not hdi_data:
        no_data_fig = go.Figure().update_layout(title="HDI Data not loaded", template='plotly_dark')
        return no_data_fig, no_data_fig, html.P("HDI data failed to load.")

    year = None if year_value == "All" else year_value
    sport = sport_value # Keep 'All' as is

    # Data for scatter plot (country-level aggregated medal counts vs HDI)
    scatter_merged_df = merge_olympic_hdi(olympic_df, hdi_data, year)
    scatter_fig = create_hdi_medal_correlation_scatter(scatter_merged_df, year)

    # Data/Plot for sport bar chart (needs original data + HDI data)
    sport_for_bar = None if sport == "All" else sport
    sport_bar_fig = create_hdi_sport_performance_bar(olympic_df, hdi_data, sport_for_bar, year)

    # Insights based on the aggregated scatter plot data
    insights = generate_hdi_insights(scatter_merged_df, sport_for_bar, year)

    return scatter_fig, sport_bar_fig, insights