from data.models import PresidentAction, PresidentActionType, Role
from prediction.game_context import GameContext
from prediction.peek import peek
from prediction.investigate import investigate


def president_action(action: PresidentAction, pres_name: str, role: dict[str, Role], context: GameContext) -> float:
    if action.action == PresidentActionType.PEEK:
        pres_role = role[pres_name]
        return peek(pres_role, action.peek_claim, context)
    elif action.action == PresidentActionType.INVESTIGATE:
        pres_role = role[pres_name]
        target_role = role[action.target_name]
        return investigate(pres_role, target_role, action.accuse, context)
    elif action.action == PresidentActionType.SHOOT and role[action.target_name] == Role.HIT:
        # If the target was Hitler, the game would have been over
        return 0
    else:
        # TODO: Implement models for selecting the next president and shooting
        return 1
