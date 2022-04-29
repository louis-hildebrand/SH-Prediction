"""
Global constants.
"""

# Default spreadsheet names
WORKBOOK_NAME = "data/example.xlsx"
WORKSHEET_NAME = "Data"

# Spreadsheet format
SPREADSHEET_HEADER = ["game", "round", "president", "chancellor", "outcome", "top_deck", "pres_get", "pres_give", "chan_get", "veto_attempt", "last_round", "pres_action", "target", "num_lib", "accuse", None, "player", "role", None, "winning_team", "win_reason", None, "pres_get_actual", "chan_get_actual"]
SPREADSHEET_NUM_COLS = len(SPREADSHEET_HEADER)
SPREADSHEET_MAX_ROWS = 10000

# Data file locations
GAME_FILE_PATH = "data/data/tables/game.csv"
PLAYER_FILE_PATH = "data/data/tables/player.csv"
LEG_SESSION_FILE_PATH = "data/data/tables/legislative_session.csv"
PRES_ACTION_FILE_PATH = "data/data/tables/president_action.csv"
