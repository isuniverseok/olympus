# app.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Initialize the app - Use pages=True
app = dash.Dash(__name__,
                use_pages=True, # Enable Dash Pages feature
                external_stylesheets=[dbc.themes.FLATLY], # Use FLATLY theme
                suppress_callback_exceptions=True # Necessary if callbacks are in other files
               )
app.title = "Olympus Insight"
server = app.server # Expose server for deployment services like Gunicorn/Waitress

# --- Navbar Definition ---
# Define the desired order of page names in the navbar
desired_order = [
    "Home",
    "Country Comparison",
    "Country Profile",
    "Globe View",
    "Host Analysis",
    "More Analysis",
    "Olympic Year",
    "Prediction",
    "Sport Profile",
    "Acknowledgement"
]

# Get all relevant pages from registry
all_pages = []
for page in dash.page_registry.values():
    # Exclude the 404 page from navbar entirely
    if page['module'] != 'pages.not_found_404':
        all_pages.append(page)

# Create a mapping from name to page dictionary for sorting
page_map = {page['name']: page for page in all_pages}

# Sort pages according to the desired order
sorted_nav_items = []
for name in desired_order:
    if name in page_map:
        page = page_map[name]
        sorted_nav_items.append(dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path'])))
        del page_map[name] # Remove page once added

# Add any remaining pages not in the desired_order list (preserves them)
for page in page_map.values():
    sorted_nav_items.append(dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path'])))

navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("Olympus Insight", href="/"),
        dbc.Nav(sorted_nav_items, navbar=True) # Single Nav with sorted items
    ], fluid=True),
    color="primary",
    dark=True,
    sticky="top",
    className="mb-4"
    # Note: Reverting back to simpler structure, relying on order
)

# --- Main Application Layout ---
app.layout = dbc.Container(
    [
        # Header/Navbar
        navbar,

        # Page Content Area
        # Content of each page will be rendered into dash.page_container
        dash.page_container,

        # Footer
        html.Footer(
            dbc.Container( # <--- Inner Container
                children=[ # <--- EXPLICITLY define children as a list
                    html.Hr(), # Child 1
                    dbc.Row([ # Child 2
                        dbc.Col("Group 10 - CS661 Big Data Visual Analytics", className="text-center text-muted"),
                    ]),
                ], # <-- End of children list
                className="mt-5 mb-3" # <-- Keyword argument is now unambiguous
            )
        )
    ],
    fluid=True # Use full width of the viewport
)

# --- Run the App ---
if __name__ == '__main__':
    # Use debug=True for development (auto-reloads, error messages in browser)
    # Set debug=False for production deployment
    app.run(debug=True, port=8050)