if [ "$1" == "" ]; then
	echo "Need 2 parameters"
	exit 127
fi
if [ "$2" == "" ]; then
	echo "Need 2 parameters"
	exit 127
fi

if [ -f "double-y-percs-base.dat" ]
then
	rm double-y-percs-base.dat
fi
ln -s $1/double-y-percs.dat double-y-percs-base.dat
cp $1/experiment.tex experiment_base.tex
sed -i 's/theexperiment/baseexperiment/' experiment_base.tex
sed -i 's/thecomment/basecomment/' experiment_base.tex

if [ -f "double-y-percs-mod.dat" ]
then
	rm double-y-percs-mod.dat
fi
ln -s $2/double-y-percs.dat double-y-percs-mod.dat
cp $2/experiment.tex experiment_mod.tex
sed -i 's/theexperiment/modexperiment/' experiment_mod.tex
sed -i 's/thecomment/modcomment/' experiment_mod.tex
