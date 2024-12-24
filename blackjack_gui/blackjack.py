import argparse
import logging

from blackjack_gui import cli, gui


def main():
    parser = argparse.ArgumentParser(
        description="Blackjack", epilog="Play responsibly!"
    )
    parser.add_argument("--cli", action="store_true", help="Open CLI version.")
    parser.add_argument("--ai", action="store_true", help="Computer play.")
    parser.add_argument(
        "--count",
        action="store_true",
        help="Count cards. Default is False. Can be used with --ai.",
    )
    parser.add_argument(
        "--bet", type=int, default=1, help="Bet size (1-10). Default is 1."
    )
    parser.add_argument(
        "--stack", type=int, default=1000, help="Stack size. Default is 1000."
    )
    parser.add_argument(
        "--n-games",
        type=int,
        default=10,
        help="Number of rounds to be played. Default is 10.",
    )
    parser.add_argument(
        "--loglevel",
        type=str,
        default="DEBUG",
        help="Log level. Can be DEBUG or INFO. Default is DEBUG.",
    )
    parser.add_argument(
        "--cards",
        type=lambda s: s.split(","),
        default=None,
        help="Determine first player cards. E.g. --cards=A,7 to simulate soft 18.",
    )
    parser.add_argument(
        "--dealer-cards",
        type=lambda s: s.split(","),
        default=None,
        help="Determine first dealer cards. Useful for tests.",
    )
    parser.add_argument(
        "--subset",
        type=str,
        choices=["hard", "soft", "pairs", "hard/soft", "soft/pairs"],
        help="Subset of hands to be played. Default is all.",
        default=None,
    )

    args = parser.parse_args()

    if args.cli:
        logging.basicConfig(level=args.loglevel, format="%(message)s")
        cli.play(args)
    else:
        logging.basicConfig(level="WARNING")
        gui.main(args)


if __name__ == "__main__":
    main()
