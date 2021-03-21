import plotly.graph_objects as go

from icecream import ic

if __name__ == "__main__":
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=[1, 2, 3],
            y=[1, 3, 1]))

    # fig.show(config={
    #     'modeBarButtonsToRemove': ['toggleSpikelines','hoverCompareCartesian']
    # })
    fig.show()
    ic(type(fig))
    # ic(fig.keys())
    # ic(fig['config'])

