import logging
import math
from time import sleep

from .lib import (
    Dealer,
    Player,
    Shoe,
    format_hand,
    get_correct_play,
    get_starting_hand,
)


def _is_correct(correct_play: str, action: str, decisions: dict) -> dict:
    if correct_play == action:
        decisions["correct"] += 1
    else:
        decisions["incorrect"] += 1
    return decisions


def play(args):
    decisions = {"correct": 0, "incorrect": 0}
    n_decs = 6
    n_total_hands = 0
    dealer = Dealer(args.rules.game_type)
    player = Player(args.rules)
    player.buy_in(args.stack)
    shoe = Shoe(n_decs)
    logging.debug("----------------")
    for _ in range(args.n_games):
        logging.debug("New round starts")
        logging.debug(f"Stack: {player.stack}")
        logging.debug("----------------")
        if args.ai is False:
            sleep(1)
        if (
            shoe.n_cards < 52
            or args.cards is not None
            or args.subset is not None
        ):
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
        player.update_counts(dealer.cards, shoe)
        dealer.deal(shoe)  # Hole card
        logging.debug(f"Dealer: {dealer.cards[0]}")
        if args.cards is not None:
            shoe.arrange(args.cards)
        elif args.subset is not None:
            cards = get_starting_hand(args.subset)
            shoe.arrange(cards)
        hand.deal(shoe)
        hand.deal(shoe)
        player.update_counts(hand, shoe)
        logging.debug(f"Player: {hand}")

        # Insurance
        if dealer.has_ace and hand.is_blackjack is False:
            should_insure = "yes" if player.true_count > 3 else "no"
            if args.ai is True:
                action = (
                    "y"
                    if should_insure == "yes" and args.count is True
                    else "n"
                )
            else:
                action = input("Take insurance? y/n [n]")
            if action == "y":
                decisions = _is_correct(should_insure, "yes", decisions)
                insurance_bet = bet / 2
                player.stack -= insurance_bet
                player.invested += insurance_bet
                dealer.insurance_bet = insurance_bet
        # Even money
        elif dealer.has_ace and hand.is_blackjack is True:
            should_take_even_money = "yes" if player.true_count > 3 else "no"
            if args.ai is True:
                action = (
                    "y"
                    if should_take_even_money == "yes" and args.count is True
                    else "n"
                )
            else:
                action = input("Take even money? y/n [n]")
            if action == "y":
                decisions = _is_correct(
                    should_take_even_money, "yes", decisions
                )
                dealer.even_money = True

        # Dealer peek
        if args.rules.region == "US" and dealer.is_blackjack is True:
            if dealer.insurance_bet > 0:
                logging.debug("You win insurance bet.")
                player.stack += dealer.insurance_bet * 3
            elif dealer.even_money is True:
                player.stack += hand.bet * 2
            else:
                if hand.is_blackjack is True:
                    logging.debug("Game is a push.")
                    player.stack += hand.bet
                else:
                    logging.debug("Dealer has BJ, you lose!")
            n_total_hands += 1
            player.update_counts(dealer.cards, shoe)
            continue

        if hand.is_blackjack is False:
            # Surrender can be done only here. And not against dealer's Ace.
            if args.rules.surrender == "2-10" and not dealer.has_ace:
                correct_play = get_correct_play(
                    hand, dealer.cards[0], len(player.hands), args.rules
                )
                if args.ai is True:
                    action = "y" if correct_play == "surrender" else "n"
                else:
                    action = input("Surrender? y/n [n]")
                if action == "y":
                    decisions = _is_correct(
                        correct_play, "surrender", decisions
                    )
                    hand.is_hittable = False
                    hand.surrender = True
                    player.stack += bet / 2

            # Splitting
            done_splitting = False
            while done_splitting is False:
                if hand.surrender is True:
                    break
                n_hands = len(player.hands)
                for ind in range(n_hands):
                    hand = player.hands[ind]
                    if (
                        hand.cards[0].value == hand.cards[1].value
                        and hand.is_asked_to_split is False
                    ):
                        correct_play = get_correct_play(
                            hand, dealer.cards[0], len(player.hands), args.rules
                        )
                        if args.ai is True:
                            action = "y" if correct_play == "split" else "n"
                        else:
                            action = input(f"Split {hand}? y/n [n]")
                        if action == "y":
                            decisions = _is_correct(
                                correct_play, "split", decisions
                            )
                            new_hand = player.start_new_hand(bet)
                            split_card = hand.cards.pop()
                            new_hand.deal(split_card)
                            # Only one card more if split card is Ace
                            # and this hand can not be doubled anymore
                            for handy in (hand, new_hand):
                                handy.deal(shoe)
                                handy.is_split_hand = True
                                handy.is_blackjack = False
                                if handy.cards[0].label == "A":
                                    handy.is_hittable = False
                            logging.debug(
                                f"Player: {format_hand(player.hands)}"
                            )
                        else:
                            hand.is_asked_to_split = True
                        if len(player.hands) == 4:
                            break
                done_splitting = True
                for hand in player.hands:
                    if (
                        hand.cards[0].value == hand.cards[1].value
                        and hand.is_asked_to_split is False
                    ):
                        done_splitting = False
                    player.update_counts(hand, shoe)
                if len(player.hands) == 4:
                    done_splitting = True

        # Deal Player:
        for hand in player.hands:
            hand_played = False
            while hand_played is False:
                if hand.surrender is True or hand.is_blackjack:
                    break
                if hand.is_split_hand and hand.sum != 21:
                    logging.debug(f"You are playing hand: {hand}")
                if len(hand.cards) == 2 and hand.is_hittable is True:
                    # Doubling
                    correct_play = get_correct_play(
                        hand, dealer.cards[0], len(player.hands), args.rules
                    )
                    if hand.sum == 21:
                        hand.played = True
                        break
                    if args.ai is True:
                        action = "y" if correct_play == "double" else "n"
                    else:
                        action = input("Double down? y/n [n]")
                    if action == "y":
                        player.stack -= bet
                        hand.bet += bet
                        player.invested += bet
                        hand.deal(shoe)
                        player.update_counts(hand, shoe)
                        # Hand can't be played anymore after doubling and dealing
                        hand.is_hittable = False
                        hand_played = True
                        decisions = _is_correct(
                            correct_play, "double", decisions
                        )
                    else:
                        if correct_play != "double":
                            decisions["correct"] += 1
                        else:
                            logging.info(
                                f"Incorrect play, correct play was {correct_play}"
                            )
                            decisions["incorrect"] += 1
                if hand.is_hittable is True:
                    # Hit or stay
                    correct_play = get_correct_play(
                        hand, dealer.cards[0], len(player.hands), args.rules
                    )
                    if args.ai is True:
                        if correct_play in ("hit", "surrender"):
                            # Can not surrender anymore
                            action = "h"
                        else:
                            action = "s"
                    else:
                        action = input("Hit or stay? h/s [h]")
                    if action == "s":
                        decisions = _is_correct(correct_play, "stay", decisions)
                        break
                    decisions = _is_correct(correct_play, "hit", decisions)
                    hand.deal(shoe)
                    player.update_counts(hand, shoe)
                else:
                    hand_played = True
                logging.debug(f"Player: {hand}")
                if hand.sum >= 21:
                    hand_played = True

        # Deal Dealer:
        if args.dealer_cards is not None and len(args.dealer_cards) > 2:
            shoe.arrange(args.dealer_cards[2:])
        hit_dealer = False
        for hand in player.hands:
            if (
                hand.is_over is False and hand.surrender is False
            ) or dealer.insurance_bet > 0:
                hit_dealer = True
        if player.hands[0].is_blackjack is True:
            if not dealer.has_ace and dealer.cards[0].value != 10:
                # Player already won
                hit_dealer = False
            else:
                hit_dealer = True
        while hit_dealer is True:
            player.update_counts(dealer.cards, shoe)
            logging.debug(f"Dealer: {dealer}")
            dealer_labels = [card.label for card in dealer.cards]
            if dealer.sum == 17:
                if args.rules.game_type == "h17" and "A" in dealer_labels:
                    hit_dealer = True
                else:
                    hit_dealer = False
            elif dealer.sum > 17:
                hit_dealer = False
            if (
                player.hands[0].is_blackjack is True
                and dealer.is_blackjack is False
            ):
                hit_dealer = False
            if hit_dealer is True:
                dealer.deal(shoe)

        # Payout

        # Even money
        if dealer.even_money is True:
            player.stack += hand.bet * 2

        # Insurance
        elif dealer.is_blackjack is True and dealer.insurance_bet > 0:
            logging.debug("You win insurance bet.")
            player.stack += dealer.insurance_bet * 3

        for hand in player.hands:
            if dealer.even_money is True:
                continue

            # Losing hands
            if hand.surrender:
                logging.debug("You lose by surrendering.")

            elif hand.sum > 21:
                logging.debug(f"Player: {hand.sum}, you lose!")

            elif (
                dealer.is_blackjack is True
                and hand.is_blackjack is False
                and hand.is_triple_seven is False
            ):
                logging.debug(
                    f"Dealer: BJ, Player: {hand.sum}, you lose to dealer BJ!"
                )

            elif hand.sum < dealer.sum <= 21:
                logging.debug(
                    f"Dealer: {dealer.sum}, Player: {hand.sum}, you lose!"
                )

            # Even hands
            elif dealer.is_blackjack is True and hand.is_blackjack is True:
                logging.debug("Dealer: BJ, Player: BJ, game is a push.")
                player.stack += hand.bet

            elif (
                hand.is_blackjack is False
                and dealer.is_blackjack is False
                and hand.sum == dealer.sum
            ):
                logging.debug(
                    f"Dealer: {dealer.sum}, Player: {hand.sum}, game is a push."
                )
                player.stack += hand.bet

            # Winning hands
            elif hand.is_triple_seven is True:
                logging.debug("You win with triple seven!")
                player.stack += hand.bet * 3

            elif hand.is_blackjack is True and dealer.is_blackjack is False:
                logging.debug("You win with BJ!")
                player.stack += hand.bet * 2.5

            elif dealer.sum > 21:
                logging.debug(f"Dealer: {dealer.sum}, you win!")
                player.stack += hand.bet * 2

            elif dealer.sum < hand.sum:
                logging.debug(
                    f"Dealer: {dealer.sum}, Player: {hand.sum}, you win!"
                )
                player.stack += hand.bet * 2

            else:
                raise ValueError("Unknown result")

        n_total_hands += len(player.hands)
        if args.ai is False:
            sleep(1)
        logging.debug("----------------")

    profit = player.stack - args.stack
    average_bet_per_hand = player.invested / n_total_hands
    average_profit_per_hand = profit / n_total_hands
    average_return_per_hand = (
        1 + average_profit_per_hand / average_bet_per_hand
    ) * 100
    logging.info(f"Number of rounds played: {args.n_games}")
    logging.info(f"Number of hands played (including splits): {n_total_hands}")
    logging.info(f"Initial bet size: {args.bet} $")
    logging.info(f"Total win: {profit} $")
    logging.info(f"Average bet / hand: {average_bet_per_hand:.3f} $")
    logging.info(f"Average win / hand: {average_profit_per_hand:.6f} $")
    logging.info(f"Average return / hand: {average_return_per_hand:.3f} %")
    if args.ai is False:
        try:
            correct_decisions = (
                decisions["correct"]
                / (decisions["correct"] + decisions["incorrect"])
                * 100
            )
        except ZeroDivisionError:
            correct_decisions = 100
        logging.info(f"Correct decisions: {correct_decisions} %")
    if args.cards is not None and args.dealer_cards is not None:
        # For integration tests
        print(player.stack)
