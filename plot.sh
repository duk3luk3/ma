name=$(basename $(pwd))
pdflatex ../testplot-stacked.tex && rm *.log *.aux && mv testplot-stacked.pdf testplot-${name}.pdf
