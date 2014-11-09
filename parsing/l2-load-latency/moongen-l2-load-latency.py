#!/usr/bin/python3

import json
from functools import reduce
from argparse import ArgumentParser, FileType
import numpy
import os


parser = ArgumentParser(description='Parse MoonGen l2-load-latency output')
parser.add_argument('--no-outliers', dest='outliers', action='store_false',
    default=True, help='turn off outlier output')
parser.add_argument('files', metavar='N', action='store', nargs='+',
    help='input files')

args = parser.parse_args()

mpps_per_mbit = 1 / 64 / 8
cycles_at_full_load = 3.301 * 10**9 * 10 # 3.301GHz times 10 seconds

#headers = ['Sent', 'TotalSent','Received','TotalReceived','HistSample', 'HistStats']
loadgen_headers = ['TotalSent','TotalReceived','HistSample']
datasets = {}

nonempty = lambda s: s != ''

for fname in args.files:
  namesplit = os.path.basename(fname)[:-4].split('-')
  with open(fname) as file:
    if 'output-send' in fname:
      run = int(namesplit[2])
      rows = {'offered_load': int(namesplit[3]) * mpps_per_mbit}
      for line in file:
        split = line.split(',')
        if split[0] in loadgen_headers:
          if not split[0] in rows:
            rows.update({split[0]: []})
          row = {}
          for column in split[1:]:
            s = column.split('=')
            row.update({s[0]: s[1]})
          rows[split[0]].append(row)
      if not run in datasets:
        datasets.update({run: {}})
      datasets[run].update({'loadgen': rows})
    elif 'output-perf' in fname:
      run = int(namesplit[1][4:])
      if not run in datasets:
        datasets.update({run: {}})
      if not 'perf' in datasets[run]:
        datasets[run].update({'perf': []})
      row = {}
      for line in file:
        split = list(filter(nonempty, line.split(' ')))
        if 'cycles' in split:
          row.update({'cycles': split[0]})
        elif 'seconds' in split:
          row.update({'seconds': split[0]})
      datasets[run]['perf'].append(row)
    else:
      print("Don't know what to do with file {}".format(fname))

#print(json.dumps(datasets, sort_keys=True, indent=4))

runs = sorted(datasets.keys())

offered_loads = []
delays = []
cpu_cycles = []

avg = lambda s : sum(s) / len(s)
cycles_tr = lambda x: int(x['cycles'].replace(',','')) / cycles_at_full_load

uniq = lambda xs: filter(lambda x: x is not None, [xs[i] if i == 0 or xs[i-1] != xs[i] else None for i in range(len(xs))])

document = []

for run in runs:
  delays = []
  for sample in datasets[run].get('loadgen', {}).get('HistSample',[]):
    for i in range(int(sample['count'])):
      delays.append(float(sample['delay']))

  cycles = list(map(cycles_tr, datasets[run]['perf']))

  delay_percs = numpy.percentile(delays, [1.5,25,50,75,98.5]) if delays else []
  cycle_percs = numpy.percentile(cycles, [1.5,25,50,75,98.5])

  delay_outliers = list(filter(lambda x: x < delay_percs[0] or x > delay_percs[4],uniq(delays))) if delays else []
  cycle_outliers = list(filter(lambda x: x < cycle_percs[0] or x > cycle_percs[4],uniq(cycles)))


  document.append({
    'run': run,
    'offered_load': datasets[run].get('loadgen', {}).get('offered_load', 0),
    'delays': {'low_whisker': delay_percs[0], 'low_quartile': delay_percs[1], 'median': delay_percs[2], 'high_quartile': delay_percs[3], 'high_whisker': delay_percs[4] } if delays else {},
    'cycles': {'low_whisker': cycle_percs[0], 'low_quartile': cycle_percs[1], 'median': cycle_percs[2], 'high_quartile': cycle_percs[3], 'high_whisker': cycle_percs[4] } if cycles else {},
    'delay_outliers': delay_outliers if args.outliers else [],
    'cycle_outliers': cycle_outliers if args.outliers else []
    })

print(json.dumps(document, indent=2))