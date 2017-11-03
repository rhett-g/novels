from pyspark import SparkContext, SparkConf
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from next_chapter import go_to_page, scrape_chapter_text
from driver import make_epub
import sys


def get_article_element(url):
    """Returns the element for which the fiction text lives in"""
    if "royalroad" in url:
        return"//div[@class='chapter-inner chapter-content']"
    elif "wuxiaworld" in url.lower():
        return "//div[@itemprop='articleBody']"
    elif "gravitytales" in url.lower():
        return "//div[@id='chapterContent']"
    elif "bastion" in url.lower():
        return"//section[@class='box style1 blacktext']"
    else:
        print "We have not implemented a scraper for this website"


def spark_driver(urls):
    """Using foreachPartitions as initializing the selenium driver is
    expensive as such we pass in a partition of urls and their chap
    numbers in the form chap_num:url"""
    # set up selenium
    CAPABILITIES = DesiredCapabilities.PHANTOMJS
    CAPABILITIES["pageLoadStrategy"] = "eager"
    DRIVER = webdriver.PhantomJS(desired_capabilities=CAPABILITIES)
    DRIVER.set_page_load_timeout(30)
    # set window size so we load desktop version
    DRIVER.set_window_size(1920, 1080)
    # set up max we so know what the latest chap num is
    max_chap = 0
    first = True
    for url in urls:
        chap_num = url.split("||")[0]
        url = url.split("||")[1]
        if first:
            element = get_article_element(url)
            first = False
        go_to_page(DRIVER, url)
        scrape_chapter_text(DRIVER, chap_num, element)
        if int(chap_num) > max_chap:
            max_chap = int(chap_num)
    DRIVER.close()
    return max_chap


def make_epubs(max, name):
    current_chap = max
    while current_chap != 0:
        current_chap = make_epub(current_chap, name)


if __name__ == "__main__":
    # arg parsing
    TEXT_FILE = sys.argv[1]
    FICTION_NAME = sys.argv[2]
    conf = SparkConf()
    conf.setAppName('novel').setMaster("local[*]")
    sc = SparkContext(conf=conf)
    CHAPTERS_RDD = sc.textFile("file://" + TEXT_FILE + "/tmp.txt", 24)
    MAX_RDD = CHAPTERS_RDD.foreachPartition(spark_driver)
    MAX = MAX_RDD.max()
    sc.stop()
    make_epubs(305, FICTION_NAME)
