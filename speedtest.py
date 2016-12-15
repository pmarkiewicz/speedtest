import subprocess
import dateutil.parser
import schedule
import time
import argparse
import redislite
import redis_collections
import daemon
from daemon import pidfile
import logging

MB = 1024.0 * 1024.0
PID_FILE = '/tmp/speedtest.pid'
LOG_FILE = "/var/log/speedtest.log"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)
logger.addHandler(handler)

redis = redislite.StrictRedis('/tmp/redis.db', serverconfig={'port': '8002'})
data = redis_collections.List(redis=redis, key='speed')
settings = redis_collections.Dict(redis=redis, key='settings')

def get_splitted_output(cmd):
    return subprocess.check_output(cmd).decode().replace('\n', '').replace('\r', '').split(',')

def get_speed():
    headers = get_splitted_output(['speedtest', '--csv-header'])
    speed = get_splitted_output(['speedtest', '--csv'])

    if len(headers) != len(speed):
        print("BAD")

    info = { key.lower(): val for key, val in zip(headers, speed) }
    info['timestamp'] = dateutil.parser.parse(info['timestamp'])
    info['download'] = int(float(info['download']))
    info['upload'] = int(float(info['upload']))
    info['ping'] = float(info['ping'])
    return info


def save_speed_data():
    data.append(get_speed())

def aggregate_hours():
    settings['last_hour'] = datetime.now().strftime('%Y%m%d%H')

def aggregate_days():
    settings['last_hour'] = datetime.now().strftime('%Y%m%d')

def run_jobs():
    save_speed_data()
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_daemon():
    with daemon.DaemonContext(umask=0o002, pidfile=pidfile.TimeoutPIDLockFile(PID_FILE)) as context:
        try:
            run_jobs()
        except Exception as ex:
            logger.error(ex)

if __name__ == "__main__":
    print('redis')
    parser = argparse.ArgumentParser(description="Speed test")
    parser.add_argument('-d', '--daemon', action='store_true', default=False, help='Run as a daemon')

    args = parser.parse_args()
    schedule.every(10).minutes.do(save_speed_data)
    schedule.every(1).hour.do(aggregate_hours)
    schedule.every(1).day.do(aggregate_days)

    if args.daemon:
        print('run as daemon')
        start_daemon()
    else:
        run_jobs()
