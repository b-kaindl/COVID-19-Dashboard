from app import app, cache
import dash
from typing import Any, List
from dash_components.dashboard_format import dashboard_layout
from dash_components.callbacks import assign_callbacks

def main() -> None:
    """
    Entry point for the application
    """
    set_layout(app, dashboard_layout)
    assign_callbacks(app)

    try:

        app.run_server(debug=False)

    finally:
        # clear application cache on exit
        with app.server.app_context():
            cache.clear()




def set_layout(application: dash.Dash, layout: List[Any]) -> None:
    """
    Sets a layout for a dash application


    Args:
        application (Dash): dash application to assign layout to
        layout (List): List containing layout elemnts


    Returns:
        None
    """

    application.layout = layout

if __name__ == "__main__":
    main()
