import sys
import os
from subprocess import PIPE, Popen, run # to execute code
import readline

# =============================================== Trie class =====================================

class Node:
    def __init__(self):
        self.children = dict()
        self.endNode = False


class Trie:
    def __init__(self):
        self.root = Node()


    def getMatchings(self, word: str) -> None | list[str]:
        """
            Given string "word" finds every word that has 
            "word" as prefix

            ARGS:
                word: str - prefix

            RETURNS:
                matching: None | list[str] - list of words or None if no words found
        """
        # BEGIN FUNCTION
        def dfs(root: Node, curWord: str) -> list[str]:
            if root.endNode:
                matches.append(curWord + " ") # don't forgen space

            for (child, nextNode) in root.children.items():
                dfs(nextNode, curWord + child)
        # END FUNCTION

        curNode = self.root
        matches = []
        
        for char in word:
            # no matching
            if char not in curNode.children:
                return None
            curNode = curNode.children[char]

        dfs(curNode, word)

        return matches

    def insert(self, word: str) -> None:
        """
            Inserts word into Trie

            ARGS:
                word: str - word to insert
        """

        curNode = self.root
        for char in word:
            curNode = curNode.children.setdefault(char, Node())
        curNode.endNode = True



# =============================================== Parsing functions ===============================

def parse(rawArgs: str) -> list[str]:
    """
        Parses raw string into arguments. Implimented as Finite State Machine
        
        ARGS:
            rawArgs: str - string with argument values
        RETURNS:
            args: list[str] - list of arguments
    """
    args = []
    currentArg = ""

    inSingleQuote = False
    inDoubleQuote = False

    i = 0
    while i < len(rawArgs):
        char = rawArgs[i]

        if inSingleQuote:
            if char == "'": inSingleQuote = False
            else:
                currentArg += char
        elif inDoubleQuote:
            if char == '\\' and rawArgs[i+1] in ['"', '\\', '$', '`']:
                currentArg += rawArgs[i+1]
                i += 2
                continue
            if char == '"': inDoubleQuote = False
            else:
                currentArg += char
        else:
            if char == "\\":
                # Can't handle invalid quotes
                currentArg += rawArgs[i+1]
                i += 2
                continue
            elif char == "'":
                inSingleQuote = True
            elif char == '"':
                inDoubleQuote = True
            elif char == '|':
                if currentArg:
                    args.append(currentArg)
                    currentArg = ''

                args.append('|')
            elif char in ">":
                if currentArg:
                    args.append(currentArg)
                    currentArg = ""

                if rawArgs[i+1] == ">":
                    args.append(">>")
                    i += 2
                    continue
                else:
                    args.append(">")

            elif char == " ":
                if currentArg:
                    args.append(currentArg)
                    currentArg = ""
            else:
                currentArg += char

        i += 1

    # Add the last arguments
    if currentArg: args.append(currentArg)

    return args

# ============================================= Builtin functions ==================================


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

    return output, error


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
    if not args:
        if args[0] == "~":
            dirName = os.environ["HOME"]
        else:
            dirName = stdin
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
TRIE = Trie()

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
        return matches[state]
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

# =================================================== Tokenizer ========================

class Token:
    def __init__(self, commandName: str, args: list[str]):
        self.commandName = commandName
        self.args = args

    def __repr__(self):
        return self.commandName

COMMAND = 1
ARG = 2
REDIRECT = 3
FILE = 4

class RawToken:
    def __init__(self, value, tokenType):
        self.value = value
        self.type = tokenType

    # To debug
    def __repr__(self):
        return f"({self.value}, {self.type})"


def tokenize(parsedString: list[str]) -> list[RawToken]:
    tokens = []

    i = 0
    while i < len(parsedString):
        currWord = parsedString[i]

        if (i == 0) or tokens[-1].value == '|':
            currToken = RawToken(currWord, COMMAND)
        elif '>' in currWord: # file descriptor is not specified. Use default 1 (stdout)
            currToken = RawToken("1" + currWord, REDIRECT)
        elif '>' in tokens[-1].value:
            currToken = RawToken(currWord, FILE)
        elif currWord.isdigit():
            if (i+1) < len(parsedString) and '>' in parsedString[i+1]:
                currToken = RawToken(currWord + parsedString[i+1], REDIRECT)  
                tokens.append(currToken)
                i += 2
                continue
            elif (i-1) >= 0 and tokens[-1].type in [COMMAND, ARG]:
                currToken = RawToken(currWord, ARG)
        elif currWord == '|':
            currToken = RawToken(currWord, REDIRECT)
        else:
            currToken = RawToken(currWord, ARG)

        tokens.append(currToken)
        i += 1

    return tokens


