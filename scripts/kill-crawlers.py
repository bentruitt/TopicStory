import psutil
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))

for proc in psutil.process_iter():
    cmd = proc.cmdline()
    if len(cmd) > 0 and cmd[0] == python_path and '--crawl' in cmd[-1]:
        proc.kill()
