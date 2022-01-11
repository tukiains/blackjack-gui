#!/usr/bin/env python3
from typing import Union
import random
import argparse
import tkinter
from dataclasses import dataclass
from PIL import Image, ImageTk


N_CARDS_MAX = 10


def evaluate_hand(cards: list) -> tuple:
    the_sum = 0
    ace_used = False
    is_hard = True
    for card in cards:
        if card.label == 'A':
            is_hard = False
            if ace_used is False:
                the_sum += 11
                ace_used = True
            else:
                the_sum += 1
        else:
            if isinstance(card.value, int):
                the_sum += card.value
    if the_sum > 21:
        the_sum = 0
        is_hard = True
        for card in cards:
            if card.label == 'A':
                the_sum += 1
            else:
                if isinstance(card.value, int):
                    the_sum += card.value
    return the_sum, is_hard


class Card:
    def __init__(self, label: str, suit: str):
        self.label = label
        self.suit = suit
        self.value = self._get_value()

    def _get_value(self) -> Union[int, tuple]:
        if self.label in ("2", "3", "4", "5", "6", "7", "8", "9", "10"):
            return int(self.label)
        if self.label in ("J", "Q", "K"):
            return 10
        elif self.label == 'A':
            return 1, 11
        raise ValueError('Bad label')

    def __repr__(self) -> str:
        return f"{self.label}"


class Deck:
    def __init__(self):
        self.cards = []
        self._build()

    def _build(self):
        for suit in ["spades", "clubs", "diamonds", "hearts"]:
            for v in ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"):
                self.cards.append(Card(v, suit))


class Shoe:
    def __init__(self, n_decs: int):
        self.cards = []
        self.n_cards = 0
        self.n_decs = n_decs
        self._n_cards_total = self.n_decs * 52
        self._build()

    def _build(self):
        for _ in range(self.n_decs):
            deck = Deck()
            for card in deck.cards:
                self.cards.append(card)
        random.shuffle(self.cards)
        self.n_cards = len(self.cards)

    def draw(self, progress: any) -> Card:
        if self.n_cards > 0:
            card = self.cards.pop(0)
            self.n_cards -= 1
            fraction = (self._n_cards_total - self.n_cards) / self._n_cards_total
            progress.place(x=30, y=150, anchor="se", relheight=fraction, relwidth=1.)
            return card
        raise ValueError('Empty shoe!')


class Hand:
    def __init__(self):
        self.cards = []
        self.sum = 0
        self.bet = 0
        self.is_hard = True
        self.is_hittable = True  # if True, can receive more cards
        self.is_blackjack = False
        self.is_over = False
        self.surrender = False
        self.is_asked_to_split = False
        self.is_split_hand = False
        self.slot = None
        self.is_finished = False  # if True, no more playing for this hand

    def deal(self, source: Union[Shoe, Card], progress: any):
        if isinstance(source, Shoe):
            self.cards.append(source.draw(progress))
        else:
            self.cards.append(source)
        self.sum, self.is_hard = evaluate_hand(self.cards)
        if self.sum > 21:
            self.is_over = True
            self.is_hittable = False
            self.is_finished = True
        if self.sum == 21 and len(self.cards) == 2 and self.is_split_hand is False:
            self.is_blackjack = True
            self.is_hittable = False
            self.is_finished = True

    def __repr__(self) -> str:
        return f'{self.cards}'


