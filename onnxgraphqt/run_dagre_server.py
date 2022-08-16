import os
from multiprocessing import Process
import subprocess
from subprocess import PIPE


def run():
    BASE_DIR = os.path.dirname(__file__)
    dagre_path = os.path.join(BASE_DIR, "dagre_server/index.js")
    proc = subprocess.Popen(["node", dagre_path], shell=False, stdout=PIPE, text=True)
    print(f"start dagre server [{proc.pid}].")
    return proc

if __name__ == "__main__":
    try:
        process = run()
        process.wait()
    except BaseException as e:
        print(e)
