import pandas as pd

# Initial setup and pruning of dictionary:
print('Loading English dictionary...')

words = []
word_length = 5
dict_file = 'scrabble-dict.txt'
all_letters = {x: 0 for x in list('abcdefghijklmnopqrstuvwxyz')}

valid_letters = []

with open('dictionaries\\' + dict_file, 'r') as fo:
    for line in fo.read().splitlines():
        line = line.lower()
        if len(line) == word_length:
            if all(letter in all_letters.keys() for letter in line):
                words.append(line.lower())


def rank_letters(letters):
    """
    Given a list of letters that may appear in the word, rank them according to the
    frequency in which they appear in the possible remaining words.

    :param letters: list of 1-character strings
    :return:
        pandas.Series, where values indicate the letter's frequency in the start,
        middle, and end of the words in our list of possibilities. We apply a bias
        multiplier to words with fewer repeating characters to ensure we get the most
        information we can out of each guess. This does make it more difficult to win
        puzzles with repeating letters, like "STATE", but increases the chance that
        we solve most puzzles within the stage constraint given.
    """
    ends = {letter: 0 for letter in letters}
    starts = {letter: 0 for letter in letters}
    middles = {letter: 0 for letter in letters}

    for word in words:
        if not all(letter in letters for letter in word):
            # This is an invalid word, like a contraction
            continue
        starts[word[0]] += 1
        ends[word[-1]] += 1
        for let in word[1:-1]:
            middles[let] += 1

    s = pd.Series(starts, name='word_start')
    e = pd.Series(ends, name='word_end')
    m = pd.Series(middles, name='middle_letters')

    df = pd.concat([s, e, m], axis=1)
    df /= df.sum()  # common size columns
    imp = df.sum(axis=1)
    imp.sort_values(ascending=False).plot.bar(title='Letter Ranking')

    return imp


def remove_invalid_words(word_list):
    for word in word_list[:]:
        for position, position_letters in grid.items():
            if word[position] not in position_letters:
                word_list.remove(word)
                break
    for word in word_list[:]:
        for required in valid_letters:
            if required not in word:
                word_list.remove(word)
                break
    return word_list


def rank_words(letter_set, word_set, rec=0):
    """
    Given a list of letters and words that we've guessed, return the most valuable next
    guess for the player to try.

    :param letter_set:
    :param word_set:
    :param rec:
    :return:
    """
    allowed = letter_set
    if SOLVE_MODE == 'EASY':
        allowed = list(set(''.join(possible_words)))
    else:
        for lets in grid.values():
            allowed.extend(lets)
    allowed = list(set(allowed))
    importance = rank_letters(allowed)

    valid_words = list(filter(
        lambda word: all(let in allowed for let in word) and word not in word_set,
        words
    ))

    if len(possible_words) == 1:
        valid_words = possible_words

    # We only want concrete guesses once we've eliminated most possibilities:
    if SOLVE_MODE == 'HARD' or len(words_tested) > 3:
        valid_words = [word for word in valid_words if word in possible_words]
        valid_words = remove_invalid_words(valid_words)
    else:
        # In EASY mode, we want to de-emphasize known letters in subsequent guesses
        point = 'break'
        for pos, values in grid.items():
            if len(values) == 1 and values[0] in importance:
                importance[values[0]] = 0
        for letter in letters_tested:
            if letter in importance:
                importance[letter] = 0

    word_rank = pd.Series({
        word: importance.loc[list(word)].sum() for word in valid_words
    }, name='letter_score', dtype='float32').to_frame()
    word_rank['unique_letters'] = word_rank.index.map(lambda x: len(set(x)))
    word_rank['word_score'] = word_rank['letter_score'] * word_rank['unique_letters']

    word_rank.sort_values('word_score', ascending=False, inplace=True)

    if not len(word_rank):
        if rec > 26:
            print('Recursion limit reached, this must be a bug.')
            exit(1)

        return rank_words(letter_set + valid_letters, word_set, rec + 1)

    return word_rank


