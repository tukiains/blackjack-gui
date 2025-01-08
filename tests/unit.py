import pytest

from blackjack_gui.lib import (
    Card,
    Hand,
    evaluate_hand,
    get_correct_play,
    get_rules,
)


@pytest.mark.parametrize(
    "cards, the_sum, is_hard",
    [
        # Hard hands (No Ace or Ace counts as 1)
        ([Card("3", "hearts"), Card("10", "hearts")], 13, True),
        (
            [Card("3", "hearts"), Card("4", "hearts"), Card("5", "hearts")],
            12,
            True,
        ),
        ([Card("10", "hearts"), Card("10", "hearts")], 20, True),
        (
            [Card("10", "hearts"), Card("10", "hearts"), Card("2", "hearts")],
            22,
            True,
        ),
        (
            [Card("8", "hearts"), Card("8", "hearts"), Card("A", "hearts")],
            17,
            True,
        ),
        (
            [Card("A", "hearts"), Card("10", "hearts"), Card("A", "hearts")],
            12,
            True,
        ),
        (
            [Card("7", "hearts"), Card("8", "hearts"), Card("A", "hearts")],
            16,
            True,
        ),
        # Soft hands (Ace counts as 11)
        ([Card("A", "hearts"), Card("2", "hearts")], 13, False),
        (
            [Card("A", "hearts"), Card("A", "hearts"), Card("2", "hearts")],
            14,
            False,
        ),
        ([Card("A", "hearts"), Card("8", "hearts")], 19, False),
        ([Card("A", "hearts"), Card("K", "hearts")], 21, False),
        ([Card("A", "hearts"), Card("9", "hearts")], 20, False),
        (
            [Card("A", "hearts"), Card("A", "hearts"), Card("9", "hearts")],
            21,
            False,
        ),
    ],
)
def test_evaluate_hand(cards, the_sum, is_hard):
    the_sum, is_hard = evaluate_hand(cards)
    assert evaluate_hand(cards) == (the_sum, is_hard)


