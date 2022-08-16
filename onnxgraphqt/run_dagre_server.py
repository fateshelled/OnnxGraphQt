import os
from multiprocessing import Process
import subprocess
from subprocess import PIPE


def execute():
    BASE_DIR = os.path.dirname(__file__)
    dagre_path = os.path.join(BASE_DIR, "dagre_server/index.js")
    proc = subprocess.run(["node", dagre_path], shell=False, stdout=PIPE, text=True)

def run() -> Process:
    process = Process(target=execute, daemon=False)
    process.start()
    print("start dagre server.")
    process.join()
    return process


if __name__ == "__main__":
    try:
        process = run()
    except BaseException as e:
        print(e)
