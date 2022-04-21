from data.models import LegislativeOutcome, LegislativeSession, PresidentAction, PresidentActionType, Role
from functools import cache
from prediction.game_context import GameContext

import math
import pandas as pd


POLICY_PRES_FILE = "prediction/model/policy_pres.csv"
POLICY_CHAN_FILE = "prediction/model/policy_chan.csv"
CLAIM_PRES_FILE = "prediction/model/claim_pres.csv"
CLAIM_CHAN_FILE = "prediction/model/claim_chan.csv"
PEEK_FILE = "prediction/model/peek.csv"
INVESTIGATE_FILE = "prediction/model/investigate.csv"


def _eval_probability(probability: str, param: dict[str, float]) -> float:
    return eval(probability, {"__builtins__": None}, param)


def _eval_table(df: pd.DataFrame, param: dict[str, float]) -> pd.DataFrame:
    _eval = lambda row: _eval_probability(row["prob_str"], param)
    probabilities = df.apply(_eval, axis=1)
    df.insert(0, "probability", probabilities)
    return df


def _prob_pres_get_actual(n: int, num_lib: dict[int, float], tot_cards: int) -> float:
    prob = 0
    for (nlib, p) in num_lib.items():
        if nlib > tot_cards:
            break
        nfas = tot_cards - nlib
        prob += p * math.comb(nlib, n) * math.comb(nfas, 3 - n) / math.comb(tot_cards, 3)
    return prob


@cache
def _get_deck_model() -> pd.DataFrame:
    data = {
        "pres_get_actual" : [0, 1, 2, 3],
        "probability_pga" : ["PGA_0", "PGA_1", "PGA_2", "PGA_3"]
    }
    return pd.DataFrame(data)


def _get_deck_parameters(context: GameContext) -> dict[str, float]:
    param = {}
    param["PGA_0"] = _prob_pres_get_actual(0, context.draw_pile_num_lib, context.draw_pile_size)
    param["PGA_1"] = _prob_pres_get_actual(1, context.draw_pile_num_lib, context.draw_pile_size)
    param["PGA_2"] = _prob_pres_get_actual(2, context.draw_pile_num_lib, context.draw_pile_size)
    param["PGA_3"] = _prob_pres_get_actual(3, context.draw_pile_num_lib, context.draw_pile_size)
    return param


