from argparse import Namespace
from stats.data import get_data

import pandas as pd


def main(args: Namespace) -> None:
    table = args.table
    df = get_data(table)
    pd.set_option(
        "display.float_format", lambda x: f"{x:.0%}",
        "display.max_rows", None,
        "display.max_columns", None,
        "display.width", None)
    df.fillna("",inplace=True)
    print(df.to_string(index=False))
