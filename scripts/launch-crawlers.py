import subprocess
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))
file_path = path.abspath(path.join(curr_dir, '..', 'newsapp', 'main.py'))

args = [
        '--crawl-foxnews',
        '--crawl-nytimes',
        '--crawl-theguardian',
        '--crawl-npr',
        '--crawl-cnn'
]

for arg in args:
  subprocess.Popen([python_path, file_path, arg])
