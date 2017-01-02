import psutil
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))
file_path = path.abspath(path.join(curr_dir, '..', 'analysis', 'main.py'))

analysis_args = ['--label', '--cosine']

for proc in psutil.process_iter():
    cmd = proc.cmdline()
    if len(cmd) > 0 and cmd[0] == python_path and len(set(cmd) & set(analysis_args)) > 0:
        proc.kill()
