# WordleBot

A simple search-based puzzle solver for [Wordle](https://www.powerlanguage.co.uk/wordle/), built in Python.

Inspired by and tested using [@adjusa's](https://github.com/ajusa) clone, [Hyperwordle](https://arhamjain.com/hyperwordle/).

By default, this uses a small dictionary (~2,500 5-letter words), and can't find solutions outside the given list. You 
can optionally switch to the complete English dictionary provided by [@dwyl](https://github.com/dwyl/english-words) 
(~16k 5-letter words), which is more comprehensive than the dictionary used by official Wordle and related puzzles. This 
means that while your chance of having the answer in the dictionary are high, you may be presented with many guesses that
are not in Wordle's dictionary. In the event that you are suggested a word that is not accepted by Wordle, press **[Enter]**
and a new word will be proposed.

To switch between dictionaries, change the `dict_file` variable in [run.py](run.py) to `large-dict.txt`.

## Requirements

* Python 3.5+
* [pandas](https://github.com/pandas-dev/pandas) (1.0 or later)
