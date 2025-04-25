# pages/comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from dash.exceptions import PreventUpdate
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value # Use NOC_OPTIONS_NO_ALL

dash.register_page(__name__, name='Country Comparison')

# Use helper for default values, ensuring they are different if possible
default_noc1 = get_default_value(NOC_OPTIONS_NO_ALL)
default_noc2 = NOC_OPTIONS_NO_ALL[1]['value'] if len(NOC_OPTIONS_NO_ALL) > 1 else default_noc1


layout = dbc.Container([
    # --- Hero Section ---
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H1("Country Comparison", className="display-4 text-primary mb-4"),
                html.P("Compare Olympic performance metrics and statistics between two countries.", 
                      className="lead text-muted mb-5")
            ], className="text-center hero-content")
        ], width=12)
    ], className="mb-4"),

    # --- Description ---
    dbc.Row([
        dbc.Col([
            html.P("Select two countries to compare their Olympic achievements, participation trends, and performance metrics.", 
                  className="lead text-muted mb-4")
        ], width=12)
    ]),
    
    # Country Selection
    dbc.Row([
        dbc.Col([
            html.Label("Select Country 1 (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='comparison-noc1-dropdown',
                options=NOC_OPTIONS_NO_ALL, # Use NOC options without 'All'
                value=default_noc1,
                clearable=False,
                optionHeight=60,  # Increased height for multi-line country names with flags
                style={'minWidth': '300px'} # Ensure dropdown is wide enough
            )
        ], width=12, md=6, lg=4, className="mb-2 mb-md-0"),
        dbc.Col([
            html.Label("Select Country 2 (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='comparison-noc2-dropdown',
                options=NOC_OPTIONS_NO_ALL,
                value=default_noc2,
                clearable=False,
                optionHeight=60,  # Increased height for multi-line country names with flags
                style={'minWidth': '300px'} # Ensure dropdown is wide enough
            )
        ], width=12, md=6, lg=4),
    ]),
    html.Hr(),
    # Placeholder for Comparison visuals
    dbc.Spinner(html.Div(id='comparison-visuals'))
])

