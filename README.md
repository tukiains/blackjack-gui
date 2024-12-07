# blackjack-gui

[![Blackjack GUI CI](https://github.com/tukiains/blackjack-gui/actions/workflows/test.yml/badge.svg)](https://github.com/tukiains/blackjack-gui/actions/workflows/test.yml)
[![Downloads](https://pepy.tech/badge/blackjack-gui)](https://pepy.tech/project/blackjack-gui)

Single-player Blackjack including GUI and CLI interfaces, written in Python. Can be used to simulate games with or without card counting
and to practise basic strategy.

<img src="https://github.com/tukiains/blackjack-gui/blob/main/blackjack_gui/images/bj-shot.png?raw=true" alt="" width="600"/>

## Installation

`blackjack-gui` requires Python 3.9 or newer and uses [tkinter](https://en.wikipedia.org/wiki/Tkinter). Make sure it's installed in your system:

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

### GUI version

```
blackjack [OPTION...]
```

### CLI version

```
blackjack --gui=False [OPTION...]
```

### Options

| Name             | Default | CLI only | Description                                                                                 |
| :--------------- | :------ | :------- | :------------------------------------------------------------------------------------------ |
| `--stack`        | 1000    |          | Initial stack.                                                                              |
| `--bet`          | 1       |          | Initial bet size.                                                                           |
| `--n_games`      | 10      | x        | Number of rounds to be played.                                                              |
| `--ai`           | False   | x        | If True, computer plays instead of you.                                                     |
| `--count`        | False   | x        | If True, `ai` uses card counting.                                                           |
| `--loglevel`     | DEBUG   | x        | Adjust amount of logging: DEBUG or INFO.                                                    |
| `--cards`        |         |          | Determine the first player cards, e.g. `--cards=A,8,K`. Shuffles the shoe after every hand. |
| `--subset`       |         |          | Instead of `--cards`, practice with one of the subsets: `hard`, `soft`, or `pairs`.         |
| `--dealer_cards` |         |          | Determine the first dealer cards. Useful for testing.                                       |

## Examples

Open the GUI version:

```
$ blackjack
```

With the default settings, play 10 rounds of Blackjack without GUI:

```
$ blackjack --gui=False
```

Let the computer play perfect basic game and use card counting technique to bring down the house:

```
$ blackjack --n_games=100000 --ai=True --count=True --loglevel=INFO --gui=False
```

Simulate soft 19 starting hand only:

```
$ blackjack --n_games=10000 --ai=True --loglevel=INFO --gui=False --cards=A,8
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
- Surrender is allowed but not against Ace
- A 7-7-7 with the first three cards (not in a split game) pays 3 to 1 directly

### Optimal basic strategy

<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/chart.png" alt="" width="400"/>
<img src="https://raw.githubusercontent.com/tukiains/blackjack-gui/main/blackjack_gui/images/chart-symbols.png" alt="" width="258"/>

- Note that 16 vs 10 with 3 or more cards = Stay

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

- Card images taken from [here](https://code.google.com/archive/p/vector-playing-cards/).

## Licence

MIT
