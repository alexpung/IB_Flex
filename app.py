import sqlite3

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from pages import futures, equity

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

# Get statement of fund and open position with security information
df_sof_info = pd.merge(df_statement_of_fund, df_security_info, on='conid')
df_open_position_info = df_open_position.merge(df_security_info, on='conid')

# Get cumulative PnL for each future contract
df_future_pnl = df_sof_info[df_sof_info.assetCategory == 'FUT'][['underlyingSymbol', 'date', 'amount']]
df_future_pnl['Profit'] = df_future_pnl.groupby('underlyingSymbol').cumsum()

df_future_open_position_info = df_open_position_info[df_open_position_info['assetCategory'] == 'FUT']
df_future_table = df_future_pnl.sort_values('date').groupby('underlyingSymbol').tail(1)
df_future_table_show = df_future_table.merge(df_future_open_position_info, how='left', on='underlyingSymbol')[[
    'underlyingSymbol', 'position', 'Profit']].round(2).fillna('Closed')

# get deposit and withdrawals
df_deposit_withdrawal = df_statement_of_fund[(df_statement_of_fund['activityCode'] == 'DEP') |
                                             (df_statement_of_fund['activityCode'] == 'WITH')]
df_deposit_withdrawal['amountInBase'] = df_deposit_withdrawal['amount'] * df_deposit_withdrawal['fxRateToBase']
df_deposit_withdrawal = df_deposit_withdrawal[['date', 'amountInBase']]
df_equity_sum = df_equity_sum.merge(df_deposit_withdrawal, how='left', left_on='reportDate', right_on='date')
df_equity_sum = df_equity_sum.drop(['date'], axis=1)
df_equity_sum = df_equity_sum.fillna(0)
df_equity_sum['Net total deposit and withdrawal'] = df_equity_sum['amountInBase'].cumsum()
df_equity_sum['Profit and Loss'] = df_equity_sum['total'] - df_equity_sum['Net total deposit and withdrawal']
# HTML layout
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
app.config.suppress_callback_exceptions = True
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/future":
        return futures.create_layout(df_future_table_show)
    if pathname == "/equity history":
        return equity.create_layout(df_equity_sum)
    else:
        return equity.create_layout(df_equity_sum)


@app.callback(
    Output('pnl_graph', 'figure'),
    [Input('future_summary_table', 'selected_rows')]
)
def update_graph(selected):
    if selected is None:
        traces = []
        symbol_name = ""
    else:
        symbol_name = df_future_table_show.iloc[selected[0]]['underlyingSymbol']
        filtered_df = df_future_pnl[df_future_pnl.underlyingSymbol == symbol_name]
        traces = [go.Scatter(x=filtered_df['date'], y=filtered_df['Profit'])]
    title = f'PnL for {symbol_name}'
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
