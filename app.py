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

tabtitle = 'ZΞD RUN Insights'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css',dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=.3"}])
server = app.server
app.title = tabtitle
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

# add variable to all sections
font_family = 'verdana'

colors = {
    'background': 'black',
    'text': 'rgb(221, 235, 234)'
}

# add file to to directory
updated = '4.17.2021 1:30am EST'
lb_df = pd.read_csv('zedrun_leaderboard-4.17.2021_1_30_at.csv')

wh_df = pd.read_csv('zedrun_leaderboard-4.17.2021_1_30_wh.csv')

com = lb_df.append(wh_df)
horseys = com.name.drop_duplicates().tolist()

coats = pd.read_csv('horse_coats_4.14.2021.csv')
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
            bgcolor='black'
        ),
    ]
)
            

def generate_table(lb_df):
    return dash_table.DataTable(
        id='table',
        columns = [{"name": i, "id": i} for i in lb_df.columns],
        data = lb_df.to_dict('records'),
        editable=False,
        cell_selectable=False,
        row_selectable=False,
        sort_action="native",
        sort_mode="single",
        row_deletable=False,
        # export_format='xlsx',
        # export_headers='display',
        page_action='none',
        fixed_rows={'headers': True, 'data': 0},
        style_table={
            # 'border': '1px solid rgb(221, 235, 234)',
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
            'font_size': '20px',
            'backgroundColor': 'black'
        },
        style_data={
            'height': '50px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'center',
            'padding': '3px',
            'backgroundColor': 'rgb(10, 10, 10)',
            'color': 'rgb(221, 235, 234)',
            'font_family': font_family,
            'font_size': '18px'
        },
        style_header_conditional=[
        {
            'if': {'column_id': 'Name'},
            'textAlign': 'center'
        }
        ],
        style_data_conditional=[
            {
            'if': {'column_id': 'Name'},
            'textAlign': 'center',
            'fontWeight': 'bold',
            'fontSize': '18px'
            },
            {
            'if': {'column_id': 'Rank'},
            'textAlign': 'center',
            'fontWeight': 'bold',
            'fontSize': '24px'
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
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Placed %}} = {}'.format(lb_df['Placed %'].max()),
                    'column_id': 'Placed %'
                },
                'backgroundColor': '#007bff',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Win %}} = {}'.format(lb_df['Win %'].max()),
                    'column_id': 'Win %'
                },
                'backgroundColor': '#007bff',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Odds}} = {}'.format(lb_df['Odds'].min()),
                    'column_id': 'Odds'
                },
                'backgroundColor': '#007bff',
                'color': 'black'
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
        ] +
        [
            {
                'if': {
                    'filter_query': '{{Rank}} = {}'.format(i),
                    'column_id': 'Name'
                },
                'color': 'tomato'
            }
            for i in lb_df['Rank'].nsmallest(10)
        ],
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'minWidth': '25px', 'width': '30px', 'maxWidth': '75px'
        } ,
        style_cell_conditional=[
        {'if': {'column_id': 'Class'},
            'display': 'none'},
        {'if': {'column_id': 'Gender'},
            'display': 'none'},
        ],
        style_as_list_view=True
    )

