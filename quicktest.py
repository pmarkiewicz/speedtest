import redislite
from redis_collections import List

import processor

if __name__ == "__main__":
    rc = redislite.StrictRedis(serverconfig={'slaveof': 'localhost 8002'})
    lst = List(redis=rc, key='speed')

    print "Keys in redis: ", rc.keys()
    print "No of items in redis: ", len(lst)
    print "Weekly speed\n", processor.average_speed_weekly(lst)
