import plotly.graph_objects as go

from icecream import ic


if __name__ == "__main__":
    tpl = go.layout.Template()
    ic(tpl, type(tpl))
    tpl.layout.annotationdefaults = dict(
        font=dict(
            color="crimson"
        )
    )

    fig = go.Figure()
    fig.update_layout(
         template=tpl,
         annotations=[
             dict(
                 text="Look Here",
                 x=1,
                 y=1,
                 showarrow=False,
             ),
             dict(text="Look There", x=2, y=2)
         ]
     )
    fig.show()
