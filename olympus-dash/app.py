# app.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Initialize the app with Bootstrap icons
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

# --- Navigation Items ---
# Define the desired order of page names
desired_order = [
    "Home",
    "Country Comparison",
    "Country Profile",
    "Globe View",
    "Host Analysis",
    "Olympic Year",
    "Prediction",
    "Sport Profile",
    "More Analysis",
    "Acknowledgement"
]

# Create navigation items and quick access buttons
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
            "More Analysis": "graph-up",
            "Acknowledgement": "info-circle-fill"
        }.get(name, "circle-fill")
        
        # Main navigation item with icon-only display option
        nav_items.append(
            dbc.NavItem(
                dbc.NavLink(
                    [
                        html.I(className=f"bi bi-{icon_class}", id=f"nav-icon-{name.lower().replace(' ', '-')}"),
                        html.Span(name, className="nav-text ms-2")
                    ],
                    href=page['relative_path'],
                    active="exact",
                    className="d-flex align-items-center"
                )
            )
        )
        
        # Quick access button - we'll keep these for redundancy
        quick_access_buttons.append(
            html.A(
                html.I(className=f"bi bi-{icon_class}"),
                href=page['relative_path'],
                className="quick-access-btn",
                title=name
            )
        )

# Add custom CSS for improved sidebar behavior
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Enhanced sidebar styling */
            .sidebar-nav {
                width: 260px !important;
                transition: all 0.3s ease;
            }
            
            /* Icons-only mode (collapsed) */
            .sidebar-nav.collapsed {
                width: 70px !important;
            }
            
            .sidebar-nav.collapsed .sidebar-brand span,
            .sidebar-nav.collapsed .nav-text,
            .sidebar-nav.collapsed .sidebar-footer span {
                display: none;
            }
            
            /* Logo styling and alignment */
            .sidebar-brand {
                padding: 0.5rem 1rem;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .sidebar-nav.collapsed .sidebar-brand {
                justify-content: center;
                padding: 0.5rem 0;
            }
            
            /* Center the icons in collapsed mode */
            .sidebar-nav.collapsed .nav-link {
                padding: 10px 0;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .sidebar-nav.collapsed .nav-link i {
                font-size: 1.5rem;
                margin: 0 !important;
            }
            
            /* Consistent padding for all nav items */
            .sidebar-nav-items {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            
            .sidebar-nav.collapsed .sidebar-nav-items {
                padding-left: 0;
                padding-right: 0;
            }
            
            .sidebar-nav.collapsed:hover {
                width: 260px !important;
            }
            
            .sidebar-nav.collapsed:hover .sidebar-brand span,
            .sidebar-nav.collapsed:hover .nav-text,
            .sidebar-nav.collapsed:hover .sidebar-footer span {
                display: inline-block;
            }
            
            /* Reset icon styling when expanded */
            .sidebar-nav.collapsed:hover .nav-link {
                padding: 0.5rem 1rem;
                justify-content: flex-start;
            }
            
            .sidebar-nav.collapsed:hover .nav-link i {
                font-size: 1rem;
                margin-right: 0.5rem !important;
            }
            
            .sidebar-nav.collapsed:hover .sidebar-nav-items {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
            
            /* Adjust main content accordingly */
            .main-content.shifted {
                margin-left: 260px;
                transition: all 0.3s ease;
            }
            
            .main-content.collapsed {
                margin-left: 70px;
                transition: all 0.3s ease;
            }
            
            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .sidebar-nav, .sidebar-nav.collapsed:hover {
                    width: 260px !important;
                }
                .main-content.shifted, .main-content.collapsed {
                    margin-left: 0;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- Sidebar Content ---
sidebar = html.Div(
    [
        # Sidebar Header with Title (Logo Removed)
        html.Div(
            [
                html.Div([
                    #html.Img(src="assets/logo.png", height="60px", className="me-2"), # Logo removed
                    html.Span("Olympus Insight", className="ms-2")
                ], className="sidebar-brand"),
                html.I(className="bi bi-x-lg", id="close-sidebar-btn"),
            ],
            className="sidebar-header"
        ),
        html.Hr(),
        
        # Navigation Section
        html.Div(
            [
                dbc.Nav(
                    nav_items,
                    vertical=True,
                    pills=True,
                    className="sidebar-nav-items"
                )
            ],
            className="sidebar-nav-section"
        ),
        
        # Footer Section in Sidebar
        html.Div(
            [
                html.Hr(),
                html.Small(
                    html.Span("Group 10 - CS661 Big Data Visual Analytics"),
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

# --- Main Application Layout ---
app.layout = html.Div(
    [
        # Sidebar Toggle Button
        html.Button(
            [
                html.Div(className="toggle-btn-line"),
                html.Div(className="toggle-btn-line"),
                html.Div(className="toggle-btn-line")
            ],
            id="sidebar-toggle",
            className="sidebar-toggle-btn"
        ),
        
        # Quick Access Panel
        quick_access_panel,
        
        # Sidebar
        sidebar,
        
        # Main Content Container with Header
        html.Div(
            [
                # Page Header (Ensuring Logo is Present)
                html.Div(
                    dbc.Container(
                        [
                            html.Div( # Outer centering Div
                                [
                                    html.Div( # Div containing logo and title
                                        [
                                            # Ensure logo.png is displayed here
                                            html.Img(src="assets/logo.png", height="70px", className="me-2"),
                                            html.Span("Olympus Insight", className="ms-3")
                                        ],
                                        className="header-brand"
                                    ),
                                ],
                                # These classes center the content within the header
                                className="d-flex align-items-center justify-content-center w-100"
                            ),
                        ],
                        fluid=True,
                        className="header-container"
                    ),
                    className="page-header"
                ),
                # Page Content
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
        
        # Store for sidebar state
        dcc.Store(id="sidebar-state", data={"is_open": True, "is_collapsed": False})
    ],
    className="wrapper"
)

# Updated callback to toggle sidebar and quick access panel
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
        is_collapsed = sidebar_state.get("is_collapsed", False)
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        if button_id == "sidebar-toggle":
            # Toggle between collapsed and expanded states
            is_open = True
            is_collapsed = not sidebar_state.get("is_collapsed", False)
        else:
            # Close sidebar completely
            is_open = False
            is_collapsed = sidebar_state.get("is_collapsed", False)
    
    sidebar_class = "sidebar-nav active" if is_open else "sidebar-nav"
    sidebar_class += " collapsed" if is_collapsed and is_open else ""
    
    content_class = "main-content shifted" if is_open and not is_collapsed else "main-content"
    content_class = "main-content collapsed" if is_open and is_collapsed else content_class
    
    quick_access_class = "quick-access-panel" if not is_open else "quick-access-panel hidden"
    
    return sidebar_class, content_class, quick_access_class, {"is_open": is_open, "is_collapsed": is_collapsed}

# Load the page with sidebar collapsed on page load (after initial render)
app.clientside_callback(
    """
    function(trigger) {
        if (trigger) {
            // Delay a bit to ensure everything is rendered
            setTimeout(function() {
                // Simulate click on the sidebar toggle to collapse it on first load
                document.getElementById('sidebar-toggle').click();
            }, 500);
        }
        return '';
    }
    """,
    Output('page-content', 'className', allow_duplicate=True),
    Input('page-load-trigger', 'children'),
    prevent_initial_call=True
)

# Create a hidden div to trigger the page load callback
app.layout.children.append(html.Div(id='page-load-trigger', style={'display': 'none'}, children='loaded'))

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)