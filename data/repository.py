"""
Repository layer to read, write, and delete gameplay data.
"""

from datetime import datetime
from models import Player, LegislativeSession, PresidentAction, Game, LegislativeOutcome, Party, PresidentActionType, Role, WinReason
from typing import Callable

import config
import csv


GAME_HEADER = ['id', 'date', 'winning_team', 'win_reason']
PLAYER_HEADER = ['game_id', 'name', 'role']
LEG_SESSION_HEADER = ['game_id', 'round', 'president', 'chancellor', 'outcome', 'top_deck', 'pres_get_claim', 'pres_give_claim', 'chan_get_claim', 'pres_get_actual', 'chan_get_actual', 'veto_attempt', 'last_round']
PRES_ACTION_HEADER = ['game_id', 'round', 'action', 'target', 'num_lib', 'accuse']


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def _get_all(file: str, parse: Callable) -> list:
    results = []
    with open(file, "r", newline="") as f:
        csv_reader = csv.reader(f)
        # Skip header
        next(csv_reader)
        for row in csv_reader:
            obj = parse(row)
            results.append(obj)
    return results


def _parse_player(row: list[str]) -> Player:
    game_id = int(row[0])
    name = row[1]
    role = Role(row[2])
    return Player(game_id, name, role)


def _parse_leg_session(row: list[str]) -> LegislativeSession:
    game_id = int(row[0])
    round_num = int(row[1])
    pres_name = row[2]
    chan_name = row[3]
    outcome = LegislativeOutcome(row[4])
    top_deck = None if not row[5] else Party(row[5])
    pres_get_claim = None if not row[6] else int(row[6])
    pres_give_claim = None if not row[7] else int(row[7])
    chan_get_claim = None if not row[8] else int(row[8])
    pres_get_actual = None if not row[9] else int(row[9])
    chan_get_actual = None if not row[10] else int(row[10])
    veto_attempt = bool(row[11])
    last_round = bool(row[12])
    return LegislativeSession(game_id, round_num, pres_name, chan_name, outcome, top_deck, pres_get_claim, pres_give_claim, chan_get_claim, pres_get_actual, chan_get_actual, veto_attempt, last_round)


def _parse_pres_action(row: list[str]) -> PresidentAction:
    game_id = int(row[0])
    round_num = int(row[1])
    action = PresidentActionType(row[2])
    target_name = None if not row[3] else row[3]
    num_lib = None if not row[4] else int(row[4])
    accuse = None if not row[5] else bool(row[5])
    return PresidentAction(game_id, round_num, action, target_name, num_lib, accuse)


def _parse_game(row: list[str]) -> Game:
    game_id = int(row[0])
    date = datetime.strptime(row[1], "%Y-%m-%d")
    winning_team = Party(row[2])
    win_reason = WinReason(row[3])
    return Game(game_id, date, winning_team, win_reason)


def _insert(row: list, file: str) -> None:
    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


# ------------------------------------------------------------------------------
# Read queries
# ------------------------------------------------------------------------------
_players = None
_leg_sessions = None
_pres_actions = None
_games = None


def get_all_pres_actions() -> list[PresidentAction]:
    global _pres_actions
    if _pres_actions is None:
        _pres_actions = _get_all(config.PRES_ACTION_FILE_PATH, _parse_pres_action)
    return _pres_actions


def get_all_leg_sessions() -> list[LegislativeSession]:
    global _leg_sessions
    if _leg_sessions is None:
        _leg_sessions = _get_all(config.LEG_SESSION_FILE_PATH, _parse_leg_session)
    return _leg_sessions


def get_all_players() -> list[Player]:
    global _players
    if _players is None:
        _players = _get_all(config.PLAYER_FILE_PATH, _parse_player)
    return _players


def get_player_by_game_and_name(game_id: int, name: str) -> Player:
    players = [p for p in get_all_players() if p.game_id == game_id and p.name == name]
    if len(players) == 1:
        return players[0]
    elif len(players) == 0:
        raise ValueError(f"No player with game ID '{game_id}' and name '{name}' found.")
    else:
        raise RuntimeError(f"Multiple players with game ID '{game_id}' and name '{name}' found.")


def get_all_games() -> list[Game]:
    global _games
    if _games is None:
        _games = _get_all(config.GAME_FILE_PATH, _parse_game)
    return _games


def get_game_by_id(game_id: int) -> Game:
    games = [g for g in get_all_games() if g.game_id == game_id]
    if len(games) == 1:
        return games[0]
    elif len(games) == 0:
        raise ValueError(f"No game with ID '{game_id}' found.")
    else:
        raise RuntimeError(f"Multiple games with ID '{game_id}' found.")


# ------------------------------------------------------------------------------
# Write queries
# ------------------------------------------------------------------------------
def save_game(g: Game) -> None:
    row = [g.game_id, g.date, g.winning_team, g.win_reason]
    _insert(row, config.GAME_FILE_PATH)


def save_player(p: Player) -> None:
    row = [p.game_id, p.name, p.role]
    _insert(row, config.PLAYER_FILE_PATH)


def save_leg_session(ls: LegislativeSession) -> None:
    row = [ls.game_id, ls.round_num, ls.pres_name, ls.chan_name, ls.outcome, ls.top_deck, ls.pres_get_claim,ls.pres_give_claim, ls.chan_get_claim, ls.pres_get_actual, ls.chan_get_actual, ls.veto_attempt, ls.last_round]
    _insert(row, config.LEG_SESSION_FILE_PATH)


def save_pres_action(a: PresidentAction) -> None:
    row = [a.game_id, a.round_num, a.action, a.target_name, a.num_lib, a.accuse]
    _insert(row, config.PRES_ACTION_FILE_PATH)


# ------------------------------------------------------------------------------
# Delete queries
# ------------------------------------------------------------------------------
def clear_all() -> None:
    """
    Clears all files and rewrites their headers.
    """
    with open(config.GAME_FILE_PATH, 'w', newline='') as game_file,\
         open(config.PLAYER_FILE_PATH, 'w', newline='') as player_file,\
         open(config.LEG_SESSION_FILE_PATH, 'w', newline='') as leg_session_file,\
         open(config.PRES_ACTION_FILE_PATH, 'w', newline='') as pres_action_file:
        # President action
        pres_action_writer = csv.writer(pres_action_file)
        pres_action_writer.writerow(PRES_ACTION_HEADER)
        # Legislative session
        leg_session_writer = csv.writer(leg_session_file)
        leg_session_writer.writerow(LEG_SESSION_HEADER)
        # Player
        player_writer = csv.writer(player_file)
        player_writer.writerow(PLAYER_HEADER)
        # Game
        game_writer = csv.writer(game_file)
        game_writer.writerow(GAME_HEADER)
