#!/usr/bin/python3

import json
from functools import reduce
from argparse import ArgumentParser, FileType
import numpy
import os

def printline(*args):
  fmt = "{}" + ((len(args)-1) * "{}\t")
  print(fmt.format(*args))


parser = ArgumentParser(description='Parse MoonGen l2-load-latency output')
parser.add_argument('--no-outliers', dest='outliers', action='store_false',
    default=True, help='turn off outlier output')
parser.add_argument('files', metavar='N', action='store', nargs='+',
    help='input files')
parser.add_argument('--cpu', dest='cpughz', action='store', default=2.0,
    type=float, help='CPU Frequency of DUT for Load Calc')

args = parser.parse_args()

mpps_per_mbit = 1 / 64 / 8
cycles_at_full_load = args.cpughz * 10**9  # 3.301GHz

#headers = ['Sent', 'TotalSent','Received','TotalReceived','HistSample', 'HistStats']
loadgen_headers = ['TotalSent','TotalReceived','HistSample', 'Sent', 'TimestampSent', 'TimestampReceived']
datasets = {}

nonempty = lambda s: s != ''
digits = lambda d: d in ['0','1','2','3','4','5','6','7','8','9','.']

for fname in args.files:
  namesplit = os.path.basename(fname)[:-4].split('-')
  with open(fname) as file:
    if 'output-send' in fname:
      run = int(namesplit[2])
      load = float(namesplit[3])
      # convert load if appears to be in mbits
      if load >= 10:
        load = load / (64*8)
      rows = {'offered_load': load}
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
        elif 'irq:irq_handler_entry' in split:
          row.update({'interrupts': split[0]})
      datasets[run]['perf'].append(row)
    elif 'output-dmesg' in fname:
      run = int(namesplit[1][5:])
      if not run in datasets:
        datasets.update({run: {}})
      if not 'dmesg' in datasets[run]:
        datasets[run].update({'dmesg': []})
      for line in file:
        split = list(filter(nonempty, line.split(' ')))
        if len(split) == 18 and 'seen' in split:
          row = {}
          row.update({'packets': ''.join(filter(digits, split[10]))})
          itr = int(split[17])
          if 'bytes' in split:
            if itr == 0:
              itr = 100000
            elif itr == 1:
              itr = 20000
            elif itr == 2:
              itr = 8000
            else:
              continue
          row.update({'itr': itr})
          datasets[run]['dmesg'].append(row)
    else:
      print("Don't know what to do with file {}".format(fname))

#print(json.dumps(datasets, sort_keys=True, indent=4))

runs = sorted(datasets.keys())

avg = lambda s : sum(s) / len(s) if len(s) > 0 else 0
cycles_tr = lambda x: int(x['cycles'].replace(',','')) / cycles_at_full_load / float(x['seconds'])
irq_sel = lambda x: int(x['interrupts'].replace(',','')) / float(x['seconds']) / 1000.0

uniq = lambda xs: filter(lambda x: x is not None, [xs[i] if i == 0 or xs[i-1] != xs[i] else None for i in range(len(xs))])


#print("#Offered Load (mpps)\tavg actual mpps sent\tRTT Lower 1% (us)\tRTT Lower Quartile (us)\tRTT Median (us)\tRTT Upper Quartile (us)\tRTT Upper 99% (us)\tAvg. CPU Load (cycles)\tCPU Load StdDev (cycles)\tInterrupts (kHz)")
#print("x\tload_avg\trtt0\trtt1\trtt2\trtt3\trtt4\tcycles_avg\tcycles_stderr\trtt_nsamples\tnsent\tnrecvd\tfrecvd\tirq_avg\tirq_stderr")
print("#Offered Load (mpps)\tavg actual mpps sent\tRTT Median (us)\tRTT 99th perc.\tAvg. CPU Load (cycles)\tCPU Load StdDev (cycles)\tInterrupts (kHz)")
print("x\tload_avg\trtt0\trtt1\trtt2\trtt3\trtt4\tcycles_avg\tcycles_stderr\trtt_nsamples\tnsent\tnrecvd\tfrecvd\ttsent\ttrecvd\ttfrac\tirq_avg\tirq_stderr\titr_avg\titr_stderr\tcycles_per_pkt")

last_load = 0

for run in runs:
  delays = []
  for sample in datasets[run].get('loadgen', {}).get('HistSample',[]):
    for i in range(int(sample['count'])):
      delays.append(float(sample['delay']) / 1000)

  sent_avg = avg([float(x['rate']) for x in datasets[run].get('loadgen',{}).get('Sent',[])])

  skip = ""
  if sent_avg < last_load:
    skip = "#"

  last_load = sent_avg

  cycles = list(map(cycles_tr, datasets[run]['perf']))

  delay_percs = numpy.percentile(delays, [1,25,50,75,99]) if delays else [0,0,0,0,0]
  cycle_vals = [avg(cycles), numpy.std(cycles)]

  interrupts = list(map(irq_sel, datasets[run]['perf']))
  irq = [avg(interrupts), numpy.std(interrupts)]

  itr_entries = [x['itr'] / 1000 if x['itr'] >= 8000 else 4000000 / x['itr'] / 1000 for x in datasets[run].get('dmesg',[])]
  if len(itr_entries) > 1:
    itr = [avg(itr_entries), numpy.std(itr_entries)]
  else:
    itr = ['nan','nan']

  delay_len = len(delays or [])

  totals = int(datasets[run].get('loadgen', {}).get('TotalSent',[{}])[0].get('packets',0))
  totalr = int(datasets[run].get('loadgen', {}).get('TotalReceived',[{}])[0].get('packets',0))

  totalts = int(datasets[run].get('loadgen', {}).get('TimestampSent',[{}])[0].get('packets',0))
  totaltr = int(datasets[run].get('loadgen', {}).get('TimestampReceived',[{}])[0].get('packets',0))


  cycles_per_packet = 3.3 * cycle_vals[0] / sent_avg if sent_avg > 0 else 0


  #delay_outliers = list(filter(lambda x: x < delay_percs[0] or x > delay_percs[4],uniq(delays))) if delays else []

  offered_load = datasets[run].get('loadgen',{}).get('offered_load',0)

  printline(
    skip,
    offered_load,
    sent_avg,
    delay_percs[0],delay_percs[1],delay_percs[2],delay_percs[3],delay_percs[4],
#    delay_percs[2],delay_percs[4],
    cycle_vals[0], cycle_vals[1],
    delay_len,
    totals, totalr,
    totalr/totals if totals > 0 else 0,
    totalts, totaltr,
    totaltr/totalts if totalts > 0 else 0,
    irq[0], irq[1],
    itr[0], itr[1],
    cycles_per_packet
    )

#  print("{}{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
#    skip,
#    offered_load,
#    sent_avg,
#    delay_percs[0],delay_percs[1],delay_percs[2],delay_percs[3],delay_percs[4],
##    delay_percs[2],delay_percs[4],
#    cycle_vals[0], cycle_vals[1],
#    delay_len,
#    totals, totalr,
#    totalr/totals if totals > 0 else 0,
#    irq[0], irq[1],
#    itr[0], itr[1]
#    ))
