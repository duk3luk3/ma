if [ -z "$1" ]
then
	h1='klaipeda'
else
	h1=$1
fi
if [ -z "$2" ]
then
	h2='tartu'
else
	h2=$2
fi
shift
shift
python ~/git/ma/parsing/l2-load-latency/moongen-l2-load-latency.py $h1/output-send-* $h2/output-perf* $* | tee double-y-percs.dat
