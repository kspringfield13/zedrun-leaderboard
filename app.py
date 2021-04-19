import base64
import datetime
import io, os
import plotly.graph_objs as go

import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import dash_table

tabtitle = 'ZΞD RUN insights'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',dbc.themes.BOOTSTRAP]

# user input update for now
updated = '4.18.2021 12:00pm EST'

# .csv files. eventually transfer to postgres db
lb_df = pd.read_csv('zedrun_leaderboard-2021-04-18T12_02_at.csv')
wh_df = pd.read_csv('zedrun_leaderboard-2021-04-18T12_02_wh.csv')
coats = pd.read_csv('horse_coats_4.14.2021.csv')

# font for most of the site
font_family = 'verdana'

# initialize Dash app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=.48"}])
server = app.server
app.title = tabtitle

# tag for Google Analytics
app.index_string = '''<!DOCTYPE html>
<html>
<head>
  <!-- Global site tag (gtag.js) - Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-Y88526KP3X"></script>
  <script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-Y88526KP3X');
  </script>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
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

# combine .csv files to get total horse count
com = lb_df.append(wh_df)
horse_cnt = len(com.name.drop_duplicates().tolist())

# create treemap/sunburst figure
coats['Label'] = coats["Horse Count"].astype(str)
color_map = dict(zip(coats.Coat, coats['Hex Color']))
color_map['(?)'] = 'black'

fig = px.treemap(coats, path=['Breed','Color Group', 'Color Box', 'Coat'], values='Horse Count', color='Coat',
                  color_discrete_map=color_map, hover_name='Coat',height=886)
fig.data[0].hovertemplate = '%{id}<br>%{value} horses'
fig.data[0].textinfo = 'label+text+value'
fig.update_layout(
    paper_bgcolor='#27282A',
    margin=dict(l=0,r=0,b=0,t=0),
    updatemenus=[
        dict(
            type = "buttons",
            direction = "left",
            buttons=list([
                dict(
                    args=["type", "treemap"],
                    label="Treemap",
                    method="restyle"
                ),
                dict(
                    args=["type", "sunburst"],
                    label="Sunburst",
                    method="restyle"
                )
            ]),
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.02,
            xanchor="left",
            y=1.06,
            yanchor="top",
            font={'size':12,
                  'family': font_family,
                  'color':'#27282A'},
            bgcolor='gray'
        ),
    ]
)

# create datatable
def generate_table(lb_df):
    return dash_table.DataTable(
        id='table',
        data = lb_df.to_dict('records'),
        columns=[{'name': 'Name', 'id':'Name','type':'text','presentation':'markdown'},
                 {'name': 'Horse', 'id':'Horse','type':'text','presentation':'markdown'},
                 {'name': 'Gen', 'id':'Gen'},
                 {'name': 'Stable', 'id':'Stable'},
                 {'name': 'Class', 'id':'Class'},
                 {'name': 'Races', 'id':'Races'},
                 {'name': 'Placed %', 'id':'Placed %'},
                 {'name': 'Win %', 'id': 'Win %'},
                 {'name': 'Odds', 'id': 'Odds'},
                 {'name': 'Rank', 'id': 'Rank'}],
        css=[dict(selector='img[alt=horse_svg]', rule='height: 65px;')],
        editable=False,
        cell_selectable=False,
        row_selectable=False,
        sort_action="native",
        sort_mode="single",
        row_deletable=False,
        page_action='none',
        fixed_rows={'headers': True, 'data': 0},
        style_table={
            'overflowX': 'auto',
            "height": "90vh", "maxHeight": "90vh"
        },
        style_header={
            'height': '40px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'center',
            'padding': '3px',
            'color': 'rgb(221, 235, 234)',
            'fontWeight': 'bold',
            'fontFamily': font_family,
            'font_size': '18px',
            'backgroundColor': 'black'
        },
        style_data={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'center',
            'padding': '3px',
            'backgroundColor': 'rgb(10, 10, 10)',
            'color': 'rgb(221, 235, 234)',
            'font_family': font_family,
            'font_size': '20px'
        },
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'minWidth': '20px', 'width': '30px', 'maxWidth': '60px',
            'whiteSpace': 'normal',
        },
        style_header_conditional=[
        {
            'if': {'column_id': 'Name'},
            'textAlign': 'left'
        }
        ],
        style_data_conditional=[
            {
            'if': {'column_id': 'Horse'},
            'minWidth': '34px', 'width': '34px', 'maxWidth': '34px',
            'paddingTop': '12px',
            'paddingLeft': '10px',
            'paddingRight': '10px'
            },
            {
            'if': {'column_id': 'Name'},
            'fontWeight': 'bold',
            'fontSize': '20px',
            'paddingLeft': '14px',
            'paddingTop': '12px'
            },
            {
            'if': {'column_id': 'Rank'},
            'textAlign': 'center',
            'fontWeight': 'bold',
            'fontSize': '26px',
            'minWidth': '26px', 'width': '30px', 'maxWidth': '30px'
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#27282A',
            },
            {
                'if': {
                    'filter_query': '{{Races}} = {}'.format(lb_df['Races'].max()),
                    'column_id': 'Races'
                },
                'backgroundColor': '#007bff',
                'color': 'rgb(221, 235, 234)',
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'filter_query': '{{Placed %}} = {}'.format(lb_df['Placed %'].max()),
                    'column_id': 'Placed %'
                },
                'backgroundColor': '#007bff',
                'color': 'rgb(221, 235, 234)',
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'filter_query': '{{Win %}} = {}'.format(lb_df['Win %'].max()),
                    'column_id': 'Win %'
                },
                'backgroundColor': '#007bff',
                'color': 'rgb(221, 235, 234)',
                'fontWeight': 'bold',
            },
            {
                'if': {
                    'filter_query': '{{Odds}} = {}'.format(lb_df['Odds'].min()),
                    'column_id': 'Odds'
                },
                'backgroundColor': '#007bff',
                'color': 'rgb(221, 235, 234)',
                'fontWeight': 'bold',
            }
        ] +
        [
            {
                'if': {
                    'filter_query': '{{Rank}} = {}'.format(i),
                    'column_id': 'Rank'
                },
                'color': 'tomato'
            }
            for i in lb_df['Rank'].nsmallest(10)
        ],
        style_cell_conditional=[
        {'if': {'column_id': 'Class'},
            'display': 'none'},
        {'if': {'column_id': 'Gender'},
            'display': 'none'},
        ],
        style_as_list_view=True
    )

# creates url links for the horse names
def display_links(df):
    links = df['zed_url'].to_list()
    names = df['name'].to_list()
    rows = []
    for URL, n in zip(links, names):
        link = f'[{n}](' +str(URL) + ')'
        rows.append(link)
    return rows

# creates the url links for the horse pictures
def horse_svg(df):
    links = df['img_url'].to_list()
    names = df['name'].to_list()
    rows = []
    for URL, n in zip(links, names):
        link = '![horse_svg](' +str(URL) + ')'
        rows.append(link)
    return rows

# data prep for the all-time dataframe
lb_df = lb_df[['img_url','zed_url','name','gen','gender','stable_name',
               'class','race_count','placed_pct','win_pct','odds','rank']]
lb_df['url_name'] = display_links(lb_df)
lb_df['Horse'] = horse_svg(lb_df)
lb_df.rename(columns={'url_name':'Name',
                      'gen':'Gen',
                      'gender':'Gender',
                      'stable_name':'Stable',
                      'class':'Class',
                      'race_count':'Races',
                      'placed_pct':'Placed %',
                      'win_pct':'Win %',
                      'odds':'Odds',
                      'rank':'Rank'}, inplace=True)

lb_df['Placed %'] = round(lb_df['Placed %'].astype(float)*100,2)
lb_df['Win %'] = round(lb_df['Win %'].astype(float)*100,2)
lb_df['Odds'] = round(lb_df['Odds'], 2)
lb_df = lb_df[['Name','Horse','Gen','Stable','Class','Races','Placed %','Win %','Odds','Rank']]

# data prep for the who's hot dataframe
wh_df = wh_df[['img_url','zed_url','name','gen','gender','stable_name',
               'class','race_count','placed_pct','win_pct','odds','rank']]
wh_df['url_name'] = display_links(wh_df)
wh_df['Horse'] = horse_svg(wh_df)
wh_df.rename(columns={'url_name':'Name',
                      'gen':'Gen',
                      'gender':'Gender',
                      'stable_name':'Stable',
                      'class':'Class',
                      'race_count':'Races',
                      'placed_pct':'Placed %',
                      'win_pct':'Win %',
                      'odds':'Odds',
                      'rank':'Rank'}, inplace=True)
wh_df = wh_df[['Name','Horse','Gen','Stable','Class','Races','Placed %','Win %','Odds','Rank']]
wh_df['Placed %'] = round(wh_df['Placed %'].astype(float)*100,2)
wh_df['Win %'] = round(wh_df['Win %'].astype(float)*100,2)
wh_df['Odds'] = round(wh_df['Odds'], 2)

# Styling
tab_style_t = {
    'borderBottom': '3px solid black',
    'borderTop': '3px solid black',
    'borderLeft': '3px solid black',
    'borderRight': '3px solid black',
    'backgroundColor': '#27282A',
    'color': 'rgb(221, 235, 234)',
    'padding': '7px',
    'borderRadius': '15px',
    'fontFamily': font_family,
    'fontWeight': 'bold',
    'fontSize': '20px',
    'margin-bottom': '4px',
    'height': '52px'
}

tab_style_b = {
    'borderBottom': '4px solid black',
    'borderTop': '3px solid black',
    'borderLeft': '3px solid black',
    'borderRight': '3px solid black',
    'backgroundColor': 'rgb(221, 235, 234)',
    'color': 'black',
    'padding': '7px',
    'borderRadius': '15px',
    'fontFamily': font_family,
    'fontWeight': 'bold',
    'fontSize': '16px',
    'margin-bottom': '4px',
    'height': '46px'
}

tab_selected_style = {
    'borderTop': '3px solid #007bff',
    'borderBottom': '3px solid #007bff',
    'borderLeft': '3px solid #007bff',
    'borderRight': '3px solid #007bff',
    'backgroundColor': 'black',
    'fontWeight': 'bold',
    'color': 'rgb(221, 235, 234)',
    'padding': '7px',
    'borderRadius': '15px',
    'fontFamily': font_family,
    'fontSize': '20px',
    'margin-bottom': '4px',
    'height': '52px'
}

tab_selected_style_b = {
    'borderTop': '3px solid #007bff',
    'borderBottom': '3px solid #007bff',
    'borderLeft': '3px solid #007bff',
    'borderRight': '3px solid #007bff',
    'backgroundColor': 'black',
    'fontWeight': 'bold',
    'color': 'rgb(221, 235, 234)',
    'padding': '7px',
    'borderRadius': '15px',
    'fontFamily': font_family,
    'fontSize': '16px',
    'margin-bottom': '4px',
    'height': '46px'
}

CONTENT_STYLE = {
    "margin-left": "1rem",
    "margin-right": "1rem",
    "padding": "1rem 1rem",
}

# leaderboard details
badge = html.Div(
    html.H5(
        [f'Updated',dbc.Badge(updated,pill=True, color="dark", className="ml-1", style={'fontSize':'14px'}),
         '    Horses', dbc.Badge(f"{horse_cnt}",pill=True, color="dark", className="ml-1", style={'fontSize':'14px'})],
        style={"color":"rgb(221, 235, 234)","padding": '3px', "fontFamily": font_family},
    )
)

# nav bar creation
items = [
    dbc.DropdownMenuItem("LΞADΞRBOARD", href="/leaderboard"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("HORSΞ COATS", href="/coats"),
]

dropdown = dbc.Row(
    [
        dbc.Col(
            dbc.DropdownMenu(items, label="INSIGHTS", color="primary", className="m-1", right=True, bs_size="lg"),
        )
    ],
    no_gutters=True,
    className="ml-auto flex-nowrap mt-3 mt-md-0",
    align="center",
)

logo = "/assets/zedruninsights_logo.png"

navbar = dbc.Navbar(
    children=[
        html.A(
            dbc.Row(
                [
                    dbc.Col(html.Img(src=logo, height='30px')),
                    dbc.Col(dbc.NavbarBrand("ZRi", className='ml-2', style={'fontSize':'20px'})),
                ],
                align='center',
                no_gutters=True,
            ),
            href="/",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(dropdown, id="navbar-collapse", navbar=True),
    ],
    color="#27282A",
    dark=True,
)

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

app.layout = html.Div(style={'backgroundColor': 'black'}, children=[
    dcc.Location(id="url"),
    navbar,
    content
])

# callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

# renders the page content
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    # eventually create a home landing page and then make another elif for /leaderboard
    if pathname == "/" or pathname == "/leaderboard":
        return [html.Div(className='row',
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div([
                                            dbc.Button(
                                                "info",
                                                id="simple-toast-toggle",
                                                color="primary",
                                                className="mb-3",
                                                size="lg",
                                                style={'height':'34px'}
                                            ),
                                            dbc.Toast(
                                                [html.P(["""A leaderboard of the top racehorses on the ZΞD RUN platform.
                                                        The Rank is generated by a weighted race performance metrics algorithm.""",
                                                        html.Br(),html.Br(),
                                                        """Included metrics:""",
                                                        html.Br(),
                                                        """Win %, Place %, ETH Profit and Races.""",
                                                        html.Br(),html.Br(),
                                                        """Horses will show up on the All-Time leaderboard once they have raced 25 paid races.
                                                        To make it on the Who's Hot leaderboard you must have raced at least 10 paid races
                                                        over the past two weeks.""",
                                                        html.Br(),html.Br(),
                                                        """- oWylee"""], className="mb-0")],
                                                id="simple-toast",
                                                icon="primary",
                                                header="LΞADΞRBOARD info",
                                                is_open=False,
                                                dismissable=True,
                                                style={"fontSize":"12px","width":400},
                                            ),
                                        ]
                                        ),
                                        width="auto",
                                        style={'margin-left': '-7px', 'margin-right': '8px'}
                                    ),
                                    dbc.Col(
                                        html.H1(
                                            children='LΞADΞRBOARD',
                                            style={
                                                'color': 'rgb(221, 235, 234)',
                                                'backgroundColor':'black',
                                                'fontSize': '44px',
                                                'fontFamily': font_family
                                            }
                                        ),
                                        width="auto",
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            badge
                                        ),
                                        width="auto",
                                    ),
                                ],
                                align="center",
                                no_gutters=False,
                            ),
                        ]),
                dcc.Tabs(
                    id="tabs-with-filter",
                    value='tab-t2',
                    parent_className='custom-tabs',
                    className='custom-tabs-container',
                    children=[
                        dcc.Tab(
                            label='All-Time',
                            value='tab-t1',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_t,
                            selected_style=tab_selected_style
                        ),
                        dcc.Tab(
                            label="Who's Hot (Last 2wks)",
                            value='tab-t2',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_t,
                            selected_style=tab_selected_style
                        ),
                ]),
                html.Div(id='tabs-content-filter'),
                dcc.Tabs(
                    id="tabs-with-classes",
                    value='tab-1',
                    parent_className='custom-tabs',
                    className='custom-tabs-container',
                    children=[
                        dcc.Tab(
                            label='Class I',
                            value='tab-1',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_b,
                            selected_style=tab_selected_style_b
                        ),
                        dcc.Tab(
                            label='Class II',
                            value='tab-2',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_b,
                            selected_style=tab_selected_style_b
                        ),
                        dcc.Tab(
                            label='Class III',
                            value='tab-3', className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_b,
                            selected_style=tab_selected_style_b
                        ),
                        dcc.Tab(
                            label='Class IV',
                            value='tab-4',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_b,
                            selected_style=tab_selected_style_b
                        ),
                        dcc.Tab(
                            label='Class V',
                            value='tab-5',
                            className='custom-tab',
                            selected_className='custom-tab--selected',
                            style=tab_style_b,
                            selected_style=tab_selected_style_b
                        ),
                ]),
                html.Div(id='tabs-content-classes'),
                html.Div(id='datatable-interactivity-container')
                ]
    elif pathname == "/coats":
        return [
                html.Div(className='row',
                        style = {'display':'flex',
                                'width': '100%'},
                        children=[
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div([
                                        dbc.Button(
                                            "info",
                                            id="simple-toast-toggle",
                                            color="primary",
                                            className="mb-3",
                                            size="lg",
                                            style={'height':'34px'}
                                        ),
                                        dbc.Toast(
                                            [html.P(["""An interactive view into the current breakdown of horse coats
                                                    scattered across the ZΞD RUN metaverse.""",
                                                    html.Br(),html.Br(),
                                                    """The Sunburst visual (my favorite), is pretty straightforward.
                                                    For the Treemap you can zoom in and out using the tabs on the top.
                                                    Billions is included in the data but not visible due to the scale.
                                                    He is the rarest horse in the game and the only horse
                                                    with a Fortune coat... for those that don't already know.""",
                                                    html.Br(),
                                                    """Enjoy zedheads!""",
                                                    html.Br(),html.Br(),
                                                    """- oWylee"""], className="mb-0")],
                                            id="simple-toast",
                                            icon="primary",
                                            header="HORSΞ COATS info",
                                            is_open=False,
                                            dismissable=True,
                                            style={"fontSize":"12px","width":400},
                                        ),
                                    ]
                                    ),
                                    width="auto",
                                    style={'margin-left': '-7px', 'margin-right': '8px'}
                                ),
                                dbc.Col(
                                    html.H1(
                                        children='HORSΞ COATS',
                                        style={
                                            'color': 'rgb(221, 235, 234)',
                                            'backgroundColor':'black',
                                            'fontSize': '44px',
                                            'fontFamily': font_family
                                        }
                                    ),
                                    width="auto",
                                ),
                                dbc.Col(
                                    html.Div(
                                        html.Div(
                                                html.H5(
                                                    [f'Updated',dbc.Badge("4.14.2021",pill=True, color="dark", className="ml-1", style={'fontSize':'14px'}),
                                                    '    Horses', dbc.Badge("19681",pill=True, color="dark", className="ml-1", style={'fontSize':'14px'})],
                                                    style={"color":"rgb(221, 235, 234)","padding": '3px', "fontFamily": font_family},
                                                )
                                            )
                                    ),
                                    width="auto",
                                ),
                            ],
                            align="center",
                            no_gutters=False,
                        ),
                        #
                        # html.H1(
                        #     children='HORSΞ COATS',
                        #     style={'height': '55px',
                        #         'color': 'rgb(221, 235, 234)',
                        #         'backgroundColor':'black',
                        #         'padding': '5px',
                        #         'width': '100%',
                        #         'textAlign': 'center',
                        #         'fontSize': '40px',
                        #         'display': 'inline-block',
                        #         'fontFamily': font_family
                        #     }
                        # ),
                        #
                        html.Div([
                            dcc.Graph(figure=fig, responsive='auto', style={'width': '100%', 'height': '100vh'}),
                        ], style = {'display': 'inline-block', 'width': '100%', 'height':'100vh', 'margin-left': '30px'}),
                        # html.Div(
                        #     children=f'Data updated: 4.14.2021 | 19681 Horses | *Billions included/hidden', style={
                        #     'textAlign': 'right',
                        #     'fontSize': '8px',
                        #     'color': 'rgb(221, 235, 234)',
                        #     'padding': '1px',
                        #     'width': '100%',
                        #     'display': 'inline-block',
                        #     'fontFamily': font_family
                        # }),
                        html.Div(
                            html.A("zed.run source", href='https://community.zed.run/breed/coat-colour/', target="_blank"), style={
                            'textAlign': 'right',
                            'fontSize': '8px',
                            'color': 'rgb(221, 235, 234)',
                            'padding': '1px',
                            'width': '100%',
                            'display': 'inline-block',
                            'fontFamily': font_family
                        })
                        ])
                ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# callback for opening toast/info
@app.callback(Output("simple-toast", "is_open"),
              Input("simple-toast-toggle", "n_clicks"))
def open_toast(n):
    if n:
        return True
    return False

# callback for using the tab filters on the leaderboard page
@app.callback(Output('tabs-content-classes', 'children'),
              Input('tabs-with-classes', 'value'),
              Input('tabs-with-filter', 'value'))
def render_content(tab,tab_fil):
    if tab == 'tab-1' and tab_fil == 'tab-t1':
        lb_dff = lb_df[lb_df['Class'] == 1]
        return generate_table(lb_dff)
    elif tab == 'tab-2' and tab_fil == 'tab-t1':
        lb_dff = lb_df[lb_df['Class'] == 2]
        return generate_table(lb_dff)
    elif tab == 'tab-3' and tab_fil == 'tab-t1':
        lb_dff = lb_df[lb_df['Class'] == 3]
        return generate_table(lb_dff)
    elif tab == 'tab-4' and tab_fil == 'tab-t1':
        lb_dff = lb_df[lb_df['Class'] == 4]
        return generate_table(lb_dff)
    elif tab == 'tab-5' and tab_fil == 'tab-t1':
        lb_dff = lb_df[lb_df['Class'] == 5]
        return generate_table(lb_dff)
    elif tab == 'tab-1' and tab_fil == 'tab-t2':
        lb_dff = wh_df[wh_df['Class'] == 1]
        return generate_table(lb_dff)
    elif tab == 'tab-2' and tab_fil == 'tab-t2':
        lb_dff = wh_df[wh_df['Class'] == 2]
        return generate_table(lb_dff)
    elif tab == 'tab-3' and tab_fil == 'tab-t2':
        lb_dff = wh_df[wh_df['Class'] == 3]
        return generate_table(lb_dff)
    elif tab == 'tab-4' and tab_fil == 'tab-t2':
        lb_dff = wh_df[wh_df['Class'] == 4]
        return generate_table(lb_dff)
    elif tab == 'tab-5' and tab_fil == 'tab-t2':
        lb_dff = wh_df[wh_df['Class'] == 5]
        return generate_table(lb_dff)
    else:
        lb_dff = lb_df[lb_df['Class'] == 1]
        return generate_table(lb_dff)

if __name__ == '__main__':
    app.run_server()