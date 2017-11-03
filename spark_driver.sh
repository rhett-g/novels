#!/bin/bash

python find_chapter_urls.py $1 > tmp.txt
mkdir tmp
spark-submit spark.py $PWD $2
rm -rf tmp/ tmp.txt *pyc