def get_correct_play(hand: Hand,
                     dealer_card: Card,
                     n_hands: int) -> str:
    cards = hand.cards
    n_cards = len(cards)
    split = 'split'
    hit = 'hit'
    stay = 'stay'
    surrender = 'surrender'
    double = 'double'
    dealer_ace = dealer_card.label == 'A'

    # Hard hands
    if hand.is_hard is True and not (n_cards == 2 and cards[0].value == cards[1].value):
        if hand.sum <= 8:
            return hit
        if hand.sum == 9:
            if dealer_card.value in range(3, 7) and n_cards == 2 and hand.is_hittable is True:
                return double
            return hit
        if hand.sum in (10, 11):
            if dealer_card.value in range(2, 10) and n_cards == 2 and hand.is_hittable is True:
                return double
            return hit
        if hand.sum == 12:
            return stay if dealer_card.value in (4, 5, 6) else hit
        if hand.sum == 13:
            return stay if dealer_card.value in range(2, 7) else hit
        if hand.sum in (14, 15):
            if dealer_ace is False:
                if dealer_card.value == 10 and n_cards == 2 and hand.is_split_hand is False:
                    return surrender
                if dealer_card.value <= 6:
                    return stay
            return hit
        if hand.sum == 16:
            if n_cards >= 3 and dealer_card.value == 10:
                return stay
            if dealer_ace is False:
                if dealer_card.value in (9, 10) and n_cards == 2 and hand.is_split_hand is False:
                    return surrender
                if dealer_card.value <= 6:
                    return stay
            return hit
        if hand.sum >= 17:
            return stay

    # Pairs
    if n_cards == 2 and cards[0].value == cards[1].value:
        if cards[0].label == 'A':
            return hit if dealer_card.label == 'A' or n_hands == 4 else split
        if cards[0].value == 10:
            return stay
        if cards[0].value == 9:
            if dealer_card.value in (7, 10) or dealer_card.label == 'A' or n_hands == 4:
                return stay
            return split
        if cards[0].value == 8:
            if dealer_card.label == 'A' or n_hands == 4:
                return hit
            if dealer_card.value == 10:
                return surrender
            return split
        if cards[0].value == 7:
            if isinstance(dealer_card.value, int) and dealer_card.value <= 7 and n_hands < 4:
                return split
            return hit
        if cards[0].value == 6:
            if isinstance(dealer_card.value, int) and dealer_card.value <= 6 and n_hands < 4:
                return split
            return hit
        if cards[0].value == 5:
            if isinstance(dealer_card.value, int) and dealer_card.value <= 9:
                if len(cards) == 2:
                    return double
            return hit
        if cards[0].value == 4:
            if dealer_card.value in (5, 6) and n_hands < 4:
                return split
            return hit
        if cards[0].value == 3:
            if isinstance(dealer_card.value, int) and dealer_card.value <= 7 and n_hands < 4:
                return split
            return hit
        if cards[0].value == 2:
            if isinstance(dealer_card.value, int) and dealer_card.value <= 7 and n_hands < 4:
                return split
            return hit

    if hand.is_hard is False:
        # Soft hands
        labels = [card.label for card in cards]
        assert 'A' in labels
        if hand.sum >= 19:
            return stay
        if hand.sum == 18:
            if dealer_card.value in range(3, 7):
                if n_cards == 2 and hand.is_hittable is True:
                    return double
                return stay
            if dealer_card.value in (2, 7, 8):
                return stay
            return hit
        if hand.sum == 17:
            if dealer_card.value in range(3, 7) and n_cards == 2 and hand.is_hittable is True:
                return double
            return hit
        if hand.sum in (15, 16):
            if dealer_card.value in (4, 5, 6) and n_cards == 2 and hand.is_hittable is True:
                return double
            return hit
        if hand.sum in (13, 14):
            if dealer_card.value in (5, 6) and n_cards == 2 and hand.is_hittable is True:
                return double
            return hit
        if hand.sum < 13:
            return hit

    raise ValueError("Don't know what to do")


class Dealer:
    def __init__(self):
        self.cards = []
        self.sum = 0
        self.is_blackjack = False
        self.is_finished = False
        self.is_over = False

    def init_hand(self):
        self.cards = []
        self.sum = 0
        self.is_blackjack = False
        self.is_finished = False
        self.is_over = False

    def deal(self, shoe: Shoe, progress: any):
        card = shoe.draw(progress)
        self.cards.append(card)
        self.sum, _ = evaluate_hand(self.cards)
        if self.sum > 16:
            self.is_finished = True
        if self.sum == 21 and len(self.cards) == 2:
            self.is_blackjack = True
        if self.sum > 21:
            self.is_over = True

    def __repr__(self) -> str:
        return f'{self.cards}'


