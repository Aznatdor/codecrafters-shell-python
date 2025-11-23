import sys
import app.file_utils as file_utils
import os
import readline

def history(args: list[str]) -> None:
    """
        Prints out history of commands

        Use "history {num}" to limit history entries

        ARGS:
            args: list[str] - list of arguments
    """

    length = readline.get_current_history_length()

    if args:
        if args[0].isdigit():
            num = int(args[0])

            for i in range(length + 1 - num, length + 1):
                cmd = readline.get_history_item(i)

                sys.stdout.write(f"{i:5} {cmd}\n")
                sys.stdout.flush()
        elif args[0] == "-r":
            historyFileName = args[1]
            readline.read_history_file(historyFileName)
        elif args[0] == "-w":
            historyFileName = args[1]
            readline.write_history_file(historyFileName)
    else:
        for i in range(1, length + 1):
            cmd = readline.get_history_item(i)

            sys.stdout.write(f"{i:5} {cmd}\n")
            sys.stdout.flush()


def _exit(args: list[str]) -> None:

    if not args:
        sys.exit(0)

    else:
        exitCode = int(args[0])
        sys.exit(exitCode)


def _pwd(args: list[str]) -> None:
    """
        Prints current working directory

        ARGS:
            args: list[str] - for compatability
    """

    output, error = os.getcwd(), ""

    sys.stdout.write(output + "\n")
    sys.stdout.flush()


def _cd(args: list[str]) -> None:
    """
        Changes current directory

        ARGS:
            args: list[str] - relative path to the current directory or empty list
    """
    if not args or args[0] == "~":
        dirName = os.environ.get("HOME", "/")
    else:
        dirName = args[0]

    try:
        os.chdir(dirName)
        sys.stdout.write('')
        sys.stdout.flush()
    except:
        error = f"cd: {dirName}: No such file or directory\n"
        sys.stderr.write(error)
        sys.stderr.flush()


def echo(args: list[str]) -> None:
    """
        Prints its arguments into stdout

        ARGS:
            args: list[str] - strings to print
    """

    output = ' '.join(args)

    sys.stdout.write(output + '\n')
    sys.stdout.flush()


def _type(args: list[str]) -> None:
    """
        Prints type of a program, i.e. if it is a builtin one or can be found
        in one of the directory specified in PATH variable

        ARGS:
            args: list[str] - list of arguments. Here, it is list of lenth 1 with command name
    """

    commandName = args[0]

    output, error = "", ""

    if commandName in BUILTINS:
        output = f"{commandName} is a shell builtin\n"
        sys.stdout.write(output)
        sys.stdout.flush()
    elif commandName in file_utils.EXECUTABLES:
        fullPath = file_utils.EXECUTABLES[commandName]
        output = f"{commandName} is {fullPath}\n"
        sys.stdout.write(output)
        sys.stdout.flush()
    else:
        error = f"{commandName}: not found\n"
        sys.stderr.write(error)
        sys.stderr.flush()

BUILTINS = {
        "exit": _exit,
        "echo": echo,
        "type": _type,
        "pwd": _pwd,
        "cd": _cd,
        "history": history
        }