# Test hands that are OK to hit
@pytest.mark.parametrize(
    "cards, dealer, correct_play",
    [
        # Hard 8
        (["5", "3"], "2", "hit"),
        (["5", "3"], "3", "hit"),
        (["5", "3"], "4", "hit"),
        (["5", "3"], "5", "hit"),
        (["5", "3"], "6", "hit"),
        (["5", "3"], "7", "hit"),
        (["5", "3"], "8", "hit"),
        (["5", "3"], "9", "hit"),
        (["5", "3"], "10", "hit"),
        (["5", "3"], "A", "hit"),
        # Hard 9
        (["5", "4"], "2", "hit"),
        (["5", "4"], "3", "double"),
        (["5", "4"], "4", "double"),
        (["5", "4"], "5", "double"),
        (["5", "4"], "6", "double"),
        (["5", "4"], "7", "hit"),
        (["5", "4"], "8", "hit"),
        (["5", "4"], "9", "hit"),
        (["5", "4"], "10", "hit"),
        (["5", "4"], "A", "hit"),
        (["2", "3", "4"], "2", "hit"),
        (["2", "3", "4"], "3", "hit"),
        (["2", "3", "4"], "4", "hit"),
        (["2", "3", "4"], "5", "hit"),
        (["2", "3", "4"], "6", "hit"),
        (["2", "3", "4"], "7", "hit"),
        (["2", "3", "4"], "8", "hit"),
        (["2", "3", "4"], "9", "hit"),
        (["2", "3", "4"], "10", "hit"),
        (["2", "3", "4"], "A", "hit"),
        # Hard 10
        (["6", "4"], "2", "double"),
        (["6", "4"], "3", "double"),
        (["6", "4"], "4", "double"),
        (["6", "4"], "5", "double"),
        (["6", "4"], "6", "double"),
        (["6", "4"], "7", "double"),
        (["6", "4"], "8", "double"),
        (["6", "4"], "9", "double"),
        (["6", "4"], "10", "hit"),
        (["6", "4"], "A", "hit"),
        (["2", "4", "4"], "2", "hit"),
        (["2", "4", "4"], "3", "hit"),
        (["2", "4", "4"], "4", "hit"),
        (["2", "4", "4"], "5", "hit"),
        (["2", "4", "4"], "6", "hit"),
        (["2", "4", "4"], "7", "hit"),
        (["2", "4", "4"], "8", "hit"),
        (["2", "4", "4"], "9", "hit"),
        (["2", "4", "4"], "10", "hit"),
        (["2", "4", "4"], "A", "hit"),
        # Hard 11
        (["7", "4"], "2", "double"),
        (["7", "4"], "3", "double"),
        (["7", "4"], "4", "double"),
        (["7", "4"], "5", "double"),
        (["7", "4"], "6", "double"),
        (["7", "4"], "7", "double"),
        (["7", "4"], "8", "double"),
        (["7", "4"], "9", "double"),
        (["7", "4"], "10", "hit"),
        (["7", "4"], "A", "hit"),
        (["2", "4", "5"], "2", "hit"),
        (["2", "4", "5"], "3", "hit"),
        (["2", "4", "5"], "4", "hit"),
        (["2", "4", "5"], "5", "hit"),
        (["2", "4", "5"], "6", "hit"),
        (["2", "4", "5"], "7", "hit"),
        (["2", "4", "5"], "8", "hit"),
        (["2", "4", "5"], "9", "hit"),
        (["2", "4", "5"], "10", "hit"),
        (["2", "4", "5"], "A", "hit"),
        # Hard 12
        (["7", "5"], "2", "hit"),
        (["7", "5"], "3", "hit"),
        (["7", "5"], "4", "stay"),
        (["7", "5"], "5", "stay"),
        (["7", "5"], "6", "stay"),
        (["7", "5"], "7", "hit"),
        (["7", "5"], "8", "hit"),
        (["7", "5"], "9", "hit"),
        (["7", "5"], "10", "hit"),
        (["7", "5"], "A", "hit"),
        # Hard 13
        (["8", "5"], "2", "stay"),
        (["8", "5"], "3", "stay"),
        (["8", "5"], "4", "stay"),
        (["8", "5"], "5", "stay"),
        (["8", "5"], "6", "stay"),
        (["8", "5"], "7", "hit"),
        (["8", "5"], "8", "hit"),
        (["8", "5"], "9", "hit"),
        (["8", "5"], "10", "hit"),
        (["8", "5"], "A", "hit"),
        # Hard 14
        (["9", "5"], "2", "stay"),
        (["9", "5"], "3", "stay"),
        (["9", "5"], "4", "stay"),
        (["9", "5"], "5", "stay"),
        (["9", "5"], "6", "stay"),
        (["9", "5"], "7", "hit"),
        (["9", "5"], "8", "hit"),
        (["9", "5"], "9", "hit"),
        (["9", "5"], "10", "surrender"),
        (["9", "3", "2"], "10", "hit"),
        (["9", "5"], "A", "hit"),
        # Hard 15
        (["9", "6"], "2", "stay"),
        (["9", "6"], "3", "stay"),
        (["9", "6"], "4", "stay"),
        (["9", "6"], "5", "stay"),
        (["9", "6"], "6", "stay"),
        (["9", "6"], "7", "hit"),
        (["9", "6"], "8", "hit"),
        (["9", "6"], "9", "hit"),
        (["9", "6"], "10", "surrender"),
        (["9", "4", "2"], "10", "hit"),
        (["9", "6"], "A", "hit"),
        # Hard 16
        (["J", "6"], "2", "stay"),
        (["J", "6"], "3", "stay"),
        (["J", "6"], "4", "stay"),
        (["J", "6"], "5", "stay"),
        (["J", "6"], "6", "stay"),
        (["J", "6"], "7", "hit"),
        (["J", "6"], "8", "hit"),
        (["J", "6"], "9", "surrender"),
        (["J", "6"], "10", "surrender"),
        (["J", "4", "2"], "9", "hit"),
        (["J", "4", "2"], "10", "stay"),  # No hitting here (known exception)
        (["J", "6"], "A", "hit"),
        # Hard 17
        (["J", "7"], "2", "stay"),
        (["J", "7"], "3", "stay"),
        (["J", "7"], "4", "stay"),
        (["J", "7"], "5", "stay"),
        (["J", "7"], "6", "stay"),
        (["J", "7"], "7", "stay"),
        (["J", "7"], "8", "stay"),
        (["J", "7"], "9", "stay"),
        (["J", "7"], "10", "stay"),
        (["J", "7"], "A", "stay"),
        # Hard 18
        (["J", "8"], "2", "stay"),
        (["J", "8"], "3", "stay"),
        (["J", "8"], "4", "stay"),
        (["J", "8"], "5", "stay"),
        (["J", "8"], "6", "stay"),
        (["J", "8"], "7", "stay"),
        (["J", "8"], "8", "stay"),
        (["J", "8"], "9", "stay"),
        (["J", "8"], "10", "stay"),
        (["J", "8"], "A", "stay"),
        # Hard 19
        (["J", "9"], "2", "stay"),
        (["J", "9"], "3", "stay"),
        (["J", "9"], "4", "stay"),
        (["J", "9"], "5", "stay"),
        (["J", "9"], "6", "stay"),
        (["J", "9"], "7", "stay"),
        (["J", "9"], "8", "stay"),
        (["J", "9"], "9", "stay"),
        (["J", "9"], "10", "stay"),
        (["J", "9"], "A", "stay"),
        # Hard 20
        (["J", "J"], "2", "stay"),
        (["5", "J", "5"], "3", "stay"),
        (["5", "J", "5"], "4", "stay"),
        (["5", "J", "5"], "5", "stay"),
        (["5", "J", "5"], "6", "stay"),
        (["5", "J", "5"], "7", "stay"),
        (["5", "J", "5"], "8", "stay"),
        (["5", "J", "5"], "9", "stay"),
        (["5", "J", "5"], "10", "stay"),
        (["J", "J"], "A", "stay"),
        # Hard 21
        (["J", "7", "4"], "2", "stay"),
        (["J", "7", "4"], "3", "stay"),
        (["J", "7", "4"], "4", "stay"),
        (["J", "7", "4"], "5", "stay"),
        (["J", "7", "4"], "6", "stay"),
        (["J", "7", "4"], "7", "stay"),
        (["J", "7", "4"], "8", "stay"),
        (["J", "7", "4"], "9", "stay"),
        (["J", "7", "4"], "10", "stay"),
        (["J", "7", "4"], "A", "stay"),
        # Soft 13
        (["A", "2"], "2", "hit"),
        (["A", "2"], "3", "hit"),
        (["A", "2"], "4", "hit"),
        (["A", "2"], "5", "double"),
        (["A", "2"], "6", "double"),
        (["A", "2"], "7", "hit"),
        (["A", "2"], "8", "hit"),
        (["A", "2"], "9", "hit"),
        (["A", "2"], "10", "hit"),
        (["A", "2"], "A", "hit"),
        # Soft 14
        (["A", "3"], "2", "hit"),
        (["A", "3"], "3", "hit"),
        (["A", "3"], "4", "hit"),
        (["A", "3"], "5", "double"),
        (["A", "3"], "6", "double"),
        (["A", "3"], "7", "hit"),
        (["A", "3"], "8", "hit"),
        (["A", "3"], "9", "hit"),
        (["A", "3"], "10", "hit"),
        (["A", "3"], "A", "hit"),
        # Soft 15
        (["A", "4"], "2", "hit"),
        (["A", "4"], "3", "hit"),
        (["A", "4"], "4", "double"),
        (["A", "4"], "5", "double"),
        (["A", "4"], "6", "double"),
        (["A", "4"], "7", "hit"),
        (["A", "4"], "8", "hit"),
        (["A", "4"], "9", "hit"),
        (["A", "4"], "10", "hit"),
        (["A", "4"], "A", "hit"),
        # Soft 16
        (["A", "5"], "2", "hit"),
        (["A", "5"], "3", "hit"),
        (["A", "5"], "4", "double"),
        (["A", "5"], "5", "double"),
        (["A", "5"], "6", "double"),
        (["A", "5"], "7", "hit"),
        (["A", "5"], "8", "hit"),
        (["A", "5"], "9", "hit"),
        (["A", "5"], "10", "hit"),
        (["A", "5"], "A", "hit"),
        # Soft 17
        (["A", "6"], "2", "hit"),
        (["A", "6"], "3", "double"),
        (["A", "6"], "4", "double"),
        (["A", "6"], "5", "double"),
        (["A", "6"], "6", "double"),
        (["A", "6"], "7", "hit"),
        (["A", "6"], "8", "hit"),
        (["A", "6"], "9", "hit"),
        (["A", "6"], "10", "hit"),
        (["A", "6"], "A", "hit"),
        # Soft 18
        (["A", "7"], "2", "stay"),
        (["A", "7"], "3", "double"),
        (["A", "7"], "4", "double"),
        (["A", "7"], "5", "double"),
        (["A", "7"], "6", "double"),
        (["A", "7"], "7", "stay"),
        (["A", "7"], "8", "stay"),
        (["A", "7"], "9", "hit"),
        (["A", "7"], "10", "hit"),
        (["A", "7"], "A", "hit"),
        # Soft 19
        (["A", "8"], "2", "stay"),
        (["A", "8"], "3", "stay"),
        (["A", "8"], "4", "stay"),
        (["A", "8"], "5", "stay"),
        (["A", "8"], "6", "stay"),
        (["A", "8"], "7", "stay"),
        (["A", "8"], "8", "stay"),
        (["A", "8"], "9", "stay"),
        (["A", "8"], "10", "stay"),
        (["A", "8"], "A", "stay"),
        # Soft 20
        (["A", "9"], "2", "stay"),
        (["A", "9"], "3", "stay"),
        (["A", "9"], "4", "stay"),
        (["A", "9"], "5", "stay"),
        (["A", "9"], "6", "stay"),
        (["A", "9"], "7", "stay"),
        (["A", "9"], "8", "stay"),
        (["A", "9"], "9", "stay"),
        (["A", "9"], "10", "stay"),
        (["A", "9"], "A", "stay"),
        # 2, 2
        (["2", "2"], "2", "split"),
        (["2", "2"], "3", "split"),
        (["2", "2"], "4", "split"),
        (["2", "2"], "5", "split"),
        (["2", "2"], "6", "split"),
        (["2", "2"], "7", "split"),
        (["2", "2"], "8", "hit"),
        (["2", "2"], "9", "hit"),
        (["2", "2"], "10", "hit"),
        (["2", "2"], "A", "hit"),
        # 3, 3
        (["3", "3"], "2", "split"),
        (["3", "3"], "3", "split"),
        (["3", "3"], "4", "split"),
        (["3", "3"], "5", "split"),
        (["3", "3"], "6", "split"),
        (["3", "3"], "7", "split"),
        (["3", "3"], "8", "hit"),
        (["3", "3"], "9", "hit"),
        (["3", "3"], "10", "hit"),
        (["3", "3"], "A", "hit"),
        # 4, 4
        (["4", "4"], "2", "hit"),
        (["4", "4"], "3", "hit"),
        (["4", "4"], "4", "hit"),
        (["4", "4"], "5", "split"),
        (["4", "4"], "6", "split"),
        (["4", "4"], "7", "hit"),
        (["4", "4"], "8", "hit"),
        (["4", "4"], "9", "hit"),
        (["4", "4"], "10", "hit"),
        (["4", "4"], "A", "hit"),
        # 5, 5
        (["5", "5"], "2", "double"),
        (["5", "5"], "3", "double"),
        (["5", "5"], "4", "double"),
        (["5", "5"], "5", "double"),
        (["5", "5"], "6", "double"),
        (["5", "5"], "7", "double"),
        (["5", "5"], "8", "double"),
        (["5", "5"], "9", "double"),
        (["5", "5"], "10", "hit"),
        (["5", "5"], "A", "hit"),
        # 6, 6
        (["6", "6"], "2", "split"),
        (["6", "6"], "3", "split"),
        (["6", "6"], "4", "split"),
        (["6", "6"], "5", "split"),
        (["6", "6"], "6", "split"),
        (["6", "6"], "7", "hit"),
        (["6", "6"], "8", "hit"),
        (["6", "6"], "9", "hit"),
        (["6", "6"], "10", "hit"),
        (["6", "6"], "A", "hit"),
        # 7, 7
        (["7", "7"], "2", "split"),
        (["7", "7"], "3", "split"),
        (["7", "7"], "4", "split"),
        (["7", "7"], "5", "split"),
        (["7", "7"], "6", "split"),
        (["7", "7"], "7", "split"),
        (["7", "7"], "8", "hit"),
        (["7", "7"], "9", "hit"),
        (["7", "7"], "10", "hit"),  # No surrender because of 7-7-7 side bet
        (["7", "7"], "A", "hit"),
        # 8, 8
        (["8", "8"], "2", "split"),
        (["8", "8"], "3", "split"),
        (["8", "8"], "4", "split"),
        (["8", "8"], "5", "split"),
        (["8", "8"], "6", "split"),
        (["8", "8"], "7", "split"),
        (["8", "8"], "8", "split"),
        (["8", "8"], "9", "split"),
        (["8", "8"], "10", "surrender"),
        (["8", "8"], "A", "hit"),
        # 9, 9
        (["9", "9"], "2", "split"),
        (["9", "9"], "3", "split"),
        (["9", "9"], "4", "split"),
        (["9", "9"], "5", "split"),
        (["9", "9"], "6", "split"),
        (["9", "9"], "7", "stay"),
        (["9", "9"], "8", "split"),
        (["9", "9"], "9", "split"),
        (["9", "9"], "10", "stay"),
        (["9", "9"], "A", "stay"),
        # 10, 10
        (["J", "J"], "2", "stay"),
        (["J", "J"], "3", "stay"),
        (["J", "J"], "4", "stay"),
        (["J", "J"], "5", "stay"),
        (["J", "J"], "6", "stay"),
        (["J", "J"], "7", "stay"),
        (["J", "J"], "8", "stay"),
        (["J", "J"], "9", "stay"),
        (["J", "J"], "10", "stay"),
        (["J", "J"], "A", "stay"),
        # A, A
        (["A", "A"], "2", "split"),
        (["A", "A"], "3", "split"),
        (["A", "A"], "4", "split"),
        (["A", "A"], "5", "split"),
        (["A", "A"], "6", "split"),
        (["A", "A"], "7", "split"),
        (["A", "A"], "8", "split"),
        (["A", "A"], "9", "split"),
        (["A", "A"], "10", "split"),
        (["A", "A"], "A", "hit"),
    ],
)
def test_get_correct_play(cards, dealer, correct_play):
    rules = get_rules("Helsinki")
    hand = Hand(rules)
    for label in cards:
        hand.cards.append(Card(label, "clubs"))
    hand.sum, hand.is_hard = evaluate_hand(hand.cards)
    n_hands = 1
    dealer_card = Card(dealer, "clubs")
    assert get_correct_play(hand, dealer_card, n_hands, rules) == correct_play


