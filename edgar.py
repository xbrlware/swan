import os
import sys
import re
import argparse
import csv
import requests
import requests_cache
import xbrl
from bs4 import BeautifulSoup


def get_all_xbrl_urls(ticker, type="10"):
    """ Return an array of urls to all of the xbrl reports for the given
    company. Note that this just looks at the first page of the search
    results from edgar but when searching for 10k or 10q reports the
    only ones with xml are the last few years so it fits on the first
    pages 100 results."""
    edgar_search_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type={0}&output=atom&CIK={1}&count=100&start=0"
    r = requests.get(edgar_search_url.format(type, ticker))
    parsed_search_results = BeautifulSoup(r.text)
    xbrl_filing_pages = [entry.find('filing-href').text for entry in parsed_search_results.find_all('entry') if entry.find('xbrl_href')]
    regex = re.compile("href=\"(.*xml)\"")
    xbrl_urls = []
    for link in xbrl_filing_pages:
        r = requests.get(link)
        match = regex.findall(r.text)
        xbrl_urls.append("http://www.sec.gov{0}".format(match[0]))
    return xbrl_urls


def download_all_xbrl_docs(ticker, type="10"):
    if not os.path.exists("data/edgar/{0}".format(ticker)):
        os.makedirs("data/edgar/{0}".format(ticker))
    links = get_all_xbrl_urls(ticker)
    xbrl_files = []
    for xbrl_url in links:
        filename = xbrl_url.split('/')[-1]
        xbrl_files.append("data/edgar/{0}/{1}".format(ticker, filename))
        if not os.path.isfile("data/edgar/{0}/{1}".format(ticker, filename)):
            print "Storing", filename
            r = requests.get(xbrl_url)
            with open("data/edgar/{0}/{1}".format(ticker, filename), 'w') as f:
                f.write(r.text)
    return xbrl_files


def parse_all_xbrl_docs(ticker):
    """ Parses all xbrl docs downloaded for the given ticker and returns an array
    of hashes each of which contains all the facts extracted from a given file """
    dir = "data/edgar/{0}".format(ticker)
    xbrl_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    all_xbrl = []
    for f in xbrl_files:
        print "Parsing", f
        try:
            x = xbrl.XBRL("data/edgar/{0}/{1}".format(ticker, f))
            # print f, "==========> Fields:", x.fields
            all_xbrl.append(x.fields)
        except:
            e = sys.exc_info()[0]
            print "Problems parsing {0}: {1}".format(f, e)
    return all_xbrl

if __name__ == '__main__':
    requests_cache.install_cache('data/requests_cache')

    parser = argparse.ArgumentParser(
        description="Download from edgar the 10q and 10k xbrl reports and extract financial data.")
    parser.add_argument('-c', '--csv', dest="csv", action="store", default="default.csv",
                        help='csv file with list of company names and tickers to download xbrl data for')
    args = parser.parse_args()

    reader = csv.reader(open(args.csv, "rU"), delimiter=',', quoting=csv.QUOTE_ALL)
    companies = {row[1]: {"name": row[0]} for row in reader}

    for ticker, filings in sorted(companies.iteritems()):
        print "Downloading filings for {0}".format(ticker)
        download_all_xbrl_docs(ticker)
        all_xbrl_facts = parse_all_xbrl_docs(ticker)
        # print all_xbrl_facts

    # print "Revenues", x.fields['Revenues']
    # print "OperatingIncomeLoss", x.fields['OperatingIncomeLoss']
