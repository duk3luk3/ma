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
\\pgfplotsset{every axis legend/.append style={at={(-.02,1)}, anchor=south east}}
  \\begin{axis}[
%    axis line style = blue,
%    every axis label/.append style ={blue},
%    every tick label/.append style ={blue},
    xmin = ${xmin}, xmax = ${xmax},
%    xticklabels = {${xticks}},
    axis y line* = left,
    ylabel = {${y0label}},
    hide x axis,
    legend cell align=left,
%    ymode=log,
  ]
${plot0}
  \\end{axis}
  \\begin{axis}[
    xmin = ${xmin}, xmax = ${xmax},
    xlabel = {${xlabel}},
    hide y axis,
    legend cell align=left,
  ]
\\pgfplotsset{every axis legend/.append style={at={(1.02,1)}, anchor=south west}}
${plot1}
  \\end{axis}
  \\begin{axis}[
%    axis line style = red,
%    every axis label/.append style ={red},
%    every tick label/.append style ={red},
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
  \\addplot[${linestyle}] table[x=load_avg, y=${ycol}]{${data}};
  \\addlegendentry{${label}}
""")
plot_err_tpl = string.Template("""
  \\addplot[
    solid,
    mark=x,
    error bars/.cd, y dir=both, y explicit
  ] table[x=x, y=${ycol}, y error={${errcol}}]{${data}};
  \\addlegendentry{${label}}
""")

plot0 = []
plot1 = []
xmin = -0.2
xmax = 3
#xticks = []
y0label = 'RTT (nsecs)'
y1label = 'Interrupts'
xlabel = 'Offered load (MPkt/s)'

percentile_plots = {
#'rtt0' : [ 'RTT Lower 1.5\\%', 'dotted'],
#'rtt1' : [ 'RTT Lower Quartile', 'dashed'],
'rtt2' : [ 'RTT Median', 'solid'],
#'rtt3' : [ 'RTT Upper Quartile', 'dashed'],
'rtt4' : [ 'RTT Upper 1.5\\%', 'dotted']
}

for col in sorted(percentile_plots.keys()):
  label = percentile_plots[col][0]
  style = percentile_plots[col][1]
  plot0.append(
    plot_tpl.substitute(
      linestyle=style,
      ycol=col,
      data='double-y-percs.dat',
      label=label
    )
  )

plot1.append(
  plot_err_tpl.substitute(
    ycol='irq_avg',
    errcol='irq_stderr',
    data='double-y-percs.dat',
    label='Interrupts'
  )
)

template = string.Template(latex_plot)

print(template.substitute(
  {
    'xmin': xmin,
    'xmax': xmax,
#    'xticks': ", ".join(xticks),
    'xticks': "",

    'y0label': y0label,
    'y1label': y1label,
    'xlabel': xlabel,

    'plot0': "\n".join(plot0),
    'plot1': "\n".join(plot1),
  }
  ))
