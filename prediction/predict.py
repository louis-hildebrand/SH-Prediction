from argparse import Namespace
from data.models import Game, LegislativeSession, Player, PresidentAction, LegislativeOutcome, Party, Role
from prediction.game_context import GameContext

import data.repository as re
import pandas as pd
import prediction.model.models as pmodel


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
        raise ValueError(f"Invalid number of players {num_players}.")


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
        num_fas_players = _count_fas_players(len(player_names))
        other_players = [p for p in player_names if p != name]
        role_assignments += _role_assignments_with_givens(other_players, given, num_fas_players)
    for ra in role_assignments:
        _fill_roles(ra, player_names)
    return role_assignments


def _prob_game_given_roles(leg_sessions: list[LegislativeSession], pres_actions: list[PresidentAction], role: dict[str, Role]) -> float:
    num_players = len(role)
    context = GameContext(num_players)
    prob = 1
    for ls in leg_sessions:
        # Skip probability calculations for rejected rounds
        if ls.outcome != LegislativeOutcome.REJECTED:
            # Reshuffle deck if necessary
            if context.draw_pile_size < 3:
                context.reshuffle_deck()
            # Legislative session
            prob *= pmodel.prob_legislative_session(ls, role, context)
            # President action (if any)
            pres_actions_in_round = [a for a in pres_actions if a.round_num == ls.round_num]
            if pres_actions_in_round:
                action = pres_actions_in_round[0]
                prob *= pmodel.prob_president_action(action, ls.pres_name, role, context)
        # Update game state
        if ls.outcome == LegislativeOutcome.FAS:
            context.fas_passed += 1
            context.draw_pile_size -= 3
        elif ls.outcome == LegislativeOutcome.LIB:
            context.lib_passed += 1
            context.draw_pile_size -= 3
        elif ls.top_deck:
            context.draw_pile_size -= 1
            if ls.top_deck == Party.FAS:
                context.fas_passed += 1
            elif ls.top_deck == Party.LIB:
                context.lib_passed += 1
                # Update draw pile state
                ...
        # End immediately if probability reaches 0
        if prob == 0:
            break
    return prob


def _get_hitler_name(role_assignment: dict[str, Role]) -> str:
    return next(name for (name, role) in role_assignment.items() if role == Role.HIT)


def _get_fascist_names(role_assignment: dict[str, Role]) -> str:
    return [name for (name, role) in role_assignment.items() if role == Role.FAS]


def main(args: Namespace) -> None:
    game, players, leg_sessions, pres_actions = _get_game(args.game, args.round)
    max_round = max([ls.round_num for ls in leg_sessions])
    print(f"Making prediction for game {game.game_id} up to and including round {max_round}.")
    player_names = [p.name for p in players]
    role_assignments = _get_all_role_assignments(player_names)
    game_probabilities = []
    num_assignments = len(role_assignments)
    for (i, ra) in enumerate(role_assignments, start=1):
        prob = _prob_game_given_roles(leg_sessions, pres_actions, ra)
        game_probabilities.append((ra, prob))
        print(f"{i}/{num_assignments}", end="\r")
    total_probability = sum([x[1] for x in game_probabilities])
    # Probabilities for role assignments
    print()
    print("Role assignment probabilities")
    print("-----------------------------")
    game_probabilities = [(ra, p/total_probability) for (ra, p) in game_probabilities]
    game_probabilities.sort(key=lambda x: x[1], reverse=True)
    for (roles, prob) in game_probabilities:
        hitler_name = _get_hitler_name(roles)
        fascist_names = _get_fascist_names(roles)
        print(f"Hitler: {hitler_name}, fascists: {fascist_names}: {100*prob:.2f}%")
    # Probabilities for individuals
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
