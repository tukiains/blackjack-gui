#!/usr/bin/env python3
from typing import Union
import random
import time
import logging
import argparse
import math
import tkinter
from dataclasses import dataclass
from PIL import Image, ImageTk
from itertools import compress


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
        self._build(n_decs)

    def _build(self, n_decs: int):
        for _ in range(n_decs):
            deck = Deck()
            for card in deck.cards:
                self.cards.append(card)
        random.shuffle(self.cards)
        self.n_cards = len(self.cards)

    def draw(self) -> Card:
        if self.n_cards > 0:
            card = self.cards.pop(0)
            self.n_cards -= 1
            return card
        raise ValueError('Empty shoe!')


class Hand:
    def __init__(self):
        self.cards = []
        self.sum = 0
        self.bet = 0
        self.is_hard = True
        self.is_hittable = True
        self.is_blackjack = False
        self.is_over = False
        self.surrender = False
        self.is_asked_to_split = False
        self.is_split_hand = False

    def deal(self, source: Union[Shoe, Card]):
        if isinstance(source, Shoe):
            self.cards.append(source.draw())
        else:
            self.cards.append(source)
        self.sum, self.is_hard = evaluate_hand(self.cards)
        if self.sum > 21:
            self.is_over = True

    def blackjack(self):
        self.is_hittable = False
        self.is_blackjack = True

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

    def init_hand(self):
        self.cards = []
        self.sum = 0
        self.is_blackjack = False

    def deal(self, shoe: Shoe):
        card = shoe.draw()
        self.cards.append(card)
        self.sum, _ = evaluate_hand(self.cards)
        if self.sum == 21 and len(self.cards) == 2:
            self.is_blackjack = True

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
        self.stack += bet

    def start_new_hand(self, bet: float) -> Hand:
        hand = Hand()
        hand.bet = bet
        self.stack -= bet
        self.invested += bet
        self.hands.append(hand)
        return hand

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
    frame_player: any
    slot_player: any
    frame_dealer: any
    slot_dealer: any
    info_text: any
    info: any


class Game:

    def __init__(self, player: Player, dealer: Dealer, gui: Gui, bet: int = 1):
        self.player = player
        self.dealer = dealer
        self.gui = gui
        self.bet = bet
        self.shoe = Shoe(6)

    def deal(self):
        self.player.init_count()
        self.player.hands = []
        hand = self.player.start_new_hand(self.bet)
        self.dealer.init_hand()
        self.dealer.deal(self.shoe)
        self.update_dealer_card(0)
        hand.deal(self.shoe)
        hand.deal(self.shoe)
        self.show()
        self.draw_player_hands()
        self.gui.label_text.set(f'Stack: {self.player.stack}')
        if hand.cards[0].value != hand.cards[1].value:
            self.gui.menu['split']['state'] = tkinter.DISABLED
        else:
            self.gui.menu['split']['state'] = tkinter.NORMAL
            self.gui.info_text['2'].set('Split?')
        if self.dealer.cards[0].label == 'A':
            self.gui.menu['surrender']['state'] = tkinter.DISABLED
        else:
            self.gui.menu['surrender']['state'] = tkinter.NORMAL

    def surrender(self):
        self.player.stack += (self.bet/2)
        self.gui.label_text.set(f'Stack: {self.player.stack}')
        self.deal()

    def double(self):
        self.player.stack -= self.bet
        for hand in self.player.hands:
            if hand.is_hittable is True:
                hand.deal(self.shoe)
                hand.is_hittable = False
                break
        for hand in self.player.hands:
            if hand.is_hittable is True:
                #self.gui.infobox_text.set(f'Playing {hand}, double up, hit or stay?')
                break

    def hit(self):
        for i in self.gui.info_text.values():
            i.set('')
        self.deal()

    def split(self):
        self.gui.menu['surrender']['state'] = tkinter.DISABLED
        self.gui.info_text['2'].set('')
        n_hands = len(self.player.hands)
        for ind in range(n_hands):
            hand = self.player.hands[ind]
            if hand.cards[0].value == hand.cards[1].value:
                new_hand = self.player.start_new_hand(self.bet)
                split_card = hand.cards.pop()
                new_hand.deal(split_card)
                hand.is_split_hand = True
                new_hand.is_split_hand = True
                for handy in (hand, new_hand):
                    handy.deal(self.shoe)
                    handy.is_split_hand = True
                    if handy.cards[0].label == 'A':
                        handy.is_hittable = False
                self.player.hands[ind] = hand
                break

        # Sort hands so that splittable hands are first
        self.player.hands.sort(key=lambda x: not x.cards[0].value == x.cards[1].value)
        n_hands = len(self.player.hands)
        for ind in range(n_hands):
            hand = self.player.hands[ind]
            if hand.cards[0].value == hand.cards[1].value and len(self.player.hands) < 4:
                self.gui.menu['split']['state'] = tkinter.NORMAL
                pos = self.get_first_slot(n_hands) + ind
                self.gui.info_text[str(pos)].set('Split, double up, hit or stay?')
                break
            else:
                self.gui.menu['split']['state'] = tkinter.DISABLED
                pos = self.get_first_slot(n_hands)
                self.clean_info()
                self.gui.info_text[str(pos)].set('Double up, hit or stay?')
                self.hide(pos)
        self.draw_player_hands()

    def show(self):
        for slot in range(4):
            for n in range(2):
                self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(state=tkinter.NORMAL)

    def hide(self, pos: int):
        for slot in range(4):
            if slot == pos:
                state = tkinter.NORMAL
            else:
                state = tkinter.DISABLED
            for n in range(2):
                self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(state=state)

    def update_dealer_card(self, pos: int):
        img, width, _ = get_image(self.dealer.cards[pos])
        self.gui.slot_dealer[str(pos)].configure(image=img)
        self.gui.slot_dealer[str(pos)].image = img

    def update_player_cards(self, hand_no: int, slot: int = 2):
        for n in range(2):
            img, width, _ = get_image(self.player.hands[hand_no].cards[n])
            self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(image=img, width=width)
            self.gui.slot_player[f'{str(slot)}{str(n)}'].image = img

    def clean_slots(self):
        width = 10
        for slot in range(4):
            for n in range(2):
                self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(image='', width=width)

    def clean_info(self):
        for slot in range(4):
            self.gui.info_text[str(slot)].set('')

    def draw_player_hands(self):
        self.clean_slots()
        n_hands = len(self.player.hands)
        if n_hands == 1:
            self.update_player_cards(0)
        elif n_hands == 2:
            self.update_player_cards(0, 1)
            self.update_player_cards(1, 2)
        elif n_hands == 3:
            self.update_player_cards(0, 1)
            self.update_player_cards(1, 2)
            self.update_player_cards(2, 3)
        elif n_hands == 4:
            self.update_player_cards(0, 0)
            self.update_player_cards(1, 1)
            self.update_player_cards(2, 2)
            self.update_player_cards(3, 3)

    @staticmethod
    def get_first_slot(n_hands: int):
        if n_hands == 1:
            return 2
        if n_hands in (2, 3):
            return 1
        return 0


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


