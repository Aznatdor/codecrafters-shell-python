from time import sleep
import readline
from trie import Trie

readline.parse_and_bind("tab: complete")

TRIE = Trie()

for c in ["exit", "echo", "cat"]:
    TRIE.insert(c)


def completer(text: str, state: int) -> str | None:
    line_buffer = readline.get_line_buffer()
    cursor_pos = readline.get_endidx()

    words = line_buffer[:cursor_pos]
    word = words.split()[-1]

    matches = TRIE.getMatchings(word)

    try:
        return matches[state]
    except:
        return None

readline.set_completer(completer)


def main():
    while True:
        input()
        

if __name__ == "__main__":
    main()
