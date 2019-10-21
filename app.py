import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

conn = sqlite3.connect("account.db")
with conn:
    # Read all tables from database
    df_equity = pd.read_sql_query("SELECT * FROM EquitySummaryByReportDateInBase", conn)
    df_statement_of_fund = pd.read_sql_query("SELECT * FROM StatementOfFundsLine", conn)
    df_open_position = pd.read_sql_query("SELECT * FROM OpenPosition", conn)
    df_security_info = pd.read_sql_query("SELECT * FROM SecurityInfo", conn)
# prepare data for graphing

# This is the account value graph, values from multiple accounts are summed, as I have more than one account
df_equity_sum = df_equity.groupby(['reportDate']).agg('sum').reset_index()
# Get cumulative PnL for each future contract
df_future_list = df_security_info[df_security_info.assetCategory == 'FUT'].underlyingSymbol.unique()
df_sof_info = pd.merge(df_statement_of_fund, df_security_info, on='conid')
df_future_pnl = df_sof_info[df_sof_info.assetCategory == 'FUT'][['underlyingSymbol', 'date', 'amount']]
df_future_pnl['cumsum'] = df_future_pnl.groupby('underlyingSymbol').cumsum()

# Prepare drop down list
graph_list = [{'label': 'Account Value', 'value': 'account value'}]
graph_list.extend([{'label': x, 'value': x} for x in df_future_list])

# HTML layout
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
        traces = [go.Scatter(x=df_equity_sum['reportDate'], y=df_equity_sum['total'])]
        title = 'Account value'
    else:
        filtered_df = df_future_pnl[df_future_pnl.underlyingSymbol == selected_contract]
        traces = [go.Scatter(x=filtered_df['date'], y=filtered_df['cumsum'])]
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
