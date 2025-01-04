import tkinter
from argparse import Namespace

FOREGROUND = "white"
BACKGROUND = "#4e9572"
BUTTON_COLOR = "#5eaa8d"


def set_window_position(root: tkinter.Tk, width: int, height: int) -> None:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = width
    window_height = height
    position_top = int(screen_height / 2 - window_height / 1.5)
    position_right = int(screen_width / 2 - window_width / 1.5)
    root.geometry(
        f"{window_width}x{window_height}+{position_right}+{position_top}"
    )


class GameOptionCheckbox:
    x = 30
    y = 50
    y_offset = 40
    font = ("Helvetica", 13, "bold")

    def __init__(
        self, root: tkinter.Tk, args: Namespace, background: str
    ) -> None:
        self.root = root
        self.args = args
        self.background = background

    def fetch_checkbox(
        self, pos: int, text: str, active: bool = False
    ) -> tkinter.BooleanVar:
        var = tkinter.BooleanVar()
        if active:
            var.set(True)
        checkbutton = tkinter.Checkbutton(
            self.root,
            text=text,
            variable=var,
            background=self.background,
            fg=FOREGROUND,
            font=GameOptionCheckbox.font,
            activebackground=BUTTON_COLOR,
            activeforeground=FOREGROUND,
            borderwidth=0,
            highlightthickness=0,
            selectcolor=BUTTON_COLOR,
        )
        checkbutton.place(
            x=GameOptionCheckbox.x,
            y=GameOptionCheckbox.y + pos * GameOptionCheckbox.y_offset,
        )
        return var

    def fetch_game_type(self, pos: int) -> tkinter.StringVar:
        var = tkinter.StringVar(value="h17")
        h17_radiobutton = self._get_radiobutton("Hit on soft 17", "h17", var)
        s17_radiobutton = self._get_radiobutton("Stand on soft 17", "s17", var)
        h17_radiobutton.place(
            x=GameOptionCheckbox.x,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        s17_radiobutton.place(
            x=GameOptionCheckbox.x + 180,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        return var

    def fetch_number_of_decs(self, pos: int) -> tkinter.IntVar:
        var = tkinter.IntVar(value=6)
        option_1 = self._get_radiobutton("2 decks", 2, var)
        option_2 = self._get_radiobutton("6 decks", 6, var)
        option_3 = self._get_radiobutton("8 decks", 8, var)
        option_1.place(
            x=GameOptionCheckbox.x,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        option_2.place(
            x=GameOptionCheckbox.x + 180,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        option_3.place(
            x=GameOptionCheckbox.x + 350,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        return var

    def fetch_surrender(self, pos: int) -> tkinter.StringVar:
        var = tkinter.StringVar(value="no")
        no_surrender = self._get_radiobutton("No surrender", "no", var)
        up_to_10 = self._get_radiobutton("Surrender against 2-10", "2-10", var)
        no_surrender.place(
            x=GameOptionCheckbox.x,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        up_to_10.place(
            x=GameOptionCheckbox.x + 180,
            y=GameOptionCheckbox.y + GameOptionCheckbox.y_offset * pos,
        )
        return var

    def _get_radiobutton(
        self,
        text: str,
        value: str | int,
        var: tkinter.StringVar | tkinter.IntVar,
    ) -> tkinter.Radiobutton:
        return tkinter.Radiobutton(
            self.root,
            text=text,
            variable=var,
            value=value,
            background=self.background,
            fg=FOREGROUND,
            font=GameOptionCheckbox.font,
            activebackground=BUTTON_COLOR,
            activeforeground=FOREGROUND,
            borderwidth=0,
            highlightthickness=0,
            selectcolor=BUTTON_COLOR,
        )
