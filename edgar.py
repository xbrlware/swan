import os
import sys
import re
import csv
import requests
import requests_cache
import xbrl
from bs4 import BeautifulSoup


def get_sp500_tickers():
    reader = csv.reader(open("sp500.csv", "rU"), delimiter=',', quoting=csv.QUOTE_ALL)
    return [row[1] for row in reader]


def get_all_xbrl_urls(cik, type="10"):
    """ Return an array of urls to all of the xbrl reports for the given
    company. Note that this just looks at the first page of the search
    results from edgar but when searching for 10k or 10q reports the
    only ones with xml are the last few years so it fits on the first
    pages 100 results."""
    edgar_search_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type={0}&output=atom&CIK={1}&count=100&start=0"
    r = requests.get(edgar_search_url.format(type, cik))
    parsed_search_results = BeautifulSoup(r.text)
    xbrl_filing_pages = [entry.find('filing-href').text for entry in parsed_search_results.find_all('entry') if entry.find('xbrl_href')]
    regex = re.compile("href=\"(.*xml)\"")
    xbrl_urls = []
    for link in xbrl_filing_pages:
        r = requests.get(link)
        match = regex.findall(r.text)
        xbrl_urls.append("http://www.sec.gov{0}".format(match[0]))
    return xbrl_urls


def download_all_xbrl_docs(cik, type="10"):
    if not os.path.exists("edgar/{0}".format(cik)):
        os.makedirs("edgar/{0}".format(cik))
    links = get_all_xbrl_urls(cik)
    xbrl_files = []
    for xbrl_url in links:
        filename = xbrl_url.split('/')[-1]
        xbrl_files.append("edgar/{0}/{1}".format(cik, filename))
        if not os.path.isfile("edgar/{0}/{1}".format(cik, filename)):
            print "Storing", filename
            r = requests.get(xbrl_url)
            with open("edgar/{0}/{1}".format(cik, filename), 'w') as f:
                f.write(r.text)
    return xbrl_files


def parse_all_xbrl_docs(cik):
    """ Parses all xbrl docs downloaded for the given cik and returns an array
    of hashes each of which contains all the facts extracted from a given file """
    dir = "edgar/{0}".format(cik)
    xbrl_files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
    all_xbrl = []
    for f in xbrl_files:
        print "Parsing", f
        try:
            x = xbrl.XBRL("edgar/{0}/{1}".format(cik, f))
            print f, "==========> Fields:", x.fields
            all_xbrl.append(x.fields)
        except:
            e = sys.exc_info()[0]
            print "Problems parsing {0}: {1}".format(f, e)
    return all_xbrl


if __name__ == '__main__':
    requests_cache.install_cache('requests_cache')
    tickers = get_sp500_tickers()
    for cik in tickers[0:1]:
        download_all_xbrl_docs(cik)
        all_xbrl_facts = parse_all_xbrl_docs(cik)

    # links = get_all_xbrl_urls("0001288776")
    # xbrl_files = download_all_xbrl_docs("0001288776")
    # xbrl_files = download_all_xbrl_docs("AAPL")


        # print "Revenues", x.fields['Revenues']
        # print "OperatingIncomeLoss", x.fields['OperatingIncomeLoss']
