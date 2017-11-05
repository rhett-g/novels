"""These are some of the common utility functions split into web
scarping and epub creation"""
import argparse
import os
import re
from collections import namedtuple
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

###############################################################################
#
#                              Calibre Utils
#
###############################################################################


def make_epubs(max_chap, name):
    current_chap = max_chap
    while current_chap != 0:
        current_chap = make_epub(current_chap, name)


def make_epub(chapter_count, name):
    first_chap = create_toc(chapter_count, name)
    make_epub_dir(chapter_count, name)
    commands = []
    commands.append(name.join(["ebook-convert tmp/", ".html ", ".epub"]))
    commands.append(name.join(["mv ", ".epub ", "/*/"]))
    commands.append("cp -rl " + name + " ~/Dropbox/novels")
    commands.append("rm -rf " + name)
    for command in commands:
        os.system(command)
    return first_chap


def write_text_to_file(text, chapter_count):
    fiction_file = open("tmp/" + str(chapter_count) + ".html", "w")
    fiction_file.write("<html>\n")
    fiction_file.write("<body>\n")
    # remove chapter links if present
    if "Next Chapter" in text:
        text = remove_chapter_links(text)
    for line in text:
        fiction_file.write(line)
    fiction_file.write("</body>\n")
    fiction_file.write("</html>\n")
    fiction_file.close()


def create_toc(chapter_count, fiction_name):
    """Calibre requires that we have a TOC for multi-chapter html input"""
    toc_file = open("tmp/" + fiction_name + ".html", "w")
    indent = "  "
    toc_file.write("<html>\n")
    toc_file.write(indent * 2 + "<body>\n")
    toc_file.write(indent * 3 + "<h1>Table of Contents</h1>\n")
    toc_file.write(indent * 3 + "<p style='text-indent:0pt'>\n")
    first_chapter = last_number_divisible_by_50(chapter_count)
    for i in xrange(first_chapter, chapter_count + 1):
        toc_file.write(indent * 4 + "<a href='" + str(i) +
                       ".html'>" + str(i) + "</a><br/>\n")
    toc_file.write(indent * 3 + "</p>\n")
    toc_file.write(indent * 2 + "</body>\n")
    toc_file.write("</html>\n")
    toc_file.close()
    return first_chapter


def last_number_divisible_by_50(currentNum):
    """Calibre fails to create TOC entries beyond 50 chapters, so we
    limit each epub to be at most 50 chapters"""
    currentNum -= 1
    while currentNum % 50 is not 0:
        currentNum -= 1
    return currentNum


def remove_chapter_links(chapter_text):
    """We don't want the next and previous chapter in our text,
    which is the first and last lines in the articleBody"""
    lines = chapter_text.split("</p>")
    return map(lambda line: line + "</p>", lines[1:-2])


def make_epub_dir(chapter_count, name):
    """We want to be able to keep track of what chapters are in an epub, so
    this function create a directory in the form #FirstChap_#LastChap"""
    if not os.path.exists(name):
        os.makedirs(name)
    first_chapter = last_number_divisible_by_50(chapter_count)
    chapter_dir = name + "/" + str(first_chapter) + "_" + str(chapter_count)
    os.makedirs(chapter_dir)

###############################################################################
#
#                             Selenium Utils
#
###############################################################################


# Named tuple is python's version of a struct and the URLINFO
# holds the chapter_number extracted from the url and url_parts
# which holds all parts of the url minus the chapter number
# ala http://www.example.com/fiction/book-2-chapter-3
# will have ['http://www.example.com/fiction/book-2-chapter-', '']
URLINFO = namedtuple('urlInfo', 'url_parts chapter_number')


def setup_web_driver():
    # setting the page load strategy to eager means we no longer have
    # to wait for adds to load before we scrape the page
    capabilities = DesiredCapabilities.PHANTOMJS
    capabilities["pageLoadStrategy"] = "eager"
    web_driver = webdriver.PhantomJS(desired_capabilities=capabilities)
    web_driver.set_page_load_timeout(10)
    # set window size so we load desktop version
    web_driver.set_window_size(1920, 1080)
    return web_driver