def linkTokens(rawTokens: list[RawToken]) -> list[Token]:
    tokens = []
    
    i = 0

    while i < len(rawTokens):
        commandName = rawTokens[i].value
        argList = []

        i += 1
        while i < len(rawTokens) and rawTokens[i].type == ARG:
            argList.append(rawTokens[i].value)
            i += 1

        if i < len(rawTokens):
            currToken = Token(commandName, argList)

            if rawTokens[i].value == "|":
                tokens.append(currToken)
                i += 1                      
            elif '>' in rawTokens[i].value:
                tokens.append(currToken)

                d = rawTokens[i].value[0] if rawTokens[i].value[0].isdigit() else None
                mode = 'a' if '>>' in rawTokens[i].value else 'w'
                fileName = rawTokens[i+1].value

                return tokens, (d, mode, fileName)
    else:
        currToken = Token(commandName, argList)
        tokens.append(currToken)

    return tokens, (None, None, None)



def main():
    while True:
        sys.stdout.write("$ ")

        # split raw string into command and (if any) "argument string"
        rawArgs = input()
        args = parse(rawArgs)

        tokens = tokenize(args)

        commands, (d, mode, fileName) = linkTokens(tokens)

        prevOut = None

        for command in commands:
            commandName, commandArgs = command.commandName, command.args

            if commandName in COMMANDS:
                output, error = COMMANDS[commandName](commandArgs, prevOut)
                prevOut = output

            elif (fullPath := locate(commandName)) is not None:
                proc = Popen([commandName] + commandArgs, stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True)

                try:
                    output, error = proc.communicate(input=prevOut, timeout=15)
                except:
                    proc.kill()
                    output, error = proc.communicate()

                prevOut = output
            else:
                print(f"{commandName}: command not found")

        # Manage redirections
        if fileName is None:
            print(output + error, end='')
        else:
            with open(fileName, mode) as f:
                if d == "1":
                    print(output, file=f, end='')
                elif d == "2":
                    print(error, file=f, end='')

        continue


        command, arguments = args[0], args[1:]
        stream, fileName, mode = None, None, None

        # Check if output should be redirected (write)
        if '>' in arguments:
            fileName = arguments.pop()                      # get the file name and both update the arguments list
            mode = "w"

            ind = arguments.index('>') 
            if arguments[ind-1].isdigit():
                streamType = arguments[ind-1]
                stream = int(streamType)                    # 1 for STDOUT, 2 for STDERR

                arguments = arguments[:ind-1]               # crop argument list
            else:
                stream = 1
                arguments = arguments[:ind]

        # Check if output should be redirected (append)
        if '>>' in arguments:
            fileName = arguments.pop()                      # get the file name and both update the arguments list
            mode = "a"

            ind = arguments.index('>>') 
            if arguments[ind-1].isdigit():
                streamType = arguments[ind-1]
                stream = int(streamType)                    # 1 for STDOUT, 2 for STDERR

                arguments = arguments[:ind-1]               # crop argument list
            else:
                stream = 1
                arguments = arguments[:ind]

        if command in COMMANDS:
            COMMANDS[command](arguments, stream, fileName, mode)
        elif locate(command) is not None:
            # Run the process and pipe streams
            if stream:
                proc = Popen([command] + arguments, stdout=PIPE, stderr=PIPE, text=True)
                output, error = proc.communicate()

                with open(fileName, mode) as f:
                    if stream == 1:
                        print(output, file=f, end='')
                        print(error, end='')
                    elif stream == 2:
                        print(output, end='')
                        print(error, file=f, end='')
            else:
                run([command] + arguments)
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
