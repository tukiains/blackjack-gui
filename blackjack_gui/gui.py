from argparse import Namespace
import os
import tkinter
from typing import Any, Literal, cast
from .lib import Count


from PIL import Image, ImageTk

from .lib import (
    Card,
    Dealer,
    Hand,
    Player,
    Shoe,
    Rules,
    get_correct_play,
    get_starting_hand,
)

from .table_components import TableComponents, get_image, CheckButton
from .settings import GameOptionCheckbox, set_window_position

TIME_DELAY = 800
N_CARDS_MAX = 11
IMG_PATH = f"{os.path.dirname(__file__)}/images/"


class Game:
    def __init__(
        self,
        player: Player,
        dealer: Dealer,
        args: Any,
        menu: dict,
        components: TableComponents,
        check_button: CheckButton,
    ):
        self.player = player
        self.dealer = dealer
        self.root = components.root
        self.menu = menu
        self.components = components
        self.check_button = check_button
        self.cards: list[str] | None = args.cards
        self.dealer_cards: list[str] | None = args.dealer_cards
        self.subset: str | None = args.subset
        self.bet: int = args.bet
        self.rules: Rules = args.rules
        self.shoe = Shoe(self.rules.number_of_decks)
        self.active_slot = None
        self.initial_bet: int = args.bet
        self._running_count_from_user: int = args.running_count
        self._n_correct_play = 0
        self._n_mistakes = 0
        self._n_rounds = 0
        self.count: Count

    def start_new_round(self):
        """Starts new round."""
        self._hide_buttons()
        self._n_rounds += 1
        self._update_accuracy()
        self.bet = int(self.components.slider.get())
        self.components.slider.configure(state=tkinter.DISABLED)
        self._hide_all_chips()
        self._hide_insurance_chip()
        self._hide_fingers()
        self._clean_player_slots()
        self._dealer_info()
        self.player.hands = []
        shuffle_limit = 52  # How many cards left in the shoe before shuffle
        is_end_of_shoe = self.shoe.n_cards < shuffle_limit
        is_user_given_cards = (
            self.cards is not None
            or self.subset is not None
            or self.dealer_cards is not None
        )
        if self.rules.csm or is_end_of_shoe or is_user_given_cards:
            self.shoe = Shoe(self.rules.number_of_decks)
            self.player.init_count()
        # Set running count if given as arguments (for testing and practice purposes)
        if self._running_count_from_user != 0 and self._n_rounds == 1:
            self.player.count.running_count = self._running_count_from_user
        self._shuffle_shoe() if is_end_of_shoe else self._finish_round()

    def surrender(self):
        """Surrender button."""
        if self._check_play(self.player.hands[0], "surrender") is False:
            return
        self._hide_buttons()
        self.player.stack += self.bet / 2
        self._display_stack()
        hand = self._get_hand_in_active_slot()
        self.root.after(TIME_DELAY, self._reveal_dealer_hidden_card, True)
        self._hide(hand)
        self._hide_chips(hand)
        self._display_info(hand, "SURRENDER")

    def even_money(self):
        """Even Money button"""
        hand = self._get_hand_in_active_slot()
        if (
            self.check_button.fix_mistakes.get() == 1
            and self._check_insurance(hand) is False
        ):
            return
        self.dealer.even_money = True
        self._hide_buttons()
        self._hide(hand)
        self._payout()

    def double(self):
        """Double button."""
        hand = self._get_hand_in_active_slot()
        if self._check_play(hand, "double") is False:
            return
        if self._check_dealer_peek():
            return
        self._hide_buttons(("surrender",))
        self.player.stack -= self.bet
        self._display_stack()
        hand.bet += self.bet
        hand.deal(self.shoe)
        self._display_chip(hand, 1)
        hand.is_finished = True
        self._display_player_cards(hand, rotate_last=True)
        if hand.is_triple_seven:
            self._hide_buttons()
            self.root.after(TIME_DELAY, self._end_round)
            return
        self._handle_counts(hand, self.shoe)
        if hand.sum > 21:
            self._hide(hand)
            self._hide_chips(hand)
        self._clean_info()
        self._resolve_next_hand()

    def reset(self):
        """Reset button."""
        self._clean_info()
        self.player.buy_in(self.player.initial_stack)
        self.shoe = Shoe(self.rules.number_of_decks)
        self._clean_dealer_slots()
        self.components.slider.set(self.initial_bet)
        self.player.init_count()
        self._reset_accuracy()
        self.start_new_round()

    def deal(self):
        """Deal button."""
        self._clean_info()
        self._clean_dealer_slots()
        self.start_new_round()

    def hit(self):
        """Hit button."""
        self._hide_buttons(("insurance",))
        hand = self._get_hand_in_active_slot()
        if self._check_play(hand, "hit") is False:
            return
        if self._check_dealer_peek():
            return
        self._hide_buttons(("surrender", "double"))
        hand.deal(self.shoe)
        self._display_player_cards(hand)
        if hand.is_triple_seven:
            self._hide_buttons()
            self.root.after(TIME_DELAY, self._end_round)
            return
        self._handle_counts(hand, self.shoe)
        if hand.is_over is True:
            self._hide(hand)
            self._hide_chips(hand)
            self._display_info(hand, "BUST")
        if hand.is_finished is False:
            self._enable_correct_buttons(hand)
        else:
            self._resolve_next_hand()

    def stay(self):
        """Stay button."""
        hand = self._get_hand_in_active_slot()
        if self._check_play(hand, "stay") is False:
            return
        hand.is_finished = True
        self._resolve_next_hand()

    def insurance(self):
        """Insurance button."""
        hand = self._get_hand_in_active_slot()
        if (
            self.check_button.fix_mistakes.get() == 1
            and self._check_insurance(hand) is False
        ):
            return
        self.dealer.insurance_bet = hand.bet / 2
        self._display_insurance_chip()
        self.player.stack -= self.dealer.insurance_bet
        self._display_stack()
        self._hide_buttons(("insurance",))
        self._check_dealer_peek()

    def split(self):
        """Split button."""
        hand = self._get_hand_in_active_slot()
        if self._check_play(hand, "split") is False:
            return
        if self._check_dealer_peek():
            return

        self._hide_buttons(("surrender", "insurance"))
        new_hand = self.player.start_new_hand(self.bet)
        split_card = hand.cards.pop()
        new_hand.deal(split_card)
        self._display_chip(new_hand, 0)
        self._display_stack()

        for split_hand in (hand, new_hand):
            split_hand.is_split_hand = True
            split_hand.deal(self.shoe)
            if split_hand.cards[0].label == "A":
                # Split Aces receive only one card more
                split_hand.is_hittable = False
                if split_hand.cards[1].label != "A":
                    split_hand.is_finished = True
                if (
                    split_hand.cards[1].label == "A"
                    and not self.rules.resplit_aces
                ):
                    split_hand.is_finished = True

        self.player.sort_hands()

        if len(self.player.hands) < 4:
            self.player.hands.sort(
                key=lambda x: not x.cards[0].value == x.cards[1].value
            )

        for hand in self.player.hands:
            two_aces = hand.cards[0].label == "A" and hand.cards[1].label == "A"
            if two_aces and len(self.player.hands) == 4:
                hand.is_finished = True
            rotate = hand.cards[0].label == "A" and hand.cards[1].label != "A"
            if two_aces and not self.rules.resplit_aces:
                rotate = True
            self._display_player_cards(hand, rotate_last=rotate)
            self._handle_counts(hand, self.shoe)

        self._resolve_next_hand()

    def _shuffle_shoe(self):
        self.shoe.fill_discard_tray(self.components.shoe_progress)
        self.bet = self.initial_bet
        self.components.slider.configure(state=tkinter.NORMAL)
        self.components.slider.set(self.bet)
        self.components.slider.configure(state=tkinter.DISABLED)
        self.components.shuffle.place(relx=0.45, rely=0.5, anchor="center")
        self.root.update_idletasks()
        self.root.after(TIME_DELAY * 2, self._hide_shuffle)

    def _hide_shuffle(self):
        self.components.shuffle.place_forget()
        self._finish_round()

    def _finish_round(self):
        self.shoe.fill_discard_tray(self.components.shoe_progress)
        hand = self.player.start_new_hand(self.bet)
        self.dealer.init_hand()
        if self.dealer_cards:
            self.shoe.arrange(self.dealer_cards)
        self.dealer.deal(self.shoe)
        self.dealer.deal(self.shoe)
        self.dealer.cards[1].visible = False
        self._display_dealer_cards()
        self._handle_counts(self.dealer.cards, self.shoe)
        if self.cards:
            self.shoe.arrange(self.cards, randomize=True)
        elif self.subset is not None:
            cards = get_starting_hand(self.subset)
            self.shoe.arrange(cards)
        hand.deal(self.shoe)
        hand.deal(self.shoe)
        self._handle_counts(hand, self.shoe)
        self._show()
        self.active_slot = hand.slot
        self._display_stack()
        self._display_chip(hand, 0)
        self._display_player_cards(hand)
        if self.dealer.has_ace:
            self._enable_correct_buttons(hand)
            if hand.is_blackjack is True:
                self._hide_buttons(("hit", "double"))
                self._show_buttons(("even-money",))
            else:
                self._show_buttons(("insurance",))
        else:
            if hand.is_blackjack:
                self.root.after(TIME_DELAY, self._end_round)
                return
            self._enable_correct_buttons(hand)
            if self.rules.surrender != "no":
                self._show_buttons(("surrender",))

    def _resolve_next_hand(self):
        hand = self._get_first_unfinished_hand()
        if hand is not None:
            self.active_slot = hand.slot
            self._enable_correct_buttons(hand)
            self._display_finger(hand)
        else:
            self._clean_info()
            self._hide_buttons()
            self._hide_fingers()
            if not self._is_all_over() or self.dealer.insurance_bet > 0:
                self.root.after(TIME_DELAY, self._reveal_dealer_hidden_card)
            else:
                self._handle_counts(self.dealer.cards, self.shoe)
                self._payout()

    def _reveal_dealer_hidden_card(self, surrender: bool = False):
        self._display_dealer_cards(hide_second=False)
        self.dealer.cards[1].visible = True
        self._handle_counts(self.dealer.cards, self.shoe)
        if surrender:
            self._show_buttons(("deal",))
            self.components.slider.configure(state=tkinter.NORMAL)
        else:
            self._check_dealer_blackjack()

    def _check_dealer_blackjack(self):
        if self.dealer.is_blackjack and self.dealer.insurance_bet > 0:
            self._display_insurance_chip(triple=True)
        else:
            self._hide_insurance_chip()

        if self.player.hands[0].is_blackjack:
            self.dealer.is_finished = True

        if not self.dealer.is_finished:
            self.root.after(TIME_DELAY, self._dealer_draw_one_card)
        else:
            self._handle_counts(self.dealer.cards, self.shoe)
            self._payout()

    def _dealer_draw_one_card(self):
        self.dealer.deal(self.shoe)
        self._display_dealer_cards()
        self._handle_counts(self.dealer.cards, self.shoe)
        if not self.dealer.is_finished:
            self.root.after(TIME_DELAY, self._dealer_draw_one_card)
        else:
            self._handle_counts(self.dealer.cards, self.shoe)
            self._payout()

    def _payout(self):
        """Handles payout of all hands."""
        self._hide_fingers()
        for hand in self.player.hands:
            if (
                self.dealer.insurance_bet > 0
                and self.dealer.is_blackjack
                and hand.slot == 2
            ):
                self.player.stack += self.dealer.insurance_bet * 3
                self._display_insurance_chip(triple=True)
                if hand.is_triple_seven:
                    self.player.stack += hand.bet * 3
                    result = "TRIPLE SEVEN + INSURANCE"
                    if hand.bet == 2 * self.bet:
                        self.bet = hand.bet
                    self._display_chips(hand, triple=True)
                else:
                    self._hide_all_chips()
                    result = "INSURANCE"
            elif self.dealer.even_money is True:
                self.player.stack += hand.bet * 2
                result = "EVEN MONEY"
                self._display_chips(hand)
            elif hand.is_triple_seven is True:
                self.player.stack += hand.bet * 3
                result = "TRIPLE SEVEN"
                if hand.bet == 2 * self.bet:
                    self.bet = hand.bet
                self._display_chips(hand, triple=True)
            elif (
                hand.is_blackjack is True and self.dealer.is_blackjack is False
            ):
                self.player.stack += hand.bet * 2.5
                result = "BLACKJACK"
                self._display_chips(hand, bj=True)
            elif hand.is_blackjack is True and self.dealer.is_blackjack is True:
                self.player.stack += hand.bet
                result = "PUSH"
            elif (
                self.dealer.is_blackjack is True
                and hand.is_blackjack is False
                and hand.is_over is False
            ):
                self._dealer_info("BLACKJACK")
                result = "LOSE"
                self._resolve_lost_hand(hand)
            elif hand.is_over is False and self.dealer.is_over is True:
                self._dealer_info("BUST")
                self.player.stack += hand.bet * 2
                result = ""
                self._display_chips(hand)
            elif hand.is_over is True:
                result = "BUST"
                self._resolve_lost_hand(hand)
            elif hand.sum < self.dealer.sum:
                result = f"LOSE ({hand.sum} vs {self.dealer.sum})"
                self._resolve_lost_hand(hand)
            elif hand.surrender is True:
                self.player.stack += hand.bet / 2
                result = ""
            elif hand.sum > self.dealer.sum:
                self.player.stack += hand.bet * 2
                result = f"WIN ({hand.sum} vs {self.dealer.sum})"
                self._display_chips(hand)
            elif hand.sum == self.dealer.sum:
                self.player.stack += hand.bet
                result = "PUSH"
            else:
                raise ValueError
            self._display_info(hand, result)
            self._handle_counts(hand, self.shoe)
        # show both dealer cards even if player busts
        if (
            len(self.dealer.cards) == 2
            and self.dealer.cards[1].visible is False
        ):
            self.dealer.is_finished = True
            self.root.after(TIME_DELAY, self._reveal_dealer_hidden_card, True)
        else:
            self._show_buttons(("deal",))
            self._handle_counts(self.dealer.cards, self.shoe)
            self.components.slider.configure(state=tkinter.NORMAL)

    def _handle_counts(self, hand: Hand | list[Card], shoe: Shoe):
        self.player.update_counts(hand, shoe)
        true_count = int(self.player.count.true_count)
        self.check_button.count_text.set(
            f"Running count: {self.player.count.running_count}\nTrue count: {true_count}"
        )

    def _resolve_lost_hand(self, hand: Hand):
        self._hide_chips(hand)
        self._hide(hand)
        hand.bet = 0

    def _check_dealer_peek(self) -> bool:
        if self.rules.peek and self.dealer.is_blackjack:
            self._hide_buttons()
            self.root.after(TIME_DELAY, self._reveal_dealer_hidden_card)
            return True
        return False

    def _end_round(self):
        self._display_dealer_cards(hide_second=False)
        self.dealer.cards[1].visible = True
        self._payout()

    def _enable_correct_buttons(self, hand: Hand):
        n_hands = len(self.player.hands)
        if (
            len(hand.cards) == 2
            and hand.is_hittable is True
            and not (hand.is_split_hand and not self.rules.double_after_split)
        ):
            self._show_buttons(("double",))
        else:
            self._hide_buttons(("double",))
        if (
            hand.cards[0].value == hand.cards[1].value
            and len(hand.cards) == 2
            and n_hands < 4
        ):
            self._show_buttons(("split",))
        else:
            self._hide_buttons(("split",))
        if hand.is_hittable is True:
            self._show_buttons(("hit", "stay"))
        else:
            self._hide_buttons(("hit", "stay"))
        if hand.is_split_hand and hand.cards[0].label == "A":
            self._show_buttons(("stay",))
        if (
            hand.is_split_hand
            and hand.cards[0].label == "A"
            and hand.cards[1].label == "A"
            and not self.rules.resplit_aces
        ):
            self._hide_buttons(("split",))

    def _check_play(self, hand: Hand, play: str) -> bool:
        """Verifies player decision. Ignores deviations."""
        if self.check_button.fix_mistakes.get() == 0:
            return True
        correct_play = get_correct_play(
            hand,
            self.dealer.cards[0],
            len(self.player.hands),
            self.rules,
            self.player.count,
            self.check_button.deviations.get() == 1,
        )
        if correct_play != play:
            self._display_info(hand, "Try again!")
            self.root.after(1000, self._clean_info)
            self._n_mistakes += 1
            return False
        self._n_correct_play += 1
        if self.check_button.fix_mistakes.get() == 1:
            self._update_accuracy()
        return True

    def _update_accuracy(self):
        n_decisions = self._n_correct_play + self._n_mistakes
        if n_decisions != 0:
            txt = f"Accuracy: {round(self._n_correct_play / (self._n_correct_play + self._n_mistakes) * 100, 2)}%"
        else:
            txt = "Accuracy: 0%"
        txt += f"\nRounds: {self._n_rounds}"
        self.check_button.accuracy_text.set(txt)

    def _check_insurance(self, hand: Hand) -> bool:
        if self.player.count.true_count < 3:
            self._display_info(hand, "Try again!")
            self.root.after(1000, self._clean_info)
            return False
        return True

    def _display_stack(self):
        unit = "$" if self.rules.region == "US" else "€"
        self.components.label_text.set(f"Stack: {self.player.stack} {unit}")

    def _display_chips(self, hand, bj: bool = False, triple: bool = False):
        if bj is True:
            self._display_chip(hand, 1)
            self._display_chip(hand, 4, color="blue")
        elif triple is True:
            self._display_chip(hand, 0)
            self._display_chip(hand, 1)
            self._display_chip(hand, 2)
        elif hand.bet == self.bet:
            self._display_chip(hand, 1)
        elif hand.bet == (2 * self.bet):
            self._display_chip(hand, 2)
            self._display_chip(hand, 3)

    def _is_all_over(self) -> bool:
        for hand in self.player.hands:
            if hand.is_over is False and hand.surrender is False:
                return False
        return True

    def _get_first_unfinished_hand(self) -> Hand | None:
        for hand in self.player.hands:
            if hand.is_finished is False:
                return hand
        return None

    def _get_hand_in_active_slot(self) -> Hand:
        for hand in self.player.hands:
            if hand.slot == self.active_slot:
                return hand
        raise RuntimeError

    def _show(self):
        for slot in range(4):
            for n in range(N_CARDS_MAX):
                self.components.slot_player[f"{str(slot)}{str(n)}"].configure(
                    state=tkinter.NORMAL
                )

    def _hide(self, hand: Hand):
        for n in range(N_CARDS_MAX):
            self.components.slot_player[f"{str(hand.slot)}{str(n)}"].configure(
                state=tkinter.DISABLED
            )

    def _hide_buttons(self, buttons: tuple | None = None):
        if buttons is None:
            for key, button in self.menu.items():
                if key != "reset":
                    button.configure(state=tkinter.DISABLED)
        else:
            for button in buttons:
                if button in self.menu.keys():
                    self.menu[button].configure(state=tkinter.DISABLED)

    def _show_buttons(self, buttons: tuple | None = None):
        if buttons is None:
            for key, button in self.menu.items():
                if key not in ("insurance", "even-money"):
                    button.configure(state=tkinter.NORMAL)
        else:
            for button in buttons:
                if button in self.menu.keys():
                    self.menu[button].configure(state=tkinter.NORMAL)

    def _clean_player_slots(self):
        for slot in range(4):
            for n in range(N_CARDS_MAX):
                self.components.slot_player[f"{str(slot)}{str(n)}"].configure(
                    image="", width=0, height=0
                )

    def _clean_dealer_slots(self):
        for pos in self.components.slot_dealer.values():
            pos.configure(image="", width=0)

    def _clean_info(self):
        for slot in range(4):
            self.components.info_text[str(slot)].set("")

    def _display_dealer_cards(self, hide_second: bool = True):
        for ind, card in enumerate(self.dealer.cards):
            if ind == 1 and hide_second is True and len(self.dealer.cards) == 2:
                img, width, _ = get_image()
            else:
                img, width, _ = get_image(card)
            self.components.slot_dealer[str(ind)].configure(
                image=img, width=width
            )
            self.components.slot_dealer[str(ind)].image = img  # type: ignore

    def _display_player_cards(self, hand: Hand, rotate_last: bool = False):
        for ind, card in enumerate(hand.cards):
            rotate = ind == len(hand.cards) - 1 and rotate_last is True
            img, width, height = get_image(card, rotate=rotate)
            self.components.slot_player[
                f"{str(hand.slot)}{str(ind)}"
            ].configure(image=img, width=width, height=height)
            self.components.slot_player[
                f"{str(hand.slot)}{str(ind)}"
            ].image = img  # type: ignore

    def _display_insurance_chip(self, triple: bool = False):
        bet = (
            self.dealer.insurance_bet
            if triple is False
            else self.dealer.insurance_bet * 3
        )
        color = "red"
        if bet == 0.5:
            color = "blue"
            text = "0.5"
        elif bet % 1 == 0:
            text = str(round(bet))
        else:
            text = str(bet)
        img = _get_chip_image(color)
        self.components.insurance_chip.configure(
            image=img,
            compound="center",
            fg="white",
            text=text,
            font="helvetica 10 bold",
        )
        self.components.insurance_chip.image = img  # type: ignore

    def _hide_insurance_chip(self):
        self.components.insurance_chip.configure(image="", text="")

    def _display_chip(self, hand: Hand, pos: int, color: str = "red"):
        img = _get_chip_image(color)
        if color == "red":
            text = str(self.bet)
        else:
            text = "0.5" if self.bet == 1 else str(self.bet / 2)
        self.components.chips[f"{str(hand.slot)}{str(pos)}"].configure(
            image=img,
            compound="center",
            fg="white",
            text=text,
            font="helvetica 10 bold",
        )
        self.components.chips[f"{str(hand.slot)}{str(pos)}"].image = img  # type: ignore

    def _display_finger(self, hand: Hand):
        self._hide_fingers()
        img = _get_finger_image()
        self.components.finger[f"{str(hand.slot)}"].configure(image=img)
        self.components.finger[f"{str(hand.slot)}"].image = img  # type: ignore

    def _dealer_info(self, text: str = ""):
        self.components.dealer_info.configure(text=text)

    def _hide_chips(self, hand: Hand):
        for pos in range(4):
            self.components.chips[f"{str(hand.slot)}{str(pos)}"].configure(
                image="", text=""
            )

    def _hide_all_chips(self):
        for chip in self.components.chips.values():
            chip.configure(image="", text="")

    def _hide_fingers(self):
        for finger in self.components.finger.values():
            finger.configure(image="")

    def _display_info(self, hand: Hand, info: str):
        self.components.info_text[str(hand.slot)].set(info)

    def _reset_accuracy(self):
        self._n_correct_play = 0
        self._n_mistakes = 0
        self._n_rounds = 0
        self.check_button.accuracy_text.set("")


