import os
import json
import yaml
import locale
import calendar
import itertools
from collections import Counter

locale.setlocale(locale.LC_ALL, 'it_IT')
files_path = os.path.dirname(os.path.realpath(__file__))
matters_path = os.path.join(files_path, 'materie')
config = yaml.load(open(os.path.join(files_path, 'timetable.yaml')), Loader=yaml.FullLoader)

def deduplicate(obj):
    try:
        return obj.copy()
    except:
        return obj

def empty_schedule(null_type):
    return {days: [deduplicate(null_type) for hours in config['timetable']] for days in config['weekdays']}

def weekday_fix(day):
    return (day)%7

def make_schedule(timelist):
    this_schedule = empty_schedule(False).copy()
    for lesson in timelist:
        for i in range(lesson['start'], lesson['start'] + lesson['duration']):
            this_schedule[weekday_fix(lesson['day'])][i] = True
    return this_schedule

def schedule_overlap(schedules):
    full_schedule = empty_schedule([])
    for matter, schedule in schedules.items():
        for day, hours in schedule.items():
            for hour, presence in enumerate(hours):
                if presence == True:
                    full_schedule[day][hour].append(matter)
    
    return full_schedule

def common_entries(*dcts):
    if not dcts:
        return
    for i in set(dcts[0]).intersection(*dcts[1:]):
        yield (i,) + tuple(d[i] for d in dcts)


def find_overlaps(overlapped):
    overlaps = []
    repeats = []

    for v in overlapped.values():
        for w in v:
            if len(w) > 1:
                overlaps.append(w)
                for z in w:
                    repeats.append(z)

    return {m: repeats.count(m) for m in schedules.keys()}

def all_subsets(ss, least=1):
    return [list(l) for l in itertools.chain(*map(lambda x: itertools.combinations(ss, x), range(least, len(ss)+1)))]

def draw_day_cycle(day_array):
    return ''.join(['-' if len(h) == 0 else '#' if len(h) == 1 else str(len(h)) for h in day_array])

def draw_day_matters(day_array):
    return [t['start'] + t['end'] + ', '.join(m) for t, m in zip(config['timetable'], day_array) if len(m) > 0]

def count_overlaps(schedule):
    tot = {}
    for d in schedule.values():
        dh = dict(Counter([len(m) for m in d]))
        for k, v in dh.items():
            if k in tot:
                tot[k] += v
            else:
                tot[k] = v
    return tot    

def valuate(benchmark, matters_qta):
    malus = sum([count*2**(amount-1) for amount, count in benchmark.items() if amount > 1])
    return matters_qta*(benchmark.get(1, 0) - malus)

#MAIN
schedules = {}

for pos_json in os.listdir(matters_path):
    if pos_json.endswith('.json'):
        with open(os.path.join(matters_path, pos_json)) as json_file:
            json_text = json.load(json_file)
            schedules[json_text['name']] = make_schedule(json_text['lessions'])

set_stats = [(subset, schedule_overlap({k:v for k, v in schedules.items() if k in subset})) for subset in all_subsets(schedules.keys(), least=2)]

def sorter(e):
    return valuate(count_overlaps(e[1]), len(e[0]))

set_stats.sort(key=sorter)

print('INITIALIZING OVERLAPPING SOFTWARE')
print('FOUND:', len(schedules), 'MATTERS')
print('OVERLAPPING:', ', '.join(schedules.keys()))
print('FOUND', len(set_stats), 'COMBINATIONS')

for subset, schedule in set_stats:
    print()
    print('SUBSET ' + str(len(subset)) + 'X:', subset)

    repeats = find_overlaps(schedule)
    overlaps_count = count_overlaps(schedule)

    print('benchmark:', valuate(overlaps_count, len(subset)))
    print(overlaps_count)
    for day, h in schedule.items():
        print(draw_day_cycle(h))

    print('overlap time:', sum(repeats.values()))
    print('repeats:', repeats)

print()
print()
print('TOP SCORE:', valuate(count_overlaps(set_stats[-1][1]), len(set_stats[-1][0])))
print()
print('BEST SOLUTIONS:')
for top in reversed(set_stats[-10:]):
    print('MATTERS:', len(top[0]), '\tSCORE:', valuate(count_overlaps(top[1]), len(top[0])), '\t', ', '.join(top[0]))