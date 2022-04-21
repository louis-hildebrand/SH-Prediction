class GameContext:
    TOTAL_POLICIES = 17

    def __init__(self, num_players: int):
        self.num_players = num_players
        self.fas_passed = 0
        self.lib_passed = 0
        self.draw_pile_size = GameContext.TOTAL_POLICIES
        self.draw_pile_num_lib = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 1.0
        }
    
    def reshuffle_deck(self) -> None:
        self.draw_pile_size = GameContext.TOTAL_POLICIES - self.fas_passed - self.lib_passed
        self.draw_pile_num_lib = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 0.0
        }
        self.draw_pile_num_lib[6 - self.lib_passed] = 1.0
