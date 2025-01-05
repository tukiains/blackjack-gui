from dataclasses import dataclass
import tkinter
from PIL import Image, ImageTk
import os
from .lib import Card
from argparse import Namespace


IMG_PATH = f"{os.path.dirname(__file__)}/images/"

FOREGROUND = "white"


class TableComponents:
    def __init__(self, root: tkinter.Tk, background: str) -> None:
        self.root = root
        self.background = background
        self._x_slot = 250
        self._padding_left = 20

    def setup_canvas(self) -> None:
        rect = tkinter.Canvas(
            self.root,
            bg=self.background,
            height=100,
            width=80,
            bd=0,
            highlightthickness=0,
            relief="ridge",
        )
        rect.place(x=525, y=485)
        _round_polygon(
            rect,
            [5, 75, 75, 5],
            [5, 5, 90, 90],
            10,
            width=4,
            outline="#bbb500",
            fill=self.background,
        )

    def set_side_panel(self) -> None:
        panel = tkinter.Label(
            self.root,
            width=200,
            height=720,
            background="lightgrey",
            borderwidth=2,
            relief="groove",
        )
        panel.place(x=1000, y=0)

    def get_shoe_progress(self, n_decks: int) -> tkinter.Label:
        shoe_status_container = tkinter.Label(
            self.root, borderwidth=0, background="white"
        )
        height = n_decks * 20
        y = 200 - height
        shoe_status_container.place(x=20, y=y, height=height, width=30)
        shoe_progress = tkinter.Label(
            shoe_status_container, background="black", borderwidth=0, anchor="e"
        )
        shoe_label = tkinter.Label(
            self.root,
            text="Discard",
            font="12",
            borderwidth=0,
            background=self.background,
            fg=FOREGROUND,
        )
        shoe_label.place(x=5, y=210)
        return shoe_progress

    def get_label(self) -> tkinter.StringVar:
        label_text = tkinter.StringVar(self.root)
        label = tkinter.Label(
            self.root,
            textvariable=label_text,
            font="Helvetica 13 bold",
            borderwidth=0,
            background=self.background,
            fg=FOREGROUND,
        )
        label.place(x=430, y=670)
        return label_text

    def get_dealer_info(self) -> tkinter.Label:
        dealer_info = tkinter.Label(
            self.root,
            text="",
            font="helvetica 11 bold",
            borderwidth=0,
            background=self.background,
            fg=FOREGROUND,
        )
        dealer_info.place(x=305, y=180)
        return dealer_info

    def get_finger(self) -> dict[str, tkinter.Label]:
        finger = {
            str(slot): tkinter.Label(
                self.root, borderwidth=0, background=self.background
            )
            for slot in range(4)
        }
        for ind, f in enumerate(finger.values()):
            f.place(x=ind * self._x_slot + self._padding_left - 5, y=250)
        return finger

    def get_info(
        self,
    ) -> tuple[dict[str, tkinter.Label], dict[str, tkinter.StringVar]]:
        info_text = {
            str(slot): tkinter.StringVar(self.root) for slot in range(4)
        }
        info = {
            str(slot): tkinter.Label(
                self.root,
                textvariable=info_text[str(slot)],
                font="helvetica 11 bold",
                borderwidth=0,
                background=self.background,
                fg=FOREGROUND,
            )
            for slot in range(4)
        }
        for ind, i in enumerate(info.values()):
            i.place(x=ind * self._x_slot + self._padding_left + 110, y=465)
        return info, info_text

    def get_player_slots(self, n_cards_max: int) -> dict[str, tkinter.Label]:
        slot_player = {
            f"{str(slot)}{str(pos)}": tkinter.Label(
                self.root, borderwidth=0, background=self.background
            )
            for slot in range(4)
            for pos in range(n_cards_max)
        }
        for frame in range(4):
            for pos in range(n_cards_max):
                slot_player[f"{str(frame)}{str(pos)}"].place(
                    x=frame * self._x_slot + pos * 30 + self._padding_left,
                    y=350 - pos * 30,
                )
        return slot_player

    def get_dealer_slot(self) -> dict[str, tkinter.Label]:
        n_cards_max = 11
        card_back_img, _, _ = get_image()
        slot_dealer = {
            f"{str(pos)}": tkinter.Label(
                self.root, borderwidth=0, background=self.background
            )
            for pos in range(n_cards_max)
        }
        for pos in range(2):
            slot_dealer[str(pos)].configure(image=card_back_img)
            slot_dealer[str(pos)].image = card_back_img  # type: ignore
            slot_dealer[str(pos)].pack(side=tkinter.LEFT)
        for pos, slot in enumerate(slot_dealer.values()):
            slot.place(y=40, x=300 + pos * 105)
        return slot_dealer

    def get_chips(self) -> dict[str, tkinter.Label]:
        chips = {
            f"{str(slot)}{str(pos)}": tkinter.Label(
                self.root, borderwidth=0, background=self.background
            )
            for slot in range(4)
            for pos in range(5)
        }

        for a_slot in range(4):
            for pos in range(5):
                padx, pady = 0, 0
                if pos == 1:
                    padx = 50
                elif pos == 2:
                    padx = -50
                elif pos == 3:
                    padx = 100
                elif pos == 4:
                    padx = 25
                    pady = 35
                chips[f"{str(a_slot)}{str(pos)}"].place(
                    x=a_slot * self._x_slot + self._padding_left + padx + 20,
                    y=500 + pady,
                )
        return chips

    def get_insurance_chip(self) -> tkinter.Label:
        insurance_chip = tkinter.Label(
            self.root, borderwidth=0, background=self.background
        )
        insurance_chip.place(x=450, y=400)
        return insurance_chip

    def get_slider(self, x_sidepanel: int, bet: int) -> tkinter.Scale:
        bet_label = tkinter.Label(text="Bet:", background="lightgray")
        slider = tkinter.Scale(
            self.root,
            from_=1,
            to=100,
            orient=tkinter.HORIZONTAL,
            background="lightgray",
        )
        slider.set(bet)
        slider.place(x=x_sidepanel + 40, y=140)
        bet_label.place(x=x_sidepanel, y=160)
        return slider


