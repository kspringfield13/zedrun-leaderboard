import base64
import datetime
import io
import plotly.graph_objs as go

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import dash_table

tabtitle = 'Leaderboard'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = tabtitle

colors = {
    'background': 'black',
    'text': 'white'
}

# add file to to directory
lb_df = pd.read_csv('zedrun_leaderboard-v6_by_class.csv')

def generate_table(lb_df):
    return dash_table.DataTable(
        id='table',
        columns = [{"name": i, "id": i} for i in lb_df.columns],
        data = lb_df.to_dict('records'),
        editable=False,
        cell_selectable=False,
        row_selectable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="single",
        row_deletable=False,
        # export_format='xlsx',
        # export_headers='display',
        page_action='none',
        fixed_rows={'headers': False},
        style_header={
            'height': 'auto',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'center',
            'padding': '3px',
            'backgroundColor': 'rgb(10, 10, 10)',
            'color': 'white',
            'fontWeight': 'bold',
            'font_family': 'arial',
            'font_size': '14px',
            'backgroundColor': 'rgb(10, 10, 10)'
        },
        style_data={
            'height': 'auto',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'textAlign': 'center',
            'padding': '3px',
            'backgroundColor': 'rgb(10, 10, 10)',
            'color': 'white',
            'font_family': 'arial',
            'font_size': '12px'
        },
        style_header_conditional=[
        {
            'if': {'column_id': 'Name'},
            'textAlign': 'right'
        }
        ],
        style_data_conditional=[
            {
            'if': {'column_id': 'Name'},
            'textAlign': 'right',
            'fontWeight': 'bold'
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(86,89,87)',
            },
            {
                'if': {
                    'filter_query': '{{Races}} = {}'.format(lb_df['Races'].max()),
                    'column_id': 'Races'
                },
                'backgroundColor': 'rgb(22, 245, 230)',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Placed %}} = {}'.format(lb_df['Placed %'].max()),
                    'column_id': 'Placed %'
                },
                'backgroundColor': 'rgb(22, 245, 230)',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Win %}} = {}'.format(lb_df['Win %'].max()),
                    'column_id': 'Win %'
                },
                'backgroundColor': 'rgb(22, 245, 230)',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{ETH Won}} = {}'.format(lb_df['ETH Won'].max()),
                    'column_id': 'ETH Won'
                },
                'backgroundColor': 'rgb(22, 245, 230)',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Rank}} = {}'.format(lb_df['Rank'].min()),
                    'column_id': 'Rank'
                },
                'backgroundColor': 'rgb(22, 245, 230)',
                'color': 'black'
            },
        ],
        style_cell_conditional=[
        {'if': {'column_id': 'Name'},
         'width': '100px'}
        ],
        style_as_list_view=True
    )

lb_df = lb_df[['name','gen','bloodline','breed_type','gender','stable_name',
               'class','race_count','placed_pct','win_pct','prize_money','rank']]
lb_df.rename(columns={'name':'Name',
                      'gen':'Gen',
                      'bloodline':'Bloodline',
                      'breed_type':'Breed',
                      'gender':'Gender',
                      'stable_name':'Stable',
                      'class':'Class',
                      'race_count':'Races',
                      'placed_pct':'Placed %',
                      'win_pct':'Win %',
                      'prize_money':'ETH Won',
                      'rank':'Rank'}, inplace=True)

lb_df['Placed %'] = round(lb_df['Placed %'].astype(float)*100,2)
lb_df['Win %'] = round(lb_df['Win %'].astype(float)*100,2)
lb_df['ETH Won'] = round(lb_df['ETH Won'], 2)

now = datetime.datetime.now()

tab_style = {
    'borderBottom': '1px solid black',
    'padding': '3px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '3px solid rgb(0, 255, 238)',
    'borderBottom': '3px solid rgb(0, 255, 238)',
    'borderLeft': '3px solid rgb(0, 255, 238)',
    'borderRight': '3px solid rgb(0, 255, 238)',
    'backgroundColor': 'black',
    'color': 'rgb(0, 255, 238)',
    'padding': '3px'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(children=f'Created by: oWylee | Data updated: {now.isoformat()[:10]}', style={
        'textAlign': 'right',
        'fontSize': '10px',
        'color': colors['text'],
        'padding': '5px'

    }),
    html.H1(
        children='♘ ZED.RUN LEADERBOARD ♘',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'backgroundColor':'black',
            'padding': '5px'
        }
    ),
    html.Div(children=f'*Ranked by Current Class & 25 Race Min.', style={
        'textAlign': 'right',
        'color': colors['text'],
        'fontSize': '10px',
        'padding': '5px'
    }),
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
                style=tab_style,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class II',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class III',
                value='tab-3', className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class IV',
                value='tab-4',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class V',
                value='tab-5',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style,
                selected_style=tab_selected_style
            ),
        ]),
    html.Div(id='tabs-content-classes'),
    html.Div(id='datatable-interactivity-container'),
])

@app.callback(Output('tabs-content-classes', 'children'),
              Input('tabs-with-classes', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        lb_dff = lb_df[lb_df['Class'] == 1]
        return generate_table(lb_dff)
    elif tab == 'tab-2':
        lb_dff = lb_df[lb_df['Class'] == 2]
        return generate_table(lb_dff)
    elif tab == 'tab-3':
        lb_dff = lb_df[lb_df['Class'] == 3]
        return generate_table(lb_dff)
    elif tab == 'tab-4':
        lb_dff = lb_df[lb_df['Class'] == 4]
        return generate_table(lb_dff)
    elif tab == 'tab-5':
        lb_dff = lb_df[lb_df['Class'] == 5]
        return generate_table(lb_dff)

if __name__ == '__main__':
    app.run_server()