rm double-y-percs-base.dat
ln -s $1/double-y-percs.dat double-y-percs-base.dat
cp $1/experiment.tex experiment_base.tex
sed -i 's/theexperiment/baseexperiment/' experiment_base.tex
