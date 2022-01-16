# blackjack-gui
Single-player Blackjack with GUI and CLI interfaces. Can be used to simulate games (with simple card counting) 
and learn basic strategy.

## Installation
``` 
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install blackjack-gui
```
<img src="blackjack_gui/images/bj-shot.png" alt="blackjack-gui" width="600"/>

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

| Name         | Default | Description                                                                                  | 
|:-------------|:--------|:---------------------------------------------------------------------------------------------|
| `--stack`    | 1000    | Initial stack. Can be used with `--gui=True` too.                                              |
| `--bet`      | 1       | Bet size.                                                                                    |
| `--n_games`  | 10      | Number of rounds to be played.                                                               |
| `--ai`       | False   | If True, computer plays instead of you.                                                      |
| `--count`    | False   | If True, `ai` uses card counting.                                                            |
| `--loglevel` | DEBUG   | Adjust amount of logging: DEBUG or INFO.                                                     |
| `--cards`    |         | Simulate certain starting hand only. E.g. `--cards=A,8`. Shuffles the shoe after every hand. |


## Examples
Open GUI version:
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

## Notes
* Uses 6 decs and shuffling when 52 cards remaining in the shoe
* Insurance and even money not implemented
* Otherwise, rules follow: https://casinohelsinki.fi/en/games/blackjack-eng/
* Basic strategy according to [American casino guidebook](https://www.americancasinoguidebook.com/wp-content/uploads/2014/04/BJ-strategy-chart-for-web.pdf)
* Card images taken from [here](https://code.google.com/archive/p/vector-playing-cards/).

## Licence
MIT
