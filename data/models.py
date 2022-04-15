from __future__ import annotations

from datetime import datetime
from enum import Enum


# ------------------------------------------------------------------------------
# Enums
# ------------------------------------------------------------------------------
class LegislativeOutcome(Enum):
    FAS = "Fas"
    HITLER = "Hitler"
    LIB = "Lib"
    REJECTED = "Rejected"
    VETO = "Veto"

    def __str__(self) -> str:
        return self.value


class Party(Enum):
    FAS = "Fas"
    LIB = "Lib"

    def __str__(self) -> str:
        return self.value


class PresidentActionType(Enum):
    ELECT = "Elect"
    INVESTIGATE = "Investigate"
    PEEK = "Peek"
    PROGRAM = "Program"
    SHOOT = "Shoot"

    def __str__(self) -> str:
        return self.value


class Role(Enum):
    FAS = "Fas"
    HIT = "Hit"
    LIB = "Lib"

    def __str__(self) -> str:
        return self.value


class WinReason(Enum):
    CONCEDE = "Concede"
    HITLER = "Hitler"
    POLICY = "Policy"
    POPULATION = "Population"

    def __str__(self) -> str:
        return self.value


# ------------------------------------------------------------------------------
# Classes
# ------------------------------------------------------------------------------
class Player:
    def __init__(self, game_id: int, name: str, role: Role):
        self.game_id = game_id
        self.name = name
        self.role = role


class LegislativeSession:
    def __init__(self, game_id: int, round_num: int, pres_name: str, chan_name: str, outcome: LegislativeOutcome, top_deck: Party | None, pres_get_claim: int | None, pres_give_claim: int | None, chan_get_claim: int | None, pres_get_actual: int | None, chan_get_actual: int | None, veto_attempt: bool, last_round: bool):
        self.game_id = game_id
        self.round_num = round_num
        self.pres_name = pres_name
        self.chan_name = chan_name
        self.outcome = outcome
        self.top_deck = top_deck
        self.pres_get_claim = pres_get_claim
        self.pres_give_claim = pres_give_claim
        self.chan_get_claim = chan_get_claim
        self.pres_get_actual = pres_get_actual
        self.chan_get_actual = chan_get_actual
        self.veto_attempt = veto_attempt
        self.last_round = last_round


class PresidentAction:
    def __init__(self, game_id: int, round_num: int, action: PresidentActionType, target_name: str | None, num_lib: int | None, accuse: bool | None):
        self.game_id = game_id
        self.round_num = round_num
        self.action = action
        self.target_name = target_name
        self.num_lib = num_lib
        self.accuse = accuse


class Game:
    def __init__(self, game_id: int, date: datetime, winning_team: Party, win_reason: WinReason):
        self.game_id = game_id
        self.date = date
        self.winning_team = winning_team
        self.win_reason = win_reason


# ------------------------------------------------------------------------------
# Validation
# ------------------------------------------------------------------------------
def is_valid(games: list[Game], players: list[Player], leg_sessions: list[LegislativeSession], pres_actions: list[PresidentAction]):
    # TODO: Implement validation
    return True
