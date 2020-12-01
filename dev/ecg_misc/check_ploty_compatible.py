import numpy as np
import plotly.graph_objs as go
from datetime import timedelta

import ecg_record


def get_time_axis_timedelta(arr):
    return np.vectorize(lambda t: timedelta(milliseconds=float(t)))(arr)


if __name__ == "__main__":
    ecg_record, seg, lead = ecg_record.EcgRecord.example()

    x_vals = np.arange(100)
    print(timedelta(milliseconds=float(x_vals[23])))
    x_vals = get_time_axis_timedelta(x_vals)
    print(type(x_vals[0]))
    y_vals = lead.get_ecg_values()[:100]
    fig = go.Figure(
        data=go.Scatter(
            x=x_vals,
            y=y_vals
        ))
    fig.show()
