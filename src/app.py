
import os
from flask import Flask
from dotenv import load_dotenv 
from apscheduler.schedulers.background import BackgroundScheduler

from service import init
from transformer import handle_data_transform

load_dotenv(verbose=True)

app = Flask(__name__)


hours = os.getenv('number_of_hours', 3)
is_not_production = os.getenv('env', 'development') != 'production'
DEBUG = False

if is_not_production:
  minutes = 1
  init()
  DEBUG=True
else:
  minutes = int(hours) * 60


schedule = BackgroundScheduler(daemon=True)
schedule.add_job(handle_data_transform, 'interval', minutes=minutes)
schedule.start()


@app.route('/')
def welcome():
    return 'Welcome to File Transformer'

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=os.getenv('PORT', 8000), debug=DEBUG, load_dotenv=True)

