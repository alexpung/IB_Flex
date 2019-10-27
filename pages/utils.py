import dash_bootstrap_components as dbc
import dash_table
import plotly.graph_objs as go


def get_menu():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(children=[dbc.NavLink("Account value history", href="/equity history")]),
            dbc.NavItem(children=[dbc.NavLink("Futures contract", href="/future")]),
        ],
        brand='Interactive broker Account Analysis',
        color="dark",
        dark=True,
    )


def make_dash_table(df, ids):
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        row_selectable='single',
        id=ids
    )


def make_graph(traces, title):
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
