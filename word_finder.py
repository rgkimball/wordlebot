

# Initial setup and pruning of dictionary:
print('Loading English dictionary...')

words = []
word_length = 5
dict_file = 'scrabble-dict.txt'
all_letters = {x: 0 for x in list('abcdefghijklmnopqrstuvwxyz')}

with open(dict_file, 'r') as fo:  # noqa
    for line in fo.read().splitlines():
        line = line.lower()
        if len(line) == word_length:
            if all(letter in all_letters.keys() for letter in line):
                words.append(line.lower())


def run():
    stype, letters = None, []
    while stype not in ('a', 'c'):
        stype = input('Search type? [a=includes any, c=contiguous] >')
    while not len(letters):
        letters = input('Which letter(s)? >')

    if stype == 'a':
        candidates = sorted(
            [w for w in words if any(letter in w for letter in letters)],
            key=lambda w: 1 / sum(letter in w for letter in letters),
        )
    elif stype == 'c':
        candidates = sorted([w for w in words if letters in w])
    print(f'Found {len(candidates):,} words of {len(words):,} in dictionary.')
    print(', '.join(candidates[:20]))


if __name__ == '__main__':

    while True:
        run()
