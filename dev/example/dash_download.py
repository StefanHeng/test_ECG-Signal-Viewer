import dash
import dash_html_components as html
import numpy as np
import pandas as pd

from dash.dependencies import Output, Input
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame

# Generate some example data.
data = np.column_stack((np.arange(10), np.arange(10) * 2))
df = pd.DataFrame(columns=["a column", "another column"], data=data)
# Create app.
app = dash.Dash(prevent_initial_callbacks=True)
app.layout = html.Div([html.Button("Download csv", id="btn"), Download(id="download")])

@app.callback(Output("download", "data"), [Input("btn", "n_clicks")])
def generate_csv(n_nlicks):
    return send_data_frame(df.to_csv, filename="some_name.csv")

if __name__ == '__main__':
    app.run_server()