"""This program is designed to scrape a designated story from royalroadl.com"""
import argparse
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities



def create_toc(chapter_count, fiction_name):
    """Calibre requires that we have a TOC for multi-chapter html input"""
    toc_file = open("tmp/"+fiction_name+".html", "w")
    indent = "  "
    toc_file.write("<html>\n")
    toc_file.write(indent*2+"<body>\n")
    toc_file.write(indent*3+"<h1>Table of Contents</h1>\n")
    toc_file.write(indent*3+"<p style='text-indent:0pt'>\n")
    for i in xrange(0, chapter_count):
        toc_file.write(indent*4+"<a href='"+str(i)+".html'>"+str(i)+"</a><br/>\n")
    toc_file.write(indent*3+"</p>\n")
    toc_file.write(indent*2+"</body>\n")
    toc_file.write("</html>\n")
    toc_file.close()

def remove_chapter_links(chapter_text):
    """We don't want the next and previous chapter in our text,
    which is the first and last lines in the articleBody"""
    lines = chapter_text.split("</p>")
    return map(lambda line: line+"</p>", lines[1:-2])

def click_next_chapter(web_driver):
    """Click the next chapter button"""
    web_driver.find_element_by_partial_link_text("Next Chapter").click()

def next_chapter_exists(web_driver):
    """If there is a next chapter button then we know 
    that there is text worth scraping on this page"""
    try:
        web_driver.find_element_by_partial_link_text("Next Chapter")
    except NoSuchElementException:
        return False
    return True

def scrape_chapter_text(web_driver, chapter_count):
    """For a particular chapter scrape only the html for the fiction"""
    article = web_driver.find_element_by_xpath("//div[@itemprop='articleBody']")
    fiction_file = open("tmp/"+str(chapter_count)+".html", "w")
    fiction_file.write("<html>\n")
    fiction_file.write("<body>\n")
    raw_text = article.get_attribute("innerHTML").encode('utf-8')
    edited_text = remove_chapter_links(raw_text)
    for line in edited_text:
        fiction_file.write(line)
    fiction_file.write("</body>\n")
    fiction_file.write("</html>\n")
    fiction_file.close()

def make_epub_dir(chapter_count, name):
    """We want to be able to keep track of what chapters are in an epub, so
    this function create a directory in the form #FirstChap_#LastChap"""
    os.makedirs(name)
    chapter_dir = name+"/1_"+str(chapter_count)
    os.makedirs(chapter_dir)

if __name__ == "__main__":
    # wuxia world is particularly bad with its adds so loading a page
    # fully can takes up to 10 minutes. For this reason we set the
    # page load strategy to greedy so we don't wait for all the adds
    CAPABILITIES = DesiredCapabilities.PHANTOMJS
    CAPABILITIES["pageLoadStrategy"] = "eager"
    DRIVER = webdriver.PhantomJS(desired_capabilities=CAPABILITIES)
    DRIVER.set_window_size(1920, 1080)
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("FIRST_CHAPTER", help="""Input the URL for the story
    you wish to create an .epub for. This should be the first chapter of the
    fiction""")
    PARSER.add_argument("FICTION_NAME", help="""The name of fiction""")
    ARGS = PARSER.parse_args()
    # go to the webpage
    DRIVER.get(ARGS.FIRST_CHAPTER)
    CHAPTER_COUNT = 0
    # while there is a next chapter scrape it's text
    while next_chapter_exists(DRIVER):
        scrape_chapter_text(DRIVER, CHAPTER_COUNT)
        click_next_chapter(DRIVER)
        CHAPTER_COUNT += 1
    # create the toc so calibre can create the epub
    create_toc(CHAPTER_COUNT, ARGS.FICTION_NAME)
    make_epub_dir(CHAPTER_COUNT, ARGS.FICTION_NAME)
