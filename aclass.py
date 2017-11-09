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
    soup = BeautifulSoup(html_text, "lxml")

    for script in soup(["script", "style"]):
        script.decompose()

    words = soup.get_text().split()
    clean_words = [i for i in words if i and i.lower() not in ignore]

    return clean_words


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
        "--export",
        help="export html bookmarks file",
        nargs="?",
        type=str,
        const="bookmark.html")
    ARGS = PARSER.parse_args()

    HEADERS = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    # Ignore
    STOP_ES = json.load(open("stop-es.json", "r"))
    STOP_EN = json.load(open("stop-en.json", "r"))
    STOP_WORDS = STOP_EN + STOP_ES

    # Extract
    HTML = requests.get(
        "https://stackoverflow.com/questions/8113782/split-string-on-whitespace-in-python",
        headers=HEADERS)
    WORDS = extract_words(HTML.content, ignore=STOP_WORDS)

    with open("debug.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(WORDS))

    COUNT = Counter(WORDS).most_common(5)
    print(COUNT)

    # print(extract_links("http://news.ycombinator.com", headers=HEADER))
