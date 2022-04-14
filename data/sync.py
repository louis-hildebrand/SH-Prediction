from argparse import Namespace
from data.models import is_valid, Game, LegislativeSession, LegislativeOutcome, Party, Player, PresidentAction, PresidentActionType, Role, WinReason
from datetime import datetime
from openpyxl import load_workbook

import config
import data.repository as repo


HEADER_ROW = ["game", "round", "president", "chancellor", "outcome", "top_deck", "pres_get", "pres_give", "chan_get", "veto_attempt", "last_round", "pres_action", "target", "num_lib", "accuse", None, "player", "role", None, "winning_team", "win_reason", None, "pres_get_actual", "chan_get_actual"]
NUM_COLS = len(HEADER_ROW)


def _read_spreadsheet(file: str) -> list[list]:
    workbook = load_workbook(filename=file, data_only=True)
    worksheet = workbook[config.WORKSHEET_NAME]
    if worksheet.max_column != NUM_COLS:
        raise ValueError(f"Wrong number of columns in spreadsheet. Expected {NUM_COLS} but received {worksheet.max_column}.")
    data = []
    for row in range(1, worksheet.max_row + 1):
        row_data = [worksheet.cell(row=row, column=col).value for col in range(1, worksheet.max_column + 1)]
        data.append(row_data)
    return data


def _is_empty(row: list) -> bool:
    return all([x is None for x in row])


def _is_date(date_str: str) -> bool:
    if not isinstance(date_str, str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _is_date_row(row: list[str]) -> bool:
    return _is_date(row[0]) and _is_empty(row[1:])


def _is_header_row(row: list[str]) -> bool:
    return row == HEADER_ROW


def _parse_data(data: list[list]) -> tuple[list[Game], list[Player], list[LegislativeSession], list[PresidentAction]]:
    games = []
    players = []
    leg_sessions = []
    pres_actions = []
    new_game = False
    for row in data:
        if _is_empty(row):
            continue
        elif _is_date_row(row):
            current_date = datetime.strptime(row[0], "%Y-%m-%d")
        elif _is_header_row(row):
            new_game = True
        else:
            # Save the new game
            if new_game:
                game_id = row[0]
                winning_team = Party(row[19])
                win_reason = WinReason(row[20])
                games.append(Game(game_id, current_date, winning_team, win_reason))
                new_game = False
            # Add player if present
            if row[16] is not None or row[17] is not None:
                name = row[16]
                role = Role(row[17])
                players.append(Player(game_id, name, role))
            # Add legislative session if present
            if row[1] is not None:
                round_num = int(row[1])
                pres_name = row[2]
                chan_name = row[3]
                outcome = LegislativeOutcome(row[4])
                top_deck = None if row[5] is None else Party(row[5])
                pres_get_claim = row[6]
                pres_give_claim = row[7]
                chan_get_claim = row[8]
                veto_attempt = row[9]
                last_round = row[10]
                pres_get_actual = row[22]
                chan_get_actual = row[23]
                leg_sessions.append(LegislativeSession(game_id, round_num, pres_name, chan_name, outcome, top_deck, pres_get_claim, pres_give_claim, chan_get_claim, pres_get_actual, chan_get_actual, veto_attempt, last_round))
                # Add president action if present
                if row[11] is not None:
                    action = PresidentActionType(row[11])
                    target_name = row[12]
                    num_lib = row[13]
                    accuse = row[14]
                    pres_actions.append(PresidentAction(game_id, round_num, action, target_name, num_lib, accuse))
    return games, players, leg_sessions, pres_actions


def main(args: Namespace) -> None:
    file = args.file
    print(f"Starting to import data from '{file}'.")
    data = _read_spreadsheet(file)
    games, players, leg_sessions, pres_actions = _parse_data(data)
    if is_valid(games, players, leg_sessions, pres_actions):
        repo.clear_all()
        for g in games:
            repo.save_game(g)
        for p in players:
            repo.save_player(p)
        for ls in leg_sessions:
            repo.save_leg_session(ls)
        for a in pres_actions:
            repo.save_pres_action(a)
    print("Import complete.")
