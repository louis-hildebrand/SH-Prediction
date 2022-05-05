from data.models import Role
from utils.utils import num_players_with_role


class GameContext:
    TOTAL_POLICIES = 17

    def __init__(self, num_players: int):
        self.num_players = num_players
        self.fas_players = num_players_with_role(Role.FAS, num_players)
        self.lib_players = num_players_with_role(Role.LIB, num_players)
        self.fas_passed = 0
        self.lib_passed = 0
        self.draw_pile_size = GameContext.TOTAL_POLICIES
        # draw_pile[n] is the probability that there are n liberal policies in the draw pile
        self.draw_pile = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 1.0
        }
    
    def hitler_knows_fas(self) -> bool:
        return self.num_players < 7
    
    def reshuffle_deck(self) -> None:
        self.draw_pile_size = GameContext.TOTAL_POLICIES - self.fas_passed - self.lib_passed
        self.draw_pile = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 0.0
        }
        self.draw_pile[6 - self.lib_passed] = 1.0
