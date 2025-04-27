# pages/misc_analysis.py
import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from data_loader import df as olympic_df
import plotly.figure_factory as ff
from wordcloud import WordCloud
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
from sklearn.preprocessing import MinMaxScaler
import re
from plotly.subplots import make_subplots

# Register the page
dash.register_page(__name__, name='More Analysis')

# Make sure we have data
try:
    # Try to get data with medals
    df_with_medals = olympic_df[olympic_df['Medal'] != 'None']
    
    # Convert height and weight to numeric, handling errors
    olympic_df = olympic_df.copy()  # Create a copy to avoid SettingWithCopyWarning
    olympic_df['Height'] = pd.to_numeric(olympic_df['Height'], errors='coerce')
    olympic_df['Weight'] = pd.to_numeric(olympic_df['Weight'], errors='coerce')
    olympic_df['Age'] = pd.to_numeric(olympic_df['Age'], errors='coerce')
    
    # Create a Year range for filtering - convert to standard Python ints
    years = sorted([int(year) for year in olympic_df['Year'].unique()])
    min_year = int(min(years))
    max_year = int(max(years))
    
    # Get list of sports for dropdown
    sports_list = sorted(olympic_df['Sport'].unique())
    
    # Get list of seasons for filtering
    seasons = ['Summer', 'Winter']
    
except Exception as e:
    print(f"Error processing Olympic data: {e}")
    df_with_medals = pd.DataFrame()
    years = []
    min_year = 1896
    max_year = 2016
    sports_list = []
    seasons = []

# Advanced analysis functions
def create_medal_trend_chart(filtered_df, n_countries=10):
    """Create a line chart showing medal trends for top countries over time"""
    if filtered_df.empty:
        # Return empty figure with text if no data
        fig = go.Figure()
        fig.update_layout(
            title="No data available for the selected filters",
            template='plotly_dark',
            height=600
        )
        return fig
        
    try:
        # CRITICAL FIX: Use exactly the same counting logic as in olympic_year.py
        # First, filter to only rows with medals
        medals_df = filtered_df[filtered_df['Medal'] != 'None'].copy()
        
        if not medals_df.empty:
            # Create a unique identifier for each medal event to handle team sports correctly
            # Each team medal should count as ONE medal per country
            medals_df['medal_key'] = medals_df['Year'].astype(str) + '_' + \
                                    medals_df['Season'] + '_' + \
                                    medals_df['Event'] + '_' + \
                                    medals_df['Medal']
            
            # Get one row per country-medal by dropping duplicates
            unique_medals = medals_df.drop_duplicates(subset=['medal_key', 'region'])
            
            # Get top countries by total medal count
            country_totals = unique_medals.groupby('region').size().nlargest(n_countries)
            top_countries = country_totals.index.tolist()
            
            # Prepare data for line chart
            all_years = sorted(filtered_df['Year'].unique())
            medal_data = []
            
            for country in top_countries:
                country_medals = unique_medals[unique_medals['region'] == country]
                
                # Count medals per year
                yearly_medals = country_medals.groupby('Year').size().reset_index(name='MedalCount')
                yearly_medals['region'] = country
                
                # Ensure all years have data points (for continuous lines)
                year_df = pd.DataFrame({'Year': all_years})
                complete_df = pd.merge(year_df, yearly_medals, on='Year', how='left')
                complete_df = complete_df.copy()  # Create a copy to avoid SettingWithCopyWarning
                complete_df['region'] = complete_df['region'].fillna(country)
                complete_df['MedalCount'] = complete_df['MedalCount'].fillna(0)
                
                medal_data.append(complete_df)
                
            # Combine all countries' data
            if medal_data:
                medal_counts = pd.concat(medal_data)
                medal_counts = medal_counts.copy()  # Create a copy to avoid SettingWithCopyWarning
                medal_counts['Year'] = medal_counts['Year'].astype(int)
                medal_counts['MedalCount'] = medal_counts['MedalCount'].astype(int)
                
                # Create line chart
                fig = px.line(
                    medal_counts,
                    x='Year',
                    y='MedalCount',
                    color='region',
                    line_shape='linear',
                    markers=True,
                    title=f'Medal Count Trends for Top {n_countries} Countries',
                    labels={'MedalCount': 'Total Medals', 'Year': 'Olympic Year', 'region': 'Country'}
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=600,
                    margin=dict(l=50, r=50, t=70, b=50),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
                )
                
                return fig
            else:
                fig = go.Figure()
                fig.update_layout(
                    title="No medal data available",
                    template='plotly_dark',
                    height=600
                )
                return fig
        else:
            fig = go.Figure()
            fig.update_layout(
                title="No medal data available",
                template='plotly_dark',
                height=600
            )
            return fig
    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        fig.update_layout(
            title=f"Error creating chart: {str(e)}",
            template='plotly_dark',
            height=600
        )
        return fig

