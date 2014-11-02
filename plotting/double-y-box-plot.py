#!/usr/bin/python3

import json
import sys
import string

latex_plot = """
\\documentclass[class=minimal,border=0pt]{standalone}

\\usepackage{pgfplots}
\\pgfplotsset{compat=newest}
\\pgfplotsset{grid style={dotted}}
\\usetikzlibrary{plotmarks}
\\usepgfplotslibrary{statistics}
\\begin{document}
\\tikzset{every mark/.append style={scale=0.9}}

\\begin{tikzpicture}
  \\begin{axis}[
    boxplot/draw direction=y,
    axis line style = blue,
    every axis label/.append style ={blue},
    every tick label/.append style ={blue},
    xmin = ${xmin}, xmax = ${xmax},
    xticklabels = {${xticks}},
    axis y line* = left,
    ylabel = {${y0label}},
    hide x axis
  ]
${plot0}
  \\end{axis}
  \\begin{axis}[
    boxplot/draw direction=y,
    xmin = ${xmin}, xmax = ${xmax},
    xlabel = {${xlabel}},
    hide y axis,
  ]
${plot1}
  \\end{axis}
  \\begin{axis}[
    axis line style = red,
    every axis label/.append style ={red},
    every tick label/.append style ={red},
    xmin = 0, xmax = 1,
    hide x axis,
    axis y line* = right,
    ylabel = {${y1label}},
    ylabel near ticks
  ]
  \\end{axis}
\\end{tikzpicture}

\\end{document}
"""

plot_tpl = string.Template("""
    \\addplot+[
      red,
      boxplot prepared={
        lower whisker=${low_whisker}, lower quartile=${low_quartile},
        median=${median},
        upper quartile=${high_quartile}, upper whisker=${high_whisker}
      },
    ]
    coordinates{};
""")

config = json.load(sys.stdin)

plot0 = []
plot1 = []
xmin = 1
xmax = len(config)
xticks = []
y0label = 'RTT (usecs)'
y1label = 'CPU load (fractional)'
xlabel = 'Offered load (MPkt/s)'

for run in config:
  xticks.append(str(run['offered_load']))

  if run['delays']:
    plot0.append(plot_tpl.substitute(**run['delays']))
  if run['cycles']:
    plot1.append(plot_tpl.substitute(**run['cycles']))

template = string.Template(latex_plot)

print(template.substitute(
  {
    'xmin': xmin,
    'xmax': xmax,
    'xticks': ", ".join(xticks),

    'y0label': y0label,
    'y1label': y1label,
    'xlabel': xlabel,

    'plot0': "\n".join(plot0),
    'plot1': "\n".join(plot1),
  }
  ))
