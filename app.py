import dash
from dash import dcc, html, dash_table
import dash.dash_table.FormatTemplate as FormatTemplate
import pandas as pd
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format


player_df = pd.read_csv("data/merged_df.csv", index_col=0)
servant_df = pd.read_csv("data/servant - manual.csv")

servant_classes = list(servant_df["Class"].unique())
servant_availability = list(servant_df["Availability"].unique())
player_types = [
    "F2P",
    "Paid Gacha Only",
    "$1-50 Monthly",
    "$51-100 Monthly",
    "$101-200 Monthly",
    "$201-300 Monthly",
    "$301- Monthly",
]

dash_classes = [
    {"label": servant_class, "value": servant_class}
    for servant_class in servant_classes
]
dash_availability = [
    {"label": availability, "value": availability}
    for availability in servant_availability
]
dash_types = [{"label": type, "value": type} for type in player_types]

app = dash.Dash(
    __name__,
    show_undo_redo=True,
    url_base_pathname="/servant-survey/",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server

app.layout = html.Div(
    children=[
        html.H2(children="FGO NA 2020-07 Servant Survey"),
        dcc.Markdown(
            "[Survey post by /u/panchovix](https://redd.it/hph5qi) | "
            "[Raw data](https://docs.google.com/spreadsheets/d/1XyHaKLaWPt_ndeACJopUl39_wk4yZAUz3NkdUK9Guw0/edit?usp=sharing) | "
            "[Processed data](https://raw.githubusercontent.com/squaresmile/fgo-servant-survey/master/data/merged_df.csv) | "
            "[Atlas Academy Discord](https://discord.gg/TKJmuCR)"
        ),
        html.Div(
            [
                html.P(
                    "Servant Class:",
                    style={"font-weight": "bold", "display": "inline-block"},
                ),
                dcc.Checklist(
                    id="class_checklist",
                    options=dash_classes,
                    labelStyle={"display": "inline-block"},
                    style={"display": "inline-block"},
                    value=servant_classes,
                ),
            ]
        ),
        html.Div(
            [
                html.P(
                    children="Servant Availability:",
                    style={"font-weight": "bold", "display": "inline-block"},
                ),
                dcc.Checklist(
                    id="availability_checklist",
                    options=dash_availability,
                    labelStyle={"display": "inline-block"},
                    style={"display": "inline-block"},
                    value=servant_availability,
                ),
            ]
        ),
        html.Div(
            [
                html.P(
                    children="Player Type:",
                    style={"font-weight": "bold", "display": "inline-block"},
                ),
                dcc.Checklist(
                    id="type_checklist",
                    options=dash_types,
                    labelStyle={"display": "inline-block"},
                    style={"display": "inline-block"},
                    value=player_types,
                ),
            ]
        ),
        # dcc.Graph(id="fgo_servant_data"),
        html.Div(
            [
                html.P(
                    "Y-axis:", style={"font-weight": "bold", "display": "inline-block"}
                ),
                dcc.RadioItems(
                    id="locked_y_axis",
                    options=[
                        {"label": "0-100%", "value": "locked_y_axis"},
                        {"label": "Relative", "value": "relative_y_axis"},
                    ],
                    labelStyle={"display": "inline-block"},
                    style={"display": "inline-block"},
                    value="locked_y_axis",
                ),
            ]
        ),
        html.Div(id="percent-chart"),
        dash_table.DataTable(
            id="table",
            columns=[
                {"name": "Servant", "id": "Servant"},
                {
                    "name": "Count",
                    "id": "Count",
                    "type": "numeric",
                    "format": Format(group=","),
                },
                {
                    "name": "% have",
                    "id": "% have",
                    "type": "numeric",
                    "format": FormatTemplate.percentage(2),
                },
            ],
            style_cell={"fontSize": "16px"},
            style_cell_conditional=[
                {
                    "if": {"column_id": "Servant"},
                    "textAlign": "left",
                    "fontFamily": "sans-serif",
                }
            ],
            style_as_list_view=True,
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
            ],
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
                "fontFamily": "sans-serif",
            },
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            selected_columns=[],
            selected_rows=[],
        ),
    ],
    className="container",
)


@app.callback(
    Output("table", "data"),
    [
        Input("class_checklist", "value"),
        Input("availability_checklist", "value"),
        Input("type_checklist", "value"),
    ],
)
def update_graph(chosen_class, chosen_availability, chosen_type):
    chosen_servants = list(
        servant_df[
            servant_df["Class"].isin(chosen_class)
            & servant_df["Availability"].isin(chosen_availability)
        ]["Servant"]
    )
    player_count = sum(player_df["Money Spent"].isin(chosen_type))
    summary = (
        player_df[player_df["Money Spent"].isin(chosen_type)][chosen_servants]
        .sum()
        .replace(False, 0)
    )
    # figure = {
    #     "data": [
    #         go.Pie(
    #             labels=list(summary.index), values=list(summary), direction="clockwise"
    #         )
    #     ]
    # }
    summary = summary.to_frame().reset_index()
    summary.columns = ["Servant", "Count"]
    summary["% have"] = summary["Count"] / player_count
    summary = summary.sort_values("% have", ascending=False)
    table_data = summary.to_dict("records")
    return table_data  # , figure


@app.callback(
    [Output("percent-chart", "children")],
    [
        Input("table", "derived_virtual_data"),
        Input("table", "derived_virtual_selected_rows"),
        Input("locked_y_axis", "value"),
    ],
)
def update_bar_charts(rows, derived_virtual_selected_rows, y_axis):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    dff = (
        pd.DataFrame.from_dict({"Servant": ["Artoria"], "Count": [1], "% have": [1]})
        if rows is None or not rows
        else pd.DataFrame(rows)
    )
    colors = [
        "#7FDBFF" if i in derived_virtual_selected_rows else "#0074D9"
        for i in range(len(dff))
    ]
    y_axis_layout = {
        "automargin": True,
        "title": {"text": "% have"},
        "tickformat": "%",
        "range": [0, 1],
    }
    if y_axis == "relative_y_axis":
        y_axis_layout.pop("range")
    percent_figure = dcc.Graph(
        id="percent-figure",
        figure={
            "data": [
                {
                    "x": dff["Servant"],
                    "y": dff["% have"],
                    "type": "bar",
                    "marker": {"color": colors},
                }
            ],
            "layout": {
                "xaxis": {"automargin": True, "tickfont": {"size": 11}},
                "yaxis": y_axis_layout,
                "height": 500,
                "margin": {"t": 10, "l": 10, "r": 10, "b": 200},
                "font": {"family": "sans-serif"},
            },
        },
        config={
            "toImageButtonOptions": {
                "format": "png",
                "filename": "Servant survey",
                "height": 500,
                "width": 1000,
                "scale": 5,
            },
            "scrollZoom": True,
        },
    )
    return [percent_figure]


if __name__ == "__main__":
    app.run_server(debug=True)
