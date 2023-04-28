import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, dash_table

app = Dash(__name__, use_pages=True)

app.layout = html.Div([
    # Website Heading
    dbc.Row([
        # Section Title
        html.H1('Stats for a country', id="page-heading",
                className="section-heading"),
        # dbc.Col([
        #     html.H1('Suicide Rates Dashboard', className='website-heading text-left mt-3'),
        # ]),
        dbc.Row([
            dbc.Col(
                dcc.Link(
                    "Single country", href="/"
                )
            ),
            dbc.Col(
                dcc.Link(
                    "Multiple country", href="/compare-countries"
                )
            ),
            dbc.Col(
                dcc.Link(
                    "Custom comparison", href="/custom-comparison"
                )
            ),
        ], className="navbar-options")
    ], className="navbar"),

    # dbc.Tabs(
    #     [
    #         dbc.Tab(label="Single Country", tab_id="single_country"),
    #         dbc.Tab(label="Multiple Country", tab_id="multiple_country"),
    #         dbc.Tab(label="Whole world", tab_id="whole_world"),
    #     ],
    #     id="tabs",
    #     active_tab="multiple_country",
    # ),

    # html.Div(
    #     [
    #         html.Div(
    #             dcc.Link(
    #                 f"{page['name']} - {page['path']}", href=page["relative_path"]
    #             )
    #         )
    #         for page in dash.page_registry.values()
    #     ]
    # ),

    dash.page_container,

    dbc.Row([
        html.Div('If you, or someone you know needs help, you can call 1.800.SUICIDE (1.800.784.2433). If it\'s an emergency, call 9.1.1.')
    ], className='warning'),

    dcc.Location(id='url')
])


@app.callback(
    Output('page-heading', 'children'),
    Input('url', 'pathname')
)
def update_page_heading(pathname):
    if pathname == "/custom-comparison":
        return "Custom comparisons"
    elif pathname == "/compare-countries":
        return "Cross-Country Comparisons"
    else:
        return "Stats for a country"


if __name__ == '__main__':
    app.run_server(debug=True)
