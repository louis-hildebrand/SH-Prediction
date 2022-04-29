from argparse import _SubParsersAction

import argparse
import config
import data.sync as sync
import prediction.predict as predict


def _try_add_private_subparsers(subparsers: _SubParsersAction) -> None:
    """
    Adds subparsers for the private subcommands if the data/data submodule is present, otherwise does nothing.
    """
    try:
        from data.data.manage import add_subparsers
        add_subparsers(subparsers)
    except ModuleNotFoundError:
        pass


def main():
    parser = argparse.ArgumentParser(description="Predict player roles in Secret Hitler.")
    subparsers = parser.add_subparsers()
    # 'import' subcommand
    import_parser = subparsers.add_parser("import", help="Import data from a spreadsheet.")
    import_parser.add_argument("--file", "-f", required=False, default=config.WORKBOOK_NAME, help="File from which to import the data.")
    import_parser.set_defaults(func=sync.main)
    # 'predict' subcommand
    predict_parser = subparsers.add_parser("predict", help="Predict roles in a game.")
    predict_parser.add_argument("--game", "-g", type=int, default=-1, help="Game for which to make the prediction")
    predict_parser.add_argument("--round", "-r", type=int, default=-1, help="Number of rounds to use in the prediction.")
    predict_parser.set_defaults(func=predict.main)
    # Private subcommands
    _try_add_private_subparsers(subparsers)
    # Parse arguments
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
