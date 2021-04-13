import base64
import datetime
import io, os
import plotly.graph_objs as go

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import dash_table

tabtitle = 'ZΞD RUN Insights'
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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

colors = {
    'background': 'black',
    'text': 'rgb(221, 235, 234)'
}

# add file to to directory
updated = '4.12.2021 8:00pm EST'
lb_df = pd.read_csv('zedrun_leaderboard-4.12.2021_8_00_at.csv')

wh_df = pd.read_csv('zedrun_leaderboard-4.12.2021_8_00_wh.csv')

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
            'color': 'rgb(221, 235, 234)',
            'fontWeight': 'bold',
            'fontFamily': 'verdana',
            'font_size': '12px',
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
            'font_family': 'verdana',
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
            'fontWeight': 'bold',
            'fontSize': '14px'
            },
            {
            'if': {'column_id': 'Rank'},
            'textAlign': 'center',
            'fontWeight': 'bold',
            'fontSize': '15px'
            },
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(69, 89, 88)',
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
                'backgroundColor': 'rgb(51, 204, 204)',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Win %}} = {}'.format(lb_df['Win %'].max()),
                    'column_id': 'Win %'
                },
                'backgroundColor': 'rgb(51, 204, 204)',
                'color': 'black'
            },
            {
                'if': {
                    'filter_query': '{{Avg. Odds}} = {}'.format(lb_df['Avg. Odds'].min()),
                    'column_id': 'Avg. Odds'
                },
                'backgroundColor': 'rgb(51, 204, 204)',
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
        style_cell_conditional=[
        {'if': {'column_id': 'Name'},
         'width': '100px'}
        ],
        style_as_list_view=True
    )

lb_df = lb_df[['name','gen','bloodline','breed_type','gender','stable_name',
               'class','race_count','placed_pct','win_pct','odds','rank']]
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
                      'odds':'Avg. Odds',
                      'rank':'Rank'}, inplace=True)

lb_df['Placed %'] = round(lb_df['Placed %'].astype(float)*100,2)
lb_df['Win %'] = round(lb_df['Win %'].astype(float)*100,2)
lb_df['Avg. Odds'] = round(lb_df['Avg. Odds'], 2)

wh_df = wh_df[['name','gen','bloodline','breed_type','gender','stable_name',
               'class','race_count','placed_pct','win_pct','odds','rank']]
wh_df.rename(columns={'name':'Name',
                      'gen':'Gen',
                      'bloodline':'Bloodline',
                      'breed_type':'Breed',
                      'gender':'Gender',
                      'stable_name':'Stable',
                      'class':'Class',
                      'race_count':'Races',
                      'placed_pct':'Placed %',
                      'win_pct':'Win %',
                      'odds':'Avg. Odds',
                      'rank':'Rank'}, inplace=True)

wh_df['Placed %'] = round(wh_df['Placed %'].astype(float)*100,2)
wh_df['Win %'] = round(wh_df['Win %'].astype(float)*100,2)
wh_df['Avg. Odds'] = round(wh_df['Avg. Odds'], 2)

tab_style_t = {
    'borderBottom': '3px solid black',
    'borderTop': '3px solid black',
    'borderLeft': '3px solid black',
    'borderRight': '3px solid black',
    'backgroundColor': 'rgb(69, 89, 88)',
    'color': 'rgb(221, 235, 234)',
    'padding': '3px',
    'borderRadius': '15px',
    'fontFamily': 'verdana'
}

tab_style_b = {
    'borderBottom': '3px solid black',
    'borderTop': '3px solid black',
    'borderLeft': '3px solid black',
    'borderRight': '3px solid black',
    'backgroundColor': 'rgb(221, 235, 234)',
    'color': 'black',
    'padding': '3px',
    'borderRadius': '15px',
    'fontFamily': 'verdana'
}

tab_selected_style = {
    'borderTop': '3px solid rgb(51, 204, 204)',
    'borderBottom': '3px solid rgb(51, 204, 204)',
    'borderLeft': '3px solid rgb(51, 204, 204)',
    'borderRight': '3px solid rgb(51, 204, 204)',
    'backgroundColor': 'black',
    'fontWeight': 'bold',
    'color': 'rgb(51, 204, 204)',
    'padding': '3px',
    'borderRadius': '15px',
    'fontFamily': 'verdana'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.Div(className='row',
        style = {'display':'flex'},
        children=[
    html.Div(
        children=f'V1.3', style={
        'textAlign': 'left',
        'fontSize': '8px',
        'color': 'rgb(221, 235, 234)',
        'padding': '5px',
        'width': '49.5%',
        'display': 'inline-block',
        'fontFamily': 'verdana'
    }), 
    html.Div(
        children=f'Created by: oWylee | Data updated: {updated}', style={
        'textAlign': 'right',
        'fontSize': '8px',
        'color': 'rgb(221, 235, 234)',
        'padding': '5px',
        'width': '49.5%',
        'display': 'inline-block',
        'fontFamily': 'verdana'
    })]
    ),
    html.Div(className='row',
             style = {'display':'flex',
                      'width': '100%'},
             children=[
            html.Img(src=app.get_asset_url('avi.png'),
                     style={
                         'height': '63px',
                         'width': '-20%',
                         'display': 'inline-block',
                         'padding': '5px'
                     }),
            html.H1(
                children='ZΞD RUN LΞADΞRBOARD',
                style={'height': '35px',
                       'color': 'rgb(221, 235, 234)',
                       'backgroundColor':'black',
                       'padding': '5px',
                       'width': '100%',
                       'textAlign': 'center',
                       'display': 'inline-block',
                       'fontFamily': 'verdana'
                }
            ),
            html.Img(src=app.get_asset_url('avi.png'),
                     style={
                         'height': '63px',
                         'width': '-20%',
                         'display': 'inline-block',
                         'padding': '5px'
                     })
            ]),
    html.Div(className='row',
             style = {'display':'flex'},
             children=[
            html.Div(
                children=f'5038 Horses *Ranked by Current Class & 20-AT|10-WH Race Min. *Paid Races Only', style={
                'textAlign': 'left',
                'fontSize': '8px',
                'color': 'rgb(221, 235, 234)',
                'padding': '5px',
                'width': '49.5%',
                'display': 'inline-block',
                'fontFamily': 'verdana'
            }), 
            html.Div(
                children=f'ETH Donations | 0x25dBcB2550Abe56e15FEC436F56fB7664dd11a07', style={
                'textAlign': 'right',
                'fontSize': '8px',
                'color': 'rgb(221, 235, 234)',
                'padding': '5px',
                'width': '49.5%',
                'display': 'inline-block',
                'fontFamily': 'verdana'
            })]
            ),
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
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class II',
                value='tab-2',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style_b,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class III',
                value='tab-3', className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style_b,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class IV',
                value='tab-4',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style_b,
                selected_style=tab_selected_style
            ),
            dcc.Tab(
                label='Class V',
                value='tab-5',
                className='custom-tab',
                selected_className='custom-tab--selected',
                style=tab_style_b,
                selected_style=tab_selected_style
            ),
    ]),
html.Div(id='tabs-content-classes'),
html.Div(id='datatable-interactivity-container'),
])

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