#!/bin/sh

cd wuxiaWorld
mkdir tmp
python wuxia_world.py $1
cd tmp
ebook-convert TOC.html ../$2.epub
cd ..
rm -rf tmp
rm -rf *.log
mv $2.epub ~/Dropbox
