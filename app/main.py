import sys
import os
import subprocess # to execute code


PATH = os.environ["PATH"]
PATH_LIST = PATH.split(os.pathsep)


def echo(arguments):
    print(' '.join(arguments))


def locate(fileName):
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
            fullPath = d + "/" + fileName

            # Check that the file exists and that it can be executed
            if os.access(fullPath, os.F_OK) and os.access(fullPath, os.X_OK):
                return fullPath
        except: pass

    return None


def _type(arguments):
    """
        Prints type of a program, i.g. if it is a builtin one or can be found
        in one of the directory specified in PATH variable

        ARGS:
            arguments: List[str] - list of arguments. Here, it is list of lenth 1 with command name
    """

    commandName = arguments[0]

    if commandName in COMMANDS:
        print(f"{commandName} is a shell builtin")
    elif (fullPath := locate(commandName)) is not None:
        print(f"{commandName} is {fullPath}")
    else:
        print(f"{commandName}: not found")


def _exit(arg):
    sys.exit(0)
        
COMMANDS = {
        "exit": _exit,
        "echo": echo,
        "type": _type,
        }

def main():
    while True:
        sys.stdout.write("$ ")
        args = input().split()

        command, arguments = args[0], args[1:]

        if command in COMMANDS:
            COMMANDS[command](arguments)
        elif locate(command) is not None:
            subprocess.run([command] + arguments)
        else:
            print(f"{command}: command not found")

if __name__ == "__main__":
    main()
