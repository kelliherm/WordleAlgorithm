import collections
import json
import os
import platform
import random

import wordle.board as board

class Game:
    def __init__(self, name: str="Player") -> None:
        self.board = board.Board()
        self.game_over = False
        self.guess_number = 1
        self.name = name

        with open("data\\words.json", "r") as f:
            self.legal_words = json.load(f)
            f.close()
        
        # TODO Figure out python filestructure system for loading words/folder usage

        self.hidden_word = random.choice(self.legal_words)

    def display(self, message="") -> None:
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        if message != "":
            print(message)
        self.board.draw()

    def get_user_guess(self) -> str:
        guess = input(f"What is {self.name}'s guess?  ").strip().upper()
        if guess not in self.legal_words:
            print("Not a valid guess.")
            return self.get_user_guess()
        return guess

        # TODO Add error handling to user guess system, check value word, etc.

    def play(self) -> None:
        while not self.game_over:
            self.display(message=f"It is guess number {self.guess_number}.")
            guess = self.get_user_guess()

            guess_key = self.return_guess_key(guess)

            self.board.update(guess, guess_key)

            if guess == self.hidden_word:
                self.game_over = True
                self.display(message=f"{self.name} has won the game. It took {self.guess_number} to guess the hidden word.")

            self.guess_number += 1
            if self.guess_number > 6:
                self.game_over = True
                self.display(message=f"{self.name} has lost the game. The hidden word was {self.hidden_word}.")
        
        answer = input("Would you like to play again? [Y/n]  ").lower()
        if answer in ("yes", "y"):
            self.reset()
        else:
            None

    def reset(self) -> None:
        self.board = board.Board()
        self.game_over = False
        self.guess_number = 1
        self.hidden_word = random.choice(self.legal_words)
        self.play()

    def return_guess_key(self, guess: str, hidden_word: str=None) -> str:
        if hidden_word == None:
            hidden = self.hidden_word
        else:
            hidden = hidden_word
        
        guess = list(guess)
        hidden = list(hidden)
        
        result = ["B" for char in guess]
        
        for i in range(5):
            if guess[i] == hidden[i]:
                result[i] = "G"
                guess[i] = None
                hidden[i] = None
        
        unmatched_counts = collections.Counter(filter(None, hidden))

        for i in range(5):
            if guess[i] is not None and unmatched_counts[guess[i]] > 0:
                result[i] = "Y"
                unmatched_counts[guess[i]] -= 1

        return "".join(result)

if __name__ == "__main__":
    my_game = Game()
    my_game.play()
