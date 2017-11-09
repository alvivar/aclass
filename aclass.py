import argparse
import json
import os
import re
import sys
from collections import Counter

import requests
from bs4 import BeautifulSoup


def extract_links(url, *, headers={}):
    page = requests.get(url, headers=HEADER)
    soup = BeautifulSoup(page.content, "html.parser")

    return [
        a['href'] for a in soup.find_all("a") if a['href'].startswith("http")
    ]


def extract_words(url, *, headers={}):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")

    for script in soup(["script", "style"]):
        script.decompose()
    text = soup.get_text().split()

    return text


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

    HEADER = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    WORDS = extract_words(
        "https://stackoverflow.com/questions/8113782/split-string-on-whitespace-in-python",
        headers=HEADER)

    STOP_ES = json.load(open("stop-es.json", "r"))
    STOP_EN = json.load(open("stop-en.json", "r"))
    STOP_WORDS = STOP_EN + STOP_ES
    CLEAN = [w for w in WORDS if w and w.lower() not in STOP_WORDS]

    with open("debug.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(CLEAN))

    COUNT = Counter(CLEAN).most_common(5)
    print(COUNT)

    # print(extract_links("http://news.ycombinator.com", headers=HEADER))
