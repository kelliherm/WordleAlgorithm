import colorama

class Board:
    def __init__(self) -> None:
        colorama.init()
        
        self.board = [[] for i in range(6)]

        """
        self.board is format as an array of arrays. The first array consists
        of each possible guess and their corresponding key. The guess number
        is the index of the array inside of self.board + 1. The array that
        holds the guess and the key looks like ["GUESS", "KEY"]. The possible
        values for "KEY" are "G", "Y", and "B". An example of the guess "LIGHT"
        with the seond and third positions being correct with the final position
        being partially correct would look like ["LIGHT", "BGGBY"].
        """

        self.colors = {
            "G" : colorama.Fore.GREEN,
            "Y" : colorama.Fore.YELLOW,
            "B" : colorama.Fore.BLACK,
            "RESET" : colorama.Style.RESET_ALL,
        }
    
    def draw(self) -> None:
        for row_index in range(6):
            print(row_index + 1, end="  ")
            if self.board[row_index] != []:
                for char_index in range(5):
                    print(self.colors[self.board[row_index][1][char_index]],
                          self.board[row_index][0][char_index],
                          sep="",
                          end="",)
            print(self.colors["RESET"])
    
    def update(self, guess: str, key: str) -> None:
        for row_index in range(6):
            if self.board[row_index] == []:
                self.board[row_index] = [guess, key]
                break

    def reset(self):
        self.board = [[] for i in range(6)]
