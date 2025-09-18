import json
import math


from .game import Game

class ComputerSolve:
    def __init__(self, verbose: bool=False):
        self.game = Game(name="Computer")
        self.verbose = verbose
        # Initialize basic attributes
        self.possible_words = set(self.game.legal_words)
        self.guess_history = []
        self.guess_number = 1
    
    def get_expected_value(self, guess, possible_words=None) -> float:
        """Calculate the expected information gain (entropy) for a guess"""
        if possible_words is None:
            possible_words = self.possible_words
            
        key_combinations = [i + j + k + l + m
                            for i in ["G", "Y", "B"]
                            for j in ["G", "Y", "B"]
                            for k in ["G", "Y", "B"]
                            for l in ["G", "Y", "B"]
                            for m in ["G", "Y", "B"]]

        keys = {}
        for key_combination in key_combinations:
            keys[key_combination] = 0

        n = len(possible_words)
        if n == 0:
            return 0

        for word in possible_words:
            keys[self.game.return_guess_key(guess, hidden_word=word)] += 1

        expected_value = 0

        for key_combination in key_combinations:
            px = keys[key_combination] / n
            if px != 0:
                expected_value += -1 * px * math.log2(px)
        
        return expected_value
    
    def filter_possible_words(self, guess, result_key):
        """Filter possible words based on guess result"""
        new_possible_words = set()
        
        for word in self.possible_words:
            if self.game.return_guess_key(guess, hidden_word=word) == result_key:
                new_possible_words.add(word)
        
        self.possible_words = new_possible_words
        return len(self.possible_words)
    
    def get_best_guess(self):
        """Get the best guess based on information theory"""
        if len(self.possible_words) == 0:
            return None
        elif len(self.possible_words) == 1:
            return list(self.possible_words)[0]
        elif len(self.possible_words) <= 2:
            # If only 1-2 words left, just guess one of them
            return list(self.possible_words)[0]
        
        # For first guess, use precomputed optimal guesses
        if self.guess_number == 1 and hasattr(self, 'first_guess_data') and self.first_guess_data:
            for word, _ in self.first_guess_data:
                if word in self.possible_words:
                    return word
            # If optimal first guess not in possible words, fall back to entropy calculation
            return self.first_guess_data[0][0]
        
        # For second guess, use precomputed optimal second guesses
        if (self.guess_number == 2 and hasattr(self, 'second_guess_data') and 
            hasattr(self, 'guess_history') and len(self.guess_history) > 0):
            
            first_guess, first_result = self.guess_history[0]
            if first_result in self.second_guess_data:
                precomputed_guess = self.second_guess_data[first_result]["best_guess"]
                if precomputed_guess and precomputed_guess in self.possible_words:
                    if self.verbose:
                        print(f"Using precomputed second guess: {precomputed_guess}")
                    return precomputed_guess
        
        # For subsequent guesses or when precomputed data not available, calculate entropy
        if self.verbose and self.guess_number <= 3:
            print(f"Calculating optimal guess for turn {self.guess_number}...")
        
        best_guess = None
        best_entropy = -1
        
        # Consider all possible words as potential guesses
        for guess in self.possible_words:
            entropy = self.get_expected_value(guess, self.possible_words)
            if entropy > best_entropy:
                best_entropy = entropy
                best_guess = guess
        
        return best_guess

    def get_top_guesses(self, mode="rw"):
        if "w" in mode:
            result = {}
            for word in self.game.legal_words:
                expected_value = self.get_expected_value(word, self.game.legal_words)
                result[word] = expected_value
                if self.verbose:
                    print(word, expected_value)
            with open("data\\first_guess.json", "w") as file:
                json.dump(result, file, indent=4)
                file.close()
        
        if "r" in mode:
            try:
                with open("data\\first_guess.json", "r") as file:
                    self.guess_data = json.load(file)
                self.guess_data = sorted(self.guess_data.items(), key=lambda item: item[1], reverse=True)
                if self.verbose:
                    print(self.guess_data[0:10])
            except:
                print("File does not exist.")
    
    def precompute_second_guesses(self, first_guess="TARES", max_results=50):
        """Pre-compute optimal second guesses for common first guess results"""
        if self.verbose:
            print(f"Pre-computing optimal second guesses for first guess: {first_guess}")
        
        # Get all possible results for the first guess
        first_guess_results = {}
        for word in self.game.legal_words:
            result = self.game.return_guess_key(first_guess, hidden_word=word)
            if result not in first_guess_results:
                first_guess_results[result] = []
            first_guess_results[result].append(word)
        
        # For each result pattern, find the optimal second guess
        second_guess_data = {}
        
        for result_pattern, possible_words in first_guess_results.items():
            if len(possible_words) <= 1:
                # If only one word possible, that's the answer
                second_guess_data[result_pattern] = {
                    "best_guess": possible_words[0] if possible_words else None,
                    "entropy": 0,
                    "possible_words_count": len(possible_words)
                }
                continue
            
            # Find the best second guess for this result pattern
            best_guess = None
            best_entropy = -1
            
            # Consider all possible words as potential second guesses
            for guess in self.game.legal_words:
                entropy = self.get_expected_value(guess, possible_words)
                if entropy > best_entropy:
                    best_entropy = entropy
                    best_guess = guess
            
            second_guess_data[result_pattern] = {
                "best_guess": best_guess,
                "entropy": best_entropy,
                "possible_words_count": len(possible_words)
            }
            
            if self.verbose and len(possible_words) > 10:  # Only show significant result patterns
                print(f"Result {result_pattern}: {len(possible_words)} words -> {best_guess} (entropy: {best_entropy:.3f})")
        
        # Save to file
        with open("data\\second_guess.json", "w") as file:
            json.dump(second_guess_data, file, indent=4)
            file.close()
        
        if self.verbose:
            print(f"Pre-computation complete! Saved {len(second_guess_data)} result patterns.")
        
        return second_guess_data


    def play(self):
        """Play a complete game using information theory to make optimal guesses"""
        # Ensure setup is done (load optimal first guesses)
        if not hasattr(self, 'first_guess_data'):
            self.setup()
        
        if self.verbose:
            print(f"\n🎯 Starting Wordle game!")
            print(f"Hidden word: {self.game.hidden_word}")
            print("="*50)
        
        while self.guess_number <= 6 and not self.game.game_over:
            # Get the best guess using information theory
            best_guess = self.get_best_guess()
            
            if best_guess is None:
                if self.verbose:
                    print("❌ No valid guesses remaining!")
                break
            
            # Make the guess
            guess_key = self.game.return_guess_key(best_guess)
            self.game.board.update(best_guess, guess_key)
            
            # Record the guess
            self.guess_history.append((best_guess, guess_key))
            
            if self.verbose:
                print(f"\nGuess {self.guess_number}: {best_guess}")
                print(f"Result: {guess_key}")
                print(f"Possible words remaining: {len(self.possible_words)}")
                self.game.board.draw()
            
            # Check if we won
            if best_guess == self.game.hidden_word:
                self.game.game_over = True
                if self.verbose:
                    print(f"\n🎉 SUCCESS! Guessed '{best_guess}' in {self.guess_number} tries!")
                return self.guess_number
            
            # Filter possible words based on the result
            remaining_count = self.filter_possible_words(best_guess, guess_key)
            
            if remaining_count == 0:
                if self.verbose:
                    print("❌ No possible words match the pattern!")
                break
            
            self.guess_number += 1
        
        # Game over - didn't solve in 6 tries
        if not self.game.game_over:
            if self.verbose:
                print(f"\n💀 FAILED! The word was '{self.game.hidden_word}'")
            return -1
        
        return self.guess_number

    def reset(self):
        """Reset the game state for a new round"""
        # Reset the game instance
        self.game = Game(name="Computer")
        
        # Reset solver state
        self.possible_words = set(self.game.legal_words)
        self.guess_history = []
        self.guess_number = 1
        
        if self.verbose:
            print(f"\n🔄 Game reset! New hidden word: {self.game.hidden_word}")
            print(f"Possible words: {len(self.possible_words)}")

    def setup(self):
        """Initialize the solver with optimal first guesses and prepare for solving"""
        # Load or generate optimal first guess data
        try:
            with open("data\\first_guess.json", "r") as file:
                self.first_guess_data = json.load(file)
                self.first_guess_data = sorted(self.first_guess_data.items(), key=lambda item: item[1], reverse=True)
                if self.verbose:
                    print("Loaded optimal first guesses from file")
        except FileNotFoundError:
            if self.verbose:
                print("First guess file not found, generating optimal first guesses...")
            self.get_top_guesses(mode="w")  # Generate and save first guesses
            with open("data\\first_guess.json", "r") as file:
                self.first_guess_data = json.load(file)
                self.first_guess_data = sorted(self.first_guess_data.items(), key=lambda item: item[1], reverse=True)
        
        # Load or generate optimal second guess data
        try:
            with open("data\\second_guess.json", "r") as file:
                self.second_guess_data = json.load(file)
                if self.verbose:
                    print("Loaded optimal second guesses from file")
        except FileNotFoundError:
            if self.verbose:
                print("Second guess file not found, generating optimal second guesses...")
            self.precompute_second_guesses(self.first_guess_data[0][0])  # Use best first guess
            with open("data\\second_guess.json", "r") as file:
                self.second_guess_data = json.load(file)
        
        # Reset possible words (starts with all legal words)
        self.possible_words = set(self.game.legal_words)
        
        # Reset game state
        self.guess_history = []
        self.guess_number = 1
        
        if self.verbose:
            print(f"Setup complete. {len(self.possible_words)} possible words remaining.")
            print(f"Best first guess: {self.first_guess_data[0][0]} (entropy: {self.first_guess_data[0][1]:.3f})")
            print(f"Pre-computed {len(self.second_guess_data)} second guess patterns.")


