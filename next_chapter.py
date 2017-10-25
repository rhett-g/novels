"""This program is designed to scrape a designated story from royalroadl.com"""
import os
from selenium.common.exceptions import NoSuchElementException

def create_toc(chapter_count, fiction_name):
    """Calibre requires that we have a TOC for multi-chapter html input"""
    toc_file = open("tmp/"+fiction_name+".html", "w")
    indent = "  "
    toc_file.write("<html>\n")
    toc_file.write(indent*2+"<body>\n")
    toc_file.write(indent*3+"<h1>Table of Contents</h1>\n")
    toc_file.write(indent*3+"<p style='text-indent:0pt'>\n")
    for i in xrange(1, chapter_count+1):
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
    web_driver.find_element_by_partial_link_text("Next").click()

def next_chapter_exists(web_driver):
    """If there is a next chapter button then we know
    that there is text worth scraping on this page"""
    try:
        web_driver.find_element_by_partial_link_text("Next")
    except NoSuchElementException:
        return False
    return True

def chapter_text_exists(web_driver, element):
    """Check to see chapter text exists"""
    try:
        web_driver.find_element_by_xpath(element)
    except NoSuchElementException:
        return False
    return True

def scrape_chapter_text(web_driver, chapter_count, element):
    """For a particular chapter scrape only the html for the fiction"""
    article = web_driver.find_element_by_xpath(element)
    fiction_file = open("tmp/"+str(chapter_count)+".html", "w")
    fiction_file.write("<html>\n")
    fiction_file.write("<body>\n")
    text = article.get_attribute("innerHTML").encode('utf-8')
    # remove chapter links if present
    if "Next Chapter" in text:
        text = remove_chapter_links(text)
    for line in text:
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
