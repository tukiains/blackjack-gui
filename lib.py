import random
from typing import Union


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

    # Soft hands
    if hand.is_hard is False:
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