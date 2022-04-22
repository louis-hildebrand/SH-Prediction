from data.models import LegislativeOutcome, LegislativeSession, PresidentAction, Role
from prediction.game_context import GameContext
from prediction.legislative_session import legislative_session
from prediction.president_action import president_action
from prediction.top_deck import top_deck


def prob_game_given_roles(leg_sessions: list[LegislativeSession], pres_actions: list[PresidentAction], role: dict[str, Role]) -> float:
    num_players = len(role)
    context = GameContext(num_players)
    prob = 1
    for ls in leg_sessions:
        # Successful government
        if ls.outcome != LegislativeOutcome.REJECTED:
            # Legislative session
            prob *= legislative_session(ls, role, context)
            # President action (if any)
            pres_actions_in_round = [a for a in pres_actions if a.round_num == ls.round_num]
            if pres_actions_in_round:
                action = pres_actions_in_round[0]
                prob *= president_action(action, ls.pres_name, role, context)
        # Unsuccessful government and top-deck
        elif ls.top_deck:
            prob *= top_deck(ls.top_deck, context)
        # End immediately if probability reaches 0
        if prob == 0:
            break
    return prob
