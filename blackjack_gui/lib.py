from dataclasses import dataclass
import random
import tkinter
from typing import List, Literal


@dataclass
class Rules:
    game_type: Literal["s17", "h17"]
    surrender: Literal["no", "2-10"]
    peek: bool
    double_after_split: bool = True
    resplit_aces: bool = True
    triple_seven: bool = False
    region: Literal["US", "Europe", "Helsinki"] = "US"
    number_of_decks: int = 6
    csm: bool = False


class Card:
    def __init__(self, label: str, suit: str, visible: bool = True):
        self.label = label
        self.suit = suit
        self.value = self._get_value()
        self.visible = visible
        self.counted = False

    def _get_value(self) -> int | tuple:
        if self.label in ("2", "3", "4", "5", "6", "7", "8", "9", "10"):
            return int(self.label)
        if self.label in ("J", "Q", "K"):
            return 10
        if self.label == "A":
            return 1, 11
        raise ValueError("Bad label")

    def __repr__(self) -> str:
        if self.suit == "spades":
            suit = "\u2660"
        elif self.suit == "clubs":
            suit = "\u2663"
        elif self.suit == "diamonds":
            suit = "\u2666"
        elif self.suit == "hearts":
            suit = "\u2665"
        else:
            raise ValueError("Bad suit")
        return f"{self.label}{suit}"


class Deck:
    def __init__(self):
        self.cards = []
        self._build()

    def _build(self):
        for suit in ["spades", "clubs", "diamonds", "hearts"]:
            for v in (
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "J",
                "Q",
                "K",
                "A",
            ):
                self.cards.append(Card(v, suit))


class Shoe:
    def __init__(self, n_decs: int):
        self.cards: List[Card] = []
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

    def draw(self) -> Card:
        """Draws a card from shoe."""
        if self.n_cards > 0:
            card = self.cards.pop(0)
            self.n_cards -= 1
            return card
        raise ValueError("Empty shoe!")

    def fill_discard_tray(self, progress: tkinter.Label) -> None:
        fraction = (self._n_cards_total - self.n_cards) / self._n_cards_total
        y = self.n_decs * 20
        if progress is not None:
            progress.place(
                x=30, y=y, anchor="se", relheight=fraction, relwidth=1.0
            )

    def arrange(self, cards: list, randomize: bool = False):
        """Arranges shoe so that next cards are the requested ones."""
        if ";" in str(cards):
            # Choose one hand randomly from input like --cards="A,7;7,7;10,10"
            options = [
                [cards[i].split(";")[-1], cards[i + 1].split(";")[0]]
                for i in range(len(cards) - 1)
            ]
            cards = random.choice(options)

        labels = [card.label for card in self.cards]
        if randomize and len(cards) > 1:
            # randomize the first two cards
            cards = random.sample(cards[0:2], 2) + cards[2:]
        for ind, card in enumerate(cards):
            indices = [i for i, x in enumerate(labels[ind:]) if x == str(card)]
            shoe_ind = random.choice(indices) + ind
            self.cards[shoe_ind], self.cards[ind] = (
                self.cards[ind],
                self.cards[shoe_ind],
            )
            labels[shoe_ind], labels[ind] = labels[ind], labels[shoe_ind]


class Hand:
    def __init__(self, rules: Rules):
        self.rules = rules
        self.cards: list[Card] = []
        self.sum = 0.0
        self.bet = 0.0
        self.is_hard = True
        self.is_hittable = True  # if True, can receive more cards
        self.is_blackjack = False
        self.is_over = False
        self.surrender = False
        self.is_asked_to_split = False
        self.is_split_hand = False
        self.slot = None
        self.is_finished = False  # if True, no more playing for this hand
        self.played = False
        self.is_triple_seven = False

    def deal(
        self,
        source: Shoe | Card,
    ):
        if isinstance(source, Shoe):
            self.cards.append(source.draw())
        else:
            self.cards.append(source)
        self.sum, self.is_hard = evaluate_hand(self.cards)

        if (
            len(self.cards) == 3
            and all(card.label == "7" for card in self.cards)
            and not self.is_split_hand
            and self.rules.triple_seven
        ):
            self.is_triple_seven = True
            self.is_finished = True
            self.is_hittable = False
        if self.sum >= 22:
            self.is_finished = True
            self.is_hittable = False
            self.is_over = True
        if self.sum == 21 and len(self.cards) == 2 and not self.is_split_hand:
            self.is_blackjack = True

    def __repr__(self) -> str:
        return format_hand(self.cards)