def main():
    root = tkinter.Tk()
    root.geometry("1600x600")

    # Stack info
    label_text = tkinter.StringVar(root)
    label = tkinter.Label(root, textvariable=label_text)
    label.grid(row=2, column=4, columnspan=1)

    # Hand info
    info_text = {str(n): tkinter.StringVar(root) for n in range(4)}
    info = {str(n): tkinter.Label(root, textvariable=info_text[str(n)], font=20, pady=30) for n in range(4)}
    for ind, i in enumerate(info.values()):
        i.grid(row=10, column=ind)

    # Dealer cards
    test, width_card, _ = get_image()
    frame_dealer = tkinter.Frame(root, pady=20)
    slot_dealer = {
        '0': tkinter.Label(frame_dealer, image=test, width=width_card),
        '1': tkinter.Label(frame_dealer, image=test, width=width_card)
    }
    slot_dealer['0'].pack(side=tkinter.LEFT)
    slot_dealer['1'].pack(side=tkinter.RIGHT)
    frame_dealer.grid(row=2, column=2, columnspan=1)

    # Player cards
    frame_player = {str(n): tkinter.Frame(root, padx=8, pady=5) for n in range(4)}
    slot_width = 10
    slot_player = {
        '00': tkinter.Label(frame_player['0'], width=slot_width),
        '01': tkinter.Label(frame_player['0'], width=slot_width),
        '10': tkinter.Label(frame_player['1'], width=slot_width),
        '11': tkinter.Label(frame_player['1'], width=slot_width),
        '20': tkinter.Label(frame_player['2'], width=width_card, image=test),
        '21': tkinter.Label(frame_player['2'], width=width_card, image=test),
        '30': tkinter.Label(frame_player['3'], width=slot_width),
        '31': tkinter.Label(frame_player['3'], width=slot_width),
    }
    for frame in range(4):
        slot_player[f'{frame}0'].pack(side=tkinter.LEFT)
        slot_player[f'{frame}1'].pack(side=tkinter.LEFT)

    for ind, frame in enumerate(frame_player.values()):
        frame.grid(row=9, column=ind)

    button_width = 15
    fontsize = 15
    menu = {
        'surrender': tkinter.Button(master=root,
                                    text="Surrender",
                                    width=button_width,
                                    font=fontsize,
                                    command=lambda: game.surrender()),
        'double': tkinter.Button(master=root,
                                 text="Double up",
                                 width=button_width,
                                 font=fontsize,
                                 command=lambda: game.double()),
        'hit': tkinter.Button(master=root,
                              text="Hit",
                              width=button_width,
                              font=fontsize,
                              command=lambda: game.hit()),
        'stay': tkinter.Button(master=root,
                               text="Stay",
                               width=button_width,
                               font=fontsize),
        'split': tkinter.Button(master=root,
                                text="Split",
                                width=button_width,
                                font=fontsize,
                                command=lambda: game.split())
    }
    for ind, button in enumerate(menu.values()):
        button.grid(row=ind+3, column=4)

    gui = Gui(root,
              menu,
              label_text,
              frame_player,
              slot_player,
              frame_dealer,
              slot_dealer,
              info_text,
              info)

    dealer = Dealer()
    player = Player()
    game = Game(player, dealer, gui)
    player.buy_in(args.stack)
    game.deal()
    tkinter.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BlackJack')
    parser.add_argument('--stack',
                        type=int,
                        default=1000,
                        help='Stack size. Default is 1000.')
    args = parser.parse_args()
    main()
