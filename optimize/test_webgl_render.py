import pandas as pd
import numpy as np
import plotly.express as px

import ecg_record

if __name__ == "__main__":
    ecg_record, seg, lead = ecg_record.EcgRecord.example()

    x_vals = seg.get_time_axis()
    df = pd.DataFrame(dict(x=np.random.randn(N),
                           y=np.random.randn(N)))

    fig = px.scatter(df, x="x", y="y", render_mode='webgl')

    fig.update_traces(marker_line=dict(width=1, color='DarkSlateGray'))

    fig.show()

