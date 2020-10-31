import plotly.graph_objs as go

import ecg_record


# x = np.arange(10)
#
# fig = go.Figure(data=go.Scatter(x=x, y=x**2))
# fig.show()

if __name__ == "__main__":
    ecg_record, seg, lead = ecg_record.EcgRecord.example()

    x_vals = seg.get_time_axis()
    # print(x_vals)
    # print(x_vals.shape[0] / (3600 * 24))
    # x_vals = x_vals[:100000]
    # x_vals = pd.Timestamp(x_vals[:100])
    y_vals = lead.get_ecg_values()
    # print(x_vals.shape[0], y_vals.shape[0])
    # print()
    fig = go.Figure(
        data=go.Scatter(
            x=x_vals,
            y=y_vals
        ))
    # fig = px.line(
    #     x=x_vals,
    #     y=y_vals,
    #     render_mode='webgl'
    # )
    fig.show()
