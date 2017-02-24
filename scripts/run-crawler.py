import subprocess
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))
file_path = path.abspath(path.join(curr_dir, '..', 'newsapp', 'main.py'))

sources = [
  'cnn.com',
  'nytimes.com',
  'theguardian.com',
  'huffingtonpost.com',
  'forbes.com',
  'yahoo.com/news',
  'foxnews.com',
  'bbc.com',
  'bloomberg.com',
  'usatoday.com',
  'reuters.com',
  'nbcnews.com',
  'time.com'
]

for source in sources:
  subprocess.Popen([python_path, file_path, '--crawl', source])
