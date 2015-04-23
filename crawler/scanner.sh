#bin/bash

echo '>>>>>>>>>>>>>>> Scanner.sh -- Stage 1 & 2 started. <<<<<<<<<<<<<<<<<<<<<'
# Stage 1 & 2
scrapy crawl ${1}_stage12 -a filename=$2 > logs/newstat_${1}_stage12
echo '>>>>>>>>>>>>>>> Scanner.sh -- Stage 1 & 2 ended. <<<<<<<<<<<<<<<<<<<<<'

echo '>>>>>>>>>>>>>>> Scanner.sh -- Stage 3 started. <<<<<<<<<<<<<<<<<<<<<'
# Stage 3
scrapy crawl ${1}_stage3 -a filename=$2 > logs/newstat_${1}_stage3
echo '>>>>>>>>>>>>>>> Scanner.sh -- Stage 3 ended. <<<<<<<<<<<<<<<<<<<<<'
echo '>>>>>>>>>>>>>>> Scanner.sh -- Stage 4 started. <<<<<<<<<<<<<<<<<<<<<'
#Stage 4
rm pycode/*
python stage4_selenium_scripts.py

echo '>>>>>>>>>>>>>>> Scanner.sh ended execution. <<<<<<<<<<<<<<<<<<<<<'
