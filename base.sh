if [ -f "double-y-percs-base.dat" ]
then
	rm "double-y-percs-base.dat"
fi
ln -s $1/double-y-percs.dat double-y-percs-base.dat
cp $1/experiment.tex experiment_base.tex
sed -i 's/theexperiment/baseexperiment/' experiment_base.tex
sed -i 's/thecomment/basecomment/' experiment_base.tex
