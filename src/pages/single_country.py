import math
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, dash_table, callback

df = pd.read_csv('../data/master.csv')

dash.register_page(__name__, path='/')

layout = dbc.Container([
    # Filters
    dbc.Col([
        html.H1('Suicide Rates Dashboard', className='website-heading text-left mt-3'),

        dbc.Col([
            html.H6('Select year range:', className="year-range-label"),
            # Dropdown section
            dbc.Col([
                # Section subtitle
                html.Div('Select the country to examine:', className='section-subheading'),
                dcc.Dropdown(
                    id='single-country-dropdown',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='France',
                    clearable=False,
                    className='mt-2'
                ),
            ], className='country-selector'),

            # Year range slider
            dbc.Row([
                dbc.Col([
                    dcc.RangeSlider(
                        id='year-slider',
                        min=df.year.min(),
                        max=df.year.max(),
                        value=[max(1988, df.year.min()), min(2017, df.year.max())],
                        marks={str(year): str(year)
                            for year in range(df.year.min(), df.year.max()+1, 2)},
                        className='year-range-slider',
                        vertical=True
                    )
                ])
            ], className='year-range-selector'),

            # Sex radio buttons
            dbc.Row([
                dbc.Row([
                    html.H6('Filter by sex:', className="sex-filter-label"),
                    dcc.RadioItems(
                        id='sex-radio',
                        options=[
                            {'label': 'Male', 'value': 'male'},
                            {'label': 'Female', 'value': 'female'},
                            {'label': 'Both', 'value': 'both'}
                        ],
                        value='both',
                        className='sex-filter-radio'
                    )
                ])
            ], className='sex-filter'),
        ], className='single-country-filters')
    
    ], className="single-country-navigator"),

    # Metrics
    dbc.Row([
        dbc.Col([
            html.H6('Suicides (last year):', className="metric-label"),
            html.H3(id='suicides-last-year', className="metric-value"),
            html.H5(id='suicides-percent-change', className="metric-change"),
        ], className="metric"),
        dbc.Col([
            html.H6('Population (last year):', className="metric-label"),
            html.H3(id='population-last-year', className="metric-value"),
            html.H5(id='population-percent-change', className="metric-change"),
        ], className="metric"),
        dbc.Col([
            html.H6('Most vulnerable age group:', className="metric-label"),
            html.H3(id='most-vulnerable-age', className="metric-value"),
        ], className="metric"),
        dbc.Col([
            html.H6('GDP per capita (last year):', className="metric-label"),
            html.H3(id='gdp', className="metric-value"),
            html.H5(id='gdp-percent-change', className="metric-change"),
        ], className="metric"),
    ], className="metrics"),

    # # Results
    # html.H2('Results', className="section-heading"),

    dbc.Row([
        dcc.Store(id='data-store-single', data=df.to_dict('records')),
        
        dbc.Col([
            dcc.Graph(id='results-general', className='result')
        ]),
        
        dbc.Col([
            dcc.Graph(id='results-pie', className='result')
        ], width={'size': 3, 'offset': 0}),
    ], className='mb-4 mt-4 results'),


], fluid=True, className="single-country")

@callback(
    Output('data-store-single', 'data'),
    [
        Input('single-country-dropdown', 'value'),
        Input('year-slider', 'value'),
        Input('sex-radio', 'value'),
    ]
)
def update_data_store(selected_country1, selected_year_range, selected_sex):
    filtered_dfs = []

    for selected_country in [selected_country1]:
        last_year = selected_year_range[1]
        while df[df['country'] == selected_country][df['year'] == last_year]['suicides_100k_pop'].sum() == 0:
            last_year -= 1
        selected_year_range[1] = last_year

        if selected_sex == 'both':
            filtered_df = df[(df['country'] == selected_country) & (
                df['year'].between(selected_year_range[0], selected_year_range[1]))]
            if filtered_df.empty:
                new_row = {'country': selected_country,
                           'year': selected_year_range[0]}
                filtered_df = filtered_df.append(new_row, ignore_index=True)
        else:
            filtered_df = df[(df['country'] == selected_country) & (df['year'].between(
                selected_year_range[0], selected_year_range[1])) & (df['sex'] == selected_sex)]
            if filtered_df.empty:
                new_row = {'country': selected_country,
                           'year': selected_year_range[0], 'sex': selected_sex}
                filtered_df = filtered_df.append(new_row, ignore_index=True)

        filtered_dfs.append(filtered_df)

    df_combined = pd.concat(filtered_dfs)
    return df_combined.to_dict('records')

