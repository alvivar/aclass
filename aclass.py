""" Analize and categorize urls, also export them to a Netscape Bookmark html
file. """

import argparse
import json
import os
import re
import sys
from collections import Counter

import requests
from bs4 import BeautifulSoup


def extract_urls(html_text):
    """ Return a list of urls from the html text. """
    soup = BeautifulSoup(html_text, "html.parser")
    return [
        a['href'] for a in soup.find_all("a") if a['href'].startswith("http")
    ]


def extract_words(html_text, *, ignore=[]):
    """ Return a list of words from the html text. """

    soup = BeautifulSoup(html_text, "html.parser")

    for script in soup(["script", "style"]):
        script.decompose()

    dirty = re.split('[^a-zA-Z]', soup.get_text().lower())
    clean = [i for i in dirty if i and i not in ignore]

    return clean


def get_top_words(urls_list, words_count):
    """ Return a list of tuples with urls and their word count dictionary. """

    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/39.0.2171.95 Safari/537.36'
    }

    top = []
    for url in urls_list:
        print(f"Analyzing {url}")
        try:
            html = requests.get(url, headers=headers)
            words = extract_words(html.content, ignore=STOP_WORDS)
            count = Counter(words).most_common(words_count)
        except requests.exceptions.ConnectionError:
            continue  # TODO Bind the url to a None kind of word count
        top.append((url, count))

    return top  # ("url", ({"word" : count}, *))


def get_top_words_categories(top_words):
    """ Return a dictionary of words referencing a list of the urls that belong
    to them, assuming top_words as a list of tuples with urls and their word
    counts dictionaries. """
    categories = {}
    for top in top_words:
        for tag in top[1]:
            categories.setdefault(tag[0], []).append(top[0])
    return categories  # {"word" : ["url that belongs", *]}


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

    # Analysis
    TOP_WORDS = get_top_words(ARGS.urls, 5)
    CATEGORIES = get_top_words_categories(TOP_WORDS)

    # Sexy print
    for t in TOP_WORDS:
        print(f"\n{t[0]}")
        for word_list in t[1]:
            print(f"({word_list[0]} {word_list[1]}) ", end='')
        print()

    for cat, url_list in CATEGORIES.items():
        print(f"\n{cat}")
        for u in url_list:
            print(u)
