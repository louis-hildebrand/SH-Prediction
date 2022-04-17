from data import sync
from data.data.archive import sync as sync_archive, migrate as migrate_archive
from data.data.randomize_names import make_mapping, apply_mapping
from prediction import predict

import argparse
import config


def _sync_archive(args) -> None:
    sync_archive.main()


def _migrate_archive(args) -> None:
    migrate_archive.main(args.file)


def _make_name_mapping(args) -> None:
    make_mapping.main()


def _apply_name_mapping(args) -> None:
    apply_mapping.main()


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
    # 'sync-archive' subcommand (private)
    archive_sync_parser = subparsers.add_parser("sync-archive")
    archive_sync_parser.set_defaults(func=_sync_archive)
    # 'migrate-archive' subcommand (private)
    archive_migrate_parser = subparsers.add_parser("migrate-archive")
    archive_migrate_parser.add_argument("--file", "-f", required=False, default=config.WORKBOOK_NAME)
    archive_migrate_parser.set_defaults(func=_migrate_archive)
    # 'make-name-mapping' subcommand (private)
    map_names_parser = subparsers.add_parser("make-name-mapping")
    map_names_parser.set_defaults(func=_make_name_mapping)
    # 'apply-name-mapping' subcommand (private)
    shuffle_names_parser = subparsers.add_parser("apply-name-mapping")
    shuffle_names_parser.set_defaults(func=_apply_name_mapping)
    # Parse arguments
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
