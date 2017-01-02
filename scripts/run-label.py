import subprocess
import sys
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))
file_path = path.abspath(path.join(curr_dir, '..', 'src', 'main.py'))

command = [python_path, file_path, '--label']

subprocess.Popen(command)
