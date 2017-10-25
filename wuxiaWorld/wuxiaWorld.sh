#!/bin/sh

python wuxiaWorld/wuxia_world.py $1 $2
ebook-convert tmp/$2.html $2.epub
mv $2.epub $2/*/
cp -rl $2 ~/Dropbox/novels
rm -rf *.log tmp $2
