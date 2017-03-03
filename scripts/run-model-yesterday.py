import datetime
import subprocess
from os import path

curr_dir = path.dirname(path.abspath(__file__))
python_path = path.abspath(path.join(curr_dir, '..', 'venv', 'bin', 'python'))
file_path = path.abspath(path.join(curr_dir, '..', 'newsapp', 'main.py'))

today = datetime.date.today()
yesterday = datetime.date.fromordinal(today.toordinal()-1)
two_weeks_prev = datetime.date.fromordinal(yesterday.toordinal()-13)

subprocess.Popen([
    python_path, file_path,
    '--run-model',
    '--start-date', str(two_weeks_prev),
    '--end-date', str(yesterday),
    '--num-topics', '100'
])
