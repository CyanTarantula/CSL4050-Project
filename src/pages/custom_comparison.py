import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, dash_table, callback

df = pd.read_csv('../data/master.csv')

dash.register_page(__name__, path="/custom-comparison", title='Custom Comparison')
layout = dbc.Container([
    # Filters
    dbc.Col([
        html.H1('Suicide Rates Dashboard', className='website-heading text-left mt-3'),

        dbc.Col([
            html.H6('Select year range:', className="year-range-label"),
            
            # Dropdown section
            dbc.Col([
                html.H6('Select the 2 countries to compare:', className='section-subheading'),
                dcc.Dropdown(
                    id='custom-country-dropdown1',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='France',
                    clearable=False,
                    className='mt-2 custom-country-dropdown'
                ),
                dcc.Dropdown(
                    id='custom-country-dropdown2',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='Brazil',
                    clearable=False,
                    className='mt-2 custom-country-dropdown'
                ),
            ], className='custom-country-selector'),

            dbc.Col([
                # Section subtitle
                html.Div('Select the comparison:', className='comparison-selector-label'),
                dcc.Dropdown(
                    id='comparison-dropdown',
                    options=[
                        {
                            'label': 'Suicides distribution (last year)',
                            'value': 'suicides_dist'
                        },
                        {
                            'label': 'Distribution over generations',
                            'value': 'generation'
                        },
                        {
                            'label': 'GDP over the years',
                            'value': 'gdp_per_capita ($)'
                        },
                        {
                            'label': 'Age group distribution',
                            'value': 'age'
                        },
                        {
                            'label': 'Suicides per 100k population',
                            'value': 'suicides_100k_pop'
                        },
                    ],
                    value='suicides_dist',
                    clearable=False,
                    className='mt-2 custom-comparison-dropdown'
                ),
            ], className='comparison-selector'),

            # Year range slider
            dbc.Row([
                dbc.Col([
                    dcc.RangeSlider(
                        id='year-slider-custom',
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
                        id='sex-radio-custom',
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
        ], className='custom-country-filters')
    
    ], className="custom-country-navigator"),

    # Metrics
    dbc.Row([
        dbc.Col([
            html.H6('Total Suicides Combined (last year):', className="metric-label"),
            html.H3(id='custom-suicides-last-year', className="metric-value"),
            html.H5(id='custom-suicides-percent-change', className="metric-change"),
        ], className="metric"),
        dbc.Col([
            html.H6('Country with the highest suicide rate:', className="metric-label"),
            html.H3(id='custom-highest-suicide-country', className="metric-value"),
            html.H5(id='custom-highest-suicide-rate', className="metric-change"),
        ], className="metric"),
        dbc.Col([
            html.H6('Most vulnerable age group (combined):', className="metric-label"),
            html.H3(id='custom-most-vulnerable-age', className="metric-value"),
        ], className="metric"),
        dbc.Col([
            html.H6('Most vulnerable generation (combined):', className="metric-label"),
            html.H3(id='custom-most-vulnerable-generation', className="metric-value"),
        ], className="metric"),
    ], className="metrics"),

    # # Results
    # html.H2('Results', className="section-heading"),

    dbc.Row([
        dcc.Store(id='data-store-custom', data=df.to_dict('records')),
        
        dbc.Col([
            dcc.Graph(id='custom-results', className='result')
        ]),
    ], className='mb-4 mt-4 results'),


], fluid=True, className="custom-comparison-page")

@callback(
    Output('data-store-custom', 'data'),
    [
        [
            Input('custom-country-dropdown1', 'value'), 
            Input('custom-country-dropdown2', 'value'),
        ],
        Input('year-slider-custom', 'value'),
        Input('sex-radio-custom', 'value'),
    ]
)
def update_data_store(selected_countries, selected_year_range, selected_sex):
    filtered_dfs = []

    for selected_country in selected_countries:
        last_year = selected_year_range[1]
        while df[(df['country'] == selected_country) & (df['year'] == last_year)]['suicides_100k_pop'].sum() == 0:
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
        Output('custom-suicides-last-year', 'children'),
        Output('custom-suicides-percent-change', 'children'),
        Output('custom-suicides-percent-change', 'style'),
        
        Output('custom-highest-suicide-country', 'children'),
        Output('custom-highest-suicide-rate', 'children'),

        Output('custom-most-vulnerable-age', 'children'),

        Output('custom-most-vulnerable-generation', 'children')
    ],
    [
        Input('data-store-custom', 'data'),
    ]
)
def update_metrics(data):
    df = pd.DataFrame.from_dict(data)

    last_year = df['year'].max()
    last_second_year = last_year - 1
    new_df = df.groupby(['country', 'year'])['suicides_no', 'suicides_100k_pop'].sum().reset_index()

    suicides_last_year = new_df[new_df['year'] == last_year]['suicides_no'].sum()
    suicides_second_last_year = new_df[new_df['year'] == last_second_year]['suicides_no'].sum()
    
    percent_change = round(
        (suicides_last_year - suicides_second_last_year) / suicides_second_last_year * 100, 2)
    percent_change_color = 'red'
    if percent_change > 0:
        percent_change = f'↑{percent_change}%'  # add a plus sign
    else:
        percent_change = f'↓{-percent_change}%'
        percent_change_color = 'green'

    highest_suicide_rate_index = new_df[new_df['year'] == last_year]['suicides_100k_pop'].idxmax()
    
    most_vulnerable_age = df.groupby('age')['suicides_100k_pop'].sum().idxmax()

    most_vulnerable_gen = df.groupby('generation')['suicides_100k_pop'].sum().idxmax()

    return [
        suicides_last_year, percent_change, {'color': percent_change_color},

        new_df.loc[highest_suicide_rate_index]['country'], new_df.loc[highest_suicide_rate_index]['suicides_100k_pop'],

        most_vulnerable_age,

        most_vulnerable_gen
    ]

@callback(
    [
        Output('custom-results', 'figure'),
    ],
    [
        Input('data-store-custom', 'data'),
        Input('comparison-dropdown', 'value')
    ]
)
def render_general_graphs(data, comparison):
    figures = []
    df = pd.DataFrame.from_dict(data)

    if comparison == 'suicides_100k_pop':
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
            paper_bgcolor='#f9f9f9'
        )

        figures.append(fig)
    elif comparison == 'generation':
        df_country_gen_suicide = df[df['country'].isin(df['country'].unique())].groupby(['country', 'generation'])['suicides_no'].sum().reset_index()
        fig = px.bar(df_country_gen_suicide, y='generation', x='suicides_no', color='country', barmode='group', orientation='h')

        figures.append(fig)
    elif comparison == 'gdp_per_capita ($)':
        fig = px.line(df.groupby(['year', 'country']).sum().reset_index(), x='year', y='gdp_per_capita ($)', color='country')
        fig.update_layout(
            xaxis=dict(
                title='Year',
                # dtick=5,              # set the interval between x-axis labels
                tickangle=-60         # set the angle to x-axis labels
            ),
            yaxis_title='GDP per capita ($)',
            legend=dict(
                title="",
                orientation="h",      # set the orientation to 'h'orizontal
                x=0.5,
                y=-0.4,
                xanchor="center",
                yanchor="bottom"
            ),
            title={
                'text': 'GDP (per capita) over the years',
                'x': 0.5,
                'y': 0.92,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            paper_bgcolor='#f9f9f9'
        )

        figures.append(fig)
    elif comparison == 'age':
        df_country_age_suicide = df[df['country'].isin(df['country'].unique())].groupby(['country', 'age'])['suicides_no'].sum().reset_index()

        # Define the order of the categories
        age_order = ['5-14 years', '15-24 years', '25-34 years', '35-54 years', '55-74 years', '75+ years']

        # Convert the 'age' column to categorical data type with the defined order
        df_country_age_suicide['age'] = pd.Categorical(df_country_age_suicide['age'], categories=age_order, ordered=True)

        # Sort the data frame based on the 'age' column
        df_country_age_suicide.sort_values('age', inplace=True)


        fig = px.line_polar(df_country_age_suicide, r='suicides_no', theta='age', line_close=True,
                        color='country', line_group='country')

        fig.update_layout(
            paper_bgcolor='#f9f9f9'
        )

        figures.append(fig)
    elif comparison=="suicides_dist":
        fig = px.box(df.groupby(['year', 'country']).sum().reset_index(), x='country', y='suicides_no')

        fig.update_layout(
            xaxis=dict(
                title='Country'
            ),
            yaxis_title='Suicides',
            legend=dict(
                title="",
                orientation="h",      # set the orientation to 'h'orizontal
                x=0.5,
                y=-0.4,
                xanchor="center",
                yanchor="bottom"
            ),
            title={
                'text': 'Suicides distribution over the years',
                'x': 0.5,
                'y': 0.92,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            paper_bgcolor='#f9f9f9'
        )

        figures.append(fig)

    return figures

