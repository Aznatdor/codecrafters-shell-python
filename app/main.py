import sys


def main():
    command = "dummy"                   # dummy command to make REPL loop more concise

    while command:
        sys.stdout.write("$ ")
        command = input()
        print(f"{command}: not found")


if __name__ == "__main__":
    main()
