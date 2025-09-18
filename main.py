import argparse
from typing import Optional

from wordle import Game, ComputerSolve


def play_interactive() -> None:
    game = Game()
    game.play()


def run_solver(games: int = 1, verbose: bool = False, word: Optional[str] = None) -> None:
    solver = ComputerSolve(verbose=verbose)
    solver.setup()

    if word:
        solver.game.hidden_word = word.upper()
        result = solver.play()
        if result > 0:
            print(f"Solved '{word.upper()}' in {result} guesses!")
        else:
            print(f"Failed to solve '{word.upper()}' in 6 guesses.")
        return

    for i in range(games):
        if games > 1:
            print(f"\n--- Game {i + 1}/{games} ---")
        if i > 0:
            solver.reset()
        result = solver.play()
        if games > 1:
            print(f"Result: {result} guesses")

    # Single-game summary (non-verbose mode)
    if games == 1 and not word:
        if result > 0:
            print(f"Solved in {result} guesses!")
        else:
            print(f"Failed to solve in 6 guesses. The word was '{solver.game.hidden_word}'.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Wordle game with an optional computer solver",
    )
    parser.add_argument(
        "--solve",
        action="store_true",
        help="Run the computer solver instead of the interactive game",
    )
    parser.add_argument(
        "--games",
        type=int,
        default=1,
        help="Number of games to play with the solver (default: 1)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose solver output",
    )
    parser.add_argument(
        "--word",
        type=str,
        help="Solve a specific word (ignores --games)",
    )

    args = parser.parse_args()

    if args.solve:
        run_solver(games=args.games, verbose=args.verbose, word=args.word)
    else:
        play_interactive()


if __name__ == "__main__":
    main()
