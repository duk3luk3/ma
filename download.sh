name=$1
h1=$2
h2=$3
if [[ "$h1x" == "x" ]]
then
	h1='klaipeda'
fi
if [[ "$h2x" == "x" ]]
then
	h2='tartu'
fi

echo "Downloading $h1 and $h2"

mkdir $name
cd $name
( scp -r kaunas:/srv/www/testbed/results/${name}/$h1 . || scp -r kaunas:/srv/www/testbed/results/${name}/$h1 . ) &
( scp -r kaunas:/srv/www/testbed/results/${name}/$h2 . || scp -r kaunas:/srv/www/testbed/results/${name}/$h2 . ) &
( scp kaunas:/srv/www/testbed/results/${name}/config/comment . || scp kaunas:/srv/www/testbed/results/${name}/config/comment . ) &
wait

echo "\newcommand{\theexperiment}{${name}}" | sed 's/_/\\_/g' > experiment.tex
comment=$(tail -n 1 comment)
echo "\newcommand{\thecomment}{${comment}}" | sed 's/_/\\_/g' >> experiment.tex

cd ..
