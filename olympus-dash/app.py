# app.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import os

# Disable debug UI
os.environ["DASH_DEBUG"] = "false"
os.environ["DASH_PROPS_CHECK"] = "false"

# Init app
app = dash.Dash(__name__,
                use_pages=True,
                external_stylesheets=[
                    dbc.themes.FLATLY,
                    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css',
                    '/assets/country_profile.css'
                ],
                suppress_callback_exceptions=True
               )
app.title = "Olympus Insight"
server = app.server

# Page order
desired_order = [
    "Home",
    "Country Profile",
    "Country Comparison",
    "Globe View",
    "Olympic Year",
    "Sport Profile",
    "Host Analysis",
    "Economic Factors (HDI)",
    "More Analysis",
    "Prediction",
    "Acknowledgement"
]

# Nav items and quick access buttons
nav_items = []
quick_access_buttons = []
page_map = {page['name']: page for page in dash.page_registry.values() if page['module'] != 'pages.not_found_404'}

for name in desired_order:
    if name in page_map:
        page = page_map[name]
        icon_class = {
            "Home": "house-fill",
            "Country Comparison": "bar-chart-fill",
            "Country Profile": "flag-fill",
            "Globe View": "globe2",
            "Host Analysis": "geo-alt-fill",
            "Olympic Year": "calendar-event-fill",
            "Prediction": "graph-up-arrow",
            "Sport Profile": "trophy-fill",
            "More Analysis": "clipboard-data",
            "Economic Factors (HDI)": "cash-coin",
            "Acknowledgement": "info-circle-fill"
        }.get(name, "circle-fill")
        
        nav_items.append(
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className=f"bi bi-{icon_class} me-2"),
                        name
                    ],
                    href=page['relative_path'],
                    active="exact"
                )
            )
        )
        
        quick_access_buttons.append(
            html.A(
                html.I(className=f"bi bi-{icon_class}"),
                href=page['relative_path'],
                className="quick-access-btn",
                title=name
            )
        )

# Sidebar
sidebar = html.Div(
    [
        html.Div(
            [
                html.Div([
                    html.I(className="bi bi-bar-chart-fill me-2"),
                    "Olympus Insight"
                ], className="sidebar-brand"),
                html.I(className="bi bi-x-lg", id="close-sidebar-btn"),
            ],
            className="sidebar-header"
        ),
        html.Hr(),
        
        html.Div(
            [
                dbc.Nav(
                    nav_items,
                    vertical=True,
                    pills=True,
                    className="sidebar-nav-items",
                    id="sidebar-navigation-links"
                )
            ],
            className="sidebar-nav-section"
        ),
        
        html.Div(
            [
                html.Hr(),
                html.Small(
                    "Group 10 - CS661 Big Data Visual Analytics",
                    className="text-white d-block text-center"
                )
            ],
            className="sidebar-footer"
        )
    ],
    id="sidebar",
    className="sidebar-nav"
)

# Quick Access Panel
quick_access_panel = html.Div(
    quick_access_buttons,
    id="quick-access-panel",
    className="quick-access-panel"
)

# App layout
app.layout = html.Div(
    [
        html.Button(
    [
                html.Div(className="toggle-btn-line"),
                html.Div(className="toggle-btn-line"),
                html.Div(className="toggle-btn-line")
            ],
            id="sidebar-toggle",
            className="sidebar-toggle-btn"
        ),

        quick_access_panel,
        sidebar,
        
        html.Div(
            [
                html.Div(
                    dbc.Container(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Img(src="assets/logo.png", height=70, className="me-2"),
                                            html.Span("Olympus Insights", className="ms-3")
                                        ],
                                        className="header-brand"
                                    ),
                                ],
                                className="d-flex align-items-center justify-content-center w-100"
                            ),
                        ],
                        fluid=True,
                        className="header-container"
                    ),
                    className="page-header"
                ),
                dbc.Container(
        dash.page_container,
                    fluid=True,
                    className="content-container",
                    style={
                        "transition": "margin-left 0.3s ease-in-out"
                    }
                )
            ],
            id="page-content",
            className="main-content"
        ),
        
        dcc.Store(id="sidebar-state", data={"is_open": True})
    ],
    className="wrapper"
)

# Toggle sidebar callback
@app.callback(
    [Output("sidebar", "className"),
     Output("page-content", "className"),
     Output("quick-access-panel", "className"),
     Output("sidebar-state", "data")],
    [Input("sidebar-toggle", "n_clicks"),
     Input("close-sidebar-btn", "n_clicks")],
    [State("sidebar-state", "data")]
)
def toggle_sidebar(toggle_clicks, close_clicks, sidebar_state):
    ctx = dash.callback_context
    if not ctx.triggered:
        is_open = sidebar_state.get("is_open", True)
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        is_open = not sidebar_state.get("is_open", True) if button_id == "sidebar-toggle" else False
    
    sidebar_class = "sidebar-nav active" if is_open else "sidebar-nav"
    content_class = "main-content shifted" if is_open else "main-content"
    quick_access_class = "quick-access-panel" if not is_open else "quick-access-panel hidden"
    
    return sidebar_class, content_class, quick_access_class, {"is_open": is_open}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=8050)