class Player:
    def __init__(self, stack: float = 1000):
        self.hands = []
        self.stack = stack
        self.invested = 0.0
        self.running_count = 0
        self.true_count = 0.0

    def buy_in(self, bet: float):
        self.stack = bet

    def start_new_hand(self, bet: float) -> Hand:
        hand = Hand()
        hand.bet = bet
        self.stack -= bet
        self.invested += bet
        hand.slot = self._get_next_free_slot()
        self.hands.append(hand)
        return hand

    def sort_hands(self):
        self.hands.sort(key=lambda x: x.slot)

    def _get_next_free_slot(self):
        n_hands = len(self.hands)
        if n_hands == 0:
            return 2
        elif n_hands == 1:
            return 1
        elif n_hands == 2:
            return 3
        elif n_hands == 3:
            return 0
        else:
            raise RuntimeError('Too many hands')

    def init_count(self):
        self.running_count = 0
        self.true_count = 0.0

    def update_count(self, dealer: Dealer, shoe: Shoe):
        hands = self.hands.copy()
        hands.append(dealer)
        for hand in hands:
            for card in hand.cards:
                if card.label == 'A' or card.value == 10:
                    self.running_count -= 1
                elif card.value <= 6:
                    self.running_count += 1
        n_decs_left = shoe.n_cards / 52
        self.true_count = self.running_count / n_decs_left


@dataclass
class Gui:
    root: any
    menu: any
    label_text: any
    slot_player: any
    slot_dealer: any
    info_text: any
    info: any
    chips: any
    finger: any
    shoe_progress: any


