# import plotly.express as px
# from skimage import data
# img = data.chelsea() # or any image represented as a numpy array
# fig = px.imshow(img)
# # Define dragmode, newshape parameters, amd add modebar buttons
# fig.update_layout(
#     dragmode='drawrect', # define dragmode
#     newshape=dict(line_color='cyan'))
# # Add modebar buttons
# fig.show(config={'modeBarButtonsToAdd':['drawline',
#                                         'drawopenpath',
#                                         'drawclosedpath',
#                                         'drawcircle',
#                                         'drawrect',
#                                         'eraseshape'
#                                        ]})

import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.express as px
# from skimage import data
import numpy as np
import math

from icecream import ic

app = dash.Dash(__name__)

img = np.zeros(100 ** 2).reshape((100, 100))

fig = px.imshow(img, color_continuous_scale='gray')
fig.update_layout(dragmode='drawline', newshape_line_color='cyan')

app.layout = html.Div(children=[
    dcc.Graph(
        id='graph',
        figure=fig,
        config={'modeBarButtonsToAdd': ['drawline',
                                        'drawopenpath',
                                        'drawclosedpath',
                                        'drawcircle',
                                        'drawrect',
                                        'eraseshape']
                }),
    html.Pre(id='content', children='Length of lines (pixels) \n')
], style={'width': '25%'})


@app.callback(
    dash.dependencies.Output('content', 'children'),
    [dash.dependencies.Input('graph', 'relayoutData')],
    [dash.dependencies.State('content', 'children')])
def shape_added(fig_data, content):
    ic(fig_data)
    if fig_data is None:
        return dash.no_update
    if 'shapes' in fig_data:
        line = fig_data['shapes'][-1]
        length = math.sqrt((line['x1'] - line['x0']) ** 2 +
                           (line['y1'] - line['y0']) ** 2)
        content += '%.1f' % length + '\n'
    return content


if __name__ == '__main__':
    app.run_server(debug=True)