def _get_chip_image(color: str = "red") -> ImageTk.PhotoImage:
    size = 50
    filename = f"{IMG_PATH}/{color}-chip.png"
    image = Image.open(filename).resize(
        (size, size - 15), Image.Resampling.LANCZOS
    )
    return ImageTk.PhotoImage(image)


def _get_finger_image() -> ImageTk.PhotoImage:
    filename = f"{IMG_PATH}/finger2.png"
    image = Image.open(filename).resize((40, 60), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)


def settings(args: Namespace):
    def close_settings():
        args.rules = Rules(
            game_type=cast(Literal["h17", "s17"], game_type.get()),
            surrender=cast(Literal["no", "2-10"], surrender.get()),
            double_after_split=das.get(),
            resplit_aces=rsa.get(),
            csm=csm.get(),
            triple_seven=triple_seven.get(),
            peek=peek.get(),
            number_of_decks=n_decks.get(),
            region=args.rules.region,
        )
        root.destroy()
        main(args)

    def set_rules(region: str):
        if region == "Helsinki":
            game_type.set("s17")
            surrender.set("2-10")
            das.set(True)
            rsa.set(True)
            csm.set(True)
            triple_seven.set(True)
            peek.set(False)
            n_decks.set(6)
            args.rules.region = "Helsinki"

        elif region == "US":
            game_type.set("h17")
            surrender.set("no")
            das.set(True)
            rsa.set(True)
            csm.set(False)
            triple_seven.set(False)
            peek.set(True)
            n_decks.set(6)
            args.rules.region = "US"

    root = tkinter.Tk()
    root.title("Select rules for the game")
    background = "#4e9572"
    root.configure(background=background)
    set_window_position(root, 780, 450)

    check_button = GameOptionCheckbox(root, args, background)
    game_type = check_button.fetch_game_type(0)
    n_decks = check_button.fetch_number_of_decs(1)
    surrender = check_button.fetch_surrender(2)
    peek = check_button.fetch_checkbox(3, "Dealer peek", active=True)
    das = check_button.fetch_checkbox(4, "Double after split", active=True)
    rsa = check_button.fetch_checkbox(5, "Resplit aces", active=True)
    csm = check_button.fetch_checkbox(6, "Continuous shuffling")
    triple_seven = check_button.fetch_checkbox(7, "7-7-7 pays 3:1")
    start_button = tkinter.Button(
        root,
        text="Start game",
        width=12,
        font="15",
        command=lambda: close_settings(),
    )
    start_button.place(x=320, y=400)

    link1 = tkinter.Label(
        root,
        text="Casino Helsinki rules",
        fg="white",
        cursor="hand2",
        background=background,
        font="helvetica 10",
    )
    link1.place(x=40, y=420)
    link1.bind(
        "<Button-1>",
        lambda _: set_rules("Helsinki"),
    )
    link2 = tkinter.Label(
        root,
        text="Typical rules in the US",
        fg="white",
        cursor="hand2",
        background=background,
        font="helvetica 10",
    )
    link2.place(x=40, y=395)
    link2.bind(
        "<Button-1>",
        lambda _: set_rules("US"),
    )
    link2.bind(
        "<Enter>",
        lambda _: link2.config(font="helvetica 10 underline"),
    )
    link2.bind(
        "<Leave>",
        lambda _: link2.config(font="helvetica 10"),
    )
    link1.bind(
        "<Enter>",
        lambda _: link1.config(font="helvetica 10 underline"),
    )
    link1.bind(
        "<Leave>",
        lambda _: link1.config(font="helvetica 10"),
    )

    tkinter.mainloop()