# ------------------------------------------------------------------------------
# Legislative session
# ------------------------------------------------------------------------------
def _get_leg_session_parameters(context: GameContext) -> dict[str, float]:
    hitler_knows_fas = context.num_players < 7
    ALMOST_IMPOSSIBLE = 1e-6
    EXTREMELY_UNLIKELY = 0.005
    VERY_UNLIKELY = 0.01
    UNLIKELY = 0.05
    # Deck
    param = _get_deck_parameters(context)
    # Policy: president
    param["PP_FF1_FORCE_FAS"] = 0.75
    param["PP_FF2_TEST"] = 0.9
    param["PP_FH1_FORCE_FAS"] = param["PP_FF1_FORCE_FAS"]
    param["PP_FH2_TEST"] = param["PP_FF2_TEST"]
    param["PP_FL1_FORCE_FAS"] = param["PP_FF1_FORCE_FAS"]
    param["PP_FL2_TEST"] = param["PP_FF2_TEST"]
    param["PP_HF1_FORCE_FAS"] = 0.4
    param["PP_HF2_TEST"] = param["PP_FF2_TEST"]
    param["PP_HL1_FORCE_FAS"] = param["PP_HF1_FORCE_FAS"]  # If you change this, keep in mind what Hitler knows
    param["PP_HL2_TEST"] = param["PP_HF2_TEST"]
    param["PP_LX1_FORCE_FAS"] = ALMOST_IMPOSSIBLE
    param["PP_LX2_TEST"] = 0.5 if context.fas_passed < 3 else UNLIKELY
    # Policy: chancellor
    param["PC_FF_FAS"] = param["PP_FF1_FORCE_FAS"] if context.lib_passed < 4 else (1 - ALMOST_IMPOSSIBLE)
    param["PC_HF_FAS"] = param["PC_FF_FAS"]
    param["PC_LF_FAS"] = 0.1 if context.lib_passed < 4 else (1 - ALMOST_IMPOSSIBLE)
    param["PC_LH_FAS"] = 0.01 if context.lib_passed < 4 else (1 - ALMOST_IMPOSSIBLE)
    if context.lib_passed < 4:
        param["PC_FH_FAS"] = param["PP_HL1_FORCE_FAS"] if hitler_knows_fas else param["PC_LH_FAS"]
    else:
        param["PC_FH_FAS"] = 1 - ALMOST_IMPOSSIBLE
    param["PC_XL_FAS"] = ALMOST_IMPOSSIBLE
    # Claim: president
    param["CP_FXF_SUICIDE"] = ALMOST_IMPOSSIBLE
    param["CP_FXX_BIG_UNDERREPORT"] = EXTREMELY_UNLIKELY
    param["CP_FXX_UNDERREPORT"] = VERY_UNLIKELY
    param["CP_FXX_OVERREPORT"] = VERY_UNLIKELY
    param["CP_FXX_BIG_OVERREPORT"] = EXTREMELY_UNLIKELY
    param["CP_FFF_ACCUSE"] = UNLIKELY
    param["CP_FFL_FORCE"] = VERY_UNLIKELY
    param["CP_FFL_TEST"] = VERY_UNLIKELY
    param["CP_FHF_ACCUSE"] = VERY_UNLIKELY
    param["CP_FHL_FORCE"] = VERY_UNLIKELY
    param["CP_FHL_TEST"] = VERY_UNLIKELY
    param["CP_FLF_FRAME"] = UNLIKELY
    param["CP_FLF_SNITCH"] = 1 - VERY_UNLIKELY
    param["CP_FLL_FORCE"] = VERY_UNLIKELY
    param["CP_FLL_TEST"] = VERY_UNLIKELY
    param["CP_HXF_SUICIDE"] = ALMOST_IMPOSSIBLE
    param["CP_HXX_BIG_UNDERREPORT"] = EXTREMELY_UNLIKELY
    param["CP_HXX_UNDERREPORT"] = VERY_UNLIKELY
    param["CP_HXX_OVERREPORT"] = VERY_UNLIKELY
    param["CP_HXX_BIG_OVERREPORT"] = EXTREMELY_UNLIKELY
    param["CP_HFF_ACCUSE"] = 0.1
    param["CP_HFL_FORCE"] = VERY_UNLIKELY
    param["CP_HFL_TEST"] = VERY_UNLIKELY
    param["CP_HLF_FRAME"] = VERY_UNLIKELY
    param["CP_HLF_SNITCH"] = 1 - UNLIKELY
    param["CP_HLL_FORCE"] = VERY_UNLIKELY
    param["CP_HLL_TEST"] = VERY_UNLIKELY
    param["CP_LXX_LIE"] = ALMOST_IMPOSSIBLE
    # Claim: chancellor
    param["CC_FX0F_SUICIDE"] = ALMOST_IMPOSSIBLE
    param["CC_FX1F_DENY"] = 1 - ALMOST_IMPOSSIBLE
    param["CC_F11L_OVERREPORT"] = ALMOST_IMPOSSIBLE
    param["CC_F21L_OVERREPORT"] = UNLIKELY
    param["CC_F12L_UNDERREPORT"] = UNLIKELY
    param["CC_F22L_UNDERREPORT"] = ALMOST_IMPOSSIBLE
    param["CC_HX0F_SUICIDE"] = ALMOST_IMPOSSIBLE
    param["CC_HX1F_DENY"] = 1 - ALMOST_IMPOSSIBLE
    param["CC_H11L_OVERREPORT"] = ALMOST_IMPOSSIBLE
    param["CC_H21L_OVERREPORT"] = UNLIKELY
    param["CC_H12L_UNDERREPORT"] = UNLIKELY
    param["CC_H22L_UNDERREPORT"] = ALMOST_IMPOSSIBLE
    param["CC_LXXX_LIE"] = ALMOST_IMPOSSIBLE
    return param


@cache
def _get_leg_session_table() -> pd.DataFrame:
    # Get tables
    deck_table = _get_deck_model()
    policy_pres = pd.read_csv(POLICY_PRES_FILE)
    policy_chan = pd.read_csv(POLICY_CHAN_FILE)
    claim_pres = pd.read_csv(CLAIM_PRES_FILE)
    claim_chan = pd.read_csv(CLAIM_CHAN_FILE)
    # Join tables
    df = pd.merge(deck_table, policy_pres,
        how="inner",
        on=["pres_get_actual"])
    df = pd.merge(df, policy_chan,
        how="inner",
        on=["president", "chancellor", "chan_get_actual"])
    df = pd.merge(df, claim_pres,
        how="inner",
        on=["president", "chancellor", "pres_get_actual","chan_get_actual", "outcome"])
    df = pd.merge(df, claim_chan,
        how="inner",
        on=["chancellor", "chan_get_actual", "pres_give_claim", "outcome"])
    # Get final probability expression (product of individual probabilities)
    # Add parentheses around each expression before multiplying
    df["probability_pga"] = "(" + df["probability_pga"] + ")"
    df["probability_pp"] = "(" + df["probability_pp"] + ")"
    df["probability_pc"] = "(" + df["probability_pc"] + ")"
    df["probability_cp"] = "(" + df["probability_cp"] + ")"
    df["probability_cc"] = "(" + df["probability_cc"] + ")"
    df["prob_str"] = df["probability_pp"].str.cat(df[["probability_pga", "probability_pc", "probability_cp", "probability_cc"]], sep="*")
    return df


