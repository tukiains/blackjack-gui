import subprocess

import pytest

prefix = "blackjack --n_games=1 --gui=False --ai=True --loglevel=WARNING --stack=10"


@pytest.mark.parametrize(
    "player, dealer, stack",
    [
        ("A,K", "10,Q", 11.5),
        ("A,K", "A,K", 10),
        ("K,J", "10,Q", 10),
        ("K,K", "A,K", 9),
        ("K,K", "9,10", 11),
        ("9,Q", "8,10", 11),
        ("8,Q", "7,10", 11),
        ("7,Q", "6,10,K", 11),
        ("6,Q", "2,10,9", 9),
        ("6,Q", "3,10,4", 9),
        ("6,Q", "4,10,3", 9),
        ("6,Q", "5,10,K", 11),
        ("6,Q", "6,10,4", 9),
    ],
)
def test_stay(player, dealer, stack):
    assert call(player, dealer) == stack


@pytest.mark.parametrize(
    "player, dealer, stack",
    [
        ("10,6", "9,Q", 9.5),
        ("10,6", "10,2", 9.5),
        ("10,5", "10,2", 9.5),
    ],
)
def test_surrender(player, dealer, stack):
    assert call(player, dealer) == stack


@pytest.mark.parametrize(
    "player, dealer, stack",
    [
        ("9,2,J", "10,Q", 11),
        ("9,2,J", "10,A", 9),
        ("8,2,8", "2,10,6", 10),
        ("8,2,8", "2,10,5", 12),
        ("5,5,K", "9,10", 12),
        ("A,7,2", "6,10,2", 12),
        ("A,6,10", "3,10,7", 8),
        ("A,2,10", "5,10,2", 8),
        ("A,2,7", "6,10,2", 12),
    ],
)
def test_double(player, dealer, stack):
    assert call(player, dealer) == stack


@pytest.mark.parametrize(
    "player, dealer, stack",
    [
        ("A,A,J,J", "10,9", 12),
        ("A,A,5,2", "5,10,J", 12),
        ("A,A,A,A,A,A,A,A", "10,7", 6),
        ("A,A,A,A,K,K,K,K", "10,K", 14),
        ("8,8,3,3,J,K", "10,K", 9.5),
        ("A,A,K,K", "A,K", 9),
    ],
)
def test_split(player, dealer, stack):
    assert call(player, dealer) == stack


def test_insurance():
    player = "K,J"
    dealer = "A,K"
    assert call(player, dealer) == 9


def call(player: str, dealer: str) -> float:
    result = subprocess.check_output(
        f"{prefix} " f"--cards={player} " f"--dealer_cards={dealer}", shell=True
    )
    return float(result)
