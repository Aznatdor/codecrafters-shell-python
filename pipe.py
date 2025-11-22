import subprocess
import sys

class ProcManager:
    def __init__(self):
        self.proc = []

    def addProc(self, command: list[str]):
        """
            Add process to the list. Connects stdout to stdin

            ARGS:
                command: list[str] - list of command argmunets (name, *args)
        """

        stdin = self.proc[-1].stdout if self.proc else None

        newProc = subprocess.Popen(command, 
                                   stdin=stdin, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True
                                   )

        # Close the reference for the previous stdout
        if stdin is not None:
            stdin.close()

        self.proc.append(newProc)


    def run(self, timeout: int = 4):
        """
            Run the "pipe"
            ARGS:
                timeout (optional): int - timeout to wait for process execution
        """

        if not self.proc:
            return "", ""

        lastProc = self.proc[-1]

        output, error = '', ''

        try:
            output, error = lastProc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.stop()
        finally:
            self.clean()

        return output, error


    def clean(self):
        """
            Gentle cleaning after last process in the list has terminated
        """

        for proc in self.proc:
            if proc.poll() is None: # if process is still running, stop it
                try: # gentle stop
                    proc.terminate()
                    proc.wait(timeout=1)            # wait for child process to terminate
                except subprocess.TimeoutExpired: # killing
                    proc.kill()
                    proc.wait()

    def stop(self):
        """
            Emergent cleaning after some failure
        """

        for proc in self.proc:
            if proc.poll() is None:
                proc.kill()
                proc.wait()


def main():
    p1 = subprocess.Popen(["tail", "-f", "app/file4.txt"], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['head', '-n', '5'], stdin=p1.stdout, stdout=subprocess.PIPE)

    p1.stdout.close()

    try:
        print(p2.stdout.read())
        # out, _ = p2.communicate(timeout=2)
        # print(out)
    except:
        p2.kill()
        out, _ = p2.communicate()
        print(out)
        p1.kill()
    finally:
        p2.kill()
        p1.kill()

    return

    manager.addProc(["tail", "-f", "app/file4.txt"])
    manager.addProc(["head", "-n", "5"])

    print(manager.run())

    return

    manager.addProc(["cat", "app/file2.txt"])
    manager.addProc(["cat"])


if __name__ == "__main__":
    main()