@callback(
    Output('comparison-visuals', 'children'),
    Input('comparison-noc1-dropdown', 'value'),
    Input('comparison-noc2-dropdown', 'value')
)
def update_comparison_visuals(noc1, noc2):
    if not noc1 or not noc2:
        return dbc.Alert("Please select two countries to compare.", color="warning")

    if noc1 == noc2:
        return dbc.Alert("Please select two different countries.", color="warning")

    if df.empty:
        return dbc.Alert("Data not loaded.", color="danger")

    # Filter data for both countries
    df_noc1 = df[df['NOC'] == noc1].copy()
    df_noc2 = df[df['NOC'] == noc2].copy()

    if df_noc1.empty or df_noc2.empty:
        missing_noc = noc1 if df_noc1.empty else noc2
        return dbc.Alert(f"No data found for {missing_noc}. Cannot perform comparison.", color="warning")

    # --- Prepare Deduplicated Medal Data & Base Athlete Data --- 
    medals_noc1 = df_noc1[df_noc1['Medal'] != 'None'].copy()
    medals_noc2 = df_noc2[df_noc2['Medal'] != 'None'].copy()

    unique_medals_noc1 = medals_noc1.drop_duplicates(subset=['Year', 'Season', 'Event', 'Medal'])
    unique_medals_noc2 = medals_noc2.drop_duplicates(subset=['Year', 'Season', 'Event', 'Medal'])

    # --- Comparison 1: Overall Medal Counts --- 
    counts1 = unique_medals_noc1['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze'], fill_value=0)
    counts2 = unique_medals_noc2['Medal'].value_counts().reindex(['Gold', 'Silver', 'Bronze'], fill_value=0)

    comp_df = pd.DataFrame({
        'Medal': ['Gold', 'Silver', 'Bronze'],
        noc1: counts1.values,
        noc2: counts2.values
    }).melt(id_vars='Medal', var_name='NOC', value_name='Count')

    fig_overall_medals = px.bar(comp_df, x='Medal', y='Count', color='NOC', barmode='group',
                                labels={'Medal': 'Medal Type', 'Count': 'Total Medals Won'},
                                category_orders={"Medal": ["Gold", "Silver", "Bronze"]},
                                color_discrete_sequence=px.colors.qualitative.Plotly,
                                template='plotly_white')
    fig_overall_medals.update_layout(legend_title_text='Country', title=None)

    # --- Comparison 2: Medal Trend Head-to-Head --- 
    trend1 = unique_medals_noc1.groupby('Year').size().reset_index(name=noc1)
    trend2 = unique_medals_noc2.groupby('Year').size().reset_index(name=noc2)
    
    # Merge trends on Year, fill missing years with 0
    medal_trend_df = pd.merge(trend1, trend2, on='Year', how='outer').fillna(0).sort_values('Year')

    fig_medal_trend = px.line(medal_trend_df, x='Year', y=[noc1, noc2],
                              labels={'value': 'Medals Won', 'variable': 'Country'},
                              markers=True,
                              template='plotly_white')
    fig_medal_trend.update_layout(xaxis_title='Year', yaxis_title='Total Unique Medals Won', hovermode="x unified", title=None)

    # --- NEW: Radar Chart for Performance Metrics --- 
    # Calculate metrics for radar chart
    # Metrics: Total medals, Gold ratio, Athlete efficiency, Summer medals, Winter medals
    
    # NOC1 metrics
    total_medals1 = unique_medals_noc1.shape[0]
    gold_ratio1 = counts1['Gold'] / total_medals1 if total_medals1 > 0 else 0
    
    unique_athletes1 = df_noc1['Name'].nunique()
    athlete_efficiency1 = total_medals1 / unique_athletes1 if unique_athletes1 > 0 else 0
    
    summer_medals1 = unique_medals_noc1[unique_medals_noc1['Season'] == 'Summer'].shape[0]
    winter_medals1 = unique_medals_noc1[unique_medals_noc1['Season'] == 'Winter'].shape[0]
    
    # NOC2 metrics
    total_medals2 = unique_medals_noc2.shape[0]
    gold_ratio2 = counts2['Gold'] / total_medals2 if total_medals2 > 0 else 0
    
    unique_athletes2 = df_noc2['Name'].nunique()
    athlete_efficiency2 = total_medals2 / unique_athletes2 if unique_athletes2 > 0 else 0
    
    summer_medals2 = unique_medals_noc2[unique_medals_noc2['Season'] == 'Summer'].shape[0]
    winter_medals2 = unique_medals_noc2[unique_medals_noc2['Season'] == 'Winter'].shape[0]
    
    # Find max values to normalize metrics (to range 0-1 for radar)
    max_total = max(total_medals1, total_medals2)
    max_gold_ratio = 1  # Already ratio 0-1
    max_efficiency = max(athlete_efficiency1, athlete_efficiency2)
    max_summer = max(summer_medals1, summer_medals2)
    max_winter = max(winter_medals1, winter_medals2)
    
    # Normalize to 0-1 scale, add small epsilon to avoid division by zero
    epsilon = 1e-10
    categories = ['Total Medals', 'Gold Medal Ratio', 'Medals per Athlete', 'Summer Medals', 'Winter Medals']
    
    values1 = [
        total_medals1 / (max_total + epsilon),
        gold_ratio1,
        athlete_efficiency1 / (max_efficiency + epsilon),
        summer_medals1 / (max_summer + epsilon),
        winter_medals1 / (max_winter + epsilon)
    ]
    
    values2 = [
        total_medals2 / (max_total + epsilon),
        gold_ratio2,
        athlete_efficiency2 / (max_efficiency + epsilon),
        summer_medals2 / (max_summer + epsilon),
        winter_medals2 / (max_winter + epsilon)
    ]
    
    # Build radar chart
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values1,
        theta=categories,
        fill='toself',
        name=noc1
    ))
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values2,
        theta=categories,
        fill='toself',
        name=noc2
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        template='plotly_white'
    )
    
    # --- NEW: Bubble Chart for Top Sports ---
    # Get medal counts by sport for each country
    sport_medals1 = unique_medals_noc1.groupby('Sport').size().reset_index(name='Medals')
    sport_medals2 = unique_medals_noc2.groupby('Sport').size().reset_index(name='Medals')
    
    # Combine the data
    sport_medals1['NOC'] = noc1
    sport_medals2['NOC'] = noc2
    sport_medals_combined = pd.concat([sport_medals1, sport_medals2])
    
    # Create a pivot table for easier plotting
    sport_pivot = sport_medals_combined.pivot_table(
        index='Sport', 
        columns='NOC', 
        values='Medals',
        fill_value=0
    ).reset_index()
    
    # Calculate total medals for sizing and filtering
    sport_pivot['Total'] = sport_pivot[noc1] + sport_pivot[noc2]
    
    # Filter to top sports by total medals
    top_sports = sport_pivot.nlargest(15, 'Total')
    
    # Create bubble chart
    fig_bubble = px.scatter(
        top_sports,
        x=noc1,
        y=noc2,
        size='Total',
        color='Sport',
        hover_name='Sport',
        log_x=True if top_sports[noc1].max() > 50 else False,
        log_y=True if top_sports[noc2].max() > 50 else False,
        size_max=50,
        template='plotly_white'
    )
    
    # Add diagonal line for equal performance
    max_val = max(top_sports[noc1].max(), top_sports[noc2].max())
    fig_bubble.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color='lightgray', dash='dash'),
            showlegend=False
        )
    )
    
    fig_bubble.update_layout(
        xaxis_title=f"{noc1} Medals",
        yaxis_title=f"{noc2} Medals",
        title=None
    )
    
    # --- Comparison 3: Athlete Participation Trend --- 
    athletes1 = df_noc1.drop_duplicates(['Year', 'Name']).groupby('Year').size().reset_index(name=noc1)
    athletes2 = df_noc2.drop_duplicates(['Year', 'Name']).groupby('Year').size().reset_index(name=noc2)
    
    athlete_trend_df = pd.merge(athletes1, athletes2, on='Year', how='outer').fillna(0).sort_values('Year')

    fig_athlete_trend = px.line(athlete_trend_df, x='Year', y=[noc1, noc2],
                                labels={'value': 'Unique Athletes', 'variable': 'Country'},
                                markers=True,
                                template='plotly_white')
    fig_athlete_trend.update_layout(xaxis_title='Year', yaxis_title='Number of Unique Athletes', hovermode="x unified", title=None)

    # --- Comparison 4: Top Common Sports --- 
    sports1 = set(unique_medals_noc1['Sport'].unique())
    sports2 = set(unique_medals_noc2['Sport'].unique())
    common_sports = list(sports1.intersection(sports2))
    
    common_sports_card = dbc.Alert("No common sports found where both countries won medals.", color="info")
    if common_sports:
        common1 = unique_medals_noc1[unique_medals_noc1['Sport'].isin(common_sports)]
        common2 = unique_medals_noc2[unique_medals_noc2['Sport'].isin(common_sports)]
        
        counts_common1 = common1.groupby('Sport').size().reset_index(name=noc1)
        counts_common2 = common2.groupby('Sport').size().reset_index(name=noc2)
        
        common_sports_df = pd.merge(counts_common1, counts_common2, on='Sport', how='outer').fillna(0)
        # Calculate total medals in common sports for sorting
        common_sports_df['Total'] = common_sports_df[noc1] + common_sports_df[noc2]
        common_sports_df = common_sports_df.sort_values('Total', ascending=False).head(10) # Top 10 common
        
        common_sports_melted = common_sports_df.melt(id_vars='Sport', value_vars=[noc1, noc2], var_name='NOC', value_name='Medals')
        
        fig_common_sports = px.bar(common_sports_melted, x='Sport', y='Medals', color='NOC',
                                   barmode='group',
                                   labels={'Medals': 'Total Medals Won'},
                                   template='plotly_white')
        fig_common_sports.update_layout(xaxis_title='Sport', yaxis_title='Medals Won', legend_title_text='Country', title=None)
        common_sports_card = dcc.Graph(figure=fig_common_sports)

    # --- Comparison 5: Medal Efficiency Trend --- 
    athletes1_yr = df_noc1.drop_duplicates(['Year', 'Name']).groupby('Year').size().reset_index(name='Athletes')
    athletes2_yr = df_noc2.drop_duplicates(['Year', 'Name']).groupby('Year').size().reset_index(name='Athletes')
    medals1_yr = unique_medals_noc1.groupby('Year').size().reset_index(name='Medals')
    medals2_yr = unique_medals_noc2.groupby('Year').size().reset_index(name='Medals')

    eff1 = pd.merge(athletes1_yr, medals1_yr, on='Year', how='left').fillna(0)
    eff2 = pd.merge(athletes2_yr, medals2_yr, on='Year', how='left').fillna(0)

    # --- FIX: Calculate efficiency using .loc for robustness ---
    eff1['Efficiency'] = 0.0 # Initialize
    eff1.loc[eff1['Athletes'] > 0, 'Efficiency'] = eff1['Medals'] / eff1['Athletes']

    eff2['Efficiency'] = 0.0 # Initialize
    eff2.loc[eff2['Athletes'] > 0, 'Efficiency'] = eff2['Medals'] / eff2['Athletes']
    # --- End FIX ---

    eff1['NOC'] = noc1
    eff2['NOC'] = noc2

    efficiency_df = pd.concat([eff1[['Year', 'NOC', 'Efficiency']], eff2[['Year', 'NOC', 'Efficiency']]])

    fig_efficiency_comp = px.line(efficiency_df, x='Year', y='Efficiency', color='NOC',
                                    labels={'Efficiency': 'Medals per Athlete', 'NOC': 'Country'},
                                    markers=True,
                                    template='plotly_white')
    fig_efficiency_comp.update_layout(yaxis_tickformat='.2f', hovermode="x unified", title=None)

    # --- Comparison 6: Summer vs Winter Medals --- 
    seasonal_medals1 = unique_medals_noc1.groupby('Season').size().reset_index(name='Count')
    seasonal_medals1['NOC'] = noc1
    seasonal_medals2 = unique_medals_noc2.groupby('Season').size().reset_index(name='Count')
    seasonal_medals2['NOC'] = noc2

    seasonal_df = pd.concat([seasonal_medals1, seasonal_medals2])

    fig_season_comp = px.bar(seasonal_df, x='Season', y='Count', color='NOC',
                             barmode='group',
                             labels={'Count': 'Total Unique Medals Won', 'NOC': 'Country'},
                             template='plotly_white')
    fig_season_comp.update_layout(title=None)

    # --- NEW: Animated Time Series of Medal Accumulation ---
    # Create cumulative medal count data for animation
    years = sorted(list(set(unique_medals_noc1['Year'].unique()).union(set(unique_medals_noc2['Year'].unique()))))
    
    # Initialize data structures
    anim_data = []
    medal_count1 = 0
    medal_count2 = 0
    
    for year in years:
        # Count medals for this year
        year_medals1 = unique_medals_noc1[unique_medals_noc1['Year'] == year].shape[0]
        year_medals2 = unique_medals_noc2[unique_medals_noc2['Year'] == year].shape[0]
        
        # Accumulate totals
        medal_count1 += year_medals1
        medal_count2 += year_medals2
        
        # Store frame data
        anim_data.append({
            'Year': year,
            noc1: medal_count1,
            noc2: medal_count2,
            f"{noc1} Year Medals": year_medals1,
            f"{noc2} Year Medals": year_medals2
        })
    
    # Create DataFrame for animation
    anim_df = pd.DataFrame(anim_data)
    
    # Create animated figure
    fig_animation = go.Figure()
    
    # Add traces for cumulative medals
    fig_animation.add_trace(
        go.Scatter(
            x=anim_df['Year'],
            y=anim_df[noc1],
            name=noc1,
            mode='lines+markers',
            line=dict(width=3, color='rgba(255, 127, 14, 1)'),
            marker=dict(size=10, symbol='circle')
        )
    )
    
    fig_animation.add_trace(
        go.Scatter(
            x=anim_df['Year'],
            y=anim_df[noc2],
            name=noc2,
            mode='lines+markers',
            line=dict(width=3, color='rgba(31, 119, 180, 1)'),
            marker=dict(size=10, symbol='circle')
        )
    )
    
    # Add vertical bar annotations for medals won in each year
    for i, year in enumerate(anim_df['Year']):
        if i > 0:  # Skip first year for better visuals
            # Medal counts for this year
            year_medals1 = anim_df.loc[i, f"{noc1} Year Medals"]
            year_medals2 = anim_df.loc[i, f"{noc2} Year Medals"]
            
            # Only add annotations if medals were won
            if year_medals1 > 0:
                fig_animation.add_trace(
                    go.Scatter(
                        x=[year, year],
                        y=[anim_df.loc[i-1, noc1], anim_df.loc[i, noc1]],
                        mode='lines',
                        line=dict(color='rgba(255, 127, 14, 0.5)', width=10),
                        showlegend=False,
                        hoverinfo='text',
                        hovertext=f"{noc1}: +{year_medals1} medals in {year}"
                    )
                )
                
            if year_medals2 > 0:
                fig_animation.add_trace(
                    go.Scatter(
                        x=[year, year],
                        y=[anim_df.loc[i-1, noc2], anim_df.loc[i, noc2]],
                        mode='lines',
                        line=dict(color='rgba(31, 119, 180, 0.5)', width=10),
                        showlegend=False,
                        hoverinfo='text',
                        hovertext=f"{noc2}: +{year_medals2} medals in {year}"
                    )
                )
    
    # Animation settings
    animation_settings = dict(
        frame=dict(duration=800, redraw=True),
        fromcurrent=True,
        transition=dict(duration=500, easing="cubic-in-out")
    )
    
    # Initialize with a subset of the data for animation starting point
    initial_years = years[:max(3, len(years)//8)]  # Show first few years initially
    
    # Set initial range to see first few points clearly
    initial_y_max = max(
        anim_df[anim_df['Year'].isin(initial_years)][noc1].max(),
        anim_df[anim_df['Year'].isin(initial_years)][noc2].max()
    ) * 1.2  # Add 20% padding
    
    # Create frames for animation
    frames = []
    for i in range(len(initial_years), len(years)):
        year_subset = years[:i+1]
        frame_data = anim_df[anim_df['Year'].isin(year_subset)]
        
        frame = go.Frame(
            data=[
                go.Scatter(
                    x=frame_data['Year'],
                    y=frame_data[noc1],
                    mode='lines+markers',
                    line=dict(width=3, color='rgba(255, 127, 14, 1)'),
                    marker=dict(size=10, symbol='circle')
                ),
                go.Scatter(
                    x=frame_data['Year'],
                    y=frame_data[noc2],
                    mode='lines+markers',
                    line=dict(width=3, color='rgba(31, 119, 180, 1)'),
                    marker=dict(size=10, symbol='circle')
                )
            ],
            traces=[0, 1],
            name=f'Frame {i}'
        )
        frames.append(frame)
    
    fig_animation.frames = frames
    
    # Add slider and buttons for animation control
    sliders = [
        dict(
            steps=[
                dict(
                    method="animate",
                    args=[
                        [f'Frame {i}'],
                        dict(
                            mode="immediate",
                            frame=dict(duration=800, redraw=True),
                            transition=dict(duration=500)
                        )
                    ],
                    label=str(years[i]) if i % 4 == 0 else ""  # Only show a subset of years
                )
                for i in range(len(initial_years), len(years))
            ],
            active=0,
            transition=dict(duration=300),
            x=0.1,
            y=0,
            currentvalue=dict(
                font=dict(size=12),
                prefix="Olympic Year: ",
                visible=True,
                xanchor="right"
            ),
            len=0.9
        )
    ]
    
    # Add play and pause buttons
    updatemenus = [
        dict(
            type="buttons",
            buttons=[
                dict(
                    label="▶️ Play",
                    method="animate",
                    args=[
                        None,
                        animation_settings
                    ]
                ),
                dict(
                    label="⏸️ Pause",
                    method="animate",
                    args=[
                        [None],
                        dict(
                            frame=dict(duration=0, redraw=True),
                            mode="immediate",
                            transition=dict(duration=0)
                        )
                    ]
                )
            ],
            direction="left",
            pad=dict(r=10, t=10),
            showactive=False,
            x=0.1,
            y=1.1,
            xanchor="right",
            yanchor="top"
        )
    ]
    
    # Update layout with animation controls
    fig_animation.update_layout(
        title=None,
        updatemenus=updatemenus,
        sliders=sliders,
        template='plotly_white',
        xaxis=dict(
            title="Olympic Year",
            range=[min(years) - 1, max(years) + 1],
            showgrid=True
        ),
        yaxis=dict(
            title="Cumulative Medal Count",
            range=[0, initial_y_max],
            showgrid=True
        ),
        legend=dict(
            title="Country",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=100),
        autosize=True,
        hovermode="x unified"
    )
    
    # Dynamically adjust y-axis based on animation progress
    for i, frame in enumerate(fig_animation.frames):
        current_year_subset = years[:len(initial_years) + i + 1]
        current_data = anim_df[anim_df['Year'].isin(current_year_subset)]
        
        y_max = max(
            current_data[noc1].max(),
            current_data[noc2].max()
        ) * 1.1  # Add 10% padding
        
        frame.layout = go.Layout(
            yaxis=dict(range=[0, y_max])
        )

    # --- Assemble Layout --- 
    visual_layout = html.Div([
        # Row 1 - Original charts
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_overall_medals))), width=12, lg=6, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_medal_trend))), width=12, lg=6, className="mb-4"),
        ]),
        # Row 2
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_athlete_trend))), width=12, lg=6, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(common_sports_card)), width=12, lg=6, className="mb-4"),
        ]),
        # Row 3
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_efficiency_comp))), width=12, lg=6, className="mb-4"),
            dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(figure=fig_season_comp))), width=12, lg=6, className="mb-4"),
        ]),
        # New row - Animated Time Series (full width)
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Animated Medal Accumulation", className="card-title"),
                        html.P("Cumulative medal count over time - press Play to watch the evolution", className="card-subtitle text-muted"),
                        dcc.Graph(figure=fig_animation)
                    ])
                ), 
                width=12, className="mb-4"
            ),
        ]),
        # Last row - Advanced Visualizations
        dbc.Row([
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Performance Metrics Comparison", className="card-title"),
                        html.P("Normalized comparison across key metrics", className="card-subtitle text-muted"),
                        dcc.Graph(figure=fig_radar)
                    ])
                ), 
                width=12, lg=6, className="mb-4"
            ),
            dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5("Sport Performance Comparison", className="card-title"),
                        html.P("Bubble size represents total medals in that sport", className="card-subtitle text-muted"),
                        dcc.Graph(figure=fig_bubble)
                    ])
                ), 
                width=12, lg=6, className="mb-4"
            ),
        ]),
    ])

    return visual_layout