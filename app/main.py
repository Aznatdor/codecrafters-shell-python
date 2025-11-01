import sys

def main():
    while True:
        sys.stdout.write("$ ")
        arguments = input()
        argumentsList = arguments.split()   # simple parsing
        command = argumentsList[0]

        if command == "exit":
            sys.exit(0)

        print(f"{arguments}: not found")


if __name__ == "__main__":
    main()
