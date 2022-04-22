from data.models import Role
from functools import cache
from prediction.game_context import GameContext

import pandas as pd
import prediction.utils as utils


INVESTIGATION_TARGET_FILE = "prediction/tables/inv_target.csv"
INVESTIGATE_FILE = "prediction/tables/investigate.csv"


def _get_investigation_parameters(context: GameContext) -> dict[str, float]:
    # Investigations only happen when there are at least 7 players, so there are always at least 2 vanilla Fascists and Hitler never knows who's who.
    param = {}
    param["INV_L_F"] = context.fas_players / (context.num_players - 1)
    param["INV_L_H"] = 1 / (context.num_players - 1)
    param["INV_F_F"] = 0.1
    param["INV_F_H"] = 0.01
    return param


@cache
def _get_investigation_table() -> pd.DataFrame:
    target_table = pd.read_csv(INVESTIGATION_TARGET_FILE)
    accusation_table = pd.read_csv(INVESTIGATE_FILE)
    df = pd.merge(target_table, accusation_table, how="inner", on=["president", "target"])
    # Add parentheses around both columns in case the files are changed later
    df["probability_target"] = "(" + df["probability_target"].astype(str) + ")"
    df["probability_accuse"] = "(" + df["probability_accuse"].astype(str) + ")"
    df["prob_str"] = df["probability_target"].str.cat(df["probability_accuse"], sep="*")
    return df


def investigate(pres: Role, target: Role, accuse: bool, context: GameContext) -> float:
    inv_table = _get_investigation_table()
    matching_row = lambda x: x["president"] == str(pres) and x["target"] == str(target) and x["accuse"] == accuse
    inv_table = inv_table[inv_table.apply(matching_row, axis=1)]
    prob_str = inv_table.iloc[0]["prob_str"]
    param = _get_investigation_parameters(context)
    return utils.eval_probability(prob_str, param)
