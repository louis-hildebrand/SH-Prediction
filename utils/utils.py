from data.models import Role


def _count_fas_players(num_players: int) -> int:
    """
    Returns the number of vanilla fascists in a game with `num_players` players.
    """
    if num_players in [5, 6]:
        return 1
    elif num_players in [7, 8]:
        return 2
    elif num_players in [9, 10]:
        return 3
    else:
        raise ValueError(f"Invalid number of players '{num_players}'.")


def num_players_with_role(role: Role, num_players: int) -> int:
    if role == Role.FAS:
        return _count_fas_players(num_players)
    elif role == Role.HIT:
        return 1
    elif role == Role.LIB:
        return num_players - 1 - _count_fas_players(num_players)
    else:
        raise ValueError(f"Invalid role '{role}'.")
