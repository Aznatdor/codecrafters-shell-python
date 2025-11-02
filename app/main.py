import sys
import os
import subprocess # to execute code


# =============================================== Parsing functions ===============================

def parse(rawArgs: str) -> list[str]:
    """
        Parses argument string for 'echo' built in
        
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
            if char == '"': inDoubleQuote = False
            else:
                currentArg += char
        else:
            if char == "'":
                inSingleQuote = True
            elif char == '"':
                inDoubleQuote = True
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


def _pwd(args: list[str]) -> None:
    """
        Prints current working directory

        ARGS:
            args: list[str] - for compatability
    """
    print(os.getcwd())


def _cd(args: list[str]) -> None:
    """
        Changes current directory

        ARGS:
            args: list[str] - relative path to the current directory or empty list
    """
    if not args or args[0] == "~":
        dirName = os.environ["HOME"]
    else:
        dirName = args[0]

    try:
        os.chdir(dirName)
    except:
        print(f"cd: {dirName}: No such file or directory")


def echo(args: list[str]) -> None:
    """
        Prints its arguments into stdout

        ARGS:
            args: list[str] - strings to print
    """

    outputLine = ' '.join(args)
    print(outputLine)


def locate(fileName) -> str | None:
    """
        Locates executable file in directories defined in PATH variable
        
        ARGS:
            fileName: str - file name

        RETURNS:
            fullPath: str | None - full path if file is executable and None otherwise
    """

    for d in PATH_LIST:
        # Such directory might not exist
        try:
            dirList = os.listdir(d)
            fullPath = os.path.join(d, fileName)

            # Check that the file exists and that it can be executed
            if os.path.isfile(fullPath) and os.access(fullPath, os.X_OK):
                return fullPath
        except: pass

    return None


def _type(args: list[str]) -> None:
    """
        Prints type of a program, i.g. if it is a builtin one or can be found
        in one of the directory specified in PATH variable

        ARGS:
            args: list[str] - list of arguments. Here, it is list of lenth 1 with command name
    """

    commandName = args[0]

    if commandName in COMMANDS:
        print(f"{commandName} is a shell builtin")
    elif (fullPath := locate(commandName)) is not None:
        print(f"{commandName} is {fullPath}")
    else:
        print(f"{commandName}: not found")


def _exit(args: list[str]) -> None:
    """
        Exit shell
        
        ARGS:
            args: list[str] - exit code
    """

    exitCode = int(args[0])
    sys.exit(exitCode)
        

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


def main():
    while True:
        sys.stdout.write("$ ")

        # split raw string into command and (if any) "argument string"
        rawArgs = input()
        args = parse(rawArgs)

        command, arguments = args[0], args[1:]

        if command in COMMANDS:
            COMMANDS[command](arguments)
        elif locate(command) is not None:
            subprocess.run([command] + arguments)
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
