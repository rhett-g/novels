"""This program is designed to scrape a designated story from royalroadl.com"""
import argparse
import time
from calibre import chapter_info, create_toc
from selenium import webdriver
from selenium.webdriver.support.ui import Select

# from selenium.webdriver.common.keys import Keys

def scrape_chapter_text(web_driver, chapt_info):
    """For a particular chapter scrape only the html for the fiction"""
    print chapt_info.url
    web_driver.get(chapt_info.url)
    time.sleep(3)
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
    table = web_driver.find_element_by_tag_name("tbody")
    for row in table.find_elements_by_xpath(".//tr"):
        chapter_url = row.get_attribute("data-url")
        for link in row.find_elements_by_xpath(".//a"):
            chapter_infos.append(chapter_info(url="https://royalroadl.com"+chapter_url, title=link.text, html=""))
            break
    return chapter_infos

def show_all_chapters(web_driver):
    """Make sure to show all chapters so we scrape all of them"""
    num_chapter_shown = Select(web_driver.find_element_by_name("chapters_length"))
    num_chapter_shown.select_by_visible_text('All')

if __name__ == "__main__":
    DRIVER = webdriver.PhantomJS()
    DRIVER.set_window_size(1920,1080)
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("TOC_URL", help="""Input the URL for the story you wish
    to create an .epub for. This should be the page that has the TOC""")
    ARGS = PARSER.parse_args()
    # go to the webpage
    DRIVER.get(ARGS.TOC_URL)
    # select the show all chapters option
    show_all_chapters(DRIVER)
    # find and record all chapter urls and titles
    CHAPTER_INFOS = find_all_chapter_urls_titles(DRIVER)
    create_toc(CHAPTER_INFOS)
    for chapter in CHAPTER_INFOS:
        scrape_chapter_text(DRIVER, chapter)

