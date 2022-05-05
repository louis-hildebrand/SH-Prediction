import math


class ProgressBar:
    # Progress bar
    TOT_BARS = 60
    FILL_SYMBOL = "#"
    EMPTY_SYMBOL = "-"

    def __init__(self, total: int):
        self.total = total
    
    def update(self, done: int) -> None:
        filled_bars = math.floor(ProgressBar.TOT_BARS*done/self.total)
        empty_bars = ProgressBar.TOT_BARS - filled_bars
        bar = f"[{ProgressBar.FILL_SYMBOL*filled_bars}{ProgressBar.EMPTY_SYMBOL*empty_bars}]"
        msg = f"{bar} {done}/{self.total} ({100*done/self.total:.0f}%)"
        print(msg, end="\r")
