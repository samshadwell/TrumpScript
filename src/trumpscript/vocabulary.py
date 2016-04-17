import re
import urllib.request

__author__ = 'github.com/samshadwell'

ENGLISH_URL = \
    "https://gist.githubusercontent.com/deekayen/4148741/raw/1e575985da4e9284e8cf8c53b7fe4ebca843df4a/1-1000.txt"
TRUMP_URL = "http://languagelog.ldc.upenn.edu/myl/TrumpAll.hist"
ADDITIONAL = ["hillary", "clinton",
              "martin", "o'malley",
              "bernie", "sanders",
              "jeb", "bush",
              "ben", "carson",
              "chris", "christie",
              "ted", "cruz",
              "carly", "fiorina",
              "jim", "gilmore",
              "mike", "huckabee",
              "john", "kasich",
              "rand", "paul",
              "marco", "rubio",
              "rick", "santorum",
              "donald", "trump",
              "barack", "obama",
              "joe", "biden",
              "ronald", "reagan",
              "vladimir", "putin",
              "sarah", "palin",
              "mitt","romney",

              # Common words we feel should be in there
              "i'll", "hello", "profitable", "earn", "that's", "policy", "policies", "you'll", "media", "spreads",
              "americans", "you're", "fired", "chinese", "global", "warming"]


def get_allowed_words(filename) -> None:
    """
    Constructs a set of all allowed words and returns it
    :param filename: the file to write the words to once they're compiled
    :return: None, writes to the file specified
    """

    # Regex for words that are composed only of letters
    word_regex = re.compile('^[A-Za-z]+\'?[A-Za-z]*$')

    # Get a set of all the words
    words = set([])
    add_words(words, ENGLISH_URL, get_only_word)
    add_words(words, TRUMP_URL, get_second_word)
    add_additional_words(words)

    # Now sort them alphabetically
    all_words = list(words)
    all_words.sort()
    all_words = filter(word_regex.match, all_words)

    # Write result to file
    my_file = open(filename, mode='wt', encoding='utf-8')
    my_file.write('ALLOWED = {')
    for word in all_words:
        my_file.write('"' + word + '",\n')
    my_file.write('}')
    my_file.close()


def add_words(word_set, url, line_function) -> None:
    """
    Add the words from the given url to the word set. Uses the line_function on each line to get the word from it
    :param url: The URL to read from
    :param word_set: the set of words to add to
    :param line_function: the function to apply to each line in the file to get its word
    :return: None, adds to word_set
    """

    # Make sure we've been passed good parameters
    assert isinstance(word_set, set)
    assert isinstance(url, str)
    assert hasattr(line_function, '__call__')

    # Open the URL, decode it as a string
    response = urllib.request.urlopen(url)
    data = response.read()
    text = data.decode('utf-8')

    # Process each line
    for line in text.split('\n'):
        word = line_function(line)
        # Only add words that are non-null
        if word is not None:
            word_set.add(word)


def get_only_word(line) -> str:
    """
    Given the line that consists of only one word, return that word in lowercase with no additional whitespace
    :param line: The string representation of the line
    :return: The lowercase, trimmed content of the given line
    """

    return line.strip().lower()


def get_second_word(line) -> str:
    """
    Given a line that has two words in it, return the second one. If there are not 2 words, returns None
    :param line: The string representation of a two-element line
    :return: The second word in the line
    """

    split = line.strip().split()
    if len(split) == 2:
        return split[1].lower()


def add_additional_words(words) -> None:
    """
    Adds a bunch of political people's names and other extra words from ADDITIONAL to the dictionary
    :param words: the set of words to add the politician names to
    :return: None, adds to the passed-in set
    """
    for candidate_word in ADDITIONAL:
        words.add(candidate_word.lower())


get_allowed_words("allowed_words.py")
