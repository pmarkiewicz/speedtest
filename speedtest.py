import subprocess
import dateutil.parser
import schedule
import time
import argparse
import redislite
import redis_collections
import daemon
from datetime import datetime, timedelta
from daemon import pidfile
import logging
from os import path

from processor import *

MB = 1024.0 * 1024.0
LOCAL_DIR = path.dirname(path.abspath(__file__))
PID_FILE = path.join(LOCAL_DIR, 'speedtest.pid')
LOG_FILE = path.join(LOCAL_DIR, 'speedtest.log')
DB_FILE = path.join(LOCAL_DIR, 'speedtest.db')
PORT = 8002

logger = logging.getLogger('speedtest')
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)
logger.addHandler(handler)

is_daemon = False

redis = redislite.StrictRedis(DB_FILE, serverconfig={'port': PORT})
data = redis_collections.List(redis=redis, key='speed')
hourly = redis_collections.List(redis=redis, key='hourly')
settings = redis_collections.Dict(redis=redis, key='settings')

def get_splitted_output(cmd):
    return subprocess.check_output(cmd).decode().replace('\n', '').replace('\r', '').split(',')

def get_speed():
    headers = get_splitted_output(['speedtest', '--csv-header'])
    try:
	speed = get_splitted_output(['speedtest', '--csv'])
    except Exception as ex:
        if not is_daemon:
            print (ex)
        logger.error(ex)

    info = { key.lower(): val for key, val in zip(headers, speed) }
    info['timestamp'] = dateutil.parser.parse(info['timestamp'])
    info['download'] = int(float(info['download']))
    info['upload'] = int(float(info['upload']))
    info['ping'] = float(info['ping'])
    return info


def save_speed_data():
    try:
        data.append(get_speed())
    except Exception as ex:
        if not is_daemon:
            print (ex)
        logger.error(ex)

def aggregate_hours():
    try:
        last_hour = settings.get('last_hour', datetime.min) - timedelta(hours=2)
        items = ([)i for i in data if i['timestamp'] >= last_hour)
        hourly.extend(average_speed_hourly(items).values())
        settings['last_hour'] = datetime.now()
        logger.info('hourly')
    except Exception as ex:
        if not is_daemon:
            print (ex)
        logger.error(ex)

def aggregate_days():
    try:
        settings['last_day'] = datetime.now().strftime('%Y%m%d')
        logger.info('daily')
    except Exception as ex:
        if not is_daemon:
            print (ex)
        logger.error(ex)

def run_jobs():
    save_speed_data()
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_daemon():
    with daemon.DaemonContext(umask=0o002,  # -rw-r--r--
                            pidfile=pidfile.TimeoutPIDLockFile(PID_FILE),
                            working_directory=LOCAL_DIR) as context:
        run_jobs()

if __name__ == "__main__":
    print('redis')
    logger.info('speedtest start')
    parser = argparse.ArgumentParser(description="Speed test")
    parser.add_argument('-d', '--daemon', action='store_true', default=False, help='Run as a daemon')

    args = parser.parse_args()
    schedule.every(10).minutes.do(save_speed_data)
    schedule.every(1).hour.do(aggregate_hours)
    schedule.every(1).day.do(aggregate_days)

    try:
        if args.daemon:
            print('run as daemon')
            is_daemon = True
            start_daemon()
        else:
            run_jobs()
    except Exception as ex:
        if not is_daemon:
            print (ex)
        logger.error(ex)
    finally:
        redis.shutdown()
