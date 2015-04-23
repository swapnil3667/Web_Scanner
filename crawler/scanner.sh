#bin/bash

# Stage 1 & 2
scrapy crawl ${1}_stage12 -a filename=$2 > newstat_${1}_stage12
# Stage 3
scrapy crawl ${1}_stage3 -a filename=$2 > newstat_${1}_stage3
#Stage 4
rm pycode/*
pyhton3 phase4_test.py

