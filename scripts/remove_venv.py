import shutil
import os

path = os.path.join(os.path.dirname(__file__), '..', 'venv')
path = os.path.normpath(path)

if os.path.exists(path):
    print('Removing', path)
    shutil.rmtree(path)
    print('Removed')
else:
    print('No venv found at', path)
