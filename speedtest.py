import argparse
import daemon
import dateutil.parser

import redis_collections
import redislite
import schedule
import subprocess
import time
from daemon import pidfile
from datetime import datetime, timedelta
from os import path
import sys

from helpers import *
from log import get_logger

MB = 1024.0 * 1024.0
LOCAL_DIR = path.dirname(path.abspath(__file__))
PID_FILE = path.join(LOCAL_DIR, 'speedtest.pid')
DB_FILE = path.join(LOCAL_DIR, 'speedtest.db')
PORT = 8002
MIN_DATETIME = datetime(2016, 1, 1)

logger = get_logger('speedtest')

is_daemon = False

redis = redislite.StrictRedis(DB_FILE, serverconfig={'port': PORT})
data = redis_collections.List(redis=redis, key='speed')
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

    info = {key.lower(): val for key, val in zip(headers, speed)}
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


def run_jobs():
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as ex:
        if not is_daemon:
            print (ex)
        logger.error(ex)
    finally:
        redis.shutdown()
        sys.exit()


def start_daemon():
    with daemon.DaemonContext(umask=0o002,  # -rw-r--r--
                              pidfile=pidfile.TimeoutPIDLockFile(PID_FILE),
                              working_directory=LOCAL_DIR) as context:
        run_jobs()


if __name__ == "__main__":
    logger.info('speedtest start')
    parser = argparse.ArgumentParser(description="Speed test")
    parser.add_argument('-d', '--daemon', action='store_true', default=False, help='Run as a daemon')

    args = parser.parse_args()
    schedule.every(10).minutes.do(save_speed_data)

    if args.daemon:
        print('run as daemon')
        is_daemon = True
        start_daemon()
    else:
        run_jobs()
