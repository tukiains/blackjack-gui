# blackjack-gui
![](https://github.com/tukiains/blackjack-gui/workflows/tests/badge.svg)

Single-player Blackjack including GUI and CLI interfaces. Can be used to simulate games (with simple card counting) 
and learn basic strategy.

## Installation
``` 
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install blackjack-gui
```
<img src="blackjack_gui/images/bj-shot.png" alt="" width="600"/>

## Usage

### GUI version
```
blackjack
```

### CLI version
```
blackjack --gui=False [OPTION...]
```

Options:

| Name             | Default | Description                                                                             | 
|:-----------------|:--------|:----------------------------------------------------------------------------------------|
| `--stack`        | 1000    | Initial stack. Can be used with `--gui=True` too.                                       |
| `--bet`          | 1       | Bet size.                                                                               |
| `--n_games`      | 10      | Number of rounds to be played.                                                          |
| `--ai`           | False   | If True, computer plays instead of you.                                                 |
| `--count`        | False   | If True, `ai` uses card counting.                                                       |
| `--loglevel`     | DEBUG   | Adjust amount of logging: DEBUG or INFO.                                                |
| `--cards`        |         | Determine first player cards, e.g. `--cards=A,8,K`. Shuffles the shoe after every hand. |
| `--dealer_cards` |         | Determine first dealer cards. Useful for testing.                                       |


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

## Tests
Install `blackjack-gui` from GitHub and `pytest`:
```
$ git clone https://github.com/tukiains/blackjack-gui
$ cd blackjack-gui/
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install .
$ pip3 install pytest
```
Run unit and integration tests:
```
$ pytest-3 tests/unit.py
$ pytest-3 tests/integration.py
```

## Basic strategy chart
<img src="blackjack_gui/images/chart.png" alt="" width="400"/>
<img src="blackjack_gui/images/chart-symbols.png" alt="" width="258"/>

* Note that 16 with 3 or more cards = Stay

## Notes
* Uses 6 decs and shuffles after 5 decs.
* Insurance and even money not implemented.
* Otherwise, rules follow: https://casinohelsinki.fi/en/games/blackjack-eng/.
* Card images taken from [here](https://code.google.com/archive/p/vector-playing-cards/).

## Licence
MIT
