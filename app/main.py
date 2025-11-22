import sys
import os
from subprocess import PIPE, Popen, run, TimeoutExpired # to execute code
import readline

import app.trie as trie
import app.parser as parser
import app.pipes as pipes

def _pwd(args: list[str], stdin: str) -> tuple[str, str]:
    """
        Prints current working directory

        ARGS:
            args: list[str] - for compatability
            stdin: str | None - argument from stdin

        RETURNS:
            output: str - output in stdout stream
            error: str - output in stderr stream
    """

    output, error = os.getcwd(), ""

    return output + "\n", error


def _cd(args: list[str], stdin: str | None) -> tuple[str, str]:
    """
        Changes current directory

        ARGS:
            args: list[str] - relative path to the current directory or empty list
            stdin: str | None - argument from stdin

        RETURNS:
            output: str - output in stdout stream
            error: str - output in stderr stream
    """
    if args[0] == "~":
        dirName = os.environ["HOME"]
    else:
        dirName = args[0]

    output, error = "", ""

    try:
        os.chdir(dirName)
    except:
        error = f"cd: {dirName}: No such file or directory\n"

    return output, error


def echo(args: list[str], stdin: str | None) -> tuple[str, str]:
    """
        Prints its arguments into stdout

        ARGS:
            args: list[str] - strings to print
            stdin: str | None - argument from stdin
    """

    if stdin is not None:
        args = parse(stdin)

    output = ' '.join(args)

    if output[-1] != "\n":
        output += "\n"

    error = ''

    return output, error

def locate(fileName) -> str | None:
    """
        Locates executable file in directories defined in PATH variable
        
        ARGS:
            fileName: str - file name

        RETURNS:
            fullPath: str | None - full path if file is executable and None otherwise
    """

    if fileName in EXECUTABLES:
        return EXECUTABLES[fileName]

    return None

def findExes() -> dict[str, str]:
    """
        Finds all executible files listed in PATH directories

        RETURNS:
            executables: dict[str, str] - list absolute pathes to executable files
    """

    executables = {}

    for d in PATH_LIST:
        try:
            dirList = os.listdir(d)

            for file in dirList:
                fullPath = os.path.join(d, file)

                if os.path.isfile(fullPath) and os.access(fullPath, os.X_OK):
                    executables[file] = fullPath
        except: pass
    
    return executables


def _type(args: list[str], stdin: str | None) -> tuple[str, str]:
    """
        Prints type of a program, i.e. if it is a builtin one or can be found
        in one of the directory specified in PATH variable

        ARGS:
            args: list[str] - list of arguments. Here, it is list of lenth 1 with command name
            stdin: str | None - argument from stdin

        RETURNS:
            output: str - output in stdout stream
            error: str - output in stderr stream
    """

    commandName = args[0]

    output, error = "", ""

    if commandName in COMMANDS:
        output = f"{commandName} is a shell builtin\n"
    elif (fullPath := locate(commandName)) is not None:
        output = f"{commandName} is {fullPath}\n"
    else:
        error = f"{commandName}: not found\n"

    return output, error



def _exit(args: list[str], stdin: str | None) -> tuple[str, str]:
    """
        Exit shell
        
        ARGS:
            args: list[str] - exit code
            stdin: str | None - argument from stdin

        RETURNS:
            output: str - output in stdout stream
            error: str - output in stderr stream
    """

    output, error = "", ""

    try:
        exitCode = int(args[0])
    except:
        exitCode = 0
        error = "exit: Not enough arguments"

    if len(args) > 1: error = "exit: Too much arguments"

    sys.exit(exitCode)

    # I don't know how can I pass further this output
    return output, error
        
# =============================================== Global variables ===============================

COMMANDS = {
        "exit": _exit,
        "echo": echo,
        "type": _type,
        "pwd": _pwd,
        "cd": _cd
        }

PATH = os.environ["PATH"]
PATH_LIST = PATH.split(os.pathsep)

EXECUTABLES = findExes()

# ====================================== readline config =======================

readline.parse_and_bind("tab: complete")
TRIE = trie.Trie()

commands = list(COMMANDS.keys()) + list(EXECUTABLES.keys())

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
        commands, (d, mode, fileName)  = parser.getArgs(rawArgs)

        output, error = '', ''

        if len(commands) == 1:
            command = commands[0]
            commandName, commandArgs = command.commandName, command.args

            if commandName in COMMANDS:
                output, error = COMMANDS[commandName](commandArgs, None)
            elif locate(commandName):
                proc = Popen([commandName] + command.args,
                             stdout=PIPE, stderr=PIPE, text=True)

                output, error = proc.communicate()
            else:
                print(f"{commandName}: command not found")

            if fileName is not None:
                with open(fileName, mode) as f:
                    if d == '1':
                        print(output, file=f, end='')
                        print(error, end='')
                    if d == '2':
                        print(output, end='')
                        print(error, file=f, end='')
            else:
                print(output, end='')
                print(error, end='')

        else:
            c1, c2 = commands

            pipes.runProc(c1, c2)

            continue

if __name__ == "__main__":
    main()
