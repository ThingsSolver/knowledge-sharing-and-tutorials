# import libraries
import pandas as pd
import numpy as np
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
import os
import plotly.graph_objs as go

# set display options
pd.set_option('display.MAX_ROWS', 500)
pd.set_option('display.MAX_COLUMNS', 500)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

# import data
df = pd.read_csv('../input_files/segmentation_data_and_clv_fake.csv')

# preprocessing data
df = df.rename(str.lower, axis='columns')
df['cluster'] = df['cluster'].astype('str')
df['clv'] = np.round(df['clv'], 2)
df.drop(['observation_date', 'birth_dt'], axis=1, inplace=True)

for i in list(df.columns):
    df[i] = df[i].replace('"', '')

# measures on a cluster level
df_agg = df[['cluster_label', 'cluster', 'recency', 'frequency', 'monetary_value', 'tenure', 'clv', 'age']].groupby(
    by=['cluster_label', 'cluster'], as_index=False).agg(
    ['count', 'mean', 'std', 'min', 'median', 'max']).sort_values(
    by=['cluster_label', 'cluster'], ascending=False)

df_agg.columns = ['_'.join(x) for x in df_agg.columns.ravel()]
df_agg.reset_index(inplace=True)

df_agg_mean = df_agg[['cluster_label', 'cluster', 'recency_mean', 'frequency_mean', 'monetary_value_mean',
                       'tenure_mean', 'clv_mean', 'age_mean']]

df_agg_mean_t = df_agg_mean.T
df_agg_mean_t.columns = ['regular', 'promising', 'premium', 'needing_attention', 'dormant', 'about_to_sleep']
df_agg_mean_t = df_agg_mean_t.iloc[2:-1, :]

# centroids overview table
df_agg_mean_centroids = df_agg_mean_t.copy()
df_agg_mean_centroids.reset_index(inplace=True)
df_agg_mean_centroids.rename(columns={'index':'centroid_parameter'}, inplace=True)

# column lists
df_agg_mean_t_cols = ['regular', 'promising', 'premium', 'needing_attention', 'dormant', 'about_to_sleep']
df_cols = list(df.columns)
df_agg_mean_centroids_cols = list(df_agg_mean_centroids.columns)

PAGE_SIZE = 10

# Plotly
# CLIENT SEGMENTS
# pie chart for clients segments
labels = np.sort(df['cluster_label'].unique())
df_cl_label = df['cluster_label'].value_counts().to_frame().sort_index()
value_list = df_cl_label['cluster_label'].tolist()

trace = go.Pie(labels=labels,
               values=value_list,
               marker=dict(
                   colors=['rgb(42,60,142)', 'rgb(199,119,68)', 'rgb(91,138,104)', 'rgb(67,125,178)', 'rgb(225,184,10)',
                           'rgb(165,12,12)'])
               )
data = [trace]
layout = go.Layout(title='Client segments')
pie_fig = go.Figure(data=data, layout=layout)

# scatterpolar charts for centroids
radar_plots = []

for feat in df_agg_mean_t.index:
    data = [go.Scatterpolar(
        r=df_agg_mean_t.loc[feat, :].values,
        theta=df_agg_mean_t.columns,
        fill='toself',
        name=feat
    )]

    layout = go.Layout(title=feat + ' by segment')
    radar_fig = go.Figure(data=data, layout=layout)

    radar_plots.append(
        html.Div(className='col-sm-4',
                 children=[
                     dcc.Graph(
                         figure=radar_fig
                     )
                 ]
                 )
    )

# Flask app instance
server = flask.Flask('main_app')
server.secret_key = os.environ.get('secret_key', 'secret')

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash('__name__', server=server, external_stylesheets=external_stylesheets)

app.scripts.config.serve_locally = False
dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'

children_list = [
    html.Div(className='mat-card', style={"display": "block", "margin": "15px"},
             children=[
                 html.H1(children='Segmentation dashboard')
             ]),

    html.Div(className='mat-card', style={"display": "block", "margin": "15px"},
             children=[
                 html.P('Filtering supports equals: eq, greater than: >, and less than: < operations. '
                        'In filter field type e.g.: eq "Adam Vladić" and for numerical columns: eq 34 or > 500')
                 ]),

    html.Div(className='mat-card', style={"display": "block", "margin": "15px"},
             children=[
                 html.H4(children='Clients dataset'),
                 dash_table.DataTable(
                     id='cust-table2',
                     columns=[{'name': i, 'id': i} for i in df_cols],
                     style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                     style_header={'backgroundColor': 'white', 'fontWeight': 'bold'},
                     pagination_settings={
                         'current_page': 0,
                         'page_size': PAGE_SIZE
                     },
                     pagination_mode='be',
                     filtering='be',
                     filtering_settings='',
                     sorting='be',
                     sorting_type='multi',
                     sorting_settings=[]
                 )
             ]),

    html.Div(className='mat-card', style={"display": "block", "margin": "15px"},
             children=[
                 html.H4(children='Centroids overview'),
                 dash_table.DataTable(
                     id='cust-table',
                     columns=[{'name': i, 'id': i} for i in df_agg_mean_centroids_cols],
                     data=df_agg_mean_centroids.to_dict("rows"),
                     style_cell_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}],
                     style_header={'backgroundColor': 'white', 'fontWeight': 'bold'}
                 )
             ]),

    html.Div(className='mat-card', style={"display": "block", "margin": "15px"},
             children=[
                 html.H4(children='Segments size'),
                 dcc.Graph(
                     figure=pie_fig
                 )
             ]),

    html.Div(className='mat-card row', style={"display": "block", "margin": "15px"},
             children=[
                 html.H4(children='Variables overview')
             ]+radar_plots)
]


app.layout = html.Div(children=children_list)


@app.callback(
    Output('cust-table2', 'data'),
    [
     Input('cust-table2', 'pagination_settings'),
     Input('cust-table2', 'sorting_settings'),
     Input('cust-table2', 'filtering_settings')
    ])
def update_table(pagination_settings, sorting_settings, filtering_settings):
    inter_df = df

    filtering_expressions = filtering_settings.split(' && ')
    dff = inter_df
    for filter in filtering_expressions:
        if ' eq ' in filter:
            col_name = filter.split(' eq ')[0]
            filter_value = filter.split(' eq ')[1]
            col_name = col_name.replace('"', '')
            filter_value = filter_value.replace('"', '')
            for i in list(df.columns):
                df[i] = df[i].astype(str)
            dff = dff.loc[dff[col_name] == filter_value]
        if ' > ' in filter:
            col_name = filter.split(' > ')[0]
            filter_value = float(filter.split(' > ')[1])
            col_name = col_name.replace('"', '')
            # filter_value = filter_value.replace('"', '')
            dff = dff.loc[dff[col_name] > filter_value]
        if ' < ' in filter:
            col_name = filter.split(' < ')[0]
            filter_value = float(filter.split(' < ')[1])
            col_name = col_name.replace('"', '')
            # filter_value = filter_value.replace('"', '')
            dff = dff.loc[dff[col_name] < filter_value]

    if len(sorting_settings):
        dff = dff.sort_values(
            [col['column_id'] for col in sorting_settings],
            ascending=[
                col['direction'] == 'asc'
                for col in sorting_settings
            ],
            inplace=False
        )
    dff = dff.loc[:, df_cols]
    return dff.iloc[
           pagination_settings['current_page'] * pagination_settings['page_size']:
           (pagination_settings['current_page'] + 1) * pagination_settings['page_size']
           ].to_dict('rows')


if __name__ == '__main__':
    app.run_server(debug=True)


