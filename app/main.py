import sys
import os
import readline
import atexit

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

    sys.stdout.write('\n')
    sys.stdout.write(" ".join(matches))
    sys.stdout.write('\n')
    sys.stdout.flush()

    sys.stdout.write("$ ")                          # write invitation
    sys.stdout.write(readline.get_line_buffer())    # write current contents of buffer
    sys.stdout.flush()                              # make sure everything is written


readline.set_completion_display_matches_hook(display)
readline.set_completer(completer)

readline.set_auto_history(False) # auto add doesn't add duplicates



def main():
    # On startup configure history file
    try:
        HISTFILE = os.environ["HISTFILE"]

        with open(HISTFILE, 'r') as f:
            for line in f:
                readline.add_history(line.strip())
    except:
        HISTFILE = os.path.join(os.path.expanduser("~"), ".my_shell_history")


    while True:
        # split raw string into command and (if any) "argument string"
        rawArgs = input("$ ")

        readline.add_history(rawArgs) # I need duplicates to be added

        commands, redirect = parser.getArgs(rawArgs)
        pipes.runMultipleProc(commands, redirect)


if __name__ == "__main__":
    main()
