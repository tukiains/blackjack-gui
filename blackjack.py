#!/usr/bin/env python3
from typing import Union
import random
import time
import logging
import argparse
import math


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
            the_sum += card.value
    if the_sum > 21:
        the_sum = 0
        is_hard = True
        for card in cards:
            if card.label == 'A':
                the_sum += 1
            else:
                the_sum += card.value
    return the_sum, is_hard


class Card:
    def __init__(self, label):
        self.label = label
        self.value = self._get_value()

    def _get_value(self):
        if self.label in ("2", "3", "4", "5", "6", "7", "8", "9", "10"):
            value = int(self.label)
            return value
        if self.label in ("J", "Q", "K"):
            return 10
        return 1, 11

    def __repr__(self):
        return f"{self.label}"


class Deck:
    def __init__(self):
        self.cards = []
        self._build()

    def _build(self):
        for _ in ["Spades", "Clubs", "Diamonds", "Hearts"]:
            for v in ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"):
                self.cards.append(Card(v))


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
        self.n_cards = len(self.cards)

    def shuffle(self):
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def draw(self):
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

    def __repr__(self):
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
            return double if dealer_card.value in (3, 4, 5, 6) and n_cards == 2 else hit
        if hand.sum in (10, 11):
            return hit if dealer_card.value == 10 or dealer_ace is True or n_cards != 2 else double
        if hand.sum == 12:
            return stay if dealer_card.value in (4, 5, 6) else hit
        if hand.sum == 13:
            return stay if dealer_card.value in (2, 3, 4, 5, 6) else hit
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
            if dealer_card.value in (3, 4, 5, 6):
                if n_cards == 2:
                    return double
                return stay
            if dealer_card.value in (2, 7, 8):
                return stay
            return hit
        if hand.sum == 17:
            if dealer_card.value in (3, 4, 5, 6) and n_cards == 2:
                return double
            return hit
        if hand.sum in (15, 16):
            if dealer_card.value in (4, 5, 6) and n_cards == 2:
                return double
            return hit
        if hand.sum in (13, 14):
            if dealer_card.value in (5, 6) and n_cards == 2:
                return double
            return hit
        if hand.sum < 13:
            return hit

    raise ValueError("Don't know what to do")


class Player:
    def __init__(self):
        self.hands = []
        self.stack = 0.0
        self.invested = 0.0
        self.running_count = 0
        self.true_count = 0

    def buy_in(self, value: int):
        self.stack += value

    def start_new_hand(self, value: int):
        hand = Hand()
        hand.bet = value
        self.stack -= value
        self.invested += value
        self.hands.append(hand)
        return hand

    def update_count(self, dealer, shoe: Shoe):
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


class Dealer:
    def __init__(self):
        self.cards = []
        self.sum = 0
        self.stack = 0
        self.is_hard = True
        self.is_blackjack = False

    def init_hand(self):
        self.cards = []
        self.sum = 0
        self.is_blackjack = False
        self.is_hard = True

    def deal(self, shoe: Shoe):
        card = shoe.draw()
        self.cards.append(card)
        self.sum, self.is_hard = evaluate_hand(self.cards)
        if self.sum == 21 and len(self.cards) == 2:
            self.is_blackjack = True

    def __repr__(self):
        return f'{self.cards}'


def _is_correct(correct_play: str, action: str, decisions: dict) -> dict:
    if correct_play == action:
        decisions['correct'] += 1
    else:
        decisions['incorrect'] += 1
    return decisions