class Dealer:
    def __init__(self, game_type: Literal["h17", "s17"]):
        self.cards: list[Card] = []
        self.sum = 0.0
        self.is_blackjack = False
        self.is_finished = False
        self.is_over = False
        self.insurance_bet = 0.0
        self.even_money = False
        self.game_type = game_type
        self.has_ace = False

    def init_hand(self):
        self.cards = []
        self.sum = 0
        self.is_blackjack = False
        self.is_finished = False
        self.is_over = False
        self.insurance_bet = 0
        self.even_money = False

    def deal(self, shoe: Shoe):
        card = shoe.draw()
        self.cards.append(card)
        self.sum, _ = evaluate_hand(self.cards)
        labels = [c.label for c in self.cards]
        self.has_ace = True if labels[0] == "A" else False
        if self.sum == 17 and self.game_type == "h17" and "A" in labels:
            pass
        elif self.sum > 16:
            self.is_finished = True
        if self.sum == 21 and len(self.cards) == 2:
            self.is_blackjack = True
        if self.sum > 21:
            self.is_over = True

    def __repr__(self) -> str:
        return format_hand(self.cards)


class Player:
    def __init__(self, rules: Rules, stack: float = 1000):
        self.rules = rules
        self.stack = stack
        self.hands: List[Hand] = []
        self.initial_stack = stack
        self.invested = 0.0
        self.running_count = 0
        self.true_count = 0.0

    def buy_in(self, bet: float):
        self.stack = bet

    def start_new_hand(self, bet: float) -> Hand:
        hand = Hand(self.rules)
        hand.bet = bet
        self.stack -= bet
        self.invested += bet
        hand.slot = self._get_next_free_slot()
        self.hands.append(hand)
        return hand

    def sort_hands(self):
        self.hands.sort(key=lambda x: x.slot)  # type: ignore

    def _get_next_free_slot(self):
        n_hands = len(self.hands)
        if n_hands == 0:
            return 2
        if n_hands == 1:
            return 1
        if n_hands == 2:
            return 3
        if n_hands == 3:
            return 0
        raise RuntimeError("Too many hands")

    def init_count(self):
        self.running_count = 0
        self.true_count = 0.0

    def update_true_count(self, shoe: Shoe):
        n_decs_left = shoe.n_cards / 52
        self.true_count = self.running_count / n_decs_left

    def update_running_count(self, card: Card):
        if not card.visible or card.counted:
            return
        if card.label == "A" or card.value == 10:
            self.running_count -= 1
        elif isinstance(card.value, int) and card.value <= 6:
            self.running_count += 1
        card.counted = True

    def update_counts(self, hand: Hand | list[Card], shoe: Shoe):
        cards = hand.cards if isinstance(hand, Hand) else hand
        for card in cards:
            self.update_running_count(card)
        self.update_true_count(shoe)


def evaluate_hand(cards: list) -> tuple:
    the_sum = 0
    ace_used = False
    is_hard = True
    for card in cards:
        if card.label == "A":
            is_hard = False
            if not ace_used:
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
            if card.label == "A":
                the_sum += 1
            else:
                if isinstance(card.value, int):
                    the_sum += card.value
    return the_sum, is_hard


def get_rules(region: Literal["US", "Europe", "Helsinki"]):
    if region == "US":
        rules = Rules(
            game_type="h17",
            surrender="no",
            peek=True,
        )
    if region == "Europe":
        rules = Rules(
            game_type="s17",
            surrender="no",
            peek=False,
        )
    if region == "Helsinki":
        rules = Rules(
            game_type="s17",
            surrender="2-10",
            peek=False,
            triple_seven=True,
        )
    rules.region = region
    return rules