def _prob_nlib_remaining(n: int, ls_table: pd.DataFrame, old_draw_pile: dict[int, float]) -> float:
    # The probability that there are n liberal policies remaining in the draw pile is
    #   P(n before, 0 used) + P(n + 1 before, 1 used) + P(n + 2 before, 2 used) + P(n + 3 before, 3 used)
    prob = 0
    for k in range(4):
        if n + k > 6:
            break
        prob_tot = sum(ls_table["probability"])
        prob_k_used = sum(ls_table.where(ls_table["pres_get_actual"] == k, 0)["probability"]) / prob_tot
        prob += old_draw_pile[n + k] * prob_k_used
    return prob


def prob_legislative_session(ls: LegislativeSession, role: dict[str, Role], context: GameContext) -> float:
    """
    Calculates the probability of the given legislative session given the specifed roles. Also updates the state of the draw pile.
    """
    pres_role = role[ls.pres_name]
    chan_role = role[ls.chan_name]
    # In Hitler Zone, if the chancellor was Hitler, the game would have been over
    if context.fas_passed >= 3 and chan_role == Role.HIT:
        return 0
    # Get the relevant rows from the probability model table
    def matching_row(row: pd.Series) -> bool:
        return (row.president == str(pres_role) and
            row.chancellor == str(chan_role) and
            row.outcome == str(ls.outcome) and
            row.pres_get_claim == ls.pres_get_claim and
            row.pres_give_claim == ls.pres_give_claim and
            row.chan_get_claim == ls.chan_get_claim)
    ls_table = _get_leg_session_table()
    ls_table = ls_table[ls_table.apply(matching_row, axis=1)]
    if len(ls_table) == 0:
        return 0
    # Calculate the probabilities for this round
    param = _get_leg_session_parameters(context)
    ls_table = _eval_table(ls_table, param)
    prob = sum(ls_table["probability"])
    # Update the probabilities for the deck
    old_draw_pile = context.draw_pile_num_lib.copy()
    for n in range(7):
        context.draw_pile_num_lib[n] = _prob_nlib_remaining(n, ls_table, old_draw_pile)
    return prob


# ------------------------------------------------------------------------------
# Any president action
# ------------------------------------------------------------------------------
def prob_president_action(action: PresidentAction, pres_name: str, role: dict[str, Role], context: GameContext) -> float:
    if action.action == PresidentActionType.PEEK:
        pres_role = role[pres_name]
        return _prob_peek(pres_role, action.num_lib, context)
    elif action.action == PresidentActionType.INVESTIGATE:
        pres_role = role[pres_name]
        target_role = role[action.target_name]
        return _prob_investigate(pres_role, target_role, action.accuse)
    elif action.action == PresidentActionType.SHOOT and role[action.target_name] == Role.HIT:
        # If the target was Hitler, the game would have been over
        return 0
    else:
        # TODO: Implement models for selecting the next president and shooting
        return 1


# ------------------------------------------------------------------------------
# Peek
# ------------------------------------------------------------------------------
@cache
def _get_peek_table() -> pd.DataFrame:
    peek_table = pd.read_csv(PEEK_FILE)
    deck_table = _get_deck_model()
    df = pd.merge(peek_table, deck_table, how="inner", on="pres_get_actual")
    # Multiply probabilities
    # Add parentheses around each column just in case the file is changed later
    df["probability_pk"] = "(" + df["probability_pk"].astype(str) + ")"
    df["probability_pga"] = "(" + df["probability_pga"] + ")"
    df["prob_str"] = df["probability_pk"].str.cat(df["probability_pga"], sep="*")
    return df


def _prob_peek(pres: Role, num_lib: int, context: GameContext) -> float:
    # Load the model and find the relevant rows
    peek_table = _get_peek_table()
    matching_row = lambda x: x["president"] == str(pres) and x["pres_get_claim"] == num_lib
    peek_table = peek_table[peek_table.apply(matching_row, axis=1)]
    # Calculate the probabilities for this round
    param = _get_deck_parameters(context)
    peek_table = _eval_table(peek_table, param)
    return sum(peek_table["probability"])


# ------------------------------------------------------------------------------
# Investigate
# ------------------------------------------------------------------------------
@cache
def _get_investigation_table() -> pd.DataFrame:
    return pd.read_csv(INVESTIGATE_FILE)


def _prob_investigate(pres: Role, target: Role, accuse: bool) -> float:
    inv_table = _get_investigation_table()
    matching_row = lambda x: x["president"] == str(pres) and x["target"] == str(target) and x["accuse"] == accuse
    inv_table = inv_table[inv_table.apply(matching_row, axis=1)]
    return inv_table.iloc[0]["probability"]


# ------------------------------------------------------------------------------
# Elect
# ------------------------------------------------------------------------------
# TODO


# ------------------------------------------------------------------------------
# Shoot
# ------------------------------------------------------------------------------
# TODO
