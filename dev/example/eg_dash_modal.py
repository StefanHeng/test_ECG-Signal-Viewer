import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = html.Div(
    [
        dbc.Button("Open", id="open-centered", n_clicks=0),
        dbc.Modal(
            [
                dbc.ModalHeader(children=[
                    "Header",
                    html.Button('asdh', className='close', n_clicks=0)
                ]),
                dbc.ModalBody("This modal is vertically centered"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close-centered", className="ml-auto", n_clicks=0
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False
        ),
    ]
)


@app.callback(
    Output("modal-centered", "is_open"),
    [Input("open-centered", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open):
    # print(f'n1 is {n1}, n2 is {n2}, is_open is {is_open}')
    # if n1 or n2:
    #     return not is_open
    # return is_open
    return not is_open


if __name__ == "__main__":
    app.run_server(debug=True)


