from data import sync
from predict import predict

import argparse
import config

def main():
    parser = argparse.ArgumentParser(description="Predict player roles in Secret Hitler.")
    subparsers = parser.add_subparsers()
    # 'import' subcommand
    import_parser = subparsers.add_parser("import", help="Import data from a spreadsheet.")
    import_parser.add_argument("--file", "-f", default=config.DEFAULT_IMPORT_FILE, help="File from which to import the data.")
    # 'predict' subcommand
    predict_parser = subparsers.add_parser("predict", help="Predict roles in a game.")
    predict_parser.add_argument("--game", "-g", type=int, default=-1, help="Game for which to make the prediction")
    predict_parser.add_argument("--round", "-r", type=int, default=-1, help="Number of rounds to use in the prediction.")
    # Parse arguments
    args = parser.parse_args()
    if args.command == "import":
        sync.main(args.file)
    elif args.command == "predict":
        predict.main(args.game, args.round)


if __name__ == "__main__":
    main()
