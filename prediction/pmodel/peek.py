from data.models import Role
from functools import cache
from prediction.pmodel.game_context import GameContext

import math
import pandas as pd


PEEK_FILE = "prediction/model/tables/peek.csv"


@cache
def _get_peek_table() -> pd.DataFrame:
    return pd.read_csv(PEEK_FILE)


def _prob_peek_given_pga(pres: Role, pres_get_actual: int, pres_get_claim: int) -> float:
    # Load the model and find the relevant rows
    peek_table = _get_peek_table()
    def matching_row(row: pd.Series) -> bool:
        return (row["president"] == str(pres) and
            row["pres_get_actual"] == pres_get_actual and
            row["pres_get_claim"] == pres_get_claim)
    peek_table = peek_table[peek_table.apply(matching_row, axis=1)]
    return peek_table.iloc[0]["probability"]


def peek(pres: Role, pres_get_claim: int, context: GameContext) -> float:
    # Find probability of the peek given each possible actual observation
    prob_peek_given_pga = {}
    for a in range(4):
        prob_peek_given_pga[a] = _prob_peek_given_pga(pres, a, pres_get_claim)
    # Find the probability of the peek given each possible number of Liberal policies in the entire draw pile
    prob_peek_given_deck = {}
    n = context.draw_pile_size
    for x in range(min(7, n + 1)):
        prob_peek_given_deck[x] = 0
        for a in range(4):
            binom_coeff = math.comb(x, a) * math.comb(n - x, 3 - a) / math.comb(n, 3)
            prob_peek_given_deck[x] += binom_coeff * prob_peek_given_pga[a]
    # Find the probability of the peek AND each possible number of Liberal policies in the entire draw pile
    prob_peek_and_deck = {}
    for x in range(min(7, n + 1)):
        prob_peek_and_deck[x] = context.draw_pile[x] * prob_peek_given_deck[x]
    # Calculate final result and update state of the draw pile
    prob_peek = sum([p for p in prob_peek_and_deck.keys()])
    for x in range(7):
        # Explicitly handle x being out of range to avoid KeyErrors
        if x <= n:
            context.draw_pile[x] = prob_peek_and_deck[x] / prob_peek
        else:
            context.draw_pile[x] = 0
    return prob_peek