def main():
    initial_stack = args.stack
    initial_bet = args.bet
    n_games = args.n_games
    sleep_time = args.delay
    decisions = {
        'correct': 0,
        'incorrect': 0
    }
    n_total_hands = 0
    n_decs = 6
    dealer = Dealer()
    player = Player()
    player.buy_in(initial_stack)
    shoe = Shoe(n_decs)
    shoe.shuffle()
    logging.debug('----------------')
    for _ in range(n_games):
        logging.debug('New round starts')
        logging.debug(f'Stack: {player.stack}')
        logging.debug('----------------')
        if shoe.n_cards < 20:
            shoe = Shoe(n_decs)
            shoe.shuffle()
            player.running_count = 0
            player.true_count = 0
        player.hands = []
        if args.ai is True and args.count is True and player.true_count > 1:
            bet = initial_bet * math.floor(player.true_count)
        else:
            bet = initial_bet
        hand = player.start_new_hand(bet)
        dealer.init_hand()
        dealer.deal(shoe)
        logging.debug(f'Dealer: {dealer}')
        hand.deal(shoe)
        hand.deal(shoe)
        logging.debug(f'Player: {hand}')
        if hand.sum == 21:
            hand.blackjack()
        else:
            # Surrender can be done only here. And not against dealer's Ace.
            if dealer.cards[0].label != 'A':
                correct_play = get_correct_play(hand, dealer.cards[0], len(player.hands))
                if args.ai is True:
                    action = 'y' if correct_play == 'surrender' else 'n'
                else:
                    action = input('Surrender? y/n [n]')
                if action == 'y':
                    decisions = _is_correct(correct_play, 'surrender', decisions)
                    hand.is_hittable = False
                    hand.surrender = True
                    player.stack += (bet/2)

            # Splitting
            done_splitting = False
            while done_splitting is False:
                if hand.surrender is True:
                    break
                n_hands = len(player.hands)
                for ind in range(n_hands):
                    hand = player.hands[ind]
                    if hand.cards[0].value == hand.cards[1].value and hand.is_asked_to_split is False:
                        correct_play = get_correct_play(hand, dealer.cards[0], len(player.hands))
                        if args.ai is True:
                            action = 'y' if correct_play == 'split' else 'n'
                        else:
                            action = input(f'Split {hand}? y/n [n]')
                        if action == 'y':
                            decisions = _is_correct(correct_play, 'split', decisions)
                            new_hand = player.start_new_hand(bet)
                            split_card = hand.cards.pop()
                            new_hand.deal(split_card)
                            hand.deal(shoe)
                            new_hand.deal(shoe)
                            hand.is_split_hand = True
                            new_hand.is_split_hand = True
                            # Only one card more if split card is Ace
                            for handy in (hand, new_hand):
                                if handy.cards[0].label == 'A':
                                    handy.is_hittable = False
                            logging.debug(f'Player: {player.hands}')
                        else:
                            hand.is_asked_to_split = True
                        if len(player.hands) == 4:
                            break
                done_splitting = True
                for hand in player.hands:
                    if hand.cards[0].value == hand.cards[1].value and hand.is_asked_to_split is False:
                        done_splitting = False
                if len(player.hands) == 4:
                    done_splitting = True

        # Deal Player:
        for hand in player.hands:
            hand_played = False
            while hand_played is False:
                if hand.surrender is True:
                    break
                logging.debug(f'You are playing hand: {hand}')
                if len(hand.cards) == 2 and hand.is_hittable is True:
                    # Doubling
                    correct_play = get_correct_play(hand, dealer.cards[0], len(player.hands))
                    if args.ai is True:
                        action = 'y' if correct_play == 'double' else 'n'
                    else:
                        action = input('Double down? y/n [n]')
                    if action == 'y':
                        player.stack -= bet
                        hand.bet += bet
                        player.invested += bet
                        hand.deal(shoe)
                        # Hand can't be played anymore after doubling and dealing
                        hand.is_hittable = False
                        hand_played = True
                        decisions = _is_correct(correct_play, 'double', decisions)
                    else:
                        if correct_play != 'double':
                            decisions['correct'] += 1
                        else:
                            logging.info(f'Incorrect play, correct play was {correct_play}')
                            decisions['incorrect'] += 1
                if hand.is_hittable is True:
                    correct_play = get_correct_play(hand, dealer.cards[0], len(player.hands))
                    if args.ai is True:
                        if correct_play in ('hit', 'surrender'):
                            # Can not surrender anymore
                            action = 'h'
                        else:
                            action = 's'
                    else:
                        action = input('Hit or stay? h/s [h]')
                    if action == 's':
                        decisions = _is_correct(correct_play, 'stay', decisions)
                        break
                    decisions = _is_correct(correct_play, 'hit', decisions)
                    hand.deal(shoe)
                else:
                    hand_played = True
                logging.debug(f'Player: {hand}')
                if hand.sum >= 21:
                    hand_played = True

        # Deal Dealer:
        hit_dealer = False
        for hand in player.hands:
            if hand.is_over is False and hand.surrender is False:
                hit_dealer = True
        if player.hands[0].is_blackjack and (dealer.cards[0].label != 'A' or
                                             dealer.cards[0].value != 10):
            # Player already won
            hit_dealer = False
        while hit_dealer is True:
            time.sleep(sleep_time)
            dealer.deal(shoe)
            logging.debug(f'Dealer: {dealer}')
            time.sleep(sleep_time)
            if dealer.sum > 16:
                hit_dealer = False

        # Pay off
        for hand in player.hands:

            # Losing hands
            if hand.surrender:
                logging.debug(f'You lose by surrendering.')

            elif hand.sum > 21:
                logging.debug(f'Player: {hand.sum}, you lose!')

            elif hand.sum < dealer.sum <= 21:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, you lose!')

            elif hand.sum == 21 and dealer.is_blackjack is True:
                logging.debug(f'Dealer: BJ, Player: {hand.sum}, you lose to dealer BJ')

            # Push hands
            elif hand.is_blackjack is True and dealer.is_blackjack is True:
                logging.debug(f'Dealer: BJ, Player: BJ, game is a push.')
                player.stack += hand.bet

            elif hand.is_blackjack is False and dealer.is_blackjack is False and hand.sum == dealer.sum:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, game is a push.')
                player.stack += hand.bet

            # Winning hands
            elif hand.is_blackjack is True and dealer.is_blackjack is False:
                logging.debug(f'You win with BJ!')
                player.stack += bet * 2.5

            elif dealer.sum > 21 >= hand.sum:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, you win!')
                player.stack += hand.bet * 2

            elif dealer.sum < hand.sum <= 21:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, you win!')
                player.stack += hand.bet * 2

            else:
                raise ValueError('Unknown result')

        n_total_hands += len(player.hands)
        player.update_count(dealer, shoe)
        logging.debug('----------------')

    profit = player.stack - initial_stack
    logging.info(f'Number of hands played: {n_total_hands}')
    logging.info(f'Bet size: {args.bet} $')
    logging.info(f'Profit: {profit} $')
    logging.info(f'Return {round((1 + profit / player.invested) * 100 * 1e4)/1e4} %')
    if args.ai is False:
        logging.info(f'Correct decisions: {decisions["correct"] / (decisions["correct"] + decisions["incorrect"]) * 100} %')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BlackJack')
    parser.add_argument('--n_games',
                        type=int,
                        default=10,
                        help='Number of rounds to be played. Default is 10.')
    parser.add_argument('--bet',
                        type=int,
                        default=1,
                        help='Bet size. Default is 1.')
    parser.add_argument('--stack',
                        type=int,
                        default=1000,
                        help='Stack size. Default is 1000.')
    parser.add_argument('--ai',
                        type=bool,
                        default=False,
                        help='Computer play. Default is False.')
    parser.add_argument('--count',
                        type=bool,
                        default=False,
                        help='Count cards. Default is False. Can be used with --ai=True.')
    parser.add_argument('--delay',
                        type=float,
                        default=0,
                        help='Delay in the game flow. Default is 0.')
    parser.add_argument('--loglevel',
                        type=str,
                        default='DEBUG',
                        help='Log level. Can be DEBUG or INFO. Default is DEBUG.')
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    main()