@callback(
    [
        Output('suicides-last-year', 'children'),
        Output('suicides-percent-change', 'children'),
        Output('suicides-percent-change', 'style'),

        Output('population-last-year', 'children'),
        Output('population-percent-change', 'children'),
        Output('population-percent-change', 'style'),

        Output('most-vulnerable-age', 'children'),
        
        Output('gdp', 'children'),
        Output('gdp-percent-change', 'children'),
        Output('gdp-percent-change', 'style'),
    ],
    [
        Input('data-store-single', 'data'),
    ]
)
def update_metrics(data):
    df = pd.DataFrame.from_dict(data)

    last_year = df['year'].max()
    last_year_df = df[df['year'] == last_year]
    last_year_suicides = last_year_df['suicides_no'].sum()
    second_last_year = last_year - 1
    second_last_year_df = df[df['year'] == second_last_year]
    second_last_year_suicides = second_last_year_df['suicides_no'].sum()
    percent_change = round(
        (last_year_suicides - second_last_year_suicides) / second_last_year_suicides * 100, 2)
    percent_change_color = 'red'
    if percent_change > 0:
        percent_change = f'↑{percent_change}%'  # add a plus sign
    else:
        percent_change = f'↓{-percent_change}%'
        percent_change_color = 'green'
    
    last_year_population = last_year_df['population'].sum()
    second_last_year_population = second_last_year_df['population'].sum()
    population_percent_change = round(
        (last_year_population - second_last_year_population) / second_last_year_population * 100, 2)
    population_percent_change_color = 'red'
    if population_percent_change > 0:
        population_percent_change = f'↑{population_percent_change}%'
    else:
        population_percent_change = f'↓{-population_percent_change}%'
        population_percent_change_color = 'green'
    
    most_vulnerable_age = df.groupby('age')['suicides_100k_pop'].sum().idxmax()

    last_year_gdp = last_year_df['gdp_per_capita ($)'].mean()
    second_last_year_gdp = second_last_year_df['gdp_per_capita ($)'].mean()
    gdp_percent_change = round(
        (last_year_gdp - second_last_year_gdp) / second_last_year_gdp * 100, 2)
    gdp_percent_change_color = 'green'
    if gdp_percent_change > 0:
        gdp_percent_change = f'↑{gdp_percent_change}%'
    else:
        gdp_percent_change = f'↓{-gdp_percent_change}%'
        gdp_percent_change_color = 'red'
    

    return [
        last_year_suicides, percent_change, {'color': percent_change_color}, 
        last_year_population, population_percent_change, {'color': population_percent_change_color}, 
        most_vulnerable_age, 
        f'${round(last_year_gdp)}', gdp_percent_change, {'color': gdp_percent_change_color},
    ]


@callback(
    [
        Output('results-general', 'figure'),
    ],
    [
        Input('data-store-single', 'data'),
    ]
)
def render_general_graphs(data):
    figures = []
    df = pd.DataFrame.from_dict(data)

    fig = px.line(df.groupby(['year', 'country']).sum().reset_index(), x='year', y='suicides_100k_pop', color='country')
    fig.update_layout(
        xaxis=dict(
            title='Year',
            # dtick=5,              # set the interval between x-axis labels
            tickangle=-60         # set the angle to x-axis labels
        ),
        yaxis_title='Number of suicides per 100K people',
        legend=dict(
            title="",
            orientation="h",      # set the orientation to 'h'orizontal
            x=0.5,
            y=-0.4,
            xanchor="center",
            yanchor="bottom"
        ),
        title={
            'text': 'Suicide rate over the years',
            'x': 0.5,
            'y': 0.92,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        # plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='#f9f9f9'
    )

    figures.append(fig)

    return figures


@callback(
    [
        Output('results-pie', 'figure'),
    ],
    [
        Input('data-store-single', 'data'),
    ]
)
def render_pie_charts(data):
    figures = []
    df = pd.DataFrame.from_dict(data)

    # Update pie charts
    legend_order = ['5-14 years', '15-24 years', '25-34 years',
                    '35-54 years', '55-74 years', '75+ years']

    # create a list of unique country names in the dataframe
    country_list = df['country'].unique()

    # loop through each country and create a pie chart
    for country in country_list:

        chart_data = df[df['country'] == country]
        if chart_data.empty:
            fig = px.pie(
                labels=["No data available for the selected year range"], values=[1])

        else:
            # add ordered categories to age column
            chart_data['age'] = pd.Categorical(
                chart_data['age'], categories=legend_order, ordered=True)
            chart_data = chart_data.sort_values(
                'age')  # sort by age column
            fig = px.pie(chart_data, values='suicides_100k_pop', names='age',
                            labels={
                                'suicides_100k_pop': 'Suicides per 100K Population', 'age': 'Age Group'},
                            title=country)
            fig.update_traces(
                textposition='inside',               # set text position to inside of the slices
                sort=False
            )
            fig.update_layout(
                # adjust margin to move the chart position
                margin=dict(l=20, r=0, t=30, b=0),
                #showlegend = False,
                legend=dict(
                    orientation='h'                 # horizontal orientation,
                ),
                paper_bgcolor='#f9f9f9'
            )
        '''
        # Only show the legend for the last pie chart
        if (country_list[len(country_list)-1] == country):
            fig.update_layout(showlegend = True)
        '''

        # Add the pie chart to the list of figures
        figures.append(fig)

    return figures

