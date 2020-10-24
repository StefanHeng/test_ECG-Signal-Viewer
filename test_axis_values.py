import plotly.graph_objs as go
import plotly.express as px
import pandas as pd


from test_data_read import DATA_PATH, selected_record
from ecgrecord import *


# x = np.arange(10)
#
# fig = go.Figure(data=go.Scatter(x=x, y=x**2))
# fig.show()

if __name__ == "__main__":
    idx_segment = 0
    idx_lead = 0
    ecg_record = ECGRecord(DATA_PATH.joinpath(selected_record))
    key = list(ecg_record.get_segment_keys())[idx_segment]
    segment = ecg_record.get_segment(key)
    lead = segment.get_lead(idx_lead)

    x_vals = segment.get_time_axis()
    # print(x_vals.shape[0] / (3600 * 24))
    # x_vals = x_vals[:100000]
    # x_vals = pd.Timestamp(x_vals[:100])
    y_vals = lead.get_ecg_values()
    fig = go.Figure(
        data=go.Scatter(
            x=x_vals,
            y=y_vals
        ))
    fig.show()