def get_correct_play(
    hand: Hand, dealer_card: Card, n_hands: int, rules: Rules
) -> str:
    cards = hand.cards
    n_cards = len(cards)
    split = "split"
    hit = "hit"
    stay = "stay"
    surrender = "surrender"
    double = "double"
    dealer_ace = dealer_card.label == "A"
    can_be_doubled = (
        n_cards == 2
        and hand.is_hittable
        and not (hand.is_split_hand and not rules.double_after_split)
    )

    # Hard hands
    if hand.is_hard and not (n_cards == 2 and cards[0].value == cards[1].value):
        if hand.sum <= 8:
            return hit
        if hand.sum == 9:
            if dealer_card.value == 2 and rules.number_of_decks == 2:
                return double
            if dealer_card.value in range(3, 7) and can_be_doubled:
                return double
            return hit
        if hand.sum == 10:
            if dealer_card.value in range(2, 10) and can_be_doubled:
                return double
            return hit
        if hand.sum == 11:
            if rules.game_type == "h17" and can_be_doubled:
                return double
            if dealer_card.value in range(2, 10) and can_be_doubled:
                return double
            return hit
        if hand.sum == 12:
            return stay if dealer_card.value in (4, 5, 6) else hit
        if hand.sum == 13:
            return stay if dealer_card.value in range(2, 7) else hit
        if hand.sum == 14:
            if rules.surrender != "no" and _should_surrender(
                hand, dealer_card, (10,)
            ):
                return surrender
            return stay if dealer_card.value in range(2, 7) else hit
        if hand.sum == 15:
            if rules.surrender != "no" and _should_surrender(
                hand, dealer_card, (10,)
            ):
                return surrender
            if not dealer_ace and dealer_card.value in range(2, 7):
                return stay
            return hit
        if hand.sum == 16:
            if rules.surrender != "no" and _should_surrender(
                hand, dealer_card, (9, 10)
            ):
                return surrender
            if n_cards >= 3 and dealer_card.value == 10:
                return stay
            if not dealer_ace and dealer_card.value in (2, 3, 4, 5, 6):
                return stay
            return hit
        if hand.sum >= 17:
            return stay

    # Pairs
    if n_cards == 2 and cards[0].value == cards[1].value:
        if cards[0].label == "A":
            if n_hands == 4:
                return hit
            if rules.game_type == "h17":
                return split
            return hit if dealer_ace else split
        if cards[0].value == 10:
            return stay
        if cards[0].value == 9:
            if dealer_card.value in (7, 10) or dealer_ace or n_hands == 4:
                return stay
            return split
        if cards[0].value == 8:
            if rules.game_type == "h17":
                return split
            if _should_surrender(hand, dealer_card, (10,)):
                return surrender
            if n_hands == 4 or dealer_ace:
                return hit
            return split
        if cards[0].value == 7:
            if dealer_card.value in (2, 3, 4, 5, 6, 7) and n_hands < 4:
                return split
            return hit
        if cards[0].value == 6:
            if (
                dealer_card.value == 2
                and not rules.double_after_split
                and rules.number_of_decks >= 4
            ):
                return hit
            if dealer_card.value in (2, 3, 4, 5, 6) and n_hands < 4:
                return split
            return hit
        if cards[0].value == 5:
            if dealer_card.value in range(2, 10) and can_be_doubled:
                return double
            return hit
        if cards[0].value == 4:
            if n_hands == 4:
                return hit
            if dealer_card.value in (5, 6) and rules.double_after_split:
                return split
            return hit
        if cards[0].value in (2, 3):
            if n_hands == 4:
                return hit
            if dealer_card.value in (2, 3) and not rules.double_after_split:
                return hit
            if dealer_card.value in (2, 3, 4, 5, 6, 7):
                return split
            return hit

    # Soft hands
    if not hand.is_hard:
        labels = [card.label for card in cards]
        assert "A" in labels
        if hand.sum > 19:
            return stay
        if hand.sum == 19:
            if (
                rules.game_type == "h17"
                and dealer_card.value == 6
                and can_be_doubled
            ):
                return double
            return stay
        if hand.sum == 18:
            if rules.game_type == "h17":
                if dealer_card.value in range(2, 7):
                    return double if can_be_doubled else stay
                if dealer_card.value in (7, 8):
                    return stay
                return hit
            if dealer_card.value in range(3, 7):
                return double if can_be_doubled else stay
            if dealer_card.value in (2, 7, 8):
                return stay
            return hit
        if hand.sum == 17:
            return (
                double
                if dealer_card.value in range(3, 7) and can_be_doubled
                else hit
            )
        if hand.sum in (15, 16):
            return (
                double
                if dealer_card.value in (4, 5, 6) and can_be_doubled
                else hit
            )
        if hand.sum in (13, 14):
            return (
                double
                if dealer_card.value in (5, 6) and can_be_doubled
                else hit
            )
        if hand.sum < 13:
            return hit

    raise ValueError("Don't know what to do")


def _should_surrender(hand: Hand, dealer_card: Card, values: tuple) -> bool:
    if hand.is_split_hand or len(hand.cards) != 2:
        return False
    if dealer_card.value in values:
        return True
    return False


def format_hand(cards: list) -> str:
    return str(cards)[1:-1].replace(",", " ") + " "


def get_starting_hand(subset: str) -> list[str]:
    hard_hands = [
        "2,3",
        "2,4",
        "2,5",
        "2,6",
        "2,7",
        "2,8",
        "2,9",
        "2,10",
        "3,4",
        "3,5",
        "3,6",
        "3,7",
        "3,8",
        "3,9",
        "3,10",
        "4,5",
        "4,6",
        "4,7",
        "4,8",
        "4,9",
        "4,10",
        "5,6",
        "5,7",
        "5,8",
        "5,9",
        "5,10",
        "6,7",
        "6,8",
        "6,9",
        "6,10",
        "7,8",
        "7,9",
        "7,10",
        "8,9",
        "8,10",
        "9,10",
    ]
    soft_hands = [
        "A,2",
        "A,3",
        "A,4",
        "A,5",
        "A,6",
        "A,7",
        "A,8",
        "A,9",
        "A,10",
    ]
    pairs = [
        "2,2",
        "3,3",
        "4,4",
        "5,5",
        "6,6",
        "7,7",
        "8,8",
        "9,9",
        "10,10",
        "A,A",
    ]
    if subset == "hard":
        cards = hard_hands
    elif subset == "soft":
        cards = soft_hands
    elif subset == "pairs":
        cards = pairs
    elif subset == "hard/soft":
        cards = hard_hands + soft_hands
    elif subset == "soft/pairs":
        cards = soft_hands + pairs
    else:
        raise ValueError("Bad subset")
    card_list = random.choice(cards).split(",")
    return card_list if random.choice([True, False]) else card_list[::-1]
