from collections import defaultdict
from functools import partial

def _group_key(f, iterable):
  return ({'group': f(i), 'upload': i['upload'], 'download': i['download'], 'ping': i['ping']} for i in iterable)

def _group_fn(acc, data):
  # reduce function
  k = data['group']
  acc[k].append(data)

  return acc

def average_speed(grouping_fn, iterable):
  grouped = defaultdict(list)
  reduce(_group_fn, _group_key(grouping_fn, iterable), grouped)

  avg =defaultdict(dict)

  for k, v in grouped.items():
    l = len(v)
    avg[k]['upload'] = sum((i['upload'] for i in v)) / l
    avg[k]['download'] = sum((i['download'] for i in v)) / l
    avg[k]['ping'] = sum((i['ping'] for i in v)) / l

  return avg

average_speed_hourly = partial(average_speed, lambda v: v['timestamp'].strftime('%Y%m%d%H'))
average_speed_daily = partial(average_speed, lambda v: v['timestamp'].strftime('%Y%m%d'))
average_speed_weekly = partial(average_speed, lambda v: '{}{}'.format(v['timestamp'].year, v['timestamp'].isocalendar()[1]))
average_speed_montly = partial(average_speed, lambda v: v['timestamp'].strftime('%Y%m'))
