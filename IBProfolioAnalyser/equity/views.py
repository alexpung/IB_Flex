import sqlite3

import pandas as pd
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, 'equity.html')


def chart_data(request):
    conn = sqlite3.connect("account.db")
    with conn:
        df_equity = pd.read_sql_query("SELECT * FROM EquitySummaryByReportDateInBase", conn,
                                      parse_dates={'reportDate': '%Y-%m-%d'}, index_col='reportDate')
        df_statement_of_fund = pd.read_sql_query("SELECT * FROM StatementOfFundsLine", conn,
                                                 parse_dates={'reportDate': '%Y-%m-%d', 'date': '%Y-%m-%d'},
                                                 index_col='reportDate')
    # This is the account value graph, values from multiple accounts are summed, as I have more than one account
    df_equity_sum = df_equity.groupby(['reportDate']).agg('sum')
    # get deposit and withdrawals
    # use .copy() to explicitly tell pandas to make a copy due to SettingwithCopyWarning
    df_deposit_withdrawal = df_statement_of_fund[(df_statement_of_fund['activityCode'] == 'DEP') |
                                                 (df_statement_of_fund['activityCode'] == 'WITH')].copy()
    df_deposit_withdrawal['amountInBase'] = df_deposit_withdrawal['amount'] * df_deposit_withdrawal['fxRateToBase']
    df_deposit_withdrawal = df_deposit_withdrawal[['amountInBase']].groupby('reportDate').sum()
    df_equity_sum = df_equity_sum.merge(df_deposit_withdrawal, how='left', on='reportDate')
    df_equity_sum = df_equity_sum.fillna(0)
    df_equity_sum['Net total deposit and withdrawal'] = df_equity_sum['amountInBase'].cumsum()
    # Calculate profit and loss data by subtracting deposit and withdrawal from account value
    df_equity_sum['Profit and Loss'] = df_equity_sum['total'] - df_equity_sum['Net total deposit and withdrawal']
    # Calculate account drawdown
    df_equity_sum['Peak Profit'] = df_equity_sum['Profit and Loss'].cummax()
    df_equity_sum['Drawdown'] = ((df_equity_sum['Peak Profit'] - df_equity_sum['Profit and Loss']) * 100
                                 / (df_equity_sum['total'] + df_equity_sum['Peak Profit']
                                    - df_equity_sum['Profit and Loss']))
    df_equity_sum = df_equity_sum.fillna(0)
    df_display = df_equity_sum[['total', 'Profit and Loss', 'Drawdown']].reset_index()
    return HttpResponse(df_display.to_json(orient='values'), content_type='application/json')
