import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

conn = sqlite3.connect("account.db")
with conn:
    df_equity = pd.read_sql_query("""SELECT reportDate, SUM(total) as total
                                     FROM EquitySummaryByReportDateInBase
                                     GROUP BY reportDate""", conn)
    graph_list = [{'label': 'Account Value', 'value': 'account value'}]
    df_future_list = pd.read_sql_query("""SELECT DISTINCT SecurityInfo.underlyingSymbol
    FROM SecurityInfo
    WHERE assetCategory = "FUT" """, conn)
    graph_list.extend([{'label': x, 'value': x} for x in df_future_list['underlyingSymbol'].tolist()])
    df_future_pnl = pd.read_sql_query("""SELECT underlyingSymbol, date, SUM(amount) OVER (PARTITION BY SecurityInfo.underlyingSymbol ORDER BY StatementOfFundsLine.date) as pnl
        FROM StatementOfFundsLine
        INNER JOIN SecurityInfo on StatementOfFundsLine.conid = SecurityInfo.conid
        WHERE StatementOfFundsLine.conid in (
        SELECT SecurityInfo.conid
        FROM SecurityInfo 
        WHERE assetCategory = "FUT")""", conn)

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    dcc.Dropdown(
        id='future_symbol',
        options=graph_list
    ),
    dcc.Graph(id='pnl_graph'),
])


@app.callback(
    Output('pnl_graph', 'figure'),
    [Input('future_symbol', 'value')]
)
def update_graph(selected_contract):
    if selected_contract == 'account value':
        traces = [go.Scatter(x=df_equity['reportDate'], y=df_equity['total'])]
        title = 'Account value'
    else:
        filtered_df = df_future_pnl[df_future_pnl.underlyingSymbol == selected_contract]
        traces = [go.Scatter(x=filtered_df['date'], y=filtered_df['pnl'])]
        title = f'PnL for {selected_contract}'
    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'title': 'Date'},
            yaxis={'title': title},
            margin={'l': 60, 'b': 40, 't': 20, 'r': 20},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
