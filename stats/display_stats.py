from argparse import Namespace
from stats.data import get_data

import pandas as pd


def _format_dataframe(df: pd.DataFrame, table_name: str) -> None:
    pd.set_option(
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", None)
    df.fillna("", inplace=True)
    if table_name == "p-values":
        pd.set_option("display.float_format", lambda x: f"{x:.3f}")
    else:
        pd.set_option("display.float_format", lambda x: f"{x:.0%}")


def main(args: Namespace) -> None:
    table_name = args.table
    df = get_data(table_name)
    _format_dataframe(df, table_name)
    print(df.to_string(index=False))