class Game:

    def __init__(self, player: Player, dealer: Dealer, gui: Gui, bet: int = 1):
        self.player = player
        self.dealer = dealer
        self.gui = gui
        self.bet = bet
        self.shoe = self.init_shoe()
        self.active_slot = None

    @staticmethod
    def init_shoe():
        return Shoe(6)

    def deal(self):
        self.hide_all_chips()
        self.hide_fingers()
        self.player.init_count()
        self.player.hands = []
        if self.shoe.n_cards < 52:
            self.shoe = Shoe(6)
        hand = self.player.start_new_hand(self.bet)
        self.dealer.init_hand()
        self.dealer.deal(self.shoe, self.gui.shoe_progress)
        self.dealer.deal(self.shoe, self.gui.shoe_progress)
        self.display_dealer_cards()
        hand.deal(self.shoe, self.gui.shoe_progress)
        hand.deal(self.shoe, self.gui.shoe_progress)
        self.show_buttons()
        self.hide_buttons(('next',))
        self.show()
        self.display_player_hands()
        self.active_slot = hand.slot
        self.display_stack()
        self.ask_what_to_do(hand)
        self.display_chip(hand, 0)
        if hand.is_blackjack:
            self.resolve_blackjack()
        if hand.cards[0].value != hand.cards[1].value:
            self.gui.menu['split']['state'] = tkinter.DISABLED
        else:
            self.gui.menu['split']['state'] = tkinter.NORMAL
        if self.dealer.cards[0].label == 'A':
            self.gui.menu['surrender']['state'] = tkinter.DISABLED
        else:
            self.gui.menu['surrender']['state'] = tkinter.NORMAL

    def resolve_blackjack(self):
        if self.dealer.cards[0].label == 'A' or self.dealer.cards[0].value == 10:
            self.display_dealer_cards(hide_second=False)
        self.payout()

    def ask_what_to_do(self, hand: Hand):
        self.clean_info()
        n_hands = len(self.player.hands)
        if len(hand.cards) == 2 and hand.is_hittable is True:
            self.show_buttons(('double',))
        else:
            self.hide_buttons(('double',))
        if hand.cards[0].value == hand.cards[1].value and len(hand.cards) == 2 and n_hands < 4:
            self.show_buttons(('split',))
        else:
            self.hide_buttons(('split',))
        if hand.is_hittable is True:
            self.show_buttons(('hit',))
        else:
            self.hide_buttons(('hit',))

    def surrender(self):
        self.player.stack += (self.bet/2)
        self.display_stack()
        self.deal()

    def double(self):
        self.hide_buttons(('surrender',))
        self.player.stack -= self.bet
        self.display_stack()
        hand = self.get_hand_in_active_slot()
        hand.bet += self.bet
        hand.deal(self.shoe, self.gui.shoe_progress)
        self.display_chip(hand, 1)
        hand.is_finished = True
        self.display_player_hands()
        if hand.sum > 21:
            self.hide(hand)
            self.hide_chips(hand)
        self.clean_info()
        self.resolve_next_hand()

    def resolve_next_hand(self):
        hand = self.get_first_unfinished_hand()
        if hand is not None:
            self.active_slot = hand.slot
            self.ask_what_to_do(hand)
            self.display_finger(hand)
        else:
            self.clean_info()
            if self.is_all_over() is False:
                self.display_dealer_cards(hide_second=False)
                while self.dealer.is_finished is False:
                    self.dealer.deal(self.shoe, self.gui.shoe_progress)
                    self.display_dealer_cards()
            self.payout()

    def payout(self):
        self.hide_fingers()
        for hand in self.player.hands:
            if hand.is_blackjack is True and self.dealer.is_blackjack is False:
                self.player.stack += hand.bet * 2.5
                result = f'Win by Blackjack!'
                self._display_chips(hand, bj=True)
            elif hand.is_blackjack is True and self.dealer.is_blackjack is True:
                self.player.stack += hand.bet
                result = f'Push hand (both have BJ)'
            elif hand.is_over is False and self.dealer.is_over is True:
                self.player.stack += hand.bet * 2
                result = f'Win (dealer > 21)'
                self._display_chips(hand)
            elif hand.is_over is True:
                result = f'Lose (player > 21)'
                self.hide_chips(hand)
                self.hide(hand)
            elif hand.sum < self.dealer.sum:
                result = f'Lose ({hand.sum} vs {self.dealer.sum})'
                self.hide_chips(hand)
                self.hide(hand)
            elif hand.surrender is True:
                self.player.stack += hand.bet / 2
                result = f'Lose by surrender'
            elif hand.sum > self.dealer.sum:
                self.player.stack += hand.bet * 2
                result = f'Win ({hand.sum} vs {self.dealer.sum})'
                self._display_chips(hand)
            elif hand.sum == self.dealer.sum:
                self.player.stack += hand.bet
                result = f'Push hand'
            else:
                raise ValueError
            self.gui.info_text[str(hand.slot)].set(result)
        self.display_stack()
        self.hide_buttons()
        self.show_buttons(('next',))

    def display_stack(self):
        self.gui.label_text.set(f'Stack: {self.player.stack} $')

    def _display_chips(self, hand, bj: bool = False):
        if bj is True:
            self.display_chip(hand, 1)
            self.display_chip(hand, 2, color='blue')
        elif hand.bet == self.bet:
            self.display_chip(hand, 1)
        elif hand.bet == (2 * self.bet):
            for n in range(4):
                self.display_chip(hand, n)

    def is_all_over(self) -> bool:
        for hand in self.player.hands:
            if hand.is_over is False and hand.surrender is False:
                return False
        return True

    def reset(self):
        self.clean_info()
        self.player.buy_in(args.stack)
        self.shoe = self.init_shoe()
        self.clean_dealer_slots()
        self.deal()

    def next(self):
        self.clean_info()
        self.clean_dealer_slots()
        self.deal()

    def hit(self):
        self.hide_buttons(('surrender', 'double'))
        hand = self.get_hand_in_active_slot()
        hand.deal(self.shoe, self.gui.shoe_progress)
        self.display_player_hands()
        if hand.is_over is True:
            self.hide(hand)
            self.hide_chips(hand)
        if hand.sum == 21:
            hand.is_finished = True
        if hand.is_finished is False:
            self.ask_what_to_do(hand)
        else:
            self.resolve_next_hand()

    def get_first_unfinished_hand(self) -> Hand:
        for hand in self.player.hands:
            if hand.is_finished is False:
                return hand

    def get_hand_in_active_slot(self) -> Hand:
        for hand in self.player.hands:
            if hand.slot == self.active_slot:
                return hand

    def stay(self):
        hand = self.get_hand_in_active_slot()
        hand.is_finished = True
        self.resolve_next_hand()

    def split(self):
        self.hide_buttons(('surrender',))
        n_hands = len(self.player.hands)
        for ind in range(n_hands):
            hand = self.player.hands[ind]
            if hand.cards[0].value == hand.cards[1].value:
                new_hand = self.player.start_new_hand(self.bet)
                split_card = hand.cards.pop()
                new_hand.deal(split_card, self.gui.shoe_progress)
                hand.is_split_hand = True
                new_hand.is_split_hand = True
                self.display_chip(new_hand, 0)
                self.display_stack()
                for handy in (hand, new_hand):
                    handy.deal(self.shoe)
                    handy.is_split_hand = True
                    if handy.sum == 21:
                        handy.is_finished = True
                    if handy.cards[0].label == 'A':
                        # Split Aces receive only one card more
                        handy.is_hittable = False
                        handy.is_finished = True
                self.player.hands[ind] = hand
                break

        self.player.hands.sort(key=lambda x: not x.cards[0].value == x.cards[1].value)
        self.display_player_hands()
        n_hands = len(self.player.hands)
        for ind in range(n_hands):
            hand = self.player.hands[ind]
            if hand.cards[0].value == hand.cards[1].value and len(self.player.hands) < 4:
                self.gui.menu['split']['state'] = tkinter.NORMAL
                self.ask_what_to_do(hand)
                break
            else:
                self.player.sort_hands()
                self.display_player_hands()
                self.resolve_next_hand()
        self.display_player_hands()

    def show(self):
        """Shows all available hands as active."""
        for slot in range(4):
            for n in range(N_CARDS_MAX):
                self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(state=tkinter.NORMAL)

    def hide(self, hand: Hand):
        """Hides cards in slot."""
        for n in range(N_CARDS_MAX):
            self.gui.slot_player[f'{str(hand.slot)}{str(n)}'].configure(state=tkinter.DISABLED)

    def hide_buttons(self, buttons: tuple = None):
        """Hides menu buttons."""
        if buttons is None:
            for key, button in self.gui.menu.items():
                if key != 'reset':
                    button.configure(state=tkinter.DISABLED)
        else:
            for button in buttons:
                if button in self.gui.menu.keys():
                    self.gui.menu[button].configure(state=tkinter.DISABLED)

    def show_buttons(self, buttons: tuple = None):
        """Shows menu buttons."""
        if buttons is None:
            for button in self.gui.menu.values():
                button.configure(state=tkinter.NORMAL)
        else:
            for button in buttons:
                if button in self.gui.menu.keys():
                    self.gui.menu[button].configure(state=tkinter.NORMAL)

    def clean_player_slots(self):
        """Cleans player card slots."""
        for slot in range(4):
            for n in range(N_CARDS_MAX):
                self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(image='', width=0)

    def clean_dealer_slots(self):
        """Cleans dealer slot."""
        for n in range(N_CARDS_MAX):
            self.gui.slot_dealer[f'{str(n)}'].configure(image='', width=0)

    def clean_info(self):
        """Removes info text behind all slots."""
        for slot in range(4):
            self.gui.info_text[str(slot)].set('')

    def display_dealer_cards(self, hide_second: bool = True):
        """Displays dealer cards."""
        for ind, card in enumerate(self.dealer.cards):
            if ind == 1 and hide_second is True and len(self.dealer.cards) == 2:
                img, width, _ = get_image()
            else:
                img, width, _ = get_image(card)
            self.gui.slot_dealer[str(ind)].configure(image=img, width=width)
            self.gui.slot_dealer[str(ind)].image = img

    def display_player_cards(self, hand: Hand):
        """Displays cards of one hand."""
        for ind, card in enumerate(hand.cards):
            img, width, _ = get_image(card)
            self.gui.slot_player[f'{str(hand.slot)}{str(ind)}'].configure(image=img, width=width)
            self.gui.slot_player[f'{str(hand.slot)}{str(ind)}'].image = img

    def display_player_hands(self):
        """Displays all player hands on the table."""
        self.clean_player_slots()
        for hand in self.player.hands:
            self.display_player_cards(hand)

    def display_chip(self, hand: Hand, pos: int, color: str = 'red'):
        img = get_chip_image(color)
        self.gui.chips[f'{str(hand.slot)}{str(pos)}'].configure(image=img)
        self.gui.chips[f'{str(hand.slot)}{str(pos)}'].image = img

    def display_finger(self, hand: Hand):
        self.hide_fingers()
        img = get_finger_image()
        self.gui.finger[f'{str(hand.slot)}'].configure(image=img)
        self.gui.finger[f'{str(hand.slot)}'].image = img

    def hide_chips(self, hand: Hand):
        for pos in range(4):
            self.gui.chips[f'{str(hand.slot)}{str(pos)}'].configure(image='')

    def hide_all_chips(self):
        for chip in self.gui.chips.values():
            chip.configure(image='')

    def hide_fingers(self):
        for finger in self.gui.finger.values():
            finger.configure(image='')


