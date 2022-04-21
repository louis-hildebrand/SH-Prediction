class GameContext:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.fas_passed = 0
        self.lib_passed = 0
        self.draw_pile_size = 17
        self.draw_pile_num_lib = {
            0: 0.0,
            1: 0.0,
            2: 0.0,
            3: 0.0,
            4: 0.0,
            5: 0.0,
            6: 1.0
        }
        self.election_tracker = 0
