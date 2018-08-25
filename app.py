import os

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

chosen_class = servant_classes[3:6]
chosen_availability = servant_availability[:2]
chosen_types = player_types[:3]

chosen_servants = list(servant_df[servant_df['Class'].isin(chosen_class) & servant_df['Availability'].isin(chosen_availability)]['Servant'])

summary = player_df[chosen_servants].sum()[2:].replace(False, 0)

app = dash.Dash(__name__)
server = app.server

app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='fgo-servant-data',
        figure={
            'data': [
                go.Pie(
					labels = list(summary.index),
					values = list(summary)
                )
            ],
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)