def main(args: Namespace):
    root = tkinter.Tk()
    set_window_position(root, 1200, 700)
    description = "H17" if args.rules.game_type == "h17" else "S17"
    description += f", {args.rules.number_of_decks} decks"
    if args.rules.peek:
        description += ", Dealer peek"
    else:
        description += ", No dealer peek"
    if args.rules.surrender != "no":
        description += ", Surrender"
    if args.rules.double_after_split:
        description += ", DAS"
    if args.rules.resplit_aces:
        description += ", RSA"
    if args.rules.triple_seven:
        description += ", 7-7-7 pays 3:1"
    root.title(f"Blackjack - {description}")
    background = "#4e9572"
    side_panel_position = 1025
    root.configure(background=background)

    components = TableComponents(root, background)
    components.setup_canvas()
    components.get_shoe_progress(args.rules.number_of_decks)
    components.get_label()
    components.get_dealer_info()
    components.get_info()
    components.get_finger()
    components.get_player_slots(N_CARDS_MAX)
    components.get_chips()
    components.get_dealer_slot()
    components.get_insurance_chip()
    components.get_shuffle_indicator()
    components.set_side_panel()
    components.get_slider(side_panel_position, args.bet)

    check_button = CheckButton(root, args, background)
    check_button.fetch_accuracy()
    check_button.fetch_count()
    check_button.fetch_deviations()

    # Buttons
    menu = {
        name.split()[0].lower(): tkinter.Button(
            master=root, text=name.replace("-", " "), width=12, font="15"
        )
        for name in (
            "Even-money",
            "Insurance",
            "Surrender",
            "Double up",
            "Split",
            "Hit",
            "Stay",
            "Deal",
            "Reset",
        )
    }
    if args.rules.surrender == "no":
        del menu["surrender"]
    for name, button in menu.items():
        if name == "hit":
            button.configure(command=lambda: game.hit())
        elif name == "split":
            button.configure(command=lambda: game.split())
        elif name == "surrender":
            button.configure(command=lambda: game.surrender())
        elif name == "stay":
            button.configure(command=lambda: game.stay())
        elif name == "double":
            button.configure(command=lambda: game.double())
        elif name == "deal":
            button.configure(command=lambda: game.deal())
        elif name == "reset":
            button.configure(command=lambda: game.reset())
        elif name == "insurance":
            button.configure(command=lambda: game.insurance())
        elif name == "even-money":
            button.configure(command=lambda: game.even_money())
        else:
            raise ValueError
    for ind, button in enumerate(menu.values()):
        button.place(x=side_panel_position, y=ind * 33 + 230)
    menu["deal"].place(x=side_panel_position, y=500)
    menu["reset"].place(x=side_panel_position, y=65)

    def open_settings():
        root.destroy()
        settings(args)

    settings_button = tkinter.Button(
        root,
        text="Restart game",
        width=12,
        font="15",
        command=lambda: open_settings(),
    )
    settings_button.place(x=side_panel_position, y=20)

    dealer = Dealer(args.rules.game_type)
    player = Player(
        rules=args.rules,
        stack=args.stack,
    )
    game = Game(player, dealer, args, menu, components, check_button)
    game.reset()
    tkinter.mainloop()
