import sys
import os
from subprocess import PIPE, Popen, run # to execute code


# =============================================== Parsing functions ===============================

def parse(rawArgs: str) -> list[str]:
    """
        Parses raw string into arguments. Implimented using Finite State Machine
        
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


def _pwd(args: list[str], stream: None | int, fileName: None | str, mode: None | str) -> None:
    """
        Prints current working directory

        ARGS:
            args: list[str] - for compatability
            stream: None | int - if specified, stream to be redirected
            fileName: None | str - fileName to redirect the output
            mode: None | str - file open mode
    """

    output, error = os.getcwd(), ""

    if stream:
        with open(fileName, mode) as f:
            if stream == 1:
                print(output, file=f)
            elif stream == 2:
                print(error, file=f)
    else:
        print(os.getcwd())


def _cd(args: list[str], stream: None | int, fileName: None | str, mode: None | str) -> None:
    """
        Changes current directory

        ARGS:
            args: list[str] - relative path to the current directory or empty list
            stream: None | int - if specified, stream to be redirected
            fileName: None | str - fileName to redirect the output
            mode: None | str - file open mode
    """
    if not args or args[0] == "~":
        dirName = os.environ["HOME"]
    else:
        dirName = args[0]

    output, error = "", ""

    try:
        os.chdir(dirName)
        output = ""
    except:
        error = f"cd: {dirName}: No such file or directory\n"

    if stream:
        with open(fileName, mode) as f:
            if stream == 1:
                print(output, file=f)       # redirect output
                print(error, end='')        # print error
            elif stream == 2:
                print(error, file=f, end='')
    else:
        if error:
            print(error, end='')


def echo(args: list[str], stream: None | int, fileName: None | str, mode: None | str) -> None:
    """
        Prints its arguments into stdout

        ARGS:
            args: list[str] - strings to print
            stream: None | int - if specified, stream to be redirected
            fileName: None | str - fileName to redirect the output
            mode: None | str - file open mode
    """

    output, error = ' '.join(args), ''

    if stream:
        with open(fileName, mode) as f:
            if stream == 1:
                print(output, file=f)
            elif stream == 2:
                print(error, file=f)
    else:
        print(output)


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


def _type(args: list[str], stream: None | int, fileName: None | str, mode: None | str) -> None:
    """
        Prints type of a program, i.g. if it is a builtin one or can be found
        in one of the directory specified in PATH variable

        ARGS:
            args: list[str] - list of arguments. Here, it is list of lenth 1 with command name
            stream: None | int - if specified, stream to be redirected
            fileName: None | str - fileName to redirect the output
            mode: None | str - file open mode
    """

    commandName = args[0]

    output, error = "", ""

    if commandName in COMMANDS:
        output = f"{commandName} is a shell builtin\n"
    elif (fullPath := locate(commandName)) is not None:
        output = f"{commandName} is {fullPath}\n"
    else:
        error = f"{commandName}: not found\n"

    if stream:
        with open(fileName, mode) as f:
            if stream == 1:
                print(output, file=f, end='')
                print(error, end='')
            elif stream == 2:
                print(output, end='')
                print(error, file=f, end='')
    else:
        print(output if output else error, end='')


def _exit(args: list[str], stream: None | int, fileName: None | str, mode: None | str) -> None:
    """
        Exit shell
        
        ARGS:
            args: list[str] - exit code
            stream: None | int - if specified, stream to be redirected
            fileName: None | str - fileName to redirect the output
            mode: None : str - file open mode
    """

    exitCode = int(args[0])

    if stream == 1:
        with open(fileName, mode) as f:
            print(exitCode, file=f)
    elif stream == 2:
        pass                # no errors currently
    else:
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
