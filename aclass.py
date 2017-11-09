import argparse
import json
import os
import re
import sys
from collections import Counter

import requests
from bs4 import BeautifulSoup


def extract_links(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return [
        a['href'] for a in soup.find_all("a") if a['href'].startswith("http")
    ]


def extract_words(html_text, *, ignore=[]):
    soup = BeautifulSoup(html_text, "html.parser")

    for script in soup(["script", "style"]):
        script.decompose()

    words = soup.get_text().split()
    clean_words = [i for i in words if i and i.lower() not in ignore]

    return clean_words


def categorize_top_words(top_words):
    pass


if __name__ == "__main__":

    # frozen? (cxfreeze compatibility)
    DIR = os.path.normpath(
        os.path.dirname(
            sys.executable if getattr(sys, 'frozen', False) else __file__))
    os.chdir(DIR)

    # Command line args
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument(
        "-u", "--urls", help="urls to analyze", nargs="+", default=[])
    PARSER.add_argument(
        "-f",
        "--files",
        help="files with urls to analyze",
        nargs="+",
        default=[])
    PARSER.add_argument(
        "-e",
        "--export-file",
        help="export html bookmarks file",
        nargs="?",
        type=str,
        const="bookmark.html")
    ARGS = PARSER.parse_args()

    # Urls are needed, of course
    if not ARGS.urls:
        PARSER.print_usage()
        print("urls are needed!")
        PARSER.exit()

    # To ignore
    STOP_ES = json.load(open("stop-es.json", "r"))
    STOP_EN = json.load(open("stop-en.json", "r"))
    STOP_WORDS = STOP_EN + STOP_ES

    # Extraction
    HEADERS = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    TOP_WORDS = []
    for url in ARGS.urls:
        html = requests.get(url, headers=HEADERS)
        words = extract_words(html.content, ignore=STOP_WORDS)
        count = Counter(words).most_common(10)
        TOP_WORDS.append((url, count))

    print(TOP_WORDS)

    # print(extract_links("http://news.ycombinator.com", headers=HEADER))
