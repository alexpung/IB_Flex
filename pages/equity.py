import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import get_menu


def make_graph(df):
    traces = [go.Scatter(x=df['reportDate'], y=df['total'], name='Account Value'),
              go.Scatter(x=df['reportDate'], y=df['Profit and Loss'], name='Profit and Loss')]
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Value'},
            margin={'l': 60, 'b': 40, 't': 20, 'r': 20},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


def create_layout(df_account_equity):
    return html.Div(
        [
            get_menu(),
            html.Div(
                [dcc.Graph(id='equity_graph', figure=make_graph(df_account_equity))],
                className="equity graph"
            )
        ],
    )
