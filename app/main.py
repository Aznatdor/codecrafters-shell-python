import sys

def main():
    while True:
        sys.stdout.write("$ ")
        rawArguments = input()

        spaceInd = rawArguments.find(" ")
        command, arguments = rawArguments[:spaceInd], rawArguments[spaceInd+1:]

        if command == "exit":
            sys.exit(0)
        elif command == "echo":
            print(arguments)
        else:
            print(f"{arguments}: not found")


if __name__ == "__main__":
    main()
