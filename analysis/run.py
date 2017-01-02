import subprocess
import os
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
python_path = os.path.join(curr_dir, 'venv', 'bin', 'python')
file_path = os.path.join(curr_dir, 'analysis', 'main.py')
args = sys.argv[1:]

command = [python_path, file_path] + args

subprocess.Popen(command)
