import os
import signal
import sys
import app.file_utils as file_utils
import app.builtin as builtin

class HistoryEntry:
    def __init__(self, entryName, number):
        self.name = entryName
        self.num = number

    def __str__(self):
        return f"\t{self.num} {self.name}\n"

HISTORY = []

def runMultipleProc(cmds: list[Token], redirect: tuple[str] | None, rawCommand: str):
    """
        Creates UNIX pipeline for commands in cmds list.

        ARGS:
            cmds: list[Token] - list of tokens to be run
            redirect: tuple[str] - is not None, consists of file desctiptor 
                                    to be redirectred, file open mode
                                    and name of the file to be opened
            rawCommand: str - full command string to be added into HISTORY list
    """

    historyEntry = HistoryEntry(rawCommand, len(HISTORY) + 1)
    HISTORY.append(historyEntry)

    if len(cmds) == 1:
        c = cmds[0]
        cName = c.commandName
        cArgs = c.args

        args = [cName, cName] + cArgs

        # This way is just easier
        if cName == "history":
            cArgs = HISTORY

        oldD = None

        if redirect is not None:
            d, mode, fileName = redirect

            flags = os.O_WRONLY | os.O_CREAT

            if mode == "a":
                flags |= os.O_APPEND
            else:
                flags |= os.O_TRUNC

            fileDesc = os.open(fileName, flags, 0o644)
            
            oldD = os.dup(d)
            os.dup2(fileDesc, d)
            os.close(fileDesc)

        if cName in builtin.BUILTINS:
            builtin.BUILTINS[cName](cArgs)
        elif cName in file_utils.EXECUTABLES:
            pid = os.fork()

            if pid == 0:
                os.execlp(*args)

            os.wait()
        else:
            sys.stderr.write(f"{cName}: command not found\n")
            sys.stderr.flush()

        # Return descriptors as they were 
        if oldD is not None:
            os.dup2(oldD, d)
            os.close(oldD)

        return 0

    else:
        pids = []
        rs, ws = [], []

        rPrev, wPrev = None, None

        isLast = False

        for i, c in enumerate(cmds):
            rCur, wCur = os.pipe()
            rs.append(rCur); ws.append(wCur)

            if i == len(cmds) - 1:
                os.close(wCur)
                wCur = None

                isLast = True

            pid = os.fork()
            pids.append(pid)

            if pids[-1] == 0:
                cName = c.commandName
                cArgs = c.args

                args = [cName, cName] + cArgs

                
                # overload pipe if there's redirect in the end
                if isLast and redirect is not None:
                    d, mode, fileName = redirect

                    flags = os.O_WRONLY | os.O_CREAT

                    if mode == "a":
                        flags |= os.O_APPEND
                    else:
                        flags |= os.O_TRUNC

                    fileDesc = os.open(fileName, flags, 0o644)
                    
                    os.dup2(fileDesc, d)
                    os.close(fileDesc)

                # Close descriptors

                if rPrev is not None:
                    os.dup2(rPrev, 0)
                if wCur is not None:
                    os.dup2(wCur, 1)

                if rPrev is not None:
                    os.close(rPrev)
                if wPrev is not None:
                    os.close(wPrev)

                if wCur is not None:
                    os.close(wCur)

                os.close(rCur)

                if cName in builtin.BUILTINS:
                    builtin.BUILTINS[cName](cArgs)
                    sys.exit(0)
                elif cName in file_utils.EXECUTABLES:
                    os.execlp(*args)

            rPrev, wPrev = rCur, wCur

        # Close all file descriptors in the parent process
        for r, w in zip(rs, ws):
            try: # If we try to close alredy closed descriptor
                os.close(w)
            except: pass
            try:
                os.close(r)
            except: pass

        # Wait for the last process to end
        if isLast:
            pidLst = pids.pop()
            os.waitpid(pidLst, 0)

        # Terminate all other processes
        for pid in reversed(pids):
            os.kill(pid, signal.SIGTERM)
            os.waitpid(pid, 0)


def main():
    inputLine = input("$ ")

    commands, redirect = parser.getArgs(inputLine)

    runMultipleProc(commands, redirect)


if __name__ == "__main__":
    import builtin
    import parser
    main()
else:
    import app.builtin as builtin
