import os
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

player_df = pd.read_csv("data/merged_df.csv", index_col=0)
servant_df = pd.read_csv("data/servant - manual.csv")

servant_classes = list(servant_df['Class'].unique())
servant_availability = list(servant_df['Availability'].unique())
player_types = list(player_df['Money Spent'].unique())

dash_classes = [{'label': servant_class, 'value': servant_class} for servant_class in servant_classes]
dash_availability = [{'label': availability, 'value': availability} for availability in servant_availability]
dash_types = [{'label': type, 'value': type} for type in player_types]

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.H1(children='FGO NA Summer Servant Survey'),

    html.Div(children='''
        Servant Class
    '''),

    dcc.Dropdown(
        id='class_checklist',
        options=dash_classes,
        multi=True,
        value=servant_classes
    ),

    html.Div(children='''
        Servant Availability
    '''),

    dcc.Dropdown(
        id='availability_checklist',
        options=dash_availability,
        multi=True,
        value=servant_availability
    ),

    html.Div(children='''
        Spending Amount
    '''),

    dcc.Dropdown(
        id='type_checklist',
        options=dash_types,
        multi=True,
        value=player_types
    ),

    dcc.Graph(id='fgo_servant_data')
], style={
    'max-width': '1000px',
    'margin': 'auto'
})

@app.callback(
    dash.dependencies.Output('fgo_servant_data', 'figure'),
    [dash.dependencies.Input('class_checklist', 'value'),
     dash.dependencies.Input('availability_checklist', 'value'),
     dash.dependencies.Input('type_checklist', 'value')])
def update_graph(chosen_class, chosen_availability, chosen_type):
    chosen_servants = list(servant_df[servant_df['Class'].isin(chosen_class) & servant_df['Availability'].isin(chosen_availability)]['Servant'])
    summary = player_df[player_df['Money Spent'].isin(chosen_type)][chosen_servants].sum().replace(False, 0)

    return {
            'data': [
                go.Pie(
					labels = list(summary.index),
					values = list(summary),
                    direction = "clockwise"
                )
            ],
        }

if __name__ == '__main__':
    app.run_server(debug=True)