def create_sport_heatmap(filtered_df):
    """Create a heatmap showing the relationships between sports and physical attributes"""
    if filtered_df.empty:
        # Return empty figure with text if no data
        fig = go.Figure()
        fig.update_layout(
            title="No data available for the selected filters",
            template='plotly_dark',
            height=600
        )
        return fig
        
    try:
        # Get top 15 sports by participation
        top_sports = filtered_df.groupby('Sport').size().nlargest(15).index.tolist()
        df_for_heatmap = filtered_df[filtered_df['Sport'].isin(top_sports)]
        
        # Calculate mean values for Age, Height, Weight
        sport_attributes = df_for_heatmap.groupby('Sport').agg({
            'Age': 'mean',
            'Height': 'mean',
            'Weight': 'mean'
        }).reset_index()
        
        # Calculate BMI
        sport_attributes['BMI'] = sport_attributes['Weight'] / ((sport_attributes['Height']/100) ** 2)
        
        # Create heatmap
        if not sport_attributes.empty:
            fig = px.imshow(
                sport_attributes.set_index('Sport')[['Age', 'Height', 'Weight', 'BMI']],
                labels=dict(x="Attribute", y="Sport", color="Value"),
                title="Sport-Attribute Heatmap",
                color_continuous_scale='Viridis',
                aspect="auto"
            )
            
            fig.update_layout(
                template='plotly_dark',
                height=600,
                margin=dict(l=70, r=50, t=70, b=50)
            )
            return fig
        else:
            # Not enough data
            fig = go.Figure()
            fig.update_layout(
                title="Not enough data for heatmap with current filters",
                template='plotly_dark',
                height=600
            )
            return fig
    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        fig.update_layout(
            title=f"Error creating chart: {str(e)}",
            template='plotly_dark',
            height=600
        )
        return fig

