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
        self.is_hittable = True  # if True, can receive more cards
        self.is_blackjack = False
        self.is_over = False
        self.surrender = False
        self.is_asked_to_split = False
        self.is_split_hand = False
        self.slot = None
        self.is_finished = False  # if True, no more playing for this hand

    def deal(self, source: Union[Shoe, Card]):
        if isinstance(source, Shoe):
            self.cards.append(source.draw())
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

    def deal(self, shoe: Shoe):
        card = shoe.draw()
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
        self.shoe = self.init_shoe()
        self.active_slot = None

    @staticmethod
    def init_shoe():
        return Shoe(6)

    def deal(self):
        self.player.init_count()
        self.player.hands = []
        hand = self.player.start_new_hand(self.bet)
        self.dealer.init_hand()
        self.dealer.deal(self.shoe)
        self.dealer.deal(self.shoe)
        self.display_dealer_cards()
        hand.deal(self.shoe)
        hand.deal(self.shoe)
        hand.cards[0]=Card('J', 'clubs')
        hand.cards[1] = Card('K', 'diamonds')
        self.show_buttons()
        self.hide_buttons(('next',))
        self.show()
        self.display_player_hands()
        self.active_slot = hand.slot
        self.gui.label_text.set(f'Stack: {self.player.stack}')
        self.ask_what_to_do(hand)
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
        if n_hands == 1 and len(hand.cards) == 2 and self.dealer.cards[0].label != 'A':
            surrender = ', surrender'
        else:
            surrender = ''
        if len(hand.cards) == 2 and hand.is_hittable is True:
            double = ', double up'
            self.show_buttons(('double',))
        else:
            double = ''
            self.hide_buttons(('double',))
        if hand.cards[0].value == hand.cards[1].value and len(hand.cards) == 2 and n_hands < 4:
            split = ', split'
            self.show_buttons(('split',))
        else:
            split = ''
            self.hide_buttons(('split',))
        if hand.is_hittable is True:
            hit = ', hit'
            self.show_buttons(('hit',))
        else:
            hit = ''
            self.hide_buttons(('hit',))
        if hand.sum >= 21:
            action = ''
        else:
            action = f'Stay{surrender}{double}{split}{hit}?'
        self.gui.info_text[str(hand.slot)].set(action)

    def surrender(self):
        self.player.stack += (self.bet/2)
        self.gui.label_text.set(f'Stack: {self.player.stack}')
        self.deal()

    def double(self):
        self.hide_buttons(('surrender',))
        self.player.stack -= self.bet
        self.gui.label_text.set(f'Stack: {self.player.stack}')
        hand = self.get_hand_in_active_slot()
        hand.deal(self.shoe)
        hand.is_finished = True
        self.display_player_hands()
        self.clean_info()
        self.resolve_next_hand()

    def resolve_next_hand(self):
        hand = self.get_first_unfinished_hand()
        if hand is not None:
            self.active_slot = hand.slot
            self.ask_what_to_do(hand)
        else:
            self.clean_info()
            if self.is_all_over() is False:
                self.display_dealer_cards(hide_second=False)
                while self.dealer.is_finished is False:
                    self.dealer.deal(self.shoe)
                    self.display_dealer_cards()
            self.payout()

    def payout(self):
        for hand in self.player.hands:
            if hand.is_blackjack is True and self.dealer.is_blackjack is False:
                self.player.stack += hand.bet * 2.5
                result = f'Win by Blackjack!'
            elif hand.is_blackjack is True and self.dealer.is_blackjack is True:
                self.player.stack += hand.bet
                result = f'Push hand'
            elif hand.is_over is False and self.dealer.is_over is True:
                self.player.stack += hand.bet * 2
                result = f'Win (dealer > 21)'
            elif hand.is_over is True:
                result = f'Lose (player > 21)'
            elif hand.sum < self.dealer.sum:
                result = f'Lose ({hand.sum} vs {self.dealer.sum})'
            elif hand.surrender is True:
                self.player.stack += hand.bet / 2
                result = f'Lose by surrender'
            elif hand.sum > self.dealer.sum:
                self.player.stack += hand.bet * 2
                result = f'Win ({hand.sum} vs {self.dealer.sum})'
            elif hand.sum == self.dealer.sum:
                self.player.stack += hand.bet
                result = f'Push hand'
            else:
                raise ValueError
            self.gui.info_text[str(hand.slot)].set(result)
        self.gui.label_text.set(f'Stack: {self.player.stack}')
        self.hide_buttons()
        self.show_buttons(('next',))

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
        hand.deal(self.shoe)
        self.display_player_hands()
        if hand.is_over is True:
            self.hide(hand.slot)
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
                new_hand.deal(split_card)
                hand.is_split_hand = True
                new_hand.is_split_hand = True
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

    def hide(self, slot):
        """Hides cards in slot."""
        for n in range(N_CARDS_MAX):
            self.gui.slot_player[f'{str(slot)}{str(n)}'].configure(state=tkinter.DISABLED)

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
                img, width, _ = get_image(full_size=True)
            else:
                img, width, _ = get_image(card, full_size=True)
            self.gui.slot_dealer[str(ind)].configure(image=img, width=width)
            self.gui.slot_dealer[str(ind)].image = img

    def display_player_cards(self, hand: Hand):
        """Displays cards of one hand."""
        for ind, card in enumerate(hand.cards):
            full_size = True if ind == len(hand.cards) - 1 else False
            img, width, _ = get_image(card, full_size=full_size)
            self.gui.slot_player[f'{str(hand.slot)}{str(ind)}'].configure(image=img, width=width)
            self.gui.slot_player[f'{str(hand.slot)}{str(ind)}'].image = img

    def display_player_hands(self):
        """Displays all player hands on the table."""
        self.clean_player_slots()
        for hand in self.player.hands:
            self.display_player_cards(hand)


