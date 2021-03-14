"""
Module containing layout definitions to be used in dashboard.
"""

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from utils.asset_loader import data_loader, model_loader

intro = html.Div(id="intro-root",
    children=[
        dbc.Row(
            dbc.Col(
                children=[
                     """
                    This web application is part of project submitted as a
                    part of Udacity's Data Scientist
                    Nanodegree and provides an interface to access predictions
                    made by Temporal Fusion Transformers.
                    """,
                    html.Br(),
                    """
                    For more information refer on how to train a
                    model for use in this dashboard consult the project's
                    """,
                    dcc.Link(
                        "GitHub Repository",
                        href="https://github.com/b-kaindl/COVID-19-Dashboard"
                    ),
                    "."
                ]
            ),
        style={"marginBottom": "10px"}
        ),
    ]
)

controls = html.Div(id="controls-root",
    children=[
        dbc.Row(
            [
                dbc.Col(
                    children=[
                        dbc.Row(
                            html.B("Training Data Set")
                        ),
                        dbc.Row(
                            [
                                dcc.Dropdown(id="training-data-dropdown",
                                    options=data_loader.get_dropdown_entries(),
                                    placeholder="Choose Dataset Used in Training",
                                    multi=False,
                                    style={
                                    "width": "80%",
                                    "marginLeft": "10px",
                                    "marginRight": "10px",
                                    "marginBottom": "10px"
                                    }
                                )
                            ]
                        ),
                        dbc.Row(
                            children=[
                                html.P("Latest Training Date: "),
                                html.B(id='latest-training-date')
                            ]
                        )
                    ],
                ),
                dbc.Col(
                    children=[
                        dbc.Row(
                            [
                                html.B("Prediction Model"),
                                html.Br(),
                                html.B(
                                    """
                                        Make sure to choose a model using the
                                        current run_config.yml file.
                                    """
                                )
                            ]
                        ),
                        dbc.Row(
                            dcc.Dropdown(id="model-dropdown",
                                options=model_loader.get_dropdown_entries(),
                                placeholder="Choose Model for Prediction",
                                multi=False,
                                style={
                                "width": "80%",
                                "marginLeft": "10px",
                                "marginRight": "10px",
                                "marginBottom": "10px"
                                }
                            )
                        ),
                    ],
                )
            ]
        ),

    ]
)

plotting_controls = html.Div(id="plotting-control-root",
    children=[
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dcc.Dropdown(
                        id="country-selector",
                        placeholder="Choose a Country",
                        multi=False,
                        style={
                            "MarginTop": "30px",
                            "MarginBottom": "30px",
                            "display": "block",
                            "width": "80%"
                            }
                        )
                    ],
                    style={"size": 1, "offset": 3}
                ),
            ]
        ),
    ]
)

plotting_area = html.Div(id="plotting-area-root",
    children=[
        dbc.Row(
            dbc.Col(id="plotting-area",
                children=None,
                style={"size": 1,
                "offset": 3,
                "MarginTop": "30px",
                "MarginBottom": "30px",
                "display": "block",
                "width": "80%"}
            )
        )
    ]
)


dashboard_layout = html.Div(id = "dashboard-root",
    children=[
        dbc.Container(intro),
        dbc.Container(controls),
        dbc.Container(plotting_controls),
        dbc.Container(plotting_area),
    ]
)