def create_age_evolution_chart(filtered_df):
    """Create a visualization of athlete age evolution over Olympic history"""
    if filtered_df.empty:
        # Return empty figure with text if no data
        fig = go.Figure()
        fig.update_layout(
            title="No data available for the selected filters",
            template='plotly_dark',
            height=500
        )
        return fig
        
    try:
        # Filter out invalid ages
        df_with_age = filtered_df[filtered_df['Age'].notna()]
        
        # Group by year and calculate age statistics
        age_stats = df_with_age.groupby('Year').agg({
            'Age': ['mean', 'median', 'min', 'max']
        }).reset_index()
        
        # Flatten multi-index columns
        age_stats.columns = ['Year', 'Mean Age', 'Median Age', 'Youngest', 'Oldest']
        
        # Convert Year to int to avoid serialization issues
        age_stats['Year'] = age_stats['Year'].astype(int)
        
        # Create line chart for age trends
        fig = go.Figure()
        
        # Add mean age line
        fig.add_trace(go.Scatter(
            x=age_stats['Year'],
            y=age_stats['Mean Age'],
            mode='lines+markers',
            name='Mean Age',
            line=dict(color='royalblue', width=3)
        ))
        
        # Add median age line
        fig.add_trace(go.Scatter(
            x=age_stats['Year'],
            y=age_stats['Median Age'],
            mode='lines+markers',
            name='Median Age',
            line=dict(color='firebrick', width=3)
        ))
        
        # Add age range as a filled area
        fig.add_trace(go.Scatter(
            x=age_stats['Year'],
            y=age_stats['Oldest'],
            fill=None,
            mode='lines',
            line=dict(color='rgba(180, 180, 180, 0.5)', width=0.5),
            name='Oldest Athlete'
        ))
        
        fig.add_trace(go.Scatter(
            x=age_stats['Year'],
            y=age_stats['Youngest'],
            fill='tonexty',
            mode='lines',
            line=dict(color='rgba(180, 180, 180, 0.5)', width=0.5),
            name='Youngest Athlete'
        ))
        
        fig.update_layout(
            title='Evolution of Athlete Ages Throughout Olympic History',
            xaxis_title='Olympic Year',
            yaxis_title='Age (years)',
            template='plotly_dark',
            height=500,
            margin=dict(l=50, r=50, t=70, b=50),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        return fig
    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        fig.update_layout(
            title=f"Error creating chart: {str(e)}",
            template='plotly_dark',
            height=500
        )
        return fig

def create_sport_characteristics(filtered_df, selected_sport=None):
    """Create visualizations showing detailed characteristics of a single sport"""
    if filtered_df.empty or not selected_sport:
        # Return empty figure with text if no data
        fig = go.Figure()
        fig.update_layout(
            title="Please select a sport to view its characteristics",
            template='plotly_dark',
            height=600
        )
        return fig, go.Figure()
        
    try:
        # Filter to the selected sport
        sport_df = filtered_df[filtered_df['Sport'] == selected_sport]
        
        if len(sport_df) < 10:
            # Not enough data for this sport
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title=f"Not enough data for {selected_sport}",
                template='plotly_dark',
                height=600
            )
            return empty_fig, empty_fig
        
        # Calculate metrics for the selected sport and all sports for comparison
        
        # Physical attributes - compare with all sports average
        sport_avg_age = sport_df['Age'].mean()
        sport_avg_height = sport_df['Height'].mean()
        sport_avg_weight = sport_df['Weight'].mean()
        
        all_avg_age = filtered_df['Age'].mean()
        all_avg_height = filtered_df['Height'].mean()
        all_avg_weight = filtered_df['Weight'].mean()
        
        # Gender distribution
        total_athletes = len(sport_df['ID'].unique())
        female_athletes = len(sport_df[sport_df['Gender'] == 'F']['ID'].unique())
        male_athletes = len(sport_df[sport_df['Gender'] == 'M']['ID'].unique()) 
        female_pct = (female_athletes / total_athletes * 100) if total_athletes > 0 else 0
        male_pct = (male_athletes / total_athletes * 100) if total_athletes > 0 else 0
        
        # Overall gender distribution
        all_total = len(filtered_df['ID'].unique())
        all_female = len(filtered_df[filtered_df['Gender'] == 'F']['ID'].unique())
        all_female_pct = (all_female / all_total * 100) if all_total > 0 else 0
        all_male_pct = 100 - all_female_pct
        
        # Medal statistics 
        medals_df = sport_df[sport_df['Medal'] != 'None'].copy()
        
        # Create a unique identifier for each medal event to handle team sports correctly
        if not medals_df.empty:
            medals_df['medal_key'] = medals_df['Year'].astype(str) + '_' + \
                                    medals_df['Season'] + '_' + \
                                    medals_df['Event'] + '_' + \
                                    medals_df['Medal']
            
            # Get one row per country-medal by dropping duplicates
            unique_medal_df = medals_df.drop_duplicates(subset=['medal_key', 'region'])
        else:
            unique_medal_df = medals_df
            
        # Count total events
        total_events = sport_df['Event'].nunique()
        medal_countries = unique_medal_df['region'].nunique() if not unique_medal_df.empty else 0
        
        # -------- PHYSICAL CHARACTERISTICS VISUALIZATION --------
        # Create a more intuitive comparison bar chart
        phys_fig = go.Figure()
        
        # Prepare data for comparison
        attributes = ['Age (years)', 'Height (cm)', 'Weight (kg)', 'Female Athletes (%)', 'Male Athletes (%)']
        sport_values = [
            round(sport_avg_age, 1) if not np.isnan(sport_avg_age) else 0,
            round(sport_avg_height, 1) if not np.isnan(sport_avg_height) else 0,
            round(sport_avg_weight, 1) if not np.isnan(sport_avg_weight) else 0,
            round(female_pct, 1),
            round(male_pct, 1)
        ]
        all_sports_values = [
            round(all_avg_age, 1) if not np.isnan(all_avg_age) else 0,
            round(all_avg_height, 1) if not np.isnan(all_avg_height) else 0,
            round(all_avg_weight, 1) if not np.isnan(all_avg_weight) else 0,
            round(all_female_pct, 1),
            round(all_male_pct, 1)
        ]
        
        # Percentage differences for color coding
        pct_diff = []
        for i in range(len(sport_values)):
            if all_sports_values[i] > 0:
                diff = ((sport_values[i] - all_sports_values[i]) / all_sports_values[i]) * 100
                pct_diff.append(round(diff, 1))
            else:
                pct_diff.append(0)
        
        # Create a horizontal bar chart for the sport
        phys_fig.add_trace(go.Bar(
            y=attributes,
            x=sport_values,
            orientation='h',
            name=selected_sport,
            marker_color='rgba(255, 102, 0, 0.7)',
            text=[f"{val} ({diff:+.1f}%)" for val, diff in zip(sport_values, pct_diff)],
            textposition='auto'
        ))
        
        # Add a bar for all sports average
        phys_fig.add_trace(go.Bar(
            y=attributes,
            x=all_sports_values,
            orientation='h',
            name='All Sports Average',
            marker_color='rgba(66, 135, 245, 0.7)',
            text=all_sports_values,
            textposition='auto'
        ))
        
        # Update layout
        phys_fig.update_layout(
            title=f"{selected_sport} vs All Sports - Physical Characteristics",
            xaxis_title='Value',
            barmode='group',
            template='plotly_dark',
            height=600,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=20, r=20, t=70, b=20)
        )
        
        # -------- MEDAL PERFORMANCE VISUALIZATION --------
        medal_fig = go.Figure()
        
        if not medals_df.empty:
            # Count medals by type
            medal_counts = unique_medal_df['Medal'].value_counts().reset_index()
            medal_counts.columns = ['Medal', 'Count']
            
            # Make sure all medal types are represented
            medal_types = ['Gold', 'Silver', 'Bronze']
            for medal in medal_types:
                if medal not in medal_counts['Medal'].values:
                    medal_counts = pd.concat([medal_counts, pd.DataFrame({'Medal': [medal], 'Count': [0]})])
            
            # Sort by medal precedence
            medal_order = {'Gold': 0, 'Silver': 1, 'Bronze': 2}
            medal_counts['Order'] = medal_counts['Medal'].map(medal_order)
            medal_counts = medal_counts.sort_values('Order')
            
            # Define colors
            medal_colors = {
                'Gold': '#FFD700',
                'Silver': '#C0C0C0',
                'Bronze': '#CD7F32'
            }
            
            # Create medal type breakdown as a pie chart for clarity
            medal_fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "pie"}, {"type": "xy"}]],
                subplot_titles=("Medal Type Distribution", "Historical Medal Performance")
            )
            
            # Add pie chart of medal types
            medal_fig.add_trace(
                go.Pie(
                    labels=medal_counts['Medal'],
                    values=medal_counts['Count'],
                    marker=dict(colors=[medal_colors[medal] for medal in medal_counts['Medal']]),
                    textinfo='label+percent',
                    hole=0.3,
                    pull=[0.1 if medal == 'Gold' else 0 for medal in medal_counts['Medal']],
                    domain=dict(x=[0, 0.45])
                ),
                row=1, col=1
            )
            
            # Add historical trend - medals over time
            # Group by year and medal type
            try:
                yearly_medals = unique_medal_df.groupby(['Year', 'Medal']).size().reset_index(name='Count')
                yearly_medals = yearly_medals.pivot(index='Year', columns='Medal', values='Count').fillna(0).reset_index()
                
                # Ensure all medal types are present
                for medal in medal_types:
                    if medal not in yearly_medals.columns:
                        yearly_medals[medal] = 0
                
                # Sort by year
                yearly_medals = yearly_medals.sort_values('Year')
                
                # Add stacked area chart for historical performance
                for medal in medal_types:
                    if medal in yearly_medals.columns:
                        medal_fig.add_trace(
                            go.Scatter(
                                x=yearly_medals['Year'],
                                y=yearly_medals[medal],
                                mode='lines',
                                stackgroup='one',
                                name=medal,
                                line=dict(color=medal_colors[medal], width=0.5),
                                hovertemplate='%{y} %{fullData.name} medals in %{x}<extra></extra>'
                            ),
                            row=1, col=2
                        )
            except Exception as e:
                print(f"Error creating historical medal chart: {e}")
                # Add a blank chart with error message
                medal_fig.add_trace(
                    go.Scatter(
                        x=[0],
                        y=[0],
                        text=["Not enough historical data"],
                        mode="text"
                    ),
                    row=1, col=2
                )
            
            # Add top countries as annotations
            if medal_countries > 0:
                top_countries = unique_medal_df['region'].value_counts().head(5)
                top_country_text = "<br>".join([f"{country}: {count} medals" for country, count in zip(top_countries.index, top_countries.values)])
                
                medal_fig.add_annotation(
                    x=0.5,
                    y=-0.15,
                    text=f"<b>Top Countries:</b><br>{top_country_text}",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    align="center",
                    bordercolor="white",
                    borderwidth=1,
                    borderpad=4,
                    bgcolor="rgba(55, 83, 109, 0.7)",
                    font=dict(size=12)
                )
            
            # Update layout
            medal_fig.update_layout(
                title=f"{selected_sport} - Medal Analysis (Total events: {total_events}, Countries with medals: {medal_countries})",
                template='plotly_dark',
                height=600,
                showlegend=True,
                legend=dict(
                    orientation='h',
                    yanchor='bottom',
                    y=1.02,
                    xanchor='right',
                    x=1
                )
            )
            
            # Update x-axis for historical chart
            medal_fig.update_xaxes(title_text="Olympic Year", row=1, col=2)
            medal_fig.update_yaxes(title_text="Medal Count", row=1, col=2)
            
        else:
            medal_fig.update_layout(
                title=f"No medal data available for {selected_sport}",
                template='plotly_dark',
                height=600
            )
        
        return phys_fig, medal_fig
    except Exception as e:
        # Return empty figure with error message
        error_fig = go.Figure()
        error_fig.update_layout(
            title=f"Error creating charts: {str(e)}",
            template='plotly_dark',
            height=600
        )
        return error_fig, error_fig

