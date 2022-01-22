import logging
import math
from .lib import Player, Dealer, Shoe, get_correct_play


def _is_correct(correct_play: str, action: str, decisions: dict) -> dict:
    if correct_play == action:
        decisions['correct'] += 1
    else:
        decisions['incorrect'] += 1
    return decisions


def main(args):
    decisions = {
        'correct': 0,
        'incorrect': 0
    }
    n_decs = 6
    n_total_hands = 0
    dealer = Dealer()
    player = Player()
    player.buy_in(args.stack)
    shoe = Shoe(n_decs)
    logging.debug('----------------')
    for _ in range(args.n_games):
        logging.debug('New round starts')
        logging.debug(f'Stack: {player.stack}')
        logging.debug('----------------')
        if shoe.n_cards < 52 or args.cards is not None:
            shoe = Shoe(n_decs)
            player.init_count()
        player.hands = []
        if args.ai is True and args.count is True and player.true_count > 1:
            bet = args.bet * math.floor(player.true_count)
        else:
            bet = args.bet
        hand = player.start_new_hand(bet)
        dealer.init_hand()
        if args.dealer_cards is not None:
            shoe.arrange(args.dealer_cards)
        dealer.deal(shoe)
        logging.debug(f'Dealer: {dealer}')
        if args.cards is not None:
            shoe.arrange(args.cards)
        hand.deal(shoe)
        hand.deal(shoe)
        logging.debug(f'Player: {hand}')

        # Insurance bet
        if dealer.cards[0].label == 'A' and hand.is_blackjack is False:
            should_insure = 'yes' if player.true_count > 3 else 'no'
            if args.ai is True:
                action = 'y' if should_insure == 'yes' and args.count is True else 'n'
            else:
                action = input('Insure? y/n [n]')
            if action == 'y':
                decisions = _is_correct(should_insure, 'yes', decisions)
                insurance_bet = bet / 2
                player.stack -= insurance_bet
                player.invested += insurance_bet
                dealer.insurance_bet = insurance_bet
        # Even money
        elif dealer.cards[0].label == 'A' and hand.is_blackjack is True:
            should_take_even_money = 'yes' if player.true_count > 3 else 'no'
            if args.ai is True:
                action = 'y' if should_take_even_money == 'yes' and args.count is True else 'n'
            else:
                action = input('Take even money? y/n [n]')
            if action == 'y':
                decisions = _is_correct(should_take_even_money, 'yes', decisions)
                dealer.even_money = True

        if hand.is_blackjack is False:
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
                            # Only one card more if split card is Ace
                            # and apparently this hand can not be doubled anymore ?!
                            for handy in (hand, new_hand):
                                handy.deal(shoe)
                                handy.is_split_hand = True
                                handy.is_blackjack = False
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
                if hand.surrender is True or hand.is_blackjack:
                    break
                if hand.is_split_hand and hand.sum != 21:
                    logging.debug(f'You are playing hand: {hand}')
                if len(hand.cards) == 2 and hand.is_hittable is True:
                    # Doubling
                    correct_play = get_correct_play(hand, dealer.cards[0], len(player.hands))
                    if hand.sum == 21:
                        hand.played = True
                        break
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
                    # Hit or stay
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
        if args.dealer_cards is not None and len(args.dealer_cards) > 1:
            shoe.arrange(args.dealer_cards[1:])
        hit_dealer = False
        for hand in player.hands:
            if (hand.is_over is False and hand.surrender is False) or dealer.insurance_bet > 0:
                hit_dealer = True
        if player.hands[0].is_blackjack is True:
            if dealer.cards[0].label != 'A' and dealer.cards[0].value != 10:
                # Player already won
                hit_dealer = False
            else:
                hit_dealer = True
        while hit_dealer is True:
            dealer.deal(shoe)
            logging.debug(f'Dealer: {dealer}')
            if dealer.sum > 16:
                hit_dealer = False
            if player.hands[0].is_blackjack is True and dealer.is_blackjack is False:
                hit_dealer = False

        # Payout

        # Even money
        if dealer.even_money is True:
            player.stack += hand.bet * 2

        # Insurance
        elif dealer.is_blackjack is True and dealer.insurance_bet > 0:
            logging.debug(f'You win insurance bet.')
            player.stack += dealer.insurance_bet * 3

        for hand in player.hands:

            if dealer.even_money is True:
                continue

            # Losing hands
            if hand.surrender:
                logging.debug(f'You lose by surrendering.')

            elif hand.sum > 21:
                logging.debug(f'Player: {hand.sum}, you lose!')

            elif dealer.is_blackjack is True and hand.is_blackjack is False:
                logging.debug(f'Dealer: BJ, Player: {hand.sum}, you lose to dealer BJ!')

            elif hand.sum < dealer.sum <= 21:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, you lose!')

            # Even hands
            elif dealer.is_blackjack is True and hand.is_blackjack is True:
                logging.debug(f'Dealer: BJ, Player: BJ, game is a push.')
                player.stack += hand.bet

            elif hand.is_blackjack is False and dealer.is_blackjack is False and hand.sum == dealer.sum:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, game is a push.')
                player.stack += hand.bet

            # Winning hands
            elif hand.is_blackjack is True and dealer.is_blackjack is False:
                logging.debug(f'You win with BJ!')
                player.stack += bet * 2.5

            elif dealer.sum > 21:
                logging.debug(f'Dealer: {dealer.sum}, you win!')
                player.stack += hand.bet * 2

            elif dealer.sum < hand.sum:
                logging.debug(f'Dealer: {dealer.sum}, Player: {hand.sum}, you win!')
                player.stack += hand.bet * 2

            else:
                raise ValueError('Unknown result')

        n_total_hands += len(player.hands)
        player.update_count(dealer, shoe)
        logging.debug('----------------')

    profit = player.stack - args.stack
    average_bet_per_hand = player.invested / n_total_hands
    average_profit_per_hand = profit / n_total_hands
    average_return_per_hand = (1 + average_profit_per_hand / average_bet_per_hand) * 100
    logging.info(f'Number of rounds played: {args.n_games}')
    logging.info(f'Number of hands played (including splits): {n_total_hands}')
    logging.info(f'Initial bet size: {args.bet} $')
    logging.info(f'Total win: {profit} $')
    logging.info(f'Average bet / hand: {"%.3f"%average_bet_per_hand} $')
    logging.info(f'Average win / hand: {"%.6f"%average_profit_per_hand} $')
    logging.info(f'Average return / hand: {"%.3f"%average_return_per_hand} %')
    if args.ai is False:
        try:
            correct_decisions = decisions["correct"] / (decisions["correct"] + decisions["incorrect"]) * 100
        except ZeroDivisionError:
            correct_decisions = 100
        logging.info(f'Correct decisions: {correct_decisions} %')
    if args.cards is not None and args.dealer_cards is not None:
        # For integration tests
        print(player.stack)
