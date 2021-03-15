import plotly.graph_objects as go

if __name__ == "__main__":
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=["2013-01-15", "2013-01-29", "2013-02-26", "2013-04-19", "2013-07-02",
           "2013-08-27",
           "2013-10-22", "2014-01-20", "2014-05-05", "2014-07-01", "2015-02-09",
           "2015-04-13",
           "2015-05-13", "2015-06-08", "2015-08-05", "2016-02-25"],
        y=["8", "3", "2", "10", "5", "5", "6", "8", "3", "3", "7", "5", "10", "10", "9",
           "14"],
        mode='markers',
        marker=dict(
            color='#FCA912'
        )
    ))

    fig.update_layout(
        shapes=[
            dict(
                type="line",
                x0="2013-01-15",
                x1="2013-10-17",
                xref="x",
                y0=0,
                y1=0.95,
                yref="paper",
                line={'color': 'cyan', 'dash': 'solid', 'width': 4},
            ),
            dict(
                type='rect',
                fillcolor="rgba(63, 81, 181, 0.6)",
                line={"width": 0},
                x0="2013-10-22",
                x1="2015-08-05",
                xref="x",
                y0=0.3,
                y1=0.7,
                yref="paper"
            )
        ]
    )

    fig.update_layout(
        xaxis=dict(
            autorange=True,
            range=["2012-10-31 18:36:37.3129", "2016-05-10 05:23:22.6871"],
            rangeslider=dict(
                autorange=True,
                range=["2012-10-31 18:36:37.3129", "2016-05-10 05:23:22.6871"]
            ),
            type="date"
        )
    )

    fig.show()

