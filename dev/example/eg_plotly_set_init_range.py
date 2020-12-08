import numpy as np
import pandas as pd

import plotly.graph_objs as go
# import plotly.plotly as py

dates = pd.date_range('01-Jan-2010', pd.datetime.now().date(), freq='D')
df = pd.DataFrame(100 + np.random.randn(dates.size).cumsum(), dates, columns=['AAPL'])

trace = go.Scatter(x=df.index, y=df.AAPL)
data = [trace]
layout = dict(
    title='Time series with range slider and selectors',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(count=1,
                     label='YTD',
                     step='year',
                     stepmode='todate'),
                dict(count=1,
                     label='1y',
                     step='year',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(),
        type='date'
    )
)

fig = go.Figure()
fig.add_trace(trace)
fig.update_layout(
    title='Time series with range slider and selectors',
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=1,
                     label='1m',
                     step='month',
                     stepmode='backward'),
                dict(count=6,
                     label='6m',
                     step='month',
                     stepmode='backward'),
                dict(count=1,
                     label='YTD',
                     step='year',
                     stepmode='todate'),
                dict(count=1,
                     label='1y',
                     step='year',
                     stepmode='backward'),
                dict(step='all')
            ])
        ),
        rangeslider=dict(
            visible=True,
            thickness=0.3
        ),
        type='date'
    ))

initial_range = ['2016-01-01', '2017-09-01']
fig['layout']['xaxis'].update(range=initial_range)
fig.show()
