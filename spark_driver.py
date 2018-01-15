import utils
from pyspark import SparkContext, SparkConf


def setup_spark():
    conf = SparkConf()
    conf.setAppName('novel').setMaster("local[*]")
    sc = SparkContext(conf=conf)
    return sc


def get_chapter_urls(url):
    """Returns all the urls for a fiction"""
    web_driver = utils.setup_web_driver()
    url_info = utils.get_chapter_number_from_url(url)
    chapters = utils.find_range_of_chapters(url_info, web_driver)
    web_driver.close()
    toReturnURLs = []
    for index in xrange(1, len(chapters)):
        toReturnURLs.append(str(index) + "||" + chapters[index - 1])
    return toReturnURLs


def spark_driver(urls):
    """Using foreachPartitions as initializing the selenium driver is
    expensive as such we pass in a partition of urls and their chap
    numbers in the form chap_num:url"""
    # set up selenium
    web_driver = utils.setup_web_driver()
    chap_nums = []
    for url in urls:
        chap_num, url = url
        element = utils.get_article_element(url)
        utils.get_with_timeout(web_driver, url)
        text = utils.scrape_chapter_text(web_driver, chap_num, element)
        utils.write_text_to_file(text, chap_num)
        chap_nums.append(chap_num)
    web_driver.close()
    yield max(chap_nums)


def create_list_of_book_endings(max_chap):
    book_endings = [50]
    while book_endings[-1] < max_chap:
        book_endings.append(book_endings[-1] + 50)
    book_endings[-1] = max_chap
    return book_endings


if __name__ == "__main__":
    URL, FICTION_NAME = utils.arg_parse()
    utils.make_tmp_dir()
    CHAPTERS = get_chapter_urls(URL)
    SC = setup_spark()
    CHAPTERS_RDD = SC.parallelize(CHAPTERS, 24)
    # split the rdd into a pair rdd with the chapter number
    # as the key and url as the value
    CHAPTERS_PAIRS_RDD = CHAPTERS_RDD.map(
        lambda x: (int(x.split("||")[0]), x.split("||")[1]))
    MAX_RDD = CHAPTERS_PAIRS_RDD.mapPartitions(spark_driver)
    MAX = MAX_RDD.max()
    BOOKS = create_list_of_book_endings(MAX)
    for ending in BOOKS:
        utils.make_epub(ending, FICTION_NAME)
    SC.stop()
    utils.clean_up(FICTION_NAME)
