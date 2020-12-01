import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import ecg_record


if __name__ == "__main__":
    # ecg_record, seg, lead = ecgrecord.ECGRecord.example()
    #
    # x_vals = seg.get_time_axis()[100000:]
    # y_vals = lead.get_ecg_values()[100000:]
    #
    # df = pd.DataFrame(dict(x=x_vals,
    #                        y=y_vals))
    #
    # fig = px.scatter(df, x="x", y="y", render_mode='webgl')
    #
    # fig.update_traces(marker_line=dict(width=1, color='DarkSlateGray'))
    #
    # fig.show()

    N = 1000000

    # Create figure
    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=np.random.randn(N),
            y=np.random.randn(N),
            mode='markers',
            marker=dict(
                line=dict(
                    width=1,
                    color='DarkSlateGrey')
            )
        )
    )

    fig.show()