@dataclass
class CheckConfig:
    location: tuple[int, int]
    txt_location: tuple[int, int]
    txt: str


class CheckButton:
    x = 1030
    y = 600
    y_offset = 25

    def __init__(
        self, root: tkinter.Tk, args: Namespace, background: str
    ) -> None:
        self.root = root
        self.args = args
        self.background = background

    def fetch_count(self) -> tuple[tkinter.StringVar, tkinter.IntVar]:
        txt_location = (10, 610)
        conf = CheckConfig(
            location=(CheckButton.x, CheckButton.y + CheckButton.y_offset),
            txt_location=txt_location,
            txt="Show count",
        )
        label, text = self._get_table_infotext(txt_location)
        checkbox = self._get_checkbutton(label, conf)
        self._show_count(label, checkbox, txt_location)
        return text, checkbox

    def fetch_accuracy(self) -> tuple[tkinter.StringVar, tkinter.IntVar]:
        txt_location = (10, 655)
        conf = CheckConfig(
            location=(CheckButton.x, CheckButton.y),
            txt_location=txt_location,
            txt="Coach mode",
        )
        label, text = self._get_table_infotext(txt_location)
        checkbox = self._get_checkbutton(label, conf)
        self._show_accuracy(label, checkbox, txt_location)
        return text, checkbox

    def _get_table_infotext(
        self, txt_location: tuple[int, int]
    ) -> tuple[tkinter.Label, tkinter.StringVar]:
        text_var = tkinter.StringVar(self.root)
        label = tkinter.Label(
            self.root,
            textvariable=text_var,
            font="Helvetica 10",
            borderwidth=0,
            background=self.background,
            fg=FOREGROUND,
            justify="left",
        )
        label.place(x=txt_location[0], y=txt_location[1])
        return label, text_var

    def _get_checkbutton(
        self, label: tkinter.Label, conf: CheckConfig
    ) -> tkinter.IntVar:
        def toggle():
            if var.get() == 1:
                label.place(x=conf.txt_location[0], y=conf.txt_location[1])
            else:
                label.place_forget()

        var = tkinter.IntVar()
        checkbutton = tkinter.Checkbutton(
            self.root,
            text=conf.txt,
            variable=var,
            background="lightgrey",
            command=toggle,
        )
        checkbutton.place(x=conf.location[0], y=conf.location[1])
        return var

    def _show_accuracy(
        self,
        label: tkinter.Label,
        var: tkinter.IntVar,
        txt_location: tuple[int, int],
    ) -> None:
        if self.args.subset is not None or self.args.cards is not None:
            var.set(1)
        if var.get() == 1:
            label.place(x=txt_location[0], y=txt_location[1])
        else:
            label.place_forget()

    def _show_count(
        self,
        label: tkinter.Label,
        var: tkinter.IntVar,
        txt_location: tuple[int, int],
    ) -> None:
        if self.args.subset is not None or self.args.cards is not None:
            var.set(1)
        if var.get() == 1:
            label.place(x=txt_location[0], y=txt_location[1])
        else:
            label.place_forget()


def get_image(
    card: Card | None = None,
    width: int = 100,
    height: int = 130,
    rotate: bool = False,
):
    if card is None:
        filename = f"{IMG_PATH}/back.png"
    else:
        mapping = {
            "A": "ace",
            "J": "jack",
            "Q": "queen",
            "K": "king",
        }
        prefix = mapping.get(card.label, card.value)
        filename = f"{IMG_PATH}/{prefix}_of_{card.suit}.png"
    image = Image.open(filename).resize(
        (width, height), Image.Resampling.LANCZOS
    )
    if rotate is True:
        image = image.resize((height, height))
        image = image.rotate(angle=90)
        image = image.resize((height, width))
        width, height = height, width
    return ImageTk.PhotoImage(image), width, height


def _round_polygon(canvas, x, y, sharpness, **kwargs):
    sharpness = max(sharpness, 2)
    ratio_multiplier = sharpness - 1
    ratio_divider = sharpness
    points = []
    for i, _ in enumerate(x):
        points.append(x[i])
        points.append(y[i])
        if i != (len(x) - 1):
            points.append((ratio_multiplier * x[i] + x[i + 1]) / ratio_divider)
            points.append((ratio_multiplier * y[i] + y[i + 1]) / ratio_divider)
            points.append((ratio_multiplier * x[i + 1] + x[i]) / ratio_divider)
            points.append((ratio_multiplier * y[i + 1] + y[i]) / ratio_divider)
        else:
            points.append((ratio_multiplier * x[i] + x[0]) / ratio_divider)
            points.append((ratio_multiplier * y[i] + y[0]) / ratio_divider)
            points.append((ratio_multiplier * x[0] + x[i]) / ratio_divider)
            points.append((ratio_multiplier * y[0] + y[i]) / ratio_divider)
            points.append(x[0])
            points.append(y[0])
    return canvas.create_polygon(points, **kwargs, smooth=tkinter.TRUE)
