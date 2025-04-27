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
                transition: none; /* Remove transition as it's always open */
                position: fixed; /* Keep sidebar fixed */
                top: 0;
                left: 0;
                height: 100vh; /* Full height */
                z-index: 1030; /* Ensure it's above content potentially */
                /* Add background/color if needed, assuming theme provides it */
            }

            /* Remove all rules related to .collapsed */

            /* Logo/Brand styling */
            .sidebar-brand {
                padding: 0.5rem 1rem;
                display: flex;
                align-items: center;
                /* Keep justify-content: center or adjust as needed */
                justify-content: center; 
            }

            /* Nav Link Styling */
            .nav-link {
                 padding: 0.5rem 1rem; /* Ensure padding is for expanded state */
                 display: flex;
                 align-items: center;
            }

            .nav-link i {
                font-size: 1rem; /* Icon size for expanded state */
                margin-right: 0.5rem !important;
            }

            .nav-text {
                 display: inline-block !important; /* Ensure text is always visible */
            }

            /* Consistent padding for nav items */
            .sidebar-nav-items {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }

            /* REMOVE HOVER EFFECT RULES */

            /* Adjust main content */
            .main-content {
                margin-left: 260px; /* Always apply margin for expanded sidebar */
                transition: none; /* Remove transition */
            }

            /* Mobile responsiveness */
            @media (max-width: 768px) {
                .sidebar-nav {
                    /* Decide mobile behavior: hide completely or keep open? */
                    /* Option 1: Hide sidebar on mobile */
                     /* left: -260px; */ 
                     /* Option 2: Keep it open (like desktop) */
                     width: 260px !important; 
                     left: 0;
                }
                .main-content {
                    /* Adjust margin if sidebar is hidden on mobile */
                     margin-left: 0; /* No margin if sidebar is hidden/overlay */
                }
                /* Add a button to toggle sidebar visibility on mobile if hidden */
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
                # Remove Close Button:
                # html.I(className="bi bi-x-lg", id="close-sidebar-btn"), 
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
    className="sidebar-nav" # Ensure no 'collapsed' or 'active' class is set here initially
)

# Remove Quick Access Panel if not needed alongside permanent sidebar
# quick_access_panel = html.Div(...)

# --- Main Application Layout ---
app.layout = html.Div(
    [
        # Remove Sidebar Toggle Button:
        # html.Button([...], id="sidebar-toggle", className="sidebar-toggle-btn"),
        
        # Remove Quick Access Panel from layout if removed above
        # quick_access_panel,
        
        # Sidebar (always present)
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
                        # Remove transition here too if needed, though CSS handles margin
                    }
                )
            ],
            id="page-content",
            className="main-content" # Class is now static, margin handled by CSS
        ),
        
        # Remove Store for sidebar state:
        # dcc.Store(id="sidebar-state", data={...})
    ],
    className="wrapper"
)

# Remove the toggle_sidebar callback entirely

# Remove the clientside callback for initial collapse entirely

# Remove the page-load-trigger div
# app.layout.children.append(html.Div(id='page-load-trigger', ...))

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=8050)