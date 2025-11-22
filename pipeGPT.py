import asyncio
import os
import signal

async def run():
    p1 = await asyncio.create_subprocess_exec(
        "tail", "-f", "app/file4.txt",
        stdout=asyncio.subprocess.PIPE,
        preexec_fn=os.setsid
    )

    p2 = await asyncio.create_subprocess_exec(
        "head", "-n", "5",
        stdin=p1.stdout,
        stdout=asyncio.subprocess.PIPE
    )

    p1.stdout.close()

    while True:
        line = await p2.stdout.readline()
        if not line:
            break
        print(line.decode(), end="", flush=True)

    await p2.wait()

    # tail должен умереть от SIGPIPE, но если жив — убиваем
    try:
        await asyncio.wait_for(p1.wait(), timeout=0.2)
    except asyncio.TimeoutError:
        os.killpg(os.getpgid(p1.pid), signal.SIGTERM)
        await p1.wait()

asyncio.run(run())