if __name__ == "__main__":
    import time
    
    # Create solver with verbose output
    my_solve = ComputerSolve(verbose=True)
    
    # Setup the solver (load optimal first guesses and second guesses)
    start_time = time.time()
    my_solve.setup()
    setup_time = time.time() - start_time
    
    print(f"\n⏱️  Setup completed in {setup_time:.2f} seconds")
    
    # Play a game
    start_time = time.time()
    result = my_solve.play()
    game_time = time.time() - start_time
    
    if result > 0:
        print(f"\n🏆 Game completed in {result} guesses! (Time: {game_time:.2f}s)")
    else:
        print(f"\n💀 Game failed after 6 guesses (Time: {game_time:.2f}s)")
    
    # Test performance with multiple games
    print("\n" + "="*60)
    print("TESTING MULTIPLE GAMES (Performance Test)")
    print("="*60)
    
    results = []
    total_time = 0
    
    for i in range(10):  # Play 10 games for better statistics
        start_time = time.time()
        my_solve.reset()
        result = my_solve.play()
        game_time = time.time() - start_time
        total_time += game_time
        
        results.append(result)
        print(f"Game {i+1}: {result} guesses ({game_time:.2f}s)")
    
    successful_games = [r for r in results if r > 0]
    if successful_games:
        avg_guesses = sum(successful_games) / len(successful_games)
        avg_time = total_time / len(results)
        print(f"\n📊 Performance Summary:")
        print(f"Games played: {len(results)}")
        print(f"Success rate: {len(successful_games)}/{len(results)} ({len(successful_games)/len(results)*100:.1f}%)")
        print(f"Average guesses (successful): {avg_guesses:.2f}")
        print(f"Average time per game: {avg_time:.2f}s")
        print(f"Total time: {total_time:.2f}s")
    else:
        print("\n❌ No successful games!")