def create_gender_participation_chart(filtered_df):
    """Create a visualization of gender participation trends"""
    if filtered_df.empty:
        # Return empty figure with text if no data
        fig = go.Figure()
        fig.update_layout(
            title="No data available for the selected filters",
            template='plotly_dark',
            height=600
        )
        return fig
        
    try:
        # Group by year and gender
        gender_counts = filtered_df.groupby(['Year', 'Gender']).size().reset_index(name='Count')
        
        # Pivot the data to get separate columns for male and female counts
        gender_pivot = gender_counts.pivot(index='Year', columns='Gender', values='Count').reset_index()
        gender_pivot.fillna(0, inplace=True)
        
        # Ensure the columns exist
        for col in ['F', 'M']:
            if col not in gender_pivot.columns:
                gender_pivot[col] = 0
        
        # Calculate the percentage
        gender_pivot['Total'] = gender_pivot['F'] + gender_pivot['M']
        gender_pivot['Female_Pct'] = (gender_pivot['F'] / gender_pivot['Total'] * 100).round(1)
        gender_pivot['Male_Pct'] = (gender_pivot['M'] / gender_pivot['Total'] * 100).round(1)
        
        # Convert Year to int
        gender_pivot['Year'] = gender_pivot['Year'].astype(int)
        
        # Create a stacked bar chart
        fig = go.Figure()
        
        # Add female percentage bars
        fig.add_trace(go.Bar(
            x=gender_pivot['Year'],
            y=gender_pivot['Female_Pct'],
            name='Female',
            marker_color='#FF69B4'
        ))
        
        # Add male percentage bars
        fig.add_trace(go.Bar(
            x=gender_pivot['Year'],
            y=gender_pivot['Male_Pct'],
            name='Male',
            marker_color='#1E90FF'
        ))
        
        # Add a line showing female percentage
        fig.add_trace(go.Scatter(
            x=gender_pivot['Year'],
            y=gender_pivot['Female_Pct'],
            mode='lines+markers',
            name='Female %',
            line=dict(color='white', width=2),
            yaxis='y2'
        ))
        
        # Set up the layout with two y-axes
        fig.update_layout(
            title='Gender Distribution in Olympic Games Over Time',
            xaxis_title='Olympic Year',
            yaxis=dict(
                title='Percentage (%)',
                range=[0, 100]
            ),
            yaxis2=dict(
                title='Female Participation (%)',
                overlaying='y',
                side='right',
                range=[0, 100],
                showgrid=False,
                showticklabels=False
            ),
            barmode='stack',
            template='plotly_dark',
            height=600,
            margin=dict(l=50, r=50, t=70, b=50),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )
        
        return fig
        
    except Exception as e:
        # Return empty figure with error message
        fig = go.Figure()
        fig.update_layout(
            title=f"Error creating chart: {str(e)}",
            template='plotly_dark',
            height=600
        )
        return fig

