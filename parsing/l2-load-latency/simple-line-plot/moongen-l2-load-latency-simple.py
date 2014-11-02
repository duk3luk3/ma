#!/usr/bin/python3

import json
from functools import reduce
from argparse import ArgumentParser, FileType
import matplotlib.pyplot as plt
import os


parser = ArgumentParser(description='Parse MoonGen l2-load-latency output')
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
cycles = lambda x: int(x['cycles'].replace(',','')) / cycles_at_full_load

for run in runs:
  try:
    cpu_cycles.append(avg(list(map(cycles, datasets[run]['perf']))))
    offered_loads.append(datasets[run]['loadgen']['offered_load'])
    delays.append(float(datasets[run]['loadgen']['HistStats'][0]['average']))
  except KeyError:
    if run == 0:
      delays.append(0.0)
      offered_loads.append(0)
    else:
      print(run)
      print(datasets[run])
      raise

print("#Offered Load (mpps); Avg RTT (us); CPU Load (cycles)")
print("x\ty0\ty1")

for i in range(len(offered_loads)):
  print("{}\t{}\t{}".format(offered_loads[i], delays[i], cpu_cycles[i]))
