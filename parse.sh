h1=$1
h2=$2
if [ "$h1x" == "x" ]
then
	h1='klaipeda'
fi
if [ "$h2x" == "x" ]
then
	h2='tartu'
fi
python ~/git/ma/parsing/l2-load-latency/moongen-l2-load-latency.py $h1/output-send-* $h2/output-perf* | tee double-y-percs.dat
