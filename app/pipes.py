import os
import signal

def runMultipleProc(cmds):
    """
        Creates UNIX pipeline for commands in cmds list.

        ARGS:
            cmds: list[Token] - list of at least two tokens
    """

    pids = []
    rs, ws = [], []

    rCur, wCur = os.pipe()

    rs.append(rCur); ws.append(wCur)

    cFst = cmds.pop(0)
    cLst = cmds.pop()

    # For the first command we should reroute only stdout
    pid = os.fork()
    pids.append(pid)

    if pids[-1] == 0:
        cName = cFst.commandName
        cArgs = cFst.args

        args = [cName, cName] + cArgs

        os.dup2(wCur, 1) 
        os.close(wCur)
        os.close(rCur)
        os.execlp(*args)

    rPrev, wPrev = rCur, wCur

    # For intermediate commads reroute both
    for c in cmds:
        rCur, wCur = os.pipe()
        rs.append(rCur); ws.append(wCur)

        pid = os.fork()
        pids.append(pid)

        if pids[-1] == 0:
            cName = c.commandName
            cArgs = c.args

            args = [cName, cName] + cArgs

            os.dup2(rPrev, 0)
            os.dup2(wCur, 1)

            os.close(rPrev)
            os.close(wPrev)
            os.close(wCur)
            os.close(rCur)

            os.execlp(*args)

        rPrev, wPrev = rCur, wCur

    # For the last reroute only stdin
    rCur, wCur = os.pipe()
    rs.append(rCur); ws.append(wCur)     

    pid = os.fork()
    pids.append(pid)

    if pids[-1] == 0:
        cName = cLst.commandName
        cArgs = cLst.args

        args = [cName, cName] + cArgs

        os.dup2(rPrev, 0)

        os.close(rCur)
        os.close(wCur)
        os.close(rPrev)
        os.close(wPrev)

        os.execlp(*args)

    # Close all file descriptors in the parent process
    for r, w in zip(rs, ws):
        os.close(w)
        os.close(r)

    pidLst = pids.pop()
    # Wait for the last process to end
    os.waitpid(pidLst, 0)

    # Terminate all other processes
    for pid in reversed(pids):
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)


def runProc(c1, c2):
    r, w = os.pipe()

    pid1 = os.fork()

    if pid1 == 0:
        commandName1 = c1.commandName
        args = [commandName1] * 2 + c1.args

        os.dup2(w, 1)
        os.close(w)
        os.close(r)
        os.execlp(*args)


    pid2 = os.fork()

    if pid2 == 0:
        commandName2 = c2.commandName
        args = [commandName2] * 2 + c2.args

        os.dup2(r, 0)
        os.close(w)
        os.close(r)
        os.execlp(*args)

    os.close(w)
    os.close(r)

    os.waitpid(pid2, 0)

    os.kill(pid1, signal.SIGTERM)
    os.waitpid(pid1, 0)

    return 0


def main():
    inputLine = input("$ ")

    commands = parser.getArgs(inputLine)

    runMultipleProc(commands)


if __name__ == "__main__":
    import parser
    main()
