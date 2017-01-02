import subprocess
import sys
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))
file_path = path.abspath(path.join(curr_dir, '..', 'src', 'main.py'))
args = sys.argv[1:]

command = [python_path, file_path] + args

subprocess.Popen(command)
