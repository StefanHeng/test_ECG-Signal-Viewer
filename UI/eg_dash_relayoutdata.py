import os
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import json


# app=dash.Dash()
#
# app.layout = html.Div([
#                 dcc.Graph(id='graph',figure=fig),
#                 html.Pre(id='relayout-data', style=styles['pre']),
#                 dcc.Graph(id='graph2', figure=fig)])
#
# # Just to see what values are captured.
# @app.callback(Output('relayout-data', 'children'),
#               [Input('graph', 'relayoutData')])
# def display_relayout_data(relayout_data):
#     return json.dumps(relayout_data, indent=2)
#
#
# @app.callback(Output('graph2', 'figure'),
#              [Input('graph', 'relayoutData')],
#              [State('graph2', 'figure')])
# def graph_event(select_data,  fig):
#     try:
#        fig['layout'] = {'xaxis':{'range':[select_data['xaxis.range[0]'],select_data['xaxis.range[1]']]}}
#     except KeyError:
#        fig['layout'] = {'xaxis':{'range':[zoomed out value]}}
#     return fig
#
# if __name__ == '__main__':
#     app.run_server(debug=True)
