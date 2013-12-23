import os
import re
import argparse
from itertools import groupby
import csv
import requests
import dateutil.parser
import requests_cache
from bs4 import BeautifulSoup


def parse_date(d):
    return dateutil.parser.parse(d).date()


def get_file(ticker, url):
    """ Return contents of url caching under data directory """
    filename = "data/{0}/{1}".format(ticker, url.split("/")[-1])
    if not os.path.isfile(filename):
        r = requests.get(url)
        with open(filename, "w") as f:
            f.write(r.text)
            return r.text
    else:
        with open(filename, "r") as f:
            return f.read()


def xbrl_urls(ticker):
    """ Return list of urls to xbrl 10-k or 10-q reports """
    edgar_search_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type={0}&output=atom&CIK={1}&count=100&start=0"
    entries = BeautifulSoup(requests.get(edgar_search_url.format("10", ticker)).text).find_all('entry')
    page_urls = [entry.find('filing-href').text for entry in entries if entry.find('xbrl_href')]
    pages = [requests.get(url).text for url in page_urls]
    regex = re.compile("href=\"(.*xml)\"")
    urls = ["http://www.sec.gov{0}".format(regex.findall(p)[0]) for p in pages]
    return urls


def xbrl_filings(ticker):
    """ Return the contents of all the xbrl 10-k and 10-q filings in an array """
    if not os.path.exists("data/{0}".format(ticker)):
        os.makedirs("data/{0}".format(ticker))
    filings = [get_file(ticker, url) for url in xbrl_urls(ticker)]
    return filings


def parse_xbrl(xbrl):
    s = BeautifulSoup(xbrl)
    instants = [c for c in s("context") if c("instant")]
    unique_instants = [(k, [i.attrs['id'] for i in list(v)]) for k, v in groupby(instants, lambda x: x.period.instant.text)]
    return unique_instants

    instant_entities = [(i[0], [c for c in i[1]]) for i in unique_instants]

    instant_entities = [(i[0], [e for e in s.find_all(contextref=re.compile(c)) for c in i[1]]) for i in unique_instants]
    instant_facts = [(i[0], list(set([(f.name, f.string) for f in i[1]]))) for i in instant_entities]
    return instant_facts

    # gaap = s.find_all(re.compile("us-gaap*"))
    # period_facts = [(c, s.find_all(contextref=re.compile(c["id"]))) for c in periods]
    # periods = [c for c in s("context") if c("startdate")]
    # [k for k,v in groupby(instants, lambda x: x.period.instant.text)]
    # [k for k,v in groupby(periods, lambda x: x.period)]
    # period_facts = [(c, s.find_all(contextref=re.compile(c["id"]))) for c in gaap]
    # instant_facts = [(c, s.find_all(contextref=re.compile(c["id"]))) for c in gaap]
    # return (instant_facts, period_facts)


if __name__ == '__main__':
    requests_cache.install_cache('data/requests_cache')

    parser = argparse.ArgumentParser(
        description="Download from edgar the 10q and 10k xbrl reports and extract financial data.")
    parser.add_argument('-c', '--csv', dest="csv", action="store", default="default.csv",
                        help='csv file with list of company names and tickers to download xbrl data for')
    parser.add_argument('-t', '--tickers', dest="tickers", action="store", default="",
                        help='comma delimited list of tickers to update')
    parser.add_argument('-r', '--refresh', dest="refresh", action="store_true", default=False,
                        help='Refresh filings from edgar instead of using local cache')
    args = parser.parse_args()

    if args.tickers != "":
        tickers = args.tickers.split(",")
    else:
        reader = csv.reader(open(args.csv, "rU"), delimiter=',', quoting=csv.QUOTE_ALL)
        tickers = [row[1] for row in reader]

    for ticker in sorted(tickers):
        print "Downloading filings for", ticker
        filings = xbrl_filings(ticker)
        print "Found", len(filings), "filings"
        for filing in filings:
            print ".",
            instant_facts = parse_xbrl(filing)

    print "Done."
