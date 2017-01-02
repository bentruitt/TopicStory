import subprocess
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))
python_path = os.path.join(curr_dir, '..', 'venv', 'bin', 'python')
python_path = os.path.abspath(python_path)
file_path = os.path.join(curr_dir, '..', 'crawler', 'main.py')
file_path  = os.path.abspath(file_path)

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