def get_image(card: Card = None, width: int = 100, height: int = 130, full_size: bool = True):
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
    width = width if full_size is True else width - 65
    return ImageTk.PhotoImage(image), width, height


def main():
    root = tkinter.Tk()
    root.geometry("1200x700")

    # Stack info
    label_text = tkinter.StringVar(root)
    label = tkinter.Label(root, textvariable=label_text)
    #label.grid(row=1, column=10, columnspan=1)

    # Hand info
    info_text = {str(slot): tkinter.StringVar(root) for slot in range(4)}
    info = {str(slot): tkinter.Label(root, textvariable=info_text[str(slot)], font=20, pady=30)
            for slot in range(4)}
    for ind, i in enumerate(info.values()):
        i.place(x=ind*250, y=500)

    # Dealer cards
    card_back_img, width_card, _ = get_image(full_size=True)
    frame_dealer = tkinter.Frame(root, pady=20)
    slot_dealer = {f'{str(pos)}': tkinter.Label(frame_dealer) for pos in range(N_CARDS_MAX)}
    for pos in range(2):
        slot_dealer[str(pos)].configure(image=card_back_img)
        slot_dealer[str(pos)].image = card_back_img
        slot_dealer[str(pos)].pack(side=tkinter.LEFT)
    for pos in range(N_CARDS_MAX):
        slot_dealer[str(pos)].pack(side=tkinter.LEFT)
    frame_dealer.place(x=330, y=30)

    # Player cards
    frame_player = {str(n): tkinter.Frame(root, padx=8, pady=5) for n in range(4)}
    slot_player = {f'{str(slot)}{str(pos)}': tkinter.Label(frame_player[str(slot)])
                   for slot in range(4) for pos in range(N_CARDS_MAX)}
    for frame in range(4):
        for pos in range(N_CARDS_MAX):
            slot_player[f'{str(frame)}{str(pos)}'].pack(side=tkinter.LEFT)
    for ind, frame in enumerate(frame_player.values()):
        frame.place(x=ind*250, y=350)

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
    button_x = 1000
    for ind, button in enumerate(menu.values()):
        button.place(x=button_x, y=ind*33+150)

    menu['next'].place(x=button_x, y=400)
    menu['reset'].place(x=button_x, y=50)

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
