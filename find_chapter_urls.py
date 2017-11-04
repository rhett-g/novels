import argparse
import os
import re
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException, TimeoutException


def get_chapter_number_from_url(url):
    """Get chapter number from the url"""
    url_base = os.path.basename(os.path.normpath(url))
    url_full_path = url.replace(url_base, "")
    # this regex finds chapters in the following formats
    # 145
    # book-2-chapter-32
    regex = r"([0-9]+(-)*)+"
    matches = re.finditer(regex, url_base)
    start = None
    for match in matches:
        start = match.start()
        end = match.end()
        chapter_number = match.group()
    # if there are no matches we reurn none
    if start is None:
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


def prev_chapter_exists(url, web_driver):
    """Checks to see if there is a previous chapter button/link"""
    try:
        web_driver.get(url)
        web_driver.find_element_by_partial_link_text("Previous")
    except NoSuchElementException:
        return False
    except TimeoutException:
        web_driver.refresh()
        prev_chapter_exists(url, web_driver)
    return True


def get_prev_chapter_url(url, web_driver):
    """Clicks the previous chapter button and then returns the url
    of that subsequent page"""
    try:
        current_url = web_driver.current_url
        web_driver.find_element_by_partial_link_text("Previous").click()
        return web_driver.current_url, current_url
    except TimeoutException:
        web_driver.refresh()
        get_prev_chapter_url(web_driver)


def find_range_of_chapters(url_info, web_driver):
    """Recursively find all the sets of chapters for a fiction
    that does not have simple chapter scheme. For example
    de-book-34-chapter-22 will generate 34 sets of chapters"""
    chapters = create_list_of_chapters(
        1, int(url_info.chapter_number), url_info.url_parts)
    if prev_chapter_exists(
        chapters[0],
            web_driver):
        prev_url, current_url = get_prev_chapter_url(chapters[0],
                                                     web_driver)
        if prev_url == current_url:
            return chapters
        prev_chap_info = get_chapter_number_from_url(prev_url)
        if prev_chap_info is None:
            return chapters
        return find_range_of_chapters(prev_chap_info, web_driver) + chapters
    return chapters


if __name__ == "__main__":

    """
        Usage: extracting info from libs
    """
    # arg parsing
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("last_chap_url", help="URL of last chapter")
    ARGS = PARSER.parse_args()
    # general setup
    URLINFO = namedtuple('urlInfo', 'url_parts chapter_number')
    CAPABILITIES = DesiredCapabilities.PHANTOMJS
    CAPABILITIES["pageLoadStrategy"] = "eager"
    DRIVER = webdriver.PhantomJS(desired_capabilities=CAPABILITIES)
    DRIVER.set_page_load_timeout(30)
    # program driver
    LAST_URL_INFO = get_chapter_number_from_url(ARGS.last_chap_url)
    CHAPTERS = find_range_of_chapters(LAST_URL_INFO, DRIVER)
    for index in xrange(1, len(CHAPTERS)):
        print str(index) + "||" + CHAPTERS[index]
    DRIVER.close()
