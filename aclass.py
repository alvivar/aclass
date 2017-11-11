import argparse
import json
import os
import re
import sys
from collections import Counter

import requests
from bs4 import BeautifulSoup


def extract_urls(html_text):
    soup = BeautifulSoup(html_text, "html.parser")
    return [
        a['href'] for a in soup.find_all("a") if a['href'].startswith("http")
    ]


def extract_words(html_text, *, ignore=[]):
    soup = BeautifulSoup(html_text, "html.parser")

    for script in soup(["script", "style"]):
        script.decompose()

    dirty = re.split('[^a-zA-Z]', soup.get_text().lower())
    clean = [i for i in dirty if i and i not in ignore]

    return clean


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

    # Urls from files to the urls list | -f
    FILE_URLS = []
    for f in ARGS.files:
        with open(f, "r", encoding="utf-8") as f:
            text = f.read()
            urls = extract_urls(text)
            FILE_URLS += urls

    # Urls are needed, of course, including from the files
    ARGS.urls += FILE_URLS
    if not ARGS.urls:
        PARSER.print_usage()
        print("urls are needed, try -u or -f")
        PARSER.exit()

    # To ignore
    STOP_ES = json.load(open("stop-es.json", "r"))
    STOP_EN = json.load(open("stop-en.json", "r"))
    STOP_WORDS = STOP_EN + STOP_ES

    # Extraction and word count | -u
    HEADERS = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    }

    TOP = []
    for url in ARGS.urls:
        print(f"Analyzing {url}")

        try:
            html = requests.get(url, headers=HEADERS)
            words = extract_words(html.content, ignore=STOP_WORDS)
            count = Counter(words).most_common(10)
        except requests.exceptions.ConnectionError:
            continue

        TOP.append((url, count))

    # Sexy print
    for url in TOP:
        print(f"\n{url[0]}")
        for count in url[1]:
            print(f"({count[0]} {count[1]}) ", end='')
        print()
