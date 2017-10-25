"""This program is designed to scrape a designated story from royalroadl.com"""
import argparse
import os
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


ChapterInfo = namedtuple('chapter_info', 'url title html number')

def create_toc(chapters, fiction_name):
    """Calibre requires that we have a TOC for multi-chapter html input"""
    toc_file = open("tmp/"+fiction_name+".html", "w")
    indent = "  "
    toc_file.write("<html>\n")
    toc_file.write(indent*2+"<body>\n")
    toc_file.write(indent*3+"<h1>Table of Contents</h1>\n")
    toc_file.write(indent*3+"<p style='text-indent:0pt'>\n")
    for chap in chapters:
        toc_file.write(indent*4+"<a href='"+chap.title+".html'>"+chap.title+"</a><br/>\n")
    toc_file.write(indent*3+"</p>\n")
    toc_file.write(indent*2+"</body>\n")
    toc_file.write("</html>\n")
    toc_file.close()

def scrape_chapter_text(web_driver, chapt_info):
    """For a particular chapter scrape only the html for the fiction"""
    print chapt_info.url
    web_driver.get(chapt_info.url)
    text_div = web_driver.find_element_by_css_selector("div.chapter-inner")
    fiction_file = open("tmp/"+chapt_info.title+".html", "w")
    fiction_file.write("<html>\n")
    fiction_file.write("<body>\n")
    fiction_file.write(text_div.get_attribute("innerHTML").encode('utf-8'))
    fiction_file.write("</body>\n")
    fiction_file.write("</html>\n")
    fiction_file.close()

def find_all_chapter_urls_titles(web_driver):
    """For a given story find all chapter urls"""
    chapter_infos = []
    chapter_number = 1
    table = web_driver.find_element_by_tag_name("tbody")
    for row in table.find_elements_by_xpath(".//tr"):
        chapter_url = row.get_attribute("data-url")
        for link in row.find_elements_by_xpath(".//a"):
            chapter_infos.append(ChapterInfo(url="https://royalroadl.com"+chapter_url, title=link.text, html="", number=chapter_number))
            chapter_number +=1
            break
    return chapter_infos

def show_all_chapters(web_driver):
    """Make sure to show all chapters so we scrape all of them"""
    num_chapter_shown = Select(web_driver.find_element_by_name("chapters_length"))
    num_chapter_shown.select_by_visible_text('All')

def make_epub_dir(chapters, name):
    """We want to be able to keep track of what chapters are in an epub, so
    this function create a directory in the form #FirstChap_#LastChap"""
    os.makedirs(name)
    first_chapter_number = str(chapters[0].number)
    last_chapter_number = str(chapters[-1].number)
    chapter_dir = name+"/"+"_".join([first_chapter_number, last_chapter_number])
    os.makedirs(chapter_dir)

if __name__ == "__main__":
    # setting the page load strategy to eager means we no longer have
    # to wait for adds to load before we scrape the page
    CAPABILITIES = DesiredCapabilities.PHANTOMJS
    CAPABILITIES["pageLoadStrategy"] = "eager"
    DRIVER = webdriver.PhantomJS(desired_capabilities=CAPABILITIES)
    DRIVER.set_window_size(1920, 1080)
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("TOC_URL", help="""Input the URL for the story you wish
    to create an .epub for. This should be the page that has the TOC""")
    PARSER.add_argument("FICTION_NAME", help="""The name of fiction""")
    ARGS = PARSER.parse_args()
    # go to the webpage
    DRIVER.get(ARGS.TOC_URL)
    # select the show all chapters option
    show_all_chapters(DRIVER)
    # find and record all chapter urls and titles
    CHAPTER_INFOS = find_all_chapter_urls_titles(DRIVER)
    create_toc(CHAPTER_INFOS, ARGS.FICTION_NAME)
    make_epub_dir(CHAPTER_INFOS, ARGS.FICTION_NAME)
    for chapter in CHAPTER_INFOS:
        scrape_chapter_text(DRIVER, chapter)
