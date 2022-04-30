from data.models import Game, Party, Role

import pandas as pd
import sys
import data.repository as repo


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def _get_games_by_num_players(n: int) -> list[Game]:
    num_players = lambda gid: len([p for p in repo.get_all_players() if p.game_id == gid])
    return [g for g in repo.get_all_games() if num_players(g.game_id) == n]


def _player_won(role: Role, winning_team: Party) -> bool:
    return ((winning_team == Party.LIB and role == Role.LIB)
        or (winning_team == Party.FAS and role in [Role.FAS, Role.HIT]))


def _count_games_by_role(history: list[tuple[Role, bool]], role: Role) -> tuple[int, int, float | None]:
    num_games = len([h for h in history if h[0] == role])
    wins = len([h for h in history if h[0] == role and h[1]])
    win_rate = None if num_games == 0 else wins / num_games
    return num_games, wins, win_rate


# ------------------------------------------------------------------------------
# Data sources
# ------------------------------------------------------------------------------
def _player_win_rates() -> pd.DataFrame:
    data = []
    players = repo.get_all_players()
    player_names = {p.name for p in players}
    for name in player_names:
        # Collect relevant data
        player_history = [(p.role, p.game_id) for p in players if p.name == name]
        history = []
        for ph in player_history:
            game = repo.get_game_by_id(ph[1])
            history.append((ph[0], _player_won(ph[0], game.winning_team)))
        # Analyse data
        num_games = len(history)
        wins = len([h for h in history if h[1]])
        win_rate = None if num_games == 0 else wins / num_games
        fas_games, fas_wins, fas_win_rate = _count_games_by_role(history, Role.FAS)
        fas_rate = None if num_games == 0 else fas_games / num_games
        hit_games, hit_wins, hit_win_rate = _count_games_by_role(history, Role.HIT)
        hit_rate = None if num_games == 0 else hit_games / num_games
        lib_games, lib_wins, lib_win_rate = _count_games_by_role(history, Role.LIB)
        lib_rate = None if num_games == 0 else lib_games / num_games
        data.append([name, num_games, wins, win_rate,
            fas_games, fas_rate, fas_wins, fas_win_rate,
            hit_games, hit_rate, hit_wins, hit_win_rate,
            lib_games, lib_rate, lib_wins, lib_win_rate])
    # Sort by name
    data.sort(key=lambda row: row[0])
    headers = ["Name", "Games", "Wins", "Win rate",
        "Fas games", "Fas %", "Fas wins", "Fas win rate",
        "Hit games", "Hit %", "Hit wins", "Hit win rate",
        "Lib games", "Lib %", "Lib wins", "Lib win rate"]
    return pd.DataFrame(data, columns=headers)


def _team_win_rates() -> pd.DataFrame:
    data = []
    for i in range(5, 11):
        games = _get_games_by_num_players(i)
        num_games = len(games)
        fas_wins = len([g for g in games if g.winning_team == Party.FAS])
        fas_win_rate = None if num_games == 0 else fas_wins / num_games
        lib_wins = num_games - fas_wins
        lib_win_rate = None if num_games == 0 else 1 - fas_win_rate
        data.append([i, len(games), fas_wins, fas_win_rate, lib_wins, lib_win_rate])
    headers = ["#players", "#games", "Fas wins", "Fas win rate", "Lib wins", "Lib win rate"]
    return pd.DataFrame(data, columns=headers)


# ------------------------------------------------------------------------------
# Interface
# ------------------------------------------------------------------------------
_data_source = {
    "player-win-rates": _player_win_rates,
    "team-win-rates": _team_win_rates,
}


def get_data(table: str) -> pd.DataFrame:
    try:
        func = _data_source[table]
        return func()
    except KeyError as e:
        print(f"Table '{table}' not found. Valid tables:")
        for k in _data_source:
            print(f"  {k}")
        sys.exit()
