# novels
This repo is to scrape certain websites for their fictions and compile them into an epub format using selenium for scraping and calibre for epub packing

## Requirements
1. Selenium
```shell
sudo -H pip install selenium
```

2.  Gecko Driver
Firefox
```shell
wget https://github.com/mozilla/geckodriver/releases/download/v0.19.0/geckodriver-v0.19.0-linux64.tar.gz
tar -xzvf geckodriver-v0.19.0-linux64.tar.gz
rm -rf geckodriver-v0.19.0-linux64.tar.gz
sudo ln -sf geckodriver /usr/bin/
```
3. PhantomJS Driver
```shell
sudo apt-get update
sudo apt-get install build-essential chrpath libssl-dev libxft-dev
sudo apt-get install libfreetype6 libfreetype6-dev
sudo apt-get install libfontconfig1 libfontconfig1-dev
export PHANTOM_JS="phantomjs-2.1.1-linux-x86_64"
wget https://bitbucket.org/ariya/phantomjs/downloads/$PHANTOM_JS.tar.bz2
sudo tar xvjf $PHANTOM_JS.tar.bz2
rm -rf $PHANTOM_JS.tar.bz2
sudo mv $PHANTOM_JS /usr/local/share
sudo ln -sf /usr/local/share/$PHANTOM_JS/bin/phantomjs /usr/local/bin
```

3. Calibre
```shell
sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.py | sudo python -c "import sys; main=lambda:sys.stderr.write('Download failed\n'); exec(sys.stdin.read()); main()"
```

## Requirements for Spark

1. Java

```shell
sudo apt-get update
sudo apt-get install default-jdk
```

2. Spark

```shell
sudo -H pip install pyspark
```

## How to run
Regular Version
```shell
./driver.py urlOfFirstChapter fictionName
```

Spark Version
```shell
spark-submit urlOfLatestChapter fictionName
```

## Spark vs Regular 
Spark shows a 40% decrease in time over the regular version for 50 chapter test and a 60% decrease over 1300 chapters on a 4 core computer. Note that partitions should be increased/decreased to better optimize for the number of cores one has.

## Desired Features

1. Splitting epubs into books based on urls

2. Handling chapter titles

3. Take out calibre and spark

## Supported Sites
* www.wuxiaworld.com
* www.royalroadl.com
* www.gravitytales.com
* www.lightnovelbastion.com

### Planned Sites
* www.bluesilvertranslations.com
