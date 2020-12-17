import plotly.graph_objects as go

trace1 = go.Scatter(
    x=[0, 1, 2],
    y=[10, 11, 12]
)
trace2 = go.Scatter(
    x=[2, 3, 4],
    y=[100, 110, 120],
    yaxis="y2"
)
trace3 = go.Scatter(
    x=[3, 4, 5],
    y=[1000, 1100, 1200],
    yaxis="y3"
)
data = [trace1, trace2, trace3]
layout = go.Layout(
    yaxis=dict(
        domain=[0, 0.33]
    ),
    legend=dict(
        traceorder="reversed"
    ),
    yaxis2=dict(
        domain=[0.33, 0.66]
    ),
    yaxis3=dict(
        domain=[0.66, 1]
    )
)

if __name__ == '__main__':
    fig = go.Figure(data=data, layout=layout)
    fig.show()