# Constants for styling
PLOTLY_TEMPLATE = "plotly_white"
olympic_colors = ["primary", "warning", "info", "success", "danger"]
card_style = {"backgroundColor": "#ffffff", "border": "1px solid #dee2e6"}
card_header_style = {"backgroundColor": "#e9ecef", "fontWeight": "600", "borderBottom": "1px solid #dee2e6"}
plot_card_body_style = {"padding": "0.5rem"}

layout = dbc.Container([
    # Hero Section
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Advanced Olympic Analysis", className="display-4 text-primary mb-4"),
                html.P("Explore deeper insights and patterns in Olympic data through advanced visualizations and analysis.",
                       className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),
    
    # Title Row
    dbc.Row([
        dbc.Col(html.H3("Advanced Analysis Dashboard", className="text-primary d-inline-block me-3"), width='auto'),
    ], align="center", className="mb-3"),
    
    # Info Alert
    dbc.Alert([
        html.H5("What is this page?", className="alert-heading"),
        html.P("Explore advanced patterns and insights across Olympic history, including athlete characteristics, medal trends, and sport-specific analysis.", className="mb-0")
    ], id='info-alert', color="info", className="shadow-sm mb-4 border border-info"),
    
    # Filters Section
    dbc.Card([
        dbc.CardBody([
            html.H5("Filters", className="card-title text-primary mb-3"),
            dbc.Row([
                dbc.Col([
                    html.Label("Year Range:", className="fw-bold small"),
                    dcc.RangeSlider(
                        id='year-range-slider',
                        min=min_year,
                        max=max_year,
                        step=2,
                        value=[min_year, max_year],
                        marks={str(year): str(year) for year in 
                               range(min_year, max_year + 1, 20)},
                        tooltip={"placement": "bottom", "always_visible": False},
                        className="mb-4"
                    ),
                ], width=12, lg=6),
                
                dbc.Col([
                    html.Label("Season:", className="fw-bold small d-block mb-2"),
                    dbc.RadioItems(
                        id='season-toggle',
                        options=[{"label": "All", "value": "All"}, 
                               {"label": "Summer", "value": "Summer"}, 
                               {"label": "Winter", "value": "Winter"}],
                        value="All",
                        inline=True,
                        className="mb-4"
                    ),
                ], width=12, lg=3),
                
                dbc.Col([
                    html.Label("Sport:", className="fw-bold small"),
                    dcc.Dropdown(
                        id='sport-characteristics-dropdown',
                        options=[{'label': 'All Sports', 'value': 'All'}] + 
                               [{'label': sport, 'value': sport} for sport in sports_list],
                        value='All',
                        clearable=False,
                        className="mb-4"
                    ),
                ], width=12, lg=3),
            ]),
            
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Update Analysis",
                        id="update-button",
                        color="primary",
                        className="w-100"
                    ),
                ], width=12),
            ]),
        ])
    ], className="mb-4 shadow bg-light border-secondary"),
    
    # Analysis Summary
    dbc.Row([
        dbc.Col([
            html.Div(id="filter-summary", className="text-muted mb-4")
        ])
    ]),
    
    # Main Analysis Section
    dbc.Tabs([
        # Medal Analysis Tab
        dbc.Tab([
            dbc.Row([
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Medal Trends Over Time", style=card_header_style, className=f"fw-bold text-{olympic_colors[0]}"),
                    dbc.CardBody(dcc.Graph(id='medal-trend-chart'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, className="mb-4"),
            ], className="align-items-stretch g-4"),
        ], label="Medal Trends"),
        
        # Physical Characteristics Tab
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dbc.Alert([
                        html.H5("Select a Sport", className="alert-heading"),
                        html.P("Please select a specific sport from the dropdown above to view its physical characteristics.", className="mb-0")
                    ], id='sport-selection-alert-physical', color="info", className="shadow-sm mb-4 border border-info"),
                ], width=12),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Sport-Attribute Heatmap", style=card_header_style, className=f"fw-bold text-{olympic_colors[1]}"),
                    dbc.CardBody(dcc.Graph(id='sport-heatmap'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, lg=6, className="mb-4"),
                
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("3D Sport Characteristics", style=card_header_style, className=f"fw-bold text-{olympic_colors[2]}"),
                    dbc.CardBody(dcc.Graph(id='sport-3d-scatter'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, lg=6, className="mb-4"),
            ], className="align-items-stretch g-4"),
        ], label="Physical Characteristics"),
        
        # Age Analysis Tab
        dbc.Tab([
            dbc.Row([
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Age Evolution", style=card_header_style, className=f"fw-bold text-{olympic_colors[3]}"),
                    dbc.CardBody(dcc.Graph(id='age-evolution-chart'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, className="mb-4"),
            ], className="align-items-stretch g-4"),
        ], label="Age Analysis"),
        
        # Gender Analysis Tab
        dbc.Tab([
            dbc.Row([
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Gender Participation", style=card_header_style, className=f"fw-bold text-{olympic_colors[4]}"),
                    dbc.CardBody(dcc.Graph(id='gender-participation-chart'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, className="mb-4"),
            ], className="align-items-stretch g-4"),
        ], label="Gender Analysis"),
        
        # Sport Deep Dive Tab
        dbc.Tab([
            dbc.Row([
                dbc.Col([
                    dbc.Alert([
                        html.H5("Select a Sport", className="alert-heading"),
                        html.P("Please select a specific sport from the dropdown above to view detailed sport characteristics and statistics.", className="mb-0")
                    ], id='sport-selection-alert-deepdive', color="info", className="shadow-sm mb-4 border border-info"),
                ], width=12),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Sport Characteristics", style=card_header_style, className=f"fw-bold text-{olympic_colors[0]}"),
                    dbc.CardBody(dcc.Graph(id='sport-radar-chart'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, lg=6, className="mb-4"),
                
                dbc.Col(dbc.Card(children=[
                    dbc.CardHeader("Sport Statistics", style=card_header_style, className=f"fw-bold text-{olympic_colors[1]}"),
                    dbc.CardBody(html.Div(id='sport-stats-card'), style=plot_card_body_style)
                ], style=card_style, className="h-100 chart-card animate-slide"), width=12, lg=6, className="mb-4"),
            ], className="align-items-stretch g-4"),
        ], label="Sport Deep Dive"),
    ], className="mb-4"),
    
    # Hidden div for page load trigger
    html.Div(id='page-load-trigger', style={'display': 'none'}),
    
], fluid=True, className="pt-3 pb-5 bg-light text-dark")

