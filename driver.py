"""This program is made to identify what website we are scraping from
and initiate the correct scraper"""
import argparse
import os
from next_chapter import *
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def select_driver(url, title, driver):
    """A switch statement that parses the url to find the correct
    driver for a website and return the command subprocess will
    use to call the bash script"""
    driver.get(url)
    if "royalroad" in url:
        print "Fiction is from Royal Road"
        next_chapter_driver(driver, title, "//div[@class='chapter-inner chapter-content']")
    elif "wuxiaworld" in url.lower():
        print "Fiction is from Wuxia World"
        next_chapter_driver(driver, title, "//div[@itemprop='articleBody']")
    elif "gravitytales" in url.lower():
        print "Fiction is from Gravity Tales"
        next_chapter_driver(driver, title, "//div[@id='chapterContent']")
    else:
        print "We have not implemented a scraper for this website"

def next_chapter_driver(web_driver, title, element):
    """This is the driver for fictions that have a next chapter button"""
    chapter_count = 1
    # while there is a next chapter scrape it's text
    while chapter_text_exists(web_driver, element):
        scrape_chapter_text(web_driver, chapter_count, element)
        if next_chapter_exists(web_driver):
            click_next_chapter(web_driver)
            chapter_count += 1
            continue
        break
    # create the toc so calibre can create the epub
    create_toc(chapter_count, title)
    make_epub_dir(chapter_count, title)


if __name__ == "__main__":
    # setting the page load strategy to eager means we no longer have
    # to wait for adds to load before we scrape the page
    CAPABILITIES = DesiredCapabilities.PHANTOMJS
    CAPABILITIES["pageLoadStrategy"] = "eager"
    DRIVER = webdriver.PhantomJS(desired_capabilities=CAPABILITIES)
    # set window size so we load desktop version

    DRIVER.set_window_size(1920, 1080)
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("URL", help="""Input the URL for the story you wish
    to create an .epub for. This should be the page that has the TOC for royal
    road and whatever chapter you wish to start from in wuxia world""")
    PARSER.add_argument("FICTION_NAME", help="The name of the fiction")
    ARGS = PARSER.parse_args()
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    select_driver(ARGS.URL, ARGS.FICTION_NAME, DRIVER)
