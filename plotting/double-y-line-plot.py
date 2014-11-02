import json
import sys
import string

latex_plot = """
\\documentclass[class=minimal,border=0pt]{standalone}

\\usepackage{pgfplots}
\\pgfplotsset{compat=newest}
\\pgfplotsset{grid style={dotted}}
\\usetikzlibrary{plotmarks}
\\begin{document}
\\tikzset{every mark/.append style={scale=0.9}}

%%\\pgfplotsset{
%%    every first x axis line/.style={},
%%    every first y axis line/.style={},
%%    every first z axis line/.style={},
%%    every second x axis line/.style={},
%%    every second y axis line/.style={},
%%    every second z axis line/.style={},
%%    first x axis line style/.style={/pgfplots/every first x axis line/.append style={#1}},
%%    first y axis line style/.style={/pgfplots/every first y axis line/.append style={#1}},
%%    first z axis line style/.style={/pgfplots/every first z axis line/.append style={#1}},
%%    second x axis line style/.style={/pgfplots/every second x axis line/.append style={#1}},
%%    second y axis line style/.style={/pgfplots/every second y axis line/.append style={#1}},
%%    second z axis line style/.style={/pgfplots/every second z axis line/.append style={#1}}
%%}
%%
%%\\makeatletter
%%\\def\pgfplots@drawaxis@outerlines@separate@onorientedsurf#1#2{%
%%    \\if2\csname pgfplots@#1axislinesnum\endcsname
%%        % centered axis lines handled elsewhere.
%%    \\else
%%    \\scope[/pgfplots/every outer #1 axis line,
%%        #1discont,decoration={pre length=\\csname #1disstart\endcsname, post length=\csname #1disend\endcsname}]
%%        \\pgfplots@ifaxisline@B@onorientedsurf@should@be@drawn{0}{%
%%            \\draw [/pgfplots/every first #1 axis line] decorate {
%%                \\pgfextra
%%                % exchange roles of A <-> B axes:
%%                \\pgfplotspointonorientedsurfaceabsetupfor{#2}{#1}{\pgfplotspointonorientedsurfaceN}%
%%                \\pgfplots@drawgridlines@onorientedsurf@fromto{\csname pgfplots@#2min\endcsname}%
%%                \\endpgfextra 
%%                };
%%        }{}%
%%        \\pgfplots@ifaxisline@B@onorientedsurf@should@be@drawn{1}{%
%%            \\draw [/pgfplots/every second #1 axis line] decorate {
%%                \\pgfextra
%%                % exchange roles of A <-> B axes:
%%                \\pgfplotspointonorientedsurfaceabsetupfor{#2}{#1}{\pgfplotspointonorientedsurfaceN}%
%%                \\pgfplots@drawgridlines@onorientedsurf@fromto{\csname pgfplots@#2max\endcsname}%
%%                \\endpgfextra 
%%                };
%%        }{}%
%%    \\endscope
%%    \\fi
%%}%
%%\makeatother

\\begin{tikzpicture}
  \\begin{axis}[
    axis line style = blue,
    every axis label/.append style ={blue},
    every tick label/.append style ={blue},
    xmin = ${xmin}, xmax = ${xmax},
    ymin = ${y0min}, ymax = ${y0max},
    axis y line* = left,
    ylabel = {${y0label}},
    hide x axis
  ]
  \\addplot[red] table[x=x, y=y0
  ]{${data}};
  \\end{axis}
  \\begin{axis}[
    xmin = ${xmin}, xmax = ${xmax},
    ymin = ${y1min}, ymax = ${y1max},
    xlabel = {${xlabel}},
    hide y axis,
  ]
  \\addplot[blue] table[x=x, y=y1
  ]{${data}};
  \\end{axis}
  \\begin{axis}[
    axis line style = red,
    every axis label/.append style ={red},
    every tick label/.append style ={red},
    xmin = 0, xmax = 1,
    ymin = ${y1min}, ymax = ${y1max},
    hide x axis,
    axis y line* = right,
    ylabel = {${y1label}},
    ylabel near ticks
  ]
  \\end{axis}
\\end{tikzpicture}

\\end{document}
"""

config = json.load(sys.stdin)

template = string.Template(latex_plot)

print(template.substitute(
  **config
  ))
