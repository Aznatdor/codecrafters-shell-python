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


def getArgs(inputLine: str):
    parsedString = parse(inputLine)
    rawTokens = tokenize(parsedString)
    tokens, (d, mode, fileName) = linkTokens(rawTokens)
    return tokens, (d, mode, fileName)
