import pytest

from blackjack_gui.lib import (
    Card,
    Hand,
    evaluate_hand,
    get_correct_play,
    Rules,
    Count,
)


@pytest.mark.parametrize(
    "cards, dealer, running_count, correct_play",
    [
        # Hard 16
        (["J", "6"], "10", 1, "stay"),
        (["J", "4", "2"], "10", 1, "stay"),
    ],
)
def test_get_correct_play(cards, dealer, running_count, correct_play):
    rules = Rules(
        game_type="h17",
        double_after_split=True,
        number_of_decks=4,
        surrender="no",
        peek=True,
        triple_seven=False,
        resplit_aces=True,
    )
    hand = Hand(rules)
    for label in cards:
        hand.cards.append(Card(label, "clubs"))
    hand.sum, hand.is_hard = evaluate_hand(hand.cards)
    n_hands = 1
    dealer_card = Card(dealer, "clubs")
    count = Count(running_count=running_count, true_count=0)
    assert (
        get_correct_play(
            hand, dealer_card, n_hands, rules, count, deviations=True
        )
        == correct_play
    )
