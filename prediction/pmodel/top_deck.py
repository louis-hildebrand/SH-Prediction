from data.models import Party
from prediction.pmodel.game_context import GameContext

import prediction.pmodel.utils as utils


def top_deck(outcome: Party, context: GameContext) -> float:
    """
    Returns the probability of the given top-deck event and updates the game state in-place.
    """
    # TODO: Is it ever necessary to reshuffle the deck here?
    if outcome == Party.FAS:
        # Find P(F)
        prob = utils.prob_pres_get_actual(0, 1, context.draw_pile, context.draw_pile_size)
        # Calculate P(X' = x | F) for each number x
        # P(X' = x | F) = (n - x) / n * P(X = x) / P(F)
        for x in range(7):
            prior_prob = context.draw_pile[x]
            updated_prob = (context.draw_pile_size - x) * prior_prob / (context.draw_pile_size * prob)
            context.draw_pile[x] = updated_prob
        # Update number of policies passed and remaining in the draw pile
        context.draw_pile_size -= 1
        context.fas_passed += 1
    elif outcome == Party.LIB:
        # Find P(L)
        prob = utils.prob_pres_get_actual(1, 1, context.draw_pile, context.draw_pile_size)
        # Calculate P(X' = x | L) for each number x
        # P(X' = x | L) = (x + 1) / n * P(X = x + 1) / P(L)
        for x in range(7):
            prior_prob = context.draw_pile[x] if x < 6 else 0
            updated_prob = (x + 1) * prior_prob / (context.draw_pile_size * prob)
            context.draw_pile[x] = updated_prob
        # Update number of policies passed and remaining in the draw pile
        context.draw_pile_size -= 1
        context.lib_passed += 1
    else:
        raise ValueError(f"Invalid outcome '{outcome}'.")
    return prob
