# pages/comparison.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.exceptions import PreventUpdate
from data_loader import df, NOC_OPTIONS_NO_ALL, get_default_value # Use NOC_OPTIONS_NO_ALL

dash.register_page(__name__, name='Country Comparison')

# Use helper for default values, ensuring they are different if possible
default_noc1 = get_default_value(NOC_OPTIONS_NO_ALL)
default_noc2 = NOC_OPTIONS_NO_ALL[1]['value'] if len(NOC_OPTIONS_NO_ALL) > 1 else default_noc1


layout = dbc.Container([
    html.H3("Compare Two Countries"),
    html.Hr(),
    dbc.Row([
        dbc.Col([
            html.Label("Select Country 1 (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='comparison-noc1-dropdown',
                options=NOC_OPTIONS_NO_ALL, # Use NOC options without 'All'
                value=default_noc1,
                clearable=False,
            )
        ], width=12, md=6, lg=4, className="mb-2 mb-md-0"),
        dbc.Col([
            html.Label("Select Country 2 (NOC):", className="fw-bold"),
            dcc.Dropdown(
                id='comparison-noc2-dropdown',
                options=NOC_OPTIONS_NO_ALL,
                value=default_noc2,
                clearable=False,
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

    # --- Prepare Deduplicated Medal Data --- 
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

    fig_overall_medals = px.bar(comp_df,
                                x='Medal', y='Count', color='NOC',
                                barmode='group',
                                title=f"Overall Medal Comparison: {noc1} vs {noc2}",
                                labels={'Medal': 'Medal Type', 'Count': 'Total Medals Won'},
                                category_orders={"Medal": ["Gold", "Silver", "Bronze"]},
                                color_discrete_sequence=px.colors.qualitative.Plotly,
                                template='plotly_white')
    fig_overall_medals.update_layout(legend_title_text='Country')

    # --- Comparison 2: Medal Trend Head-to-Head --- 
    trend1 = unique_medals_noc1.groupby('Year').size().reset_index(name=noc1)
    trend2 = unique_medals_noc2.groupby('Year').size().reset_index(name=noc2)
    
    # Merge trends on Year, fill missing years with 0
    medal_trend_df = pd.merge(trend1, trend2, on='Year', how='outer').fillna(0).sort_values('Year')

    fig_medal_trend = px.line(medal_trend_df, x='Year', y=[noc1, noc2],
                              title=f"Medal Trend Comparison: {noc1} vs {noc2}",
                              labels={'value': 'Medals Won', 'variable': 'Country'},
                              markers=True,
                              template='plotly_white')
    fig_medal_trend.update_layout(xaxis_title='Year', yaxis_title='Total Unique Medals Won', hovermode="x unified")

    # --- Comparison 3: Athlete Participation Trend --- 
    athletes1 = df_noc1.drop_duplicates(['Year', 'Name']).groupby('Year').size().reset_index(name=noc1)
    athletes2 = df_noc2.drop_duplicates(['Year', 'Name']).groupby('Year').size().reset_index(name=noc2)
    
    athlete_trend_df = pd.merge(athletes1, athletes2, on='Year', how='outer').fillna(0).sort_values('Year')

    fig_athlete_trend = px.line(athlete_trend_df, x='Year', y=[noc1, noc2],
                                title=f"Athlete Participation Trend: {noc1} vs {noc2}",
                                labels={'value': 'Unique Athletes', 'variable': 'Country'},
                                markers=True,
                                template='plotly_white')
    fig_athlete_trend.update_layout(xaxis_title='Year', yaxis_title='Number of Unique Athletes', hovermode="x unified")

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
                                   title=f"Medal Comparison in Top 10 Common Sports",
                                   labels={'Medals': 'Total Medals Won'},
                                   template='plotly_white')
        fig_common_sports.update_layout(xaxis_title='Sport', yaxis_title='Medals Won', legend_title_text='Country')
        common_sports_card = dcc.Graph(figure=fig_common_sports)

    # --- Assemble Layout --- 
    visual_layout = html.Div([
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_overall_medals), width=12, lg=6, className="mb-4"),
            dbc.Col(dcc.Graph(figure=fig_medal_trend), width=12, lg=6, className="mb-4"),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_athlete_trend), width=12, lg=6, className="mb-4"),
            dbc.Col(common_sports_card, width=12, lg=6, className="mb-4"), # Use the card/alert here
        ])
    ])

    return visual_layout