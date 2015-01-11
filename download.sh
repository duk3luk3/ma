name=$(basename $(pwd))
( scp -r kaunas:/srv/www/testbed/results/${name}/klaipeda . || scp -r kaunas:/srv/www/testbed/results/${name}/klaipeda . ) &
( scp -r kaunas:/srv/www/testbed/results/${name}/tartu . || scp -r kaunas:/srv/www/testbed/results/${name}/tartu . ) &
( scp kaunas:/srv/www/testbed/results/config/comment . || scp kaunas:/srv/www/testbed/results/config/comment . )

echo "\newcommand{\theexperiment}{${name}}" | sed 's/_/\\_/g' > experiment.tex
