import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
from dash import Dash, html, dcc, dash_table, callback

df = pd.read_csv('../data/master.csv')

dash.register_page(__name__, path="/compare-countries", title="Compare countries")

# Define layout
layout = dbc.Container([
    # Filters
    dbc.Col([
        html.H1('Suicide Rates Dashboard', className='website-heading text-left mt-3'),

        dbc.Col([
            html.H6('Select year range:', className="year-range-label"),
            
            # Dropdown section
            dbc.Col([
                html.H6('Select 4 countries to compare:', className='section-subheading'),
                dcc.Dropdown(
                    id='multiple-country-dropdown1',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='Canada',
                    clearable=False,
                    className='mt-2 multiple-country-dropdown'
                ),
                dcc.Dropdown(
                    id='multiple-country-dropdown2',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='Germany',
                    clearable=False,
                    className='mt-2 multiple-country-dropdown'
                ),
                dcc.Dropdown(
                    id='multiple-country-dropdown3',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='France',
                    clearable=False,
                    className='mt-2 multiple-country-dropdown'
                ),
                dcc.Dropdown(
                    id='multiple-country-dropdown4',
                    options=[{'label': country, 'value': country}
                            for country in sorted(df.country.unique())],
                    value='Mexico',
                    clearable=False,
                    className='mt-2 multiple-country-dropdown'
                ),
            ], className='multiple-country-selector'),

            # Year range slider
            dbc.Row([
                dbc.Col([
                    dcc.RangeSlider(
                        id='year-slider-multiple',
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
                        id='sex-radio-multiple',
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
        
        ], className="multiple-country-filters"),
    ], className="multiple-country-navigator"),

    # Metrics
    dbc.Row([
        dbc.Col([
            html.H6('Total Suicides Combined (last year):', className="metric-label"),
            html.H3(id='multiple-suicides-last-year', className="metric-value"),
            html.H5(id='multiple-suicides-percent-change', className="metric-change"),
        ], className="metric"),

        dbc.Col([
            html.H6('Country with the highest suicide rate:', className="metric-label"),
            html.H3(id='highest-suicide-country', className="metric-value"),
            html.H5(id='highest-suicide-rate', className="metric-change"),
        ], className="metric"),

        dbc.Col([
            html.H6('Country with the lowest suicide rate:', className="metric-label"),
            html.H3(id='lowest-suicide-country', className="metric-value"),
            html.H5(id='lowest-suicide-rate', className="metric-change"),
        ], className="metric"),
        
        dbc.Col([
            html.H6('Most vulnerable age group (combined):', className="metric-label"),
            html.H3(id='multiple-most-vulnerable-age', className="metric-value"),
        ], className="metric"),

    ], className="metrics"),
    
    # Results general
    dbc.Row([
        dcc.Store(id='data-store-multiple', data=df.to_dict('records')),
        
        dbc.Col([
            dcc.Graph(id='results-general1', className='graph-result')
        ]),
        
        dbc.Col([
            dcc.Graph(id='results-general2', className='graph-result')
        ]),
    ], className='mb-4 mt-4 graph-results'),

    # Section Title
    html.H1('Miscellaneous world charts ', className="section-heading"),
    
    # Results pie
    dbc.Col([        
        dbc.Col([
            dcc.Graph(id='results-world1', className='world-result')
        ]),
        
        # dbc.Col([
        #     dcc.Graph(id='results-world2', className='world-result')
        # ], width={'size': 3, 'offset': 0}),
        
        # dbc.Col([
        #     dcc.Graph(id='results-world3', className='world-result')
        # ], width={'size': 3, 'offset': 0}),
        
        # dbc.Col([
        #     dcc.Graph(id='results-world4', className='world-result')
        # ], width={'size': 3, 'offset': 0}),
    
    ], className='mb-4 mt-4 world-results'),

], fluid=True, className="multiple-country")

@callback(
    Output('data-store-multiple', 'data'),
    [
        [
            Input('multiple-country-dropdown1', 'value'), 
            Input('multiple-country-dropdown2', 'value'), 
            Input('multiple-country-dropdown3', 'value'), 
            Input('multiple-country-dropdown4', 'value'), 
        ],
        Input('year-slider-multiple', 'value'),
        Input('sex-radio-multiple', 'value'),
    ]
)
def update_data_store(selected_countries, selected_year_range, selected_sex):
    filtered_dfs = []

    for selected_country in selected_countries:
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
        Output('multiple-suicides-last-year', 'children'),
        Output('multiple-suicides-percent-change', 'children'),
        Output('multiple-suicides-percent-change', 'style'),

        Output('highest-suicide-country', 'children'),
        Output('highest-suicide-rate', 'children'),
        
        Output('lowest-suicide-country', 'children'),
        Output('lowest-suicide-rate', 'children'),
        
        Output('multiple-most-vulnerable-age', 'children'),
    ],
    [
        Input('data-store-multiple', 'data'),
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

    country_wise_suicide_rate = df.groupby('country')['suicides_100k_pop'].sum()
    # print(country_wise_suicide_rate)
    highest_suicide_rate_country = country_wise_suicide_rate.idxmax()
    lowest_suicide_rate_country = country_wise_suicide_rate.idxmin()
    
    most_vulnerable_age = df.groupby('age')['suicides_100k_pop'].sum().idxmax()
    
    return [
        suicides_last_year, percent_change, {'color': percent_change_color},
        highest_suicide_rate_country, round(country_wise_suicide_rate[highest_suicide_rate_country], 2),
        lowest_suicide_rate_country, round(country_wise_suicide_rate[lowest_suicide_rate_country], 2),
        most_vulnerable_age,
    ]

@callback(
    [
        Output('results-general1', 'figure'),
        Output('results-general2', 'figure'),
    ],
    [
        Input('data-store-multiple', 'data'),
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
        paper_bgcolor='#f9f9f9'
    )

    figures.append(fig)

    df_country_age_suicide = df[df['country'].isin(df['country'].unique())].groupby(['country', 'age'])['suicides_no'].sum().reset_index()

    # Define the order of the categories
    age_order = ['5-14 years', '15-24 years', '25-34 years', '35-54 years', '55-74 years', '75+ years']

    # Convert the 'age' column to categorical data type with the defined order
    df_country_age_suicide['age'] = pd.Categorical(df_country_age_suicide['age'], categories=age_order, ordered=True)

    # Sort the data frame based on the 'age' column
    df_country_age_suicide.sort_values('age', inplace=True)


    fig2 = px.line_polar(df_country_age_suicide, r='suicides_no', theta='age', line_close=True,
                    color='country', line_group='country')

    fig2.update_layout(
        paper_bgcolor='#f9f9f9'
    )

    figures.append(fig2)

    return figures


@callback(
    [
        Output('results-world1', 'figure'),
    ],
    [
        Input('data-store-multiple', 'data'),
    ]
)
def render_world_charts(data):
    figures = []
    # df = pd.DataFrame.from_dict(data)
    temp = data
    # print(df['country'].unique())
    df_grouped = df.groupby(['country', 'age']).agg({'suicides_no': 'sum'}).reset_index()

    # Create the TreeMap chart
    fig = px.treemap(df_grouped, path=['country', 'age'], values='suicides_no')

    fig.update_layout(
        title={
            'text': 'Distribution of suicides across age groups over the world',
            'x': 0.5,
            'y': 0.92,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        paper_bgcolor='#f9f9f9'
    )

    figures.append(fig)

    # # Update pie charts
    # legend_order = ['5-14 years', '15-24 years', '25-34 years',
    #                 '35-54 years', '55-74 years', '75+ years']

    # # create a list of unique country names in the dataframe
    # country_list = df['country'].unique()

    # # loop through each country and create a pie chart
    # for country in country_list:

    #     chart_data = df[df['country'] == country]
    #     if chart_data.empty:
    #         fig = px.pie(
    #             labels=["No data available for the selected year range"], values=[1])

    #     else:
    #         # add ordered categories to age column
    #         chart_data['age'] = pd.Categorical(
    #             chart_data['age'], categories=legend_order, ordered=True)
    #         chart_data = chart_data.sort_values(
    #             'age')  # sort by age column
    #         fig = px.pie(chart_data, values='suicides_100k_pop', names='age',
    #                         labels={
    #                             'suicides_100k_pop': 'Suicides per 100K Population', 'age': 'Age Group'},
    #                         title=country)
    #         fig.update_traces(
    #             textposition='inside',               # set text position to inside of the slices
    #             sort=False
    #         )
    #         fig.update_layout(
    #             # adjust margin to move the chart position
    #             margin=dict(l=20, r=0, t=30, b=0),
    #             #showlegend = False,
    #             # legend=dict(
    #             #     orientation='h'                 # horizontal orientation,
    #             # ),
    #             paper_bgcolor='#f9f9f9',
    #             showlegend=False
    #         )
    #     '''
    #     # Only show the legend for the last pie chart
    #     if (country_list[len(country_list)-1] == country):
    #         fig.update_layout(showlegend = True)
    #     '''

    #     # Add the pie chart to the list of figures
    #     figures.append(fig)

    return figures
