import plotly.graph_objects as go


DEFAULT_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {
        "family": "IBM Plex Sans",
        "color": "#EEF3F5",
    },
}


def apply_equitylens_layout(
    figure,
    *,
    height=None,
    margin=None,
):
    layout = dict(DEFAULT_LAYOUT)
    if height is not None:
        layout["height"] = height
    if margin is not None:
        layout["margin"] = margin
    figure.update_layout(**layout)
    return figure


def line_figure(
    x,
    y,
    *,
    name="",
    height=360,
):
    figure = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="lines",
            name=name,
        )
    )
    return apply_equitylens_layout(
        figure,
        height=height,
        margin={
            "l": 10,
            "r": 10,
            "t": 20,
            "b": 10,
        },
    )
