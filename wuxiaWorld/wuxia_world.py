"""This program is designed to scrape a designated story from royalroadl.com"""
import argparse
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def create_toc(chapter_count):
    """Calibre requires that we have a TOC for multi-chapter html input"""
    toc_file = open("tmp/TOC.html", "w")
    indent = "  "
    toc_file.write("<html>\n")
    toc_file.write(indent*2+"<body>\n")
    toc_file.write(indent*3+"<h1>Table of Contents</h1>\n")
    toc_file.write(indent*3+"<p style='text-indent:0pt'>\n")
    for i in xrange(0,chapter_count):
        toc_file.write(indent*4+"<a href='"+str(i)+".html'>"+str(i)+"</a><br/>\n")
    toc_file.write(indent*3+"</p>\n")
    toc_file.write(indent*2+"</body>\n")
    toc_file.write("</html>\n")
    toc_file.close()

def remove_chapter_links(chapter_text):
    """We don't want the next and previous chapter in our text, which is the first and last
    lines in the articleBody"""
    lines = chapter_text.split("</p>")
    return map(lambda line: line+"</p>", lines[1:-2])

def click_next_chapter(web_driver):
    """Click the next chapter button"""
    web_driver.find_element_by_partial_link_text("Next Chapter").click()

def next_chapter_exists(web_driver):
    """If there is a next chapter button then we know that there is text worth scraping
    on this page"""
    try:
        web_driver.find_element_by_partial_link_text("Next Chapter")
    except NoSuchElementException:
        return False
    return True

def scrape_chapter_text(web_driver, chapter_count):
    """For a particular chapter scrape only the html for the fiction"""
    article = web_driver.find_element_by_xpath("//div[@itemProp='articleBody']")
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

if __name__ == "__main__":
    DRIVER = webdriver.Firefox()
    # DRIVER.set_window_size(1920, 1080)
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("FIRST_CHAPTER", help="""Input the URL for the story
    you wish to create an .epub for. This should be the first chapter of the
    fiction""")
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
    create_toc(CHAPTER_COUNT)
