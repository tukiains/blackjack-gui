# blackjackpy
Single-player Blackjack with possibility to simulate games.

## Installation
``` 
$ git clone  https://github.com/tukiains/blackjackpy/
$ cd blackjackpy/
```

Blackjackpy GUI uses [Pillow](https://pillow.readthedocs.io/en/stable/). 
You might need to install it system-wide using, e.g.
```
$ sudo apt install python3-pil.imagetk
```
or using pip, e.g.
```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install pillow
```

## Usage

```
blackjack.py [OPTION...]
```

Options:

| Name         | Default | Description                                  | 
|:-------------|:--------|:---------------------------------------------|
| `--help`     |         | Show help and exit.                          |
| `--n_games`  | 10      | Number of rounds to be played.               |
| `--bet`      | 1       | Bet size.                                    |
| `--stack`    | 1000    | Initial stack.                               |
| `--ai`       | False   | If True, computer plays instead of you.      |
| `--count`    | False   | If True, computer player uses card counting. |
| `--loglevel` | DEBUG   | Adjust amount of logging: DEBUG or INFO.     |
| `--gui`      | True    | Play with GUI.                               |



## Examples
Open GUI version of blackjackpy:
```
$ ./blackjack.py
```

With the default settings, play 10 rounds of Blackjack without GUI:
```
$ ./blackjack.py --gui=False
```

Let the computer play perfect basic game and use card counting technique to bring down the house:
```
$ ./blackjack.py --n_games=100000 --ai=True --count=True --loglevel=INFO --gui=False
```

## Notes
* Insurance and even money not implemented
* Otherwise, rules follow: https://casinohelsinki.fi/en/games/blackjack-eng/


## Licence
MIT