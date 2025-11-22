import sys
import os
import readline

import app.trie as trie
import app.parser as parser
import app.pipes as pipes
import app.file_utils as file_utils
import app.builtin as builtin

# ====================================== readline config =======================

readline.parse_and_bind("tab: complete")
TRIE = trie.Trie()

commands = list(builtin.BUILTINS.keys()) + list(file_utils.EXECUTABLES.keys())

for c in commands:
    TRIE.insert(c)

def completer(text: str, state: int) -> str | None:
    """
        Custom complition function
    """
    line_buffer = readline.get_line_buffer()
    cursor_pos = readline.get_endidx()

    words = line_buffer[:cursor_pos]
    word = words.split()[-1]

    matches = TRIE.getMatchings(word)

    try:
        return matches[state] + " "
    except:
        return None


def display(substring: str, matches: list[str], maxLen: int) -> None:
    """
        Custom display function

        ARGS:
            substring: str - word to be completed
            matches: list[str] - possible complitions
            maxLen: int - maximum length of match
    """

    print()
    print(" ".join(matches))

    sys.stdout.write("$ ")                          # write invitation
    sys.stdout.write(readline.get_line_buffer())    # write current contents of buffer
    sys.stdout.flush()                              # make sure everything is written


readline.set_completion_display_matches_hook(display)
readline.set_completer(completer)

def main():
    while True:
        sys.stdout.write("$ ")

        # split raw string into command and (if any) "argument string"
        rawArgs = input()

        commands, redirect = parser.getArgs(rawArgs)
        pipes.runMultipleProc(commands, redirect)


if __name__ == "__main__":
    main()
