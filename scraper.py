#!/usr/bin/env python3.5
import json
import re
from argparse import ArgumentParser, Namespace

import requests

args = Namespace()


def main():

    parser = ArgumentParser(description="Dive into the rabbit hole")
    parser.add_argument('url', help="Url to reddit comment")
    parser.add_argument('-v', help="Use verbose mode", action='store_true', default=False, dest='v')
    parser.add_argument('--print', help="Print only the specified debug statues", action='append', dest="print")
    parser.add_argument("-r", help="Use reddit formatting", action="store_true", default=False, dest="reddit")
    parser.parse_args(namespace=args)

    if args.print:
        for i in range(len(args.print)):
            args.print[i] = args.print[i].upper()

    reddit_headers = {
        'User-agent': 'Rabbithole Diver Bot v.0.1'
    }

    json_url = build_url(args.url, ".json")

    json_file = requests.get(json_url, headers=reddit_headers)

    log("GET", "Fetched json file: %s" % json_url)

    j_file = json_file
    found_link = True

    links = []

    while found_link:
        loaded_data = json.loads(j_file.text)
        found_link = False

        log("PARSE", "Parsed json data")

        post_title = loaded_data[0]["data"]["children"][0]["data"]["title"]
        comment_body = loaded_data[1]["data"]["children"][0]["data"]["body"]

        log("FIND", "Extracted post title: %s" % post_title)
        log("FIND", "Extracted comment body: %s" % comment_body)

        link_text, link = extract_link(comment_body)

        links.append((post_title ,link_text, link))

        if link:
            link = build_url(link, ".json")
            found_link = True
            j_file = requests.get(link, headers=reddit_headers)
            log("GET", "Fetched json file: %s" % link)
        else:
            print("\nRabbithole ended")

    print("Rabbithole: %d posts:" % len(links))
    if args.reddit:
        print_reddit(links)
    else:
        for post in links:
            print("\t- " + str(post))


def extract_link(string: str):
    pattern = r".*?\[(.+?)\]\((.+?)\).*?"
    # log("debug", "Trying to match '%s' to ''%s" % (string, pattern))
    match = re.match(pattern, string, flags=re.IGNORECASE | re.MULTILINE | re.UNICODE)

    if match:
        log("LINK", "Found link '%s'" % match[2])
        log("LINKTEXT", "Found link text: %s" % match[1])
    else:
        log("EXTRACT", "Found no link")

    return (match[1], match[2]) if match else (None, None)


def clean_url(url: str) -> str:

    cleaned_url = url

    if url.find("?"):
        cleaned_url = url.split("?")[0]

    while cleaned_url[len(cleaned_url) - 1] == "/":
        cleaned_url = cleaned_url[:-1:]

    log("PARSE", "Cleaned url: %s" % cleaned_url)

    return cleaned_url


def log(status: str, message: str) -> None:
    if args.v or (args.print and status.upper() in args.print):
        print("[%s] %s" % (status.upper(), message))


def build_url(url: str, suffix:str) -> str:
    out = clean_url(url) + suffix
    log("BUILD", "Built JSON url: %s" % out)

    return out


def print_reddit(posts):
    for post in posts:
        print("+ \"%s\": [%s](%s)" % post)


if __name__ == "__main__":
    main()
