import argparse
import redislite
from redis_collections import List

import processor

ipaddress = '192.168.10.150'
port = '8002'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Speedtest quicktest")
    parser.add_argument('-a', '--address', help='Remote IP address')
    parser.add_argument('-p', '--port', help='Remote port')

    args = parser.parse_args()

    if args.address:
        ipaddress = args.address

    if args.port:
        port = args.port

    slave = '{} {}'.format(ipaddress, port)
    print slave
    #rc = redislite.StrictRedis(serverconfig={'slaveof': slave})
    rc = redislite.StrictRedis(host = ipaddress, port = port)
    lst = List(redis=rc, key='speed')

    print "Keys in redis: ", rc.keys()
    print "No of items in redis: ", len(lst)
    print "Weekly speed\n", processor.average_speed_weekly(lst)
