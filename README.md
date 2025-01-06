# blackjack-gui

[![Blackjack GUI CI](https://github.com/tukiains/blackjack-gui/actions/workflows/test.yml/badge.svg)](https://github.com/tukiains/blackjack-gui/actions/workflows/test.yml)
[![Downloads](https://pepy.tech/badge/blackjack-gui)](https://pepy.tech/project/blackjack-gui)

Single-player Blackjack including graphical and command line interfaces, written in Python. Can be used to simulate games
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
| `--count`        | `False` | If True, `ai` uses card counting. Only with `--cli` and `--ai`.                                                                                                                          |
| `--bet`          | 10      | Bet size (max 100).                                                                                                                                                                      |
| `--stack`        | 200     | Initial stack.                                                                                                                                                                           |
| `--n-games`      | 10      | Number of rounds to be played. Only with `--cli`.                                                                                                                                        |
| `--loglevel`     | `DEBUG` | Adjust amount of logging: DEBUG or INFO. Only with `--cli`.                                                                                                                              |
| `--cards`        |         | Determine the first player cards, e.g. `--cards=A,8,K`. Shuffles the shoe after every hand. Multiple options (one will be randomly selected) can be defined like this: `"A,7;9,9;10,2"`. |
| `--subset`       |         | Instead of `--cards`, practice with one of the subsets: `hard`, `soft`, `pairs`, `hard/soft`, or `soft/pairs`                                                                            |
| `--dealer-cards` |         | Determine the first dealer cards. Useful for testing.                                                                                                                                    |
| `--rules`        | `US`    | Rules to be used. Can be `Helsinki` or `US`. See the basic strategy charts below.                                                                                                        |

## Examples

Open the GUI version with Casino Helsinki Rules:

```
$ blackjack
```

With US rules:

```
$ blackjack --rules US
```

With the default settings, play 10 rounds of Blackjack with the command line interface:

```
$ blackjack --cli
```

Let the computer play perfect basic game and use card counting technique to bring down the house:

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

## Rules

Blackjack rules vary depending on the casino. In this application they follow the rules of Casino Helsinki,
explained in Finnish [here](http://www.rahapeliopas.fi/kasinopelit/blackjack/), i.e.:

- 6 decs
- Blackjack pays 3 to 2
- Dealer must stand on soft 17
- Any two cards can be doubled
- Max. 4 hands can be achieved by splitting
- Aces can be split but they receive only one extra card
- Doubling after splitting is allowed
- Dealer peek not in use
- Early surrender is allowed but not against Ace
- A 7-7-7 with the first three cards (not in a split game) pays 3 to 1 directly

See overview of the most common rule variations [here](rule-variations.md).

### Optimal basic strategy for Casino Helsinki

<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/chart-helsinki.png" alt="" width="400"/>
<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/helsinki-symbols.png" alt="" width="218"/>

- Note that 16 vs 10 with 3 or more cards = Stay
- 7,7 would be normally Surrender, but not in Helsinki because of the 7-7-7 rule

### Optimal basic strategy for a typical U.S. casino

The rules in the U.S. typically include:

- Dealer must hit on soft 17
- Dealer peek is in use
- Late surrender is not available
- Doubling and splitting rules same as above

<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/chart-usa.png" alt="" width="400"/>
<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/usa-symbols.png" alt="" width="320"/>

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

## Notes

- Deviations from the basic strategy are not yet implemented.
- Card images taken from [here](https://code.google.com/archive/p/vector-playing-cards/).

## Licence

MIT