@callback(
    [Output('medal-trend-chart', 'figure'),
     Output('age-evolution-chart', 'figure'),
     Output('sport-heatmap', 'figure'),
     Output('gender-participation-chart', 'figure'),
     Output('filter-summary', 'children')],
    [Input('update-button', 'n_clicks')],
    [State('year-range-slider', 'value'),
     State('season-toggle', 'value')],
    prevent_initial_call=False
)
def update_all_visualizations(n_clicks, year_range, season):
    # Apply filters
    filtered_df = olympic_df.copy()
    
    # Create default empty figures in case of errors
    default_fig = go.Figure()
    default_fig.update_layout(title="Loading data...", template='plotly_dark')
    
    try:
        # Year range filter - ensure int type
        if year_range:
            year_range = [int(year_range[0]), int(year_range[1])]
            filtered_df = filtered_df[(filtered_df['Year'] >= year_range[0]) & 
                                    (filtered_df['Year'] <= year_range[1])]
        
        # Season filter - handle "All" case
        if season and season != "All":
            filtered_df = filtered_df[filtered_df['Season'] == season]
        
        # Create filter summary text
        year_text = f"{year_range[0]}-{year_range[1]}" if year_range else "All years"
        season_text = season if season else "All seasons"
        filter_summary = f"Showing: {year_text}, {season_text}"
        
        # Generate all visualizations
        medal_trend = create_medal_trend_chart(filtered_df)
        age_evolution = create_age_evolution_chart(filtered_df)
        sport_heatmap = create_sport_heatmap(filtered_df)
        gender_participation = create_gender_participation_chart(filtered_df)
        
        return medal_trend, age_evolution, sport_heatmap, gender_participation, filter_summary
    
    except Exception as e:
        print(f"Error updating visualizations: {e}")
        return default_fig, default_fig, default_fig, default_fig, f"Error: {str(e)}"

