import os
import re
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input
import pandas as pd
import plotly.graph_objs as go


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

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    children=[
        html.H1(children="FGO NA 2020-01 Survey"),
        html.Div(children="Servant Class"),
        dcc.Checklist(
            id="class_checklist",
            options=dash_classes,
            labelStyle={"display": "inline-block"},
            value=servant_classes,
        ),
        html.Div(children="Servant Availability"),
        dcc.Checklist(
            id="availability_checklist",
            options=dash_availability,
            labelStyle={"display": "inline-block"},
            value=servant_availability,
        ),
        html.Div(children="Spending Amount"),
        dcc.Checklist(
            id="type_checklist",
            options=dash_types,
            labelStyle={"display": "inline-block"},
            value=player_types,
        ),
        dcc.Graph(id="fgo_servant_data"),
        html.Div(id="percent-chart"),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in ["Servant", "Count", "% have"]],
            style_cell_conditional=[
                {"if": {"column_id": "Servant"}, "textAlign": "left"}
            ],
            style_as_list_view=True,
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
            ],
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold",
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
    [Output("fgo_servant_data", "figure"), Output("table", "data"),],
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
    figure = {
        "data": [
            go.Pie(
                labels=list(summary.index), values=list(summary), direction="clockwise"
            )
        ]
    }
    summary = summary.to_frame().reset_index()
    summary.columns = ["Servant", "Count"]
    summary["% have"] = (summary["Count"] / player_count * 100).round(2)
    summary = summary.sort_values("% have", ascending=False)
    table_data = summary.to_dict("records")
    return figure, table_data


@app.callback(
    [Output("percent-chart", "children"),],
    [
        Input("table", "derived_virtual_data"),
        Input("table", "derived_virtual_selected_rows"),
    ],
)
def update_bar_charts(rows, derived_virtual_selected_rows):
    if derived_virtual_selected_rows is None:
        derived_virtual_selected_rows = []
    dff = (
        pd.DataFrame.from_dict({"Servant": ["Artoria"], "Count": [1], "% have": [1]})
        if rows is None
        else pd.DataFrame(rows)
    )
    colors = [
        "#7FDBFF" if i in derived_virtual_selected_rows else "#0074D9"
        for i in range(len(dff))
    ]
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
                "xaxis": {"automargin": True},
                "yaxis": {"automargin": True, "title": {"text": "% have"}},
                "height": 500,
                "margin": {"t": 10, "l": 10, "r": 10, "b": 200},
            },
        },
    )
    return [percent_figure]


if __name__ == "__main__":
    app.run_server(debug=True)