def get_with_timeout(web_driver, url):
    """Goes to a url and refreshes if it doesn't load within a timeout
    period"""
    try:
        web_driver.get(url)
    except TimeoutException:
        get_with_timeout(web_driver, url)


def chapter_exists(web_driver, button_text):
    """If there is a next/prev chapter button then we know
    that there is text worth scraping on that page. 'button_text'
    should be 'Next" or 'Previous' for now"""
    try:
        web_driver.find_element_by_partial_link_text(button_text)
    except NoSuchElementException:
        return False
    except TimeoutException:
        web_driver.refresh()
        chapter_exists(web_driver, button_text)
    return True


def click_chapter(web_driver, button_text):
    """Click the next/prev chapter button. 'button_text'
    should be 'Next" or 'Previous' for now"""
    try:
        web_driver.find_element_by_partial_link_text(button_text).click()
    except TimeoutException:
        web_driver.refresh()
        click_chapter(web_driver, button_text)


def chapter_text_exists(web_driver, element):
    """Check to see chapter text exists"""
    try:
        web_driver.find_element_by_xpath(element)
    except NoSuchElementException:
        return False
    return True


def scrape_chapter_text(web_driver, chapter_count, element):
    """For a particular chapter scrape only the html for the fiction"""
    try:
        article = web_driver.find_element_by_xpath(element)
        text = article.get_attribute("innerHTML").encode('utf-8')
        return text
    except TimeoutException:
        web_driver.refresh()
        scrape_chapter_text(web_driver, chapter_count, element)


def get_chapter_number_from_url(url):
    """Get chapter number from the url"""
    url_base = os.path.basename(os.path.normpath(url))
    url_full_path = url.replace(url_base, "")
    # this regex finds chapters in the following formats
    # 145
    # book-2-chapter-32
    regex = r"([0-9]+(-)*)+"
    matches = re.finditer(regex, url_base)
    start = 0
    for match in matches:
        start = match.start()
        end = match.end()
        chapter_number = match.group()
    # if there are no matches we reurn none
    if start == 0:
        return None
    url_parts = [url_full_path[:], url_base[:start], "||", url_base[end:]]
    return URLINFO(url_parts=url_parts, chapter_number=chapter_number)


def create_list_of_chapters(first_chapter_num, last_chapter_num, url_parts):
    """Creates a list of urls created by inserting the chapter number into
    a common url scheme"""
    toReturnUrls = []
    for i in xrange(first_chapter_num, last_chapter_num + 1):
        url = "".join(url_parts).replace("||", str(i))
        toReturnUrls.append(url)
    return toReturnUrls


def find_range_of_chapters(url_info, web_driver):
    """Recursively find all the sets of chapters for a fiction
    that does not have simple chapter scheme. For example
    de-book-34-chapter-22 will generate 34 sets of chapters"""
    chapters = create_list_of_chapters(
        1, int(url_info.chapter_number), url_info.url_parts)
    web_driver.get(chapters[0])
    if chapter_exists(web_driver, "Previous"):
        current_url = chapters[0]
        click_chapter(web_driver, "Previous")
        prev_url = web_driver.current_url
        prev_chap_info = get_chapter_number_from_url(prev_url)
        if not is_first_chapter(prev_url, current_url, prev_chap_info):
            return find_range_of_chapters(prev_chap_info, web_driver) + chapters
    return chapters


def is_first_chapter(prev_url, current_url, prev_chap_info):
    """Check if this is the first chapter by seeing if the previous
    chapter button is just redirecting us to the same page or if it's
    redirecting us to a synopsis page """
    if prev_url == current_url:
        return True
    if prev_chap_info is None:
        return True
    return False


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

###############################################################################
#
#                             Common Utils
#
###############################################################################


def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="""Input the URL for the story you wish
    to create an .epub. This should be the latest url""")
    parser.add_argument("fiction_name", help="The name of the fiction")
    args = parser.parse_args()
    return args.url, args.fiction_name


def make_tmp_dir():
    """Remove any existing tmp dir and create an empty one"""
    os.system("rm -rf tmp")
    if not os.path.exists("tmp"):
        os.makedirs("tmp")


def clean_up(fiction_name):
    """Clean up after ourselves"""
    os.system("rm -rf *.log tmp argparse *.pyc " + fiction_name)
