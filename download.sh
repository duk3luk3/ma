name=$(basename $(pwd))
( scp -r kaunas:/srv/www/testbed/results/${name}/klaipeda . || scp -r kaunas:/srv/www/testbed/results/${name}/klaipeda . ) &
( scp -r kaunas:/srv/www/testbed/results/${name}/tartu . || scp -r kaunas:/srv/www/testbed/results/${name}/tartu . ) &
( scp kaunas:/srv/www/testbed/results/${name}/config/comment . || scp kaunas:/srv/www/testbed/results/${name}/config/comment . ) &
wait

echo "\newcommand{\theexperiment}{${name}}" | sed 's/_/\\_/g' > experiment.tex
comment=$(tail -n 1 comment)
echo "\newcommand{\thecomment}{${comment}}" | sed 's/_/\\_/g' >> experiment.tex
