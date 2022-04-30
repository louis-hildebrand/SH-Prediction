from data.models import Game, Party

import pandas as pd
import sys
import data.repository as repo


def _get_games_by_num_players(n: int) -> list[Game]:
    num_players = lambda gid: len([p for p in repo.get_all_players() if p.game_id == gid])
    return [g for g in repo.get_all_games() if num_players(g.game_id) == n]


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
    return pd.DataFrame(data, columns=["#players", "#games", "Fas wins", "Fas win rate", "Lib wins", "Lib win rate"])


_data_source = {
    "team-win-rates": _team_win_rates
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