lb_df = lb_df[['name','gen','gender','stable_name','class','race_count','placed_pct','win_pct','odds','rank']]
lb_df.rename(columns={'name':'Name',
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

wh_df = wh_df[['name','gen','gender','stable_name',
               'class','race_count','placed_pct','win_pct','odds','rank']]
wh_df.rename(columns={'name':'Name',
                      'gen':'Gen',
                      'gender':'Gender',
                      'stable_name':'Stable',
                      'class':'Class',
                      'race_count':'Races',
                      'placed_pct':'Placed %',
                      'win_pct':'Win %',
                      'odds':'Odds',
                      'rank':'Rank'}, inplace=True)

wh_df['Placed %'] = round(wh_df['Placed %'].astype(float)*100,2)
wh_df['Win %'] = round(wh_df['Win %'].astype(float)*100,2)
wh_df['Odds'] = round(wh_df['Odds'], 2)

tab_style_t = {
    'borderBottom': '3px solid black',
    'borderTop': '3px solid black',
    'borderLeft': '3px solid black',
    'borderRight': '3px solid black',
    'backgroundColor': '#27282A',
    'color': 'rgb(221, 235, 234)',
    'padding': '8px',
    'borderRadius': '15px',
    'fontFamily': font_family,
    'fontWeight': 'bold',
    'fontSize': '20px',
    'margin-bottom': '4px',
    'height': '6vh'
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
    'height': '5vh'
}

tab_selected_style = {
    # 'borderTop': '3px solid rgb(51, 204, 204)',
    # 'borderBottom': '3px solid rgb(51, 204, 204)',
    # 'borderLeft': '3px solid rgb(51, 204, 204)',
    # 'borderRight': '3px solid rgb(51, 204, 204)',
    'borderTop': '3px solid #007bff',
    'borderBottom': '3px solid #007bff',
    'borderLeft': '3px solid #007bff',
    'borderRight': '3px solid #007bff',
    'backgroundColor': 'black',
    'fontWeight': 'bold',
    'color': 'rgb(221, 235, 234)',
    'padding': '8px',
    'borderRadius': '15px',
    'fontFamily': font_family,
    'fontSize': '20px',
    'margin-bottom': '4px',
    'height': '6vh'
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
    'height': '5vh'
}

CONTENT_STYLE = {
    "margin-left": "1rem",
    "margin-right": "1rem",
    "padding": "1rem 1rem",
}

badge = html.Div(
    html.H5(
        [f'Updated',dbc.Badge(updated,pill=True, color="dark", className="ml-1"),'    Horses', dbc.Badge("4171",pill=True, color="dark", className="ml-1")],
        style={"color":"rgb(221, 235, 234)","padding": '3px', "fontFamily": font_family},
    )
)

items = [
    dbc.DropdownMenuItem("LΞADΞRBOARD", href="/leaderboard"),
    dbc.DropdownMenuItem(divider=True),
    dbc.DropdownMenuItem("HORSΞ COATS", href="/coats"),
]

dropdown = dbc.Row(
    [
        dbc.Col(
            dbc.DropdownMenu(items, label="CONTΞNT", color="primary", className="m-1", right=True,
                             style={'fontSize':'18px'}),
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

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    dcc.Location(id="url"),
    # sidebar,
    navbar,
    content
])

# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    # eventually create a home landing page and push this down to /leaderboard
    if pathname == "/":
        return [html.Div(className='row',
                        style = {'display':'flex',
                                'width': '100%'},
                        children=[
                        html.H1(
                            children='LΞADΞRBOARD',
                            style={'height': '55px',
                                'color': 'rgb(221, 235, 234)',
                                'backgroundColor':'black',
                                'paddingTop': '5px',
                                'width': '100%',
                                'textAlign': 'center',
                                'fontSize': '40px',
                                'display': 'inline-block',
                                'fontFamily': font_family
                            }
                        ),
                        badge,
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
    if pathname == "/leaderboard":
        return [html.Div(className='row',
                        style = {'display':'flex',
                                'width': '100%'},
                        children=[
                        html.H1(
                            children='LΞADΞRBOARD',
                            style={'height': '55px',
                                'color': 'rgb(221, 235, 234)',
                                'backgroundColor':'black',
                                'paddingTop': '5px',
                                'width': '100%',
                                'textAlign': 'center',
                                'fontSize': '40px',
                                'display': 'inline-block',
                                'fontFamily': font_family
                            }
                        ),
                        badge,
                        ]),
                dcc.Tabs(
                    id="tabs-with-filter",
                    value='tab-1',
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
                        html.H1(
                            children='HORSΞ COATS',
                            style={'height': '55px',
                                'color': 'rgb(221, 235, 234)',
                                'backgroundColor':'black',
                                'padding': '5px',
                                'width': '100%',
                                'textAlign': 'center',
                                'fontSize': '40px',
                                'display': 'inline-block',
                                'fontFamily': font_family
                            }
                        ),
                        html.Div([
                            dcc.Graph(figure=fig),
                        ], style = {'display': 'inline-block', 'width': '100%', 'height':'100%', 'margin-left': '30px'}),
                        html.Div(
                            children=f'Data updated: 4.14.2021 | 19681 Horses | *Billions included/hidden', style={
                            'textAlign': 'right',
                            'fontSize': '8px',
                            'color': 'rgb(221, 235, 234)',
                            'padding': '1px',
                            'width': '100%',
                            'display': 'inline-block',
                            'fontFamily': font_family
                        }),
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
    elif pathname == "/page-2":
        return [
                html.H1('Test page-2',
                        style={'textAlign':'center'})
                ]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

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