def get_image(card: Card = None, width: int = 100, height: int = 130):
    if card is None:
        filename = 'images/back.png'
    else:
        prefix = {
            'A': 'ace',
            'J': 'jack',
            'Q': 'queen',
            'K': 'king',
        }
        if card.label in prefix.keys():
            fix = prefix[card.label]
        else:
            fix = str(card.value)
        filename = f'images/{fix}_of_{card.suit}.png'
    image = Image.open(filename).resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image), width, height


def get_chip_image(color: str = 'red'):
    size = 50
    filename = f'images/{color}-chip.png'
    image = Image.open(filename).resize((size, size), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)


def get_finger_image():
    filename = f'images/finger2.png'
    image = Image.open(filename).resize((40, 60), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)


def main():
    root = tkinter.Tk()
    root.geometry("1200x700")

    # Shoe status
    shoe_status_container = tkinter.Label(root, borderwidth=0, background='white')
    shoe_status_container.place(x=20, y=30, height=150, width=30)
    shoe_progress = tkinter.Label(shoe_status_container, background="black", borderwidth=0,
                                  anchor="e")
    shoe_label = tkinter.Label(root, text='Discard', font=12)
    shoe_label.place(x=5, y=190)

    # Stack info
    label_text = tkinter.StringVar(root)
    label = tkinter.Label(root, textvariable=label_text, font=15)
    label.place(x=1050, y=520)

    # Hand info
    info_text = {str(slot): tkinter.StringVar(root) for slot in range(4)}
    info = {str(slot): tkinter.Label(root, textvariable=info_text[str(slot)], font=20, pady=30)
            for slot in range(4)}
    for ind, i in enumerate(info.values()):
        i.place(x=ind*250, y=600)

    # Dealer finger
    finger = {str(slot): tkinter.Label(root) for slot in range(4)}
    info = {str(slot): tkinter.Label(root) for slot in range(4)}
    for ind, f in enumerate(finger.values()):
        f.place(x=ind*250+20, y=260)

    # Dealer cards
    card_back_img, width_card, _ = get_image()
    slot_dealer = {f'{str(pos)}': tkinter.Label(root) for pos in range(N_CARDS_MAX)}
    for pos in range(2):
        slot_dealer[str(pos)].configure(image=card_back_img)
        slot_dealer[str(pos)].image = card_back_img
        slot_dealer[str(pos)].pack(side=tkinter.LEFT)
    for pos in range(N_CARDS_MAX):
        slot_dealer[str(pos)].place(y=40, x=350+pos*105)

    # Player cards
    slot_player = {f'{str(slot)}{str(pos)}': tkinter.Label(root)
                   for slot in range(4) for pos in range(N_CARDS_MAX)}
    for frame in range(4):
        for pos in range(N_CARDS_MAX):
            slot_player[f'{str(frame)}{str(pos)}'].place(x=frame*250+pos*30, y=350-pos*15)

    # Chips
    chips = {f'{str(slot)}{str(pos)}': tkinter.Label(root)
             for slot in range(4) for pos in range(4)}
    for slot in range(4):
        for pos in range(4):
            padx, pady = 0, 0
            if pos in (1, 3):
                padx = 50
            if pos in (2, 3):
                pady = 50
            chips[f'{str(slot)}{str(pos)}'].place(x=slot*250+padx, y=500+pady)

    # Buttons
    menu = {name.split()[0].lower(): tkinter.Button(master=root, text=name, width=15, font=15)
            for name in ('Surrender', 'Double up', 'Hit', 'Stay', 'Split', 'Next deal', 'Reset')}
    for name, button in menu.items():
        if name == 'hit':
            button.configure(command=lambda: game.hit())
        elif name == 'split':
            button.configure(command=lambda: game.split())
        elif name == 'surrender':
            button.configure(command=lambda: game.surrender())
        elif name == 'stay':
            button.configure(command=lambda: game.stay())
        elif name == 'double':
            button.configure(command=lambda: game.double())
        elif name == 'next':
            button.configure(command=lambda: game.next())
        elif name == 'reset':
            button.configure(command=lambda: game.reset())
        else:
            raise ValueError
    x_sidepanel = 1000
    for ind, button in enumerate(menu.values()):
        button.place(x=x_sidepanel, y=ind*33+150)

    menu['next'].place(x=x_sidepanel, y=400)
    menu['reset'].place(x=x_sidepanel, y=50)

    gui = Gui(root,
              menu,
              label_text,
              slot_player,
              slot_dealer,
              info_text,
              info,
              chips,
              finger,
              shoe_progress)

    dealer = Dealer()
    player = Player()
    game = Game(player, dealer, gui)
    game.reset()
    tkinter.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BlackJack')
    parser.add_argument('--stack',
                        type=int,
                        default=1000,
                        help='Stack size. Default is 1000.')
    args = parser.parse_args()
    main()
