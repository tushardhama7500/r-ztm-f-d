import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))


parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import create_app

app = create_app('dev')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)