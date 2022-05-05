from data.models import Game, Party, Role
from utils.progress_bar import ProgressBar
from utils.utils import num_players_with_role

import itertools
import math
import pandas as pd
import sys
import data.repository as repo


# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------
def _num_players(gid: int) -> int:
    return len([p for p in repo.get_all_players() if p.game_id == gid])


def _get_games_by_num_players(n: int) -> list[Game]:
    return [g for g in repo.get_all_games() if _num_players(g.game_id) == n]


def _player_won(role: Role, winning_team: Party) -> bool:
    return ((winning_team == Party.LIB and role == Role.LIB)
        or (winning_team == Party.FAS and role in [Role.FAS, Role.HIT]))


def _count_wins_by_role(history: list[tuple[Role, bool]], role: Role) -> tuple[int, int, float | None]:
    num_games = len([h for h in history if h[0] == role])
    wins = len([h for h in history if h[0] == role and h[1]])
    win_rate = None if num_games == 0 else wins / num_games
    return num_games, wins, win_rate


def _count_games_by_num_players(player_name: str) -> dict[int, int]:
    num_games = {n: 0 for n in range(5, 11)}
    game_ids = [p.game_id for p in repo.get_all_players() if p.name == player_name]
    for gid in game_ids:
        num_games[_num_players(gid)] += 1
    return num_games


def _prob_role(role: Role, num_players: int) -> float:
    return num_players_with_role(role, num_players) / num_players


def _prob_x_iplayer_games_in_role(x: int, num_games: int, role: Role, num_players: int) -> float:
    p = _prob_role(role, num_players)
    return math.comb(num_games, x) * p**x * (1 - p)**(num_games - x)


def _prob_x_games_in_role(num_games: dict[int, int], role: Role) -> dict[int, float]:
    tot_num_games = sum(v for v in num_games.values())
    prob = {n: 0 for n in range(tot_num_games + 1)}
    for x5 in range(num_games[5] + 1):
        p5 = _prob_x_iplayer_games_in_role(x5, num_games[5], role, 5)
        for x6 in range(num_games[6] + 1):
            p6 = _prob_x_iplayer_games_in_role(x6, num_games[6], role, 6)
            for x7 in range(num_games[7] + 1):
                p7 = _prob_x_iplayer_games_in_role(x7, num_games[7], role, 7)
                for x8 in range(num_games[8] + 1):
                    p8 = _prob_x_iplayer_games_in_role(x8, num_games[8], role, 8)
                    for x9 in range(num_games[9] + 1):
                        p9 = _prob_x_iplayer_games_in_role(x9, num_games[9], role, 9)
                        for x10 in range(num_games[10] + 1):
                            p10 = _prob_x_iplayer_games_in_role(x10, num_games[10], role, 10)
                            x = x5 + x6 + x7 + x8 + x9 + x10
                            prob[x] += p5 * p6 * p7 * p8 * p9 * p10
    return prob


def _p_value(player_name: str, role: Role) -> float:
    num_games = _count_games_by_num_players(player_name)
    tot_num_games = sum(v for v in num_games.values())
    # Probability of getting the role x times (for every possible value of x)
    probabilities = _prob_x_games_in_role(num_games, role)
    # Expected value and observed deviation from the expectation
    mu = sum(x*probabilities[x] for x in range(tot_num_games + 1))
    num_games_in_role = len([p for p in repo.get_all_players() if p.name == player_name and p.role == role])
    deviation = abs(num_games_in_role - mu)
    # Probability of being at least as far from the mean on the lower side
    p = 0
    for k in range(math.floor(mu - deviation) + 1):
        p += probabilities[k]
    # Probability of being at least as far from the mean on the upper side
    for k in range(math.ceil(mu + deviation), tot_num_games + 1):
        p += probabilities[k]
    return mu, num_games_in_role, p


# ------------------------------------------------------------------------------
# Data sources
# ------------------------------------------------------------------------------
def _p_values() -> pd.DataFrame:
    player_names = {p.name for p in repo.get_all_players()}
    data = []
    progress_bar = ProgressBar(len(player_names))
    for i, name in enumerate(player_names, start=1):
        expected_fas, actual_fas, p_fas = _p_value(name, Role.FAS)
        expected_hit, actual_hit, p_hit = _p_value(name, Role.HIT)
        expected_lib, actual_lib, p_lib = _p_value(name, Role.LIB)
        data.append([name,
            expected_fas, actual_fas, p_fas,
            expected_hit, actual_hit, p_hit,
            expected_lib, actual_lib, p_lib])
        progress_bar.update(i)
    # Sort by name
    data.sort(key=lambda row: row[0])
    column_tuples = list(itertools.product(["Fas", "Hit", "Lib"], ["Expected", "Actual", "p"]))
    column_tuples = [("", "Name")] + column_tuples
    columns = pd.MultiIndex.from_tuples(column_tuples)
    df = pd.DataFrame(data, columns=columns)
    # Round expected values to 1 decimal place
    df[("Fas", "Expected")] = df[("Fas", "Expected")].map(lambda x: f"{x:.1f}")
    df[("Hit", "Expected")] = df[("Hit", "Expected")].map(lambda x: f"{x:.1f}")
    df[("Lib", "Expected")] = df[("Lib", "Expected")].map(lambda x: f"{x:.1f}")
    return df


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
        fas_games, fas_wins, fas_win_rate = _count_wins_by_role(history, Role.FAS)
        fas_rate = None if num_games == 0 else fas_games / num_games
        hit_games, hit_wins, hit_win_rate = _count_wins_by_role(history, Role.HIT)
        hit_rate = None if num_games == 0 else hit_games / num_games
        lib_games, lib_wins, lib_win_rate = _count_wins_by_role(history, Role.LIB)
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
    "p-values": _p_values,
    "player-win-rates": _player_win_rates,
    "team-win-rates": _team_win_rates,
}


def get_data(table: str) -> pd.DataFrame:
    if table in _data_source:
        func = _data_source[table]
        return func()
    else:
        print(f"Table '{table}' not found. Valid tables:")
        for k in _data_source:
            print(f"  {k}")
        sys.exit()
