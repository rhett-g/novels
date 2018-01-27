#!/usr/bin/env python
"""This program is made to identify what website we are scraping from
and initiate the correct scraper"""
import utils


def driver(url, title, debug):
    """This is the driver for fictions that have a next chapter button"""
    web_driver = utils.setup_web_driver(debug)
    utils.get_with_timeout(web_driver, url)
    chapter_count = 0
    element = utils.get_article_element(url)
    # while there is a next chapter scrape it's text
    while utils.chapter_text_exists(web_driver, element):
        if chapter_count % 50 == 0 and chapter_count != 0:
            utils.make_epub(chapter_count, title)
        text = utils.scrape_chapter_text(web_driver, chapter_count, element)
        utils.write_text_to_file(text, chapter_count)
        if utils.chapter_exists(web_driver, "Next"):
            utils.click_chapter(web_driver, "Next")
            chapter_count += 1
            continue
        break
    utils.make_epub(chapter_count, title)
    web_driver.close()


if __name__ == "__main__":
    URL, FICTION_NAME = utils.arg_parse()
    utils.make_tmp_dir()
    driver(URL, FICTION_NAME, True)
    utils.clean_up(FICTION_NAME)
