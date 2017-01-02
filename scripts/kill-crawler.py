import psutil
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))
python_path = os.path.join(curr_dir, '..', 'venv', 'bin', 'python')
python_path = os.path.abspath(python_path)
file_path = os.path.join(curr_dir, '..', 'crawler', 'main.py')
file_path = os.path.abspath(file_path)

for proc in psutil.process_iter():
    cmd = proc.cmdline()
    if len(cmd) > 0 and cmd[0] == python_path and cmd[1] == file_path:
        proc.kill()
