# app.py
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Initialize the app - Use pages=True
app = dash.Dash(__name__,
                use_pages=True, # Enable Dash Pages feature
                external_stylesheets=[dbc.themes.BOOTSTRAP], # Use Bootstrap theme
                suppress_callback_exceptions=True # Necessary if callbacks are in other files
               )
app.title = "Olympus Insight"
server = app.server # Expose server for deployment services like Gunicorn/Waitress

# --- Navbar Definition ---
# Uses dash.page_registry to automatically find pages
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page['name'], href=page['relative_path']))
        for page in dash.page_registry.values()
        if page['module'] != 'pages.not_found_404' # Exclude 404 from main nav
    ],
    brand="Olympus Insight",
    brand_href="/", # Link brand to landing page
    color="primary",
    dark=True,
    sticky="top", # Make navbar stick to top
    className="mb-4" # Margin bottom
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