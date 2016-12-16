import argparse
import redislite
from redis_collections import List, Dict
from datetime import datetime

import processor

host = '192.168.10.150'
port = '8002'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speedtest quicktest")
    parser.add_argument('-t', '--host', help='Remote host address')
    parser.add_argument('-p', '--port', help='Remote port')

    args = parser.parse_args()

    if args.host:
        host = args.host

    if args.port:
        port = args.port

    slave = '{} {}'.format(host, port)
    print slave
    #rc = redislite.StrictRedis(serverconfig={'slaveof': slave})
    rc = redislite.StrictRedis(host = host, port = port)
    lst = List(redis=rc, key='speed')

    print "Keys in redis: ", rc.keys()
    print "No of items in redis['speed']: ", len(lst)
    print "Weekly speed\n", processor.average_speed_weekly(lst)

    settings = Dict(redis=rc, key='settings')
    if settings.get('last_test'):
        print 'Last test: ', settings['last_test']
    else:
        print 'No last run'

    settings['last_test'] = datetime.now()