# Test hands that can not be doubled
@pytest.mark.parametrize(
    "cards, dealer, correct_play",
    [
        # Hard 9
        (["5", "4"], "3", "hit"),
        (["5", "4"], "6", "hit"),
        # Hard 10
        (["6", "4"], "2", "hit"),
        (["6", "4"], "9", "hit"),
        # Hard 11
        (["7", "4"], "2", "hit"),
        (["7", "4"], "9", "hit"),
        # Soft 13
        (["A", "2"], "5", "hit"),
        (["A", "2"], "6", "hit"),
        # Soft 14
        (["A", "3"], "5", "hit"),
        (["A", "3"], "6", "hit"),
        # Soft 15
        (["A", "4"], "4", "hit"),
        (["A", "4"], "6", "hit"),
        # Soft 16
        (["A", "5"], "4", "hit"),
        (["A", "5"], "6", "hit"),
        # Soft 17
        (["A", "6"], "3", "hit"),
        (["A", "6"], "6", "hit"),
        # Soft 18
        (["A", "7"], "3", "stay"),
        (["A", "7"], "6", "stay"),
    ],
)
def test_get_correct_play_no_double(cards, dealer, correct_play):
    rules = get_rules("Helsinki")
    hand = Hand(rules)
    for label in cards:
        hand.cards.append(Card(label, "clubs"))
    hand.sum, hand.is_hard = evaluate_hand(hand.cards)
    n_hands = 1
    hand.is_hittable = False
    dealer_card = Card(dealer, "hearts")
    assert get_correct_play(hand, dealer_card, n_hands, rules) == correct_play


@pytest.mark.parametrize(
    "cards, dealer, correct_play, n_hands",
    [
        (["2", "2"], "2", "hit", 3),
        (["2", "2"], "3", "hit", 3),
        (["2", "2"], "4", "split", 3),
        (["2", "2"], "4", "hit", 4),
        (["3", "3"], "2", "hit", 3),
        (["3", "3"], "3", "hit", 3),
        (["2", "2"], "4", "split", 3),
        (["2", "2"], "4", "hit", 4),
        (["6", "6"], "2", "hit", 3),
    ],
)
def test_get_correct_play_no_das(cards, dealer, correct_play, n_hands):
    rules = get_rules("Helsinki")
    rules.double_after_split = False
    hand = Hand(rules)
    for label in cards:
        hand.cards.append(Card(label, "clubs"))
    hand.sum, hand.is_hard = evaluate_hand(hand.cards)
    hand.is_hittable = False
    dealer_card = Card(dealer, "hearts")
    assert get_correct_play(hand, dealer_card, n_hands, rules) == correct_play
