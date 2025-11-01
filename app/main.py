import sys
import os

PATH = os.environ["PATH"]
PATH_LIST = PATH.split(os.pathsep)


def echo(arguments):
    print(arguments)


def _type(arguments):
    commandName = arguments
    if commandName in COMMANDS:
        print(f"{commandName} is a shell builtin")
        return
    else:
        for d in PATH_LIST:
            # Such directory might not exist
            try:
                dirList = os.listdir(d)

                # Check that the directory containts the file and that the file can be executed
                fullPath = d + "/" + commandName
                if commandName in dirList and os.access(fullPath, os.X_OK):
                    print(f"{commandName} is {fullPath}")
                    return
            except: pass
            
    print(f"{arguments}: not found")


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
        rawArguments = input()

        if " " in rawArguments:
            spaceInd = rawArguments.find(" ")
            command, arguments = rawArguments[:spaceInd], rawArguments[spaceInd+1:]
        else:
            command, arguments = rawArguments, []

        if command in COMMANDS:
            COMMANDS[command](arguments)
        else:
            print(f"{command}: not found")


if __name__ == "__main__":
    main()
