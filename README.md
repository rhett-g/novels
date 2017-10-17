# novels
This repo is to scrape certain websites for their fictions and compile them into an epub format using selenium for scraping and calibre for epub packing

## Requirements
1. Selenium
```shell
sudo -H pip install selenium
```

2. Gecko Driver
Linux
```shell
wget https://github.com/mozilla/geckodriver/releases/download/v0.19.0/geckodriver-v0.19.0-linux64.tar.gz
tar -xzvf geckodriver-v0.19.0-linux64.tar.gz
rm -rf geckodriver-v0.19.0-linux64.tar.gz
sudo mv geckodriver /usr/bin/
```
Windows
Download the zip, extract exe, and run
https://github.com/mozilla/geckodriver/releases/download/v0.19.0/geckodriver-v0.19.0-win64.zip

3. Calibre
