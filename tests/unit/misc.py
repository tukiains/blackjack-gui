import pytest

from blackjack_gui.lib import (
    Card,
    evaluate_hand,
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