# Separate callback for the Sport Characteristics visualizations
@callback(
    [Output('sport-radar-chart', 'figure'),
     Output('sport-3d-scatter', 'figure')],
    [Input('update-button', 'n_clicks'),
     Input('sport-characteristics-dropdown', 'value')],
    [State('year-range-slider', 'value'),
     State('season-toggle', 'value')],
    prevent_initial_call=False
)
def update_sport_characteristics(n_clicks, selected_sport, year_range, season):
    # Apply filters
    filtered_df = olympic_df.copy()
    
    # Create default empty figure in case of errors
    default_fig = go.Figure()
    default_fig.update_layout(title="Loading data...", template='plotly_dark')
    
    try:
        # Year range filter - ensure int type
        if year_range:
            year_range = [int(year_range[0]), int(year_range[1])]
            filtered_df = filtered_df[(filtered_df['Year'] >= year_range[0]) & 
                                    (filtered_df['Year'] <= year_range[1])]
        
        # Season filter - handle "All" case
        if season and season != "All":
            filtered_df = filtered_df[filtered_df['Season'] == season]
        
        # Generate characteristics charts with selected sport
        radar_fig, scatter_3d_fig = create_sport_characteristics(filtered_df, selected_sport)
        
        return radar_fig, scatter_3d_fig
    
    except Exception as e:
        print(f"Error updating sport characteristics: {e}")
        return default_fig, default_fig

# Initialize the page on load
@callback(
    Output('page-load-trigger', 'children'),
    Input('page-load-trigger', 'children')
)
def initialize_page(_):
    # This callback runs on page load and doesn't need to return anything meaningful
    return "Page initialized"