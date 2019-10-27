import dash_core_components as dcc
import dash_html_components as html

from utils import get_menu, make_dash_table


def create_layout(df_future_list):
    return html.Div(
        [
            get_menu(),
            html.Div(
                [make_dash_table(df_future_list, 'future_summary_table')],
                className="selectable table"
            ),
            html.Div(
                [dcc.Graph(id='pnl_graph')],
                className="future graph"
            )
        ],
    )
