from __future__ import annotations
from argparse import _SubParsersAction, ArgumentParser

import argparse
import config
import data.sync as sync
import os
import prediction.predict as predict
import stats.display_stats as display_stats


def _try_add_private_subparsers(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    """
    Adds subparsers for the private subcommands if the data/data submodule is present, otherwise creates a data/data/table folder.
    """
    try:
        from data.data.manage import add_subparsers
        add_subparsers(subparsers)
    except ModuleNotFoundError:
        os.makedirs(config.DATA_TABLE_FOLDER, exist_ok=True)


def _add_import_parser(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    import_parser = subparsers.add_parser("import", help="Import data from a spreadsheet.")
    import_parser.add_argument("--file", "-f", required=False, default=config.WORKBOOK_NAME, help="File from which to import the data.")
    import_parser.set_defaults(func=sync.main)


def _add_predict_parser(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    predict_parser = subparsers.add_parser("predict", help="Predict roles in a game.")
    predict_parser.add_argument("--game", "-g", type=int, default=-1, help="Game for which to make the prediction")
    predict_parser.add_argument("--round", "-r", type=int, default=-1, help="Number of rounds to use in the prediction.")
    predict_parser.set_defaults(func=predict.main)


def _add_stats_parser(subparsers: _SubParsersAction[ArgumentParser]) -> None:
    stats_parser = subparsers.add_parser("stats", help="Display stats.")
    stats_parser.add_argument("table", type=str, help="Which statistics to display.")
    stats_parser.set_defaults(func=display_stats.main)


def main():
    parser = argparse.ArgumentParser(description="Predict player roles in Secret Hitler.")
    subparsers = parser.add_subparsers()
    _add_import_parser(subparsers)
    _add_predict_parser(subparsers)
    _add_stats_parser(subparsers)
    _try_add_private_subparsers(subparsers)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
