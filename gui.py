#!/usr/bin/env python3
import tkinter
from dataclasses import dataclass
from PIL import Image, ImageTk
from lib import Card, Hand, Player, Dealer, Shoe, get_correct_play


N_CARDS_MAX = 10


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
    fix_mistakes: any


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
        """Starts new round."""
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
        self.hide_buttons(('deal',))
        self.show()
        self.display_player_hands()
        self.active_slot = hand.slot
        self.display_stack()
        self.enable_correct_buttons(hand)
        self.display_chip(hand, 0)
        if hand.is_blackjack:
            self.resolve_blackjack()
        if self.dealer.cards[0].label == 'A':
            self.hide_buttons(('surrender', ))

    def resolve_blackjack(self):
        if self.dealer.cards[0].label == 'A' or self.dealer.cards[0].value == 10:
            self.display_dealer_cards(hide_second=False)
        self.payout()

    def enable_correct_buttons(self, hand: Hand):
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
        """Method for Surrender button."""
        if self.gui.fix_mistakes.get() == 1:
            if self.check_play(self.player.hands[0], 'surrender') is False:
                return
        self.player.stack += (self.bet/2)
        self.display_stack()
        self.deal()

    def double(self):
        """Method for Double button."""
        hand = self.get_hand_in_active_slot()
        if self.gui.fix_mistakes.get() == 1:
            if self.check_play(hand, 'double') is False:
                return
        self.hide_buttons(('surrender',))
        self.player.stack -= self.bet
        self.display_stack()
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

    def check_play(self, hand: Hand, play: str) -> bool:
        correct_play = get_correct_play(hand, self.dealer.cards[0], len(self.player.hands))
        if correct_play != play:
            self.display_info(hand, 'Incorrect! Try again..')
            self.gui.root.after(1000, self.clean_info)
            return False
        return True

    def resolve_next_hand(self):
        hand = self.get_first_unfinished_hand()
        if hand is not None:
            self.active_slot = hand.slot
            self.enable_correct_buttons(hand)
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
            self.display_info(hand, result)
        self.hide_buttons()
        self.show_buttons(('deal',))

    def display_stack(self):
        self.gui.label_text.set(f'Stack: {self.player.stack} $')

    def _display_chips(self, hand, bj: bool = False):
        if bj is True:
            self.display_chip(hand, 1)
            self.display_chip(hand, 4, color='blue')
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

    def display_info(self, hand: Hand, info: str):
        """Prints text below hand."""
        self.gui.info_text[str(hand.slot)].set(info)

    def reset(self):
        """Method for Reset button."""
        self.clean_info()
        self.player.buy_in(self.player.initial_stack)
        self.shoe = self.init_shoe()
        self.clean_dealer_slots()
        self.deal()

    def next(self):
        self.clean_info()
        self.clean_dealer_slots()
        self.deal()

    def hit(self):
        """Method for Hit button."""
        hand = self.get_hand_in_active_slot()
        if self.gui.fix_mistakes.get() == 1:
            if self.check_play(hand, 'hit') is False:
                return
        self.hide_buttons(('surrender', 'double'))
        hand.deal(self.shoe, self.gui.shoe_progress)
        self.display_player_hands()
        if hand.is_over is True:
            self.hide(hand)
            self.hide_chips(hand)
        if hand.sum == 21:
            hand.is_finished = True
        if hand.is_finished is False:
            self.enable_correct_buttons(hand)
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
        """Method for Stay button."""
        hand = self.get_hand_in_active_slot()
        if self.gui.fix_mistakes.get() == 1:
            if self.check_play(hand, 'stay') is False:
                return
        hand.is_finished = True
        self.resolve_next_hand()

    def split(self):
        """Method for Split button."""
        hand = self.get_hand_in_active_slot()
        if self.gui.fix_mistakes.get() == 1:
            if self.check_play(hand, 'split') is False:
                return
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
                    handy.deal(self.shoe, self.gui.shoe_progress)
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
                self.display_finger(hand)
                self.enable_correct_buttons(hand)
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
        for pos in self.gui.slot_dealer.values():
            pos.configure(image='', width=0)

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
        """Displays dealer finger over hand."""
        self.hide_fingers()
        img = get_finger_image()
        self.gui.finger[f'{str(hand.slot)}'].configure(image=img)
        self.gui.finger[f'{str(hand.slot)}'].image = img

    def hide_chips(self, hand: Hand):
        """Hides chips of a hand."""
        for pos in range(4):
            self.gui.chips[f'{str(hand.slot)}{str(pos)}'].configure(image='')

    def hide_all_chips(self):
        """Hides chips of all hands."""
        for chip in self.gui.chips.values():
            chip.configure(image='')

    def hide_fingers(self):
        """Hides all dealer fingers."""
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
    image = Image.open(filename).resize((size, size-15), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)


def get_finger_image():
    filename = f'images/finger2.png'
    image = Image.open(filename).resize((40, 60), Image.ANTIALIAS)
    return ImageTk.PhotoImage(image)


def main(args):
    root = tkinter.Tk()
    root.geometry("1200x700")
    root.title('Blackjack')

    # Advisor button
    fix_mistakes = tkinter.IntVar()
    checkbox_container = tkinter.Checkbutton(root,
                                             text='Coach mode',
                                             variable=fix_mistakes)
    checkbox_container.place(x=1025, y=600)

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
    label.place(x=1035, y=520)

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
        slot_dealer[str(pos)].place(y=40, x=300+pos*105)

    # Player cards
    slot_player = {f'{str(slot)}{str(pos)}': tkinter.Label(root, borderwidth=0)
                   for slot in range(4) for pos in range(N_CARDS_MAX)}
    for frame in range(4):
        for pos in range(N_CARDS_MAX):
            slot_player[f'{str(frame)}{str(pos)}'].place(x=frame*250+pos*30, y=350-pos*15)

    # Chips
    chips = {f'{str(slot)}{str(pos)}': tkinter.Label(root, borderwidth=0)
             for slot in range(4) for pos in range(5)}
    for slot in range(4):
        for pos in range(5):
            padx, pady = 0, 0
            if pos in (1, 3):
                padx = 50
            if pos in (2, 3, 4):
                pady = 35
            if pos == 4:
                padx = 25
            chips[f'{str(slot)}{str(pos)}'].place(x=slot*250+padx, y=500+pady)

    # Buttons
    menu = {name.split()[0].lower(): tkinter.Button(master=root, text=name, width=15, font=15)
            for name in ('Surrender', 'Double up', 'Hit', 'Stay', 'Split', 'Deal', 'Reset')}
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
        elif name == 'deal':
            button.configure(command=lambda: game.next())
        elif name == 'reset':
            button.configure(command=lambda: game.reset())
        else:
            raise ValueError
    x_sidepanel = 1000
    for ind, button in enumerate(menu.values()):
        button.place(x=x_sidepanel, y=ind*33+150)

    menu['deal'].place(x=x_sidepanel, y=400)
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
              shoe_progress,
              fix_mistakes)

    dealer = Dealer()
    player = Player(stack=args.stack)
    game = Game(player, dealer, gui)
    game.reset()
    tkinter.mainloop()
