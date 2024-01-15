import configparser

from flask import Flask

from src.eventstracker import EventsTracker

CONFIG_FILE_PATH = 'config.ini'

config = configparser.ConfigParser()
if not config.read(CONFIG_FILE_PATH):
    raise FileNotFoundError(f'Cannot read config file "{CONFIG_FILE_PATH}"')

tracker = EventsTracker(config)
app = Flask(__name__)


@app.route("/averages")
def hello_world():
    return tracker.get_average_event_times()
