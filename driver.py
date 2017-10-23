"""This program is made to identify what website we are scraping from
and initiate the correct scraper"""
import argparse
import subprocess

def select_driver(url, title):
    """A switch statement that parses the url to find the correct
    driver for a website and return the command subprocess will
    use to call the bash script"""
    if "royalroad" in url:
        print "Fiction is from Royal Road"
        send_to_terminal(["royalRoad/royalRoad.sh", url, title])
    elif "wuxiaworld" in url.lower():
        send_to_terminal(["wuxiaWorld/wuxiaWorld.sh", url, title])
    else:
        print "We have not implemented a scraper for this website"

def send_to_terminal(command):
    """Utility function for subprocess commands"""
    subprocess.call(command)

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("URL", help="""Input the URL for the story you wish
    to create an .epub for. This should be the page that has the TOC for royal
    road and whatever chapter you wish to start from in wuxia world""")
    PARSER.add_argument("FICTION_NAME", help="The name of the fiction")
    ARGS = PARSER.parse_args()
    select_driver(ARGS.URL, ARGS.FICTION_NAME)
