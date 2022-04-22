from argparse import Namespace
from data.models import Game, LegislativeSession, Player, PresidentAction, LegislativeOutcome, Party, Role
from prediction.game_context import GameContext

import data.repository as re
import matplotlib.pyplot as plt
import pandas as pd
import prediction.model.pmodel as pmodel


# Chart colours
rgb = lambda r, g, b: (r/255, g/255, b/255)
FAS_COLOUR = rgb(255, 124, 36)  # "chocolate1"
HIT_COLOUR = rgb(208, 4, 4)  # "red3"
LIB_COLOUR = rgb(136, 204, 252)  # "skyblue1"


def _max_round(leg_sessions: list[LegislativeSession]) -> int:
    # Find the maximum number of rounds that can be used in the prediction
    # Stop the round *before* the game is complete
    # TODO: Allow rounds to be used after 5 fascist policies have been passed
    leg_sessions.sort(key=lambda ls: ls.round_num)
    fas_passed = 0
    for ls in leg_sessions:
        if ls.last_round:
            return ls.round_num - 1
        if ls.outcome == LegislativeOutcome.FAS:
            fas_passed += 1
            if fas_passed >= 5:
                return ls.round_num
    # No last round found: all rounds can be used in prediction
    return leg_sessions[-1].round_num


def _get_game(game_id: int, round_num: int) -> tuple[Game, list[Player], list[LegislativeSession], list[PresidentAction]]:
    # Game
    games = re.get_all_games()
    if game_id < 0:
        game_id += 1 + len(games)
    games_with_id = [g for g in games if g.game_id == game_id]
    if len(games_with_id) == 0:
        raise ValueError(f"No game with ID {game_id} found.")
    game = games_with_id[0]
    # Players
    players = [p for p in re.get_all_players() if p.game_id == game_id]
    # Legislative sessions
    leg_sessions = [ls for ls in re.get_all_leg_sessions() if ls.game_id == game_id]
    max_round = _max_round(leg_sessions)
    if round_num < 0:
        round_num += 1 + len(leg_sessions)
    if round_num < max_round:
        max_round = round_num
    leg_sessions = [ls for ls in leg_sessions if ls.round_num <= max_round]
    # President actions
    pres_actions = [a for a in re.get_all_pres_actions() if a.game_id == game_id and a.round_num <= max_round]
    return game, players, leg_sessions, pres_actions


def _role_assignments_with_givens(player_names: list[str], givens: dict[str, Role], remaining_fas: int) -> list[dict[str, Role]]:
    if remaining_fas == 0:
        return [givens]
    num_players = len(player_names)
    role_assignments = []
    for (i, name) in enumerate(player_names):
        # If there wouldn't be enough players left to fill the required number of fascists, stop right away
        if remaining_fas > num_players - i:
            break
        other_players = player_names[(i+1):]
        new_givens = givens.copy()
        new_givens[name] = Role.FAS
        role_assignments += _role_assignments_with_givens(other_players, new_givens, remaining_fas - 1)
    return role_assignments


def _fill_roles(role_assignment: dict[str, Role], player_names: list[str]) -> None:
    for name in player_names:
        if name not in role_assignment:
            role_assignment[name] = Role.LIB


def _get_all_role_assignments(player_names: list[str]) -> list[dict[str, Role]]:
    role_assignments = []
    for name in player_names:
        given = {name: Role.HIT}
        num_fas_players = GameContext.count_fas_players(len(player_names))
        other_players = [p for p in player_names if p != name]
        role_assignments += _role_assignments_with_givens(other_players, given, num_fas_players)
    for ra in role_assignments:
        _fill_roles(ra, player_names)
    return role_assignments


def _get_hitler_name(role_assignment: dict[str, Role]) -> str:
    return next(name for (name, role) in role_assignment.items() if role == Role.HIT)


def _get_fascist_names(role_assignment: dict[str, Role]) -> str:
    return [name for (name, role) in role_assignment.items() if role == Role.FAS]


def _plot_individual_probabilities(ind_prob: pd.DataFrame) -> None:
    labels = ind_prob.keys()
    prob_fas = [x[0] for x in ind_prob.values()]
    prob_hit = [x[1] for x in ind_prob.values()]
    prob_lib = [x[2] for x in ind_prob.values()]

    _, ax = plt.subplots()
    ax.bar(labels, prob_fas, label="Fas", color=FAS_COLOUR)
    ax.bar(labels, prob_hit, bottom = prob_fas, label="Hit", color=HIT_COLOUR)
    ax.bar(labels, prob_lib, bottom = [pf + ph for (pf, ph) in zip(prob_fas, prob_hit)], label="Lib", color=LIB_COLOUR)

    plt.show()


def _display_team_probabilities(game_probabilities: list[tuple[dict[str, Role], float]]) -> None:
    print()
    print("Role assignment probabilities")
    print("-----------------------------")
    game_probabilities.sort(key=lambda x: x[1], reverse=True)
    for (roles, prob) in game_probabilities:
        if prob == 0:
            break
        hitler_name = _get_hitler_name(roles)
        fascist_names = _get_fascist_names(roles)
        print(f"Hitler: {hitler_name}, fascists: {fascist_names}: {100*prob:.2f}%")


def _display_individual_probabilities(game_probabilities: list[tuple[dict[str, Role], float]], player_names: list[str]) -> None:
    print()
    print("Individual probabilities")
    print("------------------------")
    individual_probabilities = {}
    for name in player_names:
        ind_prob = [0, 0, 0]
        for (role, prob) in game_probabilities:
            if role[name] == Role.FAS:
                ind_prob[0] += prob
            elif role[name] == Role.HIT:
                ind_prob[1] += prob
            else:
                ind_prob[2] += prob
        individual_probabilities[name] = ind_prob
    print(pd.DataFrame(individual_probabilities, index=["Fas", "Hit", "Lib"]))
    _plot_individual_probabilities(individual_probabilities)


def main(args: Namespace) -> None:
    game, players, leg_sessions, pres_actions = _get_game(args.game, args.round)
    max_round = max([ls.round_num for ls in leg_sessions])
    print(f"Making prediction for game {game.game_id} up to and including round {max_round}.")
    player_names = [p.name for p in players]
    role_assignments = _get_all_role_assignments(player_names)
    game_probabilities = []
    num_assignments = len(role_assignments)
    for (i, ra) in enumerate(role_assignments, start=1):
        prob = pmodel.prob_game_given_roles(leg_sessions, pres_actions, ra)
        game_probabilities.append((ra, prob))
        print(f"{i}/{num_assignments}", end="\r")
    total_probability = sum([x[1] for x in game_probabilities])
    game_probabilities = [(ra, p/total_probability) for (ra, p) in game_probabilities]
    _display_team_probabilities(game_probabilities)
    _display_individual_probabilities(game_probabilities, player_names)
