import psutil
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))
python_path = os.path.join(curr_dir, 'venv', 'bin', 'python')

for proc in psutil.process_iter():
    cmd = proc.cmdline
    if len(cmd) > 0 and cmd[0] == python_path:
        proc.kill()
