# blackjack-gui

<img src="blackjack_gui/images/blackjack-gui-logo.png" alt="Blacjack GUI" width="75px"/>

[![Blackjack GUI CI](https://github.com/tukiains/blackjack-gui/actions/workflows/test.yml/badge.svg)](https://github.com/tukiains/blackjack-gui/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/blackjack-gui.svg)](https://badge.fury.io/py/blackjack-gui)

Single-player blackjack including graphical and command line interfaces, written in Python. Can be used to simulate games
and to practise basic strategy and card counting.

<img src="https://github.com/tukiains/blackjack-gui/blob/main/blackjack_gui/images/bj-shot.png?raw=true" alt="" width="600"/>

## Installation

`blackjack-gui` requires Python 3.10 or newer and uses [tkinter](https://en.wikipedia.org/wiki/Tkinter). Make sure it's installed in your system:

```
$ sudo apt install python3-tk
```

or similar (otherwise, you'll see `ModuleNotFoundError: No module named 'tkinter'`).

Then:

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install blackjack-gui
```

## Usage

```
blackjack [-h] [--cli] [--ai] [--count] [--bet BET] [--stack STACK]
    [--n-games N_GAMES] [--loglevel LOGLEVEL] [--cards CARDS]
    [--dealer-cards DEALER_CARDS] [--subset {hard,soft,pairs,hard/soft,soft/pairs}]
    [--rules {US,Helsinki}]

```

### Options

| Name             | Default | Description                                                                                                                                                                              |
| :--------------- | :------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--cli`          | `False` | Use command line version.                                                                                                                                                                |
| `--ai`           | `False` | If True, computer plays instead of you. Only with `--cli`.                                                                                                                               |
| `--count`        | `False` | If True, `ai` uses card counting. Only with `--cli` and `--ai`. The bet spread: 1 unit (true count<1), 2 units (TC=1), 3 units (TC=3), 4 units (TC=4), 8 units (TC=5), 12 units (TC>=6). |
| `--bet`          | 10      | Bet size (max 100).                                                                                                                                                                      |
| `--stack`        | 200     | Initial stack.                                                                                                                                                                           |
| `--n-games`      | 10      | Number of rounds to be played. Only with `--cli`.                                                                                                                                        |
| `--loglevel`     | `DEBUG` | Adjust amount of logging: DEBUG or INFO. Only with `--cli`.                                                                                                                              |
| `--cards`        |         | Determine the first player cards, e.g. `--cards=A,8,K`. Shuffles the shoe after every hand. Multiple options (one will be randomly selected) can be defined like this: `"A,7;9,9;10,2"`. |
| `--subset`       |         | Instead of `--cards`, practice with one of the subsets: `hard`, `soft`, `pairs`, `hard/soft`, or `soft/pairs`                                                                            |
| `--dealer-cards` |         | Determine the first dealer cards. Useful for testing.                                                                                                                                    |
| `--rules`        | `US`    | Rules to be used. Can be `Helsinki` or `US`. See the basic strategy charts below.                                                                                                        |

## Examples

Start the game:

```
$ blackjack
```

With the default settings, play 10 rounds of blackjack using the command line interface:

```
$ blackjack --cli
```

Let the computer play blackjack using perfect basic strategy and card counting to beat the house.

```
$ blackjack --cli --ai --count --n-games=100000 --loglevel=INFO
```

Simulate soft 19 starting hand only:

```
$ blackjack --cli --ai --n-games=10000 --loglevel=INFO --cards=A,8
```

Practise to play "hard" starting hands:

```
$ blackjack --subset hard
```

## Optimal basic strategy

Blackjack rules vary depending on the casino, and the optimal basic strategy depends on the rules.
See overview of the most common rule variations [here](rule-variations.md).

### Optimal basic strategy for Casino Helsinki

The rules at Casino Helsinki:

- 6 decks
- Blackjack pays 3 to 2
- Dealer must stand on soft 17
- Dealer peek is not in use
- Any two cards can be doubled
- Max. 4 hands can be achieved by splitting
- Doubling after splitting is allowed
- Aces can be split but they receive only one extra card
- Resplit of aces is allowed
- Early surrender is allowed but not against Ace
- A 7-7-7 with the first three cards (not in a split game) pays 3 to 1 directly

The dealers at Casino Helsinki use shuffling machines.

<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/chart-helsinki.png" alt="" width="400"/>
<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/helsinki-symbols.png" alt="" width="218"/>

- Note that 16 vs 10 with 3 or more cards = Stay
- 7,7 would be normally Surrender, but not in Helsinki because of the 7-7-7 rule

### Optimal basic strategy for a typical U.S. casino

The rules in the U.S. typically include:

- Dealer must hit on soft 17
- Dealer peek is in use
- Late surrender is not available
- Re-splitting of Aces (RSA) is not available
- Doubling and splitting rules otherwise same as above
- 7-7-7 rule is not available

<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/chart-usa.png" alt="" width="400"/>
<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/usa-symbols.png" alt="" width="320"/>

### Rule-based deviations

There are a few deviations from the basic strategy, which depend on the
specific combination of the table rules. For a detailed, rule-specific strategy,
consult the [Wizard of Odds Blackjack Strategy Calculator](https://wizardofodds.com/games/blackjack/strategy/calculator/) to identify the optimal basic strategy for each game configuration.

## Count-based deviations

Card counting affects the basic strategy. The following deviations are implemented
in `blackjack-gui` (I will slowly add more). Use "Coach mode" with "Include deviations" to verify your play!

| Your Hand | Dealer's Upcard | Basic strategy        | Deviation | Index |
| :-------- | :-------------- | :-------------------- | :-------- | :---- |
| 2-10      | A               | Don't take insurance  | Take      | +3    |
| A         | A               | Don't take even money | Take      | +3    |
| 16        | 10              | Hit                   | Stand     | 0+    |
| 12        | 2               | Hit                   | Stand     | +3    |
| 12        | 3               | Hit                   | Stand     | +2    |
| 12        | 4               | Stand                 | Hit       | 0-    |
| A,4       | 4               | Double                | Hit       | 0-    |

Where 0- means any negative running count, 0+ means any positive running count, and +X means true count of X or greater.

## Development

Install `blackjack-gui` with dev-dependencies from GitHub:

```sh
git clone https://github.com/tukiains/blackjack-gui
cd blackjack-gui/
python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install .[dev,test]
pre-commit install
```

Run unit and integration tests:

```sh
pytest tests/unit.py
pytest tests/integration.py
```

Run `pre-commit` checks:

```
pre-commit run --all
```

## Credits

- Card images sourced from [Google's Vector Playing Cards](https://code.google.com/archive/p/vector-playing-cards/).
- Basic strategy follows [Wizard of Odds Blackjack Strategy Calculator](https://wizardofodds.com/games/blackjack/strategy/calculator/).
- Deviations are based on [A1 Blackjack](https://www.youtube.com/channel/UCk52qcPJUckYK4fY2I1qvNw/videos),
  an excellent source of free and useful blackjack content.
- Inspiration drawn from [Blackjack Apprenticeship](https://www.blackjackapprenticeship.com/) the premier resource for serious card counters.

## Licence

MIT
