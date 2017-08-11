# -*- coding: utf-8 -*- 
import urllib.request
import re
import html.parser as hp
from urllib.parse import urlparse
from argparse import ArgumentParser

# parser
def parser():
    usage = 'Usage: python {} URL [--pattern <regex>] [--deepth <number>] [--help]'\
            .format(__file__)
    argparser = ArgumentParser(usage=usage)
    argparser.add_argument('url', type=str,
                           help='root url')
    argparser.add_argument('-p', '--pattern', type=str,
                           help='script src regex pattern')
    argparser.add_argument('-d', '--deepth', type=int,
                           help='crawling deepth')

    args = argparser.parse_args()
    return args

# LinkParser
class LinkParser(hp.HTMLParser):
    def __init__(self, regex):
        hp.HTMLParser.__init__(self)
        self.url = ""
        self.links = []
        self.embedded = False
        self.regex = regex
        self.a_count = 0

    def feed(self, page):
        self.links = []
        self.embedded = False
        super(LinkParser, self).feed(page)

    def get_links(self):
        return self.links

    def handle_starttag(self, tag, attrs):
        if tag == "a": # 開始タグがaであるかどうか判定
            self.a_count += 1
            attrs = dict(attrs) # タプルを辞書に変換する
            if 'href' in attrs: # キー値(属性名)がhrefであるか判定
                self.url = attrs['href']
        elif tag == "script":
            attrs = dict(attrs) # タプルを辞書に変換する
            if 'src' in attrs: # キー値(属性名)にsrcを含むか判定
                if re.search(self.regex, attrs['src']) != None:
                  self.embedded = True
              
    def handle_endtag(self, tag): # 開始・終了タグに囲まれた中身の処理
        if tag == "a" and self.url and re.match('^http', self.url): # 先頭がhttpであるか判定
            self.links.append(self.url)


def get_page(url):
    try:
        return urllib.request.urlopen(url).read().decode('utf-8')
    except:
        return ""

def ptint_result(matches, non_matches):
    print("\n\nRESULT:")
    print('=========== MATCH ==========')
    for url in  matches:
      print(url)
    print('=========== DON''T MATCH ==========')
    for url in  non_matches:
      print(url)

def crawl_web(seed, regex, max_deepth = 3):
    # seed : 一番最初の元となるページ
    # clawled : クロールが終了したページ
    # tocrawl : クロールするページ
    tocrawl = [seed]
    nextcrawl = []
    crawled = []
    match_pages = []
    non_match_pages = []
    parser = LinkParser(regex)
    deepth = 0
    domain = urlparse(seed).netloc

    while deepth < max_deepth:
        while tocrawl:
            page = tocrawl.pop()
            if page not in crawled and urlparse(page).netloc == domain:
                print(page)
                parser.feed(get_page(page))
                if parser.embedded == True:
                    match_pages.append(page)
                else:
                    non_match_pages.append(page)
                crawled.append(page)
                nextcrawl.extend(parser.links)

        tocrawl = nextcrawl
        nextcrawl = []
        deepth += 1

    # print result
    ptint_result(match_pages, non_match_pages)
    return crawled

if __name__ == '__main__':
    result = parser()
    print(result)
    crawl_web(result.url, result.pattern or 'analytics.fs-bdash.com', result.deepth or 3)

#crawl_web('https://f-scratch.co.jp/', 'analytics.fs-bdash.com')
