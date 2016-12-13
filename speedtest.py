import subprocess
import dateutil.parser
import schedule
import time
import argparse
import redislite
import redis_collections
import daemon
from daemon import pidfile


MB = 1024.0 * 1024.0
PID_FILE = '/tmp/speedtest.pid'

redis = redislite.StrictRedis('/tmp/redis.db', serverconfig={'port': '8002'})
data = redis_collections.List(redis=redis, key='speed')

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


def job():
    data.append(get_speed())


def run_job():
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_daemon():
    with daemon.DaemonContext(
        umask=0o002,
        pidfile=pidfile.TimeoutPIDLockFile(PID_FILE),
        ) as context:
            run_job()


if __name__ == "__main__":
    print('redis')
    parser = argparse.ArgumentParser(description="Speed test")
    parser.add_argument('-d', '--daemon', action='store_true', default=False, help='Run as a daemon')

    args = parser.parse_args()
    schedule.every(10).minutes.do(job)

    if args.daemon:
        print('run as daemon')
        start_daemon()
    else:
        run_job()