def parse_response(response, guess_word):
    """
    Reads the input from the user about letter guesses.

        c: letter is in the correct position
        i: letter is included, but in the wrong position
        _: letter is not included

    :param response: string of length {word_length}
    :param guess_word: string, the word guessed in this turn
    :return: N/A, modifies globals:
        Removes letters that do not conform to what we learned from the guess response
        from the grid of possibilities, "grid"

        Adds all letters that will appear in the final word to "valid_letters", which
        is used to ensure we don't accidentally remove valid words when a letter repeats
    """
    global grid, valid_letters

    valid = list('ci_')
    if not len(response):
        return None

    if len(response) > word_length:
        err = f'`{response}` is invalid, must {word_length} of {valid}. Try again:'
        user_input = input(err)
        return parse_response(user_input, guess_word)

    if not all(letter in valid for letter in response):
        if all(letter in all_letters.keys() for letter in response):
            print(f'User override of suggested word: {response}\n')
            user_input = input(f'Now provide feedback response using {valid}: ')
            return parse_response(user_input, response)
        else:
            err = f'`{response}` is invalid, must {word_length} of {valid}. Try again:'
            user_input = input(err)
            return parse_response(user_input, guess_word)

    if all(i == 'c' for i in response):
        w1, w2 = ('were', 'words') if len(possible_words) > 1 else ('was', 'word')
        rem = ', '.join(list(map(str.upper, possible_words)))
        print(f'Congrats!'
              f'\nThere {w1} {len(possible_words)} {w2} remaining: {rem}')
        return True

    for i, char in enumerate(response):
        this_letter = guess_word[i]
        if char == 'c':
            # Remove all other possibilities
            grid[i] = [this_letter]
            valid_letters.append(this_letter)
        if char == 'i':
            # Remove only the current letter, since the position is wrong
            try:
                grid[i].remove(this_letter)
            except ValueError:
                pass

            valid_letters.append(this_letter)
        elif char == '_':
            # Remove letter from all positions
            for j in grid.keys():
                if this_letter not in valid_letters:
                    try:
                        grid[j].remove(this_letter)
                    except ValueError:
                        pass

    return guess_word


grid = {}
words_tested = []
letters_tested = []
possible_words = []


def run():
    global grid, words_tested, letters_tested, possible_words, valid_letters

    words_tested = []
    valid_letters = []
    letters_tested = []
    possible_words = words.copy()
    grid = {i: list(all_letters.copy().keys()) for i in range(word_length)}

    turns = 6
    for turn in range(turns):
        lset = [let for let in all_letters.keys() if let not in letters_tested]
        ranked = rank_words(lset, words_tested)

        guess, counter = None, 0

        while not guess:
            w = ranked.iloc[counter]
            this_word, score = w.name, w.word_score
            print(
                f'\nTurn {turn + 1}/{turns}: {this_word.upper()} '
                f'(word score: {score:0.2f}, remaining possible words: '
                f'{len(possible_words):,})'
            )
            guess = parse_response(user := input('Response:'), this_word)

            counter += 1

        if guess is True:
            break

        words_tested.append(guess)
        possible_words = remove_invalid_words(possible_words)
        if len(possible_words) < 10:
            print(f"\nOnly {len(possible_words)} words remain in the dictionary!"
                  f"\n\t{', '.join(list(map(str.upper, possible_words)))}")
        letters_tested.extend(list(guess))

    if guess is not True:
        print(
            f"Better luck next time. Possible words were:"
            f"{', '.join(list(map(str.upper, possible_words)))}"
        )


if __name__ == '__main__':

    print(f"""
WordleBot
====================================
This puzzle solver implements a search algorithm that systematically tests the most
common letters at the beginning, middle and end of English words consisting of {word_length} 
letter{'s' if word_length > 1 else ''}.

In each stage, use the proposed word in the puzzle. When you receive a response, enter
one character for each letter and press Enter. For example, if your first guess is "STARE"
the puzzle may reveal that the "A" is in the correct position, and the "E" is in the word
but in the wrong position. In this case, you'd enter: 

__c_i

If the algorithm proposes a word that is not in the Wordle dictionary, press Enter and
a new suggestion will be generated.

If you want to guess something other than what is suggested, simply type your guess
instead. The solver will then prompt for the response to your guess.

Good luck!
    """)  # noqa

    SOLVE_MODE = 'EASY'  # EASY or HARD; whether you must use all hints in guesses
    """
    Note:

    If the game is being played in "hard" mode, where any previous 
    hints must be included in subsequent guesses, words like "STATE" will be less likely
    to solve since your guesses can only permute one letter if starting from "STARE":

        Stage 1: stare (score: 5.8072429895401)
        Response >? ccc_c
        Stage 2: stale (score: 5.797328352928162)
        Response >? ccc_c
        Stage 3: stage (score: 5.335524678230286)
        Response >? ccc_c
        Stage 4: stake (score: 5.272907614707947)
        Response >? ccc_c
        Stage 5: stave (score: 5.085055232048035)
        Response >? ccc_c
        Stage 6: state (score: 4.729284286499023)
        Response >? ccccc
    """

    while True:
        run()
