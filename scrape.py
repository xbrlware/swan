# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

"""
Scrape edgar for all the xbrl filings from one company, extract all of 
the facts accross all the filings and output a unified set of facts by 
instant and period.
"""
import os, re
from itertools import groupby
import requests, requests_cache
from bs4 import BeautifulSoup

# <codecell>

def download_filings(ticker):
    """ Download the text of all the edgar filings for specified ticker """
    requests_cache.install_cache("/data/swan/%s" % ticker)
    edgar_search_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type={0}&output=atom&CIK={1}&count=100&start=0"
    entries = BeautifulSoup(requests.get(edgar_search_url.format("10", ticker)).text).find_all('entry')
    page_urls = [entry.find('filing-href').text for entry in entries if entry.find('xbrl_href')]
    pages = [requests.get(url).text for url in page_urls]
    regex = re.compile("href=\"(.*xml)\"")
    urls = ["http://www.sec.gov{0}".format(regex.findall(p)[0]) for p in pages]
    filings = [requests.get(url).text for url in urls]
    print urls
    return filings
    
if __name__ == "__main__":
    ticker = 'AAPL'
    filings = download_filings(ticker)
    print "Found", len(filings), "filings for", ticker

# <codecell>

s = cStringIO.StringIO(filings[0])

# <codecell>

s.read()

# <codecell>

from xbrl import XBRLParser, GAAP, GAAPSerializer
import cStringIO


xbrl_parser = XBRLParser(precision=0)

# Parse an incoming XBRL file
xbrl = xbrl_parser.parse(cStringIO.StringIO(filings[0]))

# Parse just the GAAP data from the xbrl object
# gaap_obj = xbrl_parser.parseGAAP(xbrl,
#                                  doc_date="20130629",
#                                  doc_type="10-K",
#                                  context="current",
#                                  ignore_errors=0)
gaap_obj = xbrl_parser.parseGAAP(xbrl,
                                 ignore_errors=0)


# Serialize the GAAP data
serialized = GAAPSerializer(gaap_obj)

# Print out the serialized GAAP data
print serialized.data

# <codecell>

xbrl

# <codecell>

def get_dates_and_instants(filing_soup):
    """ Return all the unique dates and a list of instants for each of them. """
    instants = [c for c in filing_soup("context") if c("instant")]
    unique_instants = [(k, [i.attrs['id'] for i in list(v)]) for k, v in groupby(instants, lambda x: x.period.instant.text)]
    return unique_instants
    
if __name__ == "__main__":
    all_dates = [get_dates_and_instants(BeautifulSoup(f)) for f in filings]
    print "Dates:", all_dates
#     print "Found", len(dates_instants), "dates"
    
# def get_dates_and_instants(unique_instants):
#     """ Return all the entities given the unique instants """
#     instant_entities = [((i[0], [e for e in s.find_all(contextref=re.compile(c))]) for c in i[1]) for i in unique_instants]
#     return instant_entities

# if __name__ == "__main__":
#     instant_entities = get_instant_entities(unique_instants)
#     print "Found", len(instant_entities), "entities"
    
#     print unique_instants

# instant_entities = [(i[0], [e for e in s.find_all(contextref=re.compile(str(c))) for c in i[1]]) for i in unique_instants]
# instant_facts = [(i[0], list(set([(f.name, f.string) for f in i[1]]))) for i in instant_entities]
# print [i for i in instant_entities]

# <codecell>

all_dates = [get_dates_and_instants(BeautifulSoup(f)) for f in filings]

# <codecell>

def extract_gaap_facts(dates_instants, filing_soup):
    """ Return a list of (date, xbrl fact tag, value) for the given filing """
    try:
        for instant in dates_instants:
            for context in instant[1]:
                for e in filing_soup.find_all(contextref=re.compile(context)):
                    if  "xsi:nil" not in e.attrs and e.name.startswith("us-gaap"):
                        yield((instant[0], e.name, float(e.contents[0])))
    except:
        print "Problem extracting gaap facts"
                    
if __name__ == "__main__":
    gaap_facts = extract_gaap_facts(all_dates, BeautifulSoup(filings[0]))
    facts = [f for f in gaap_facts]
    print "Found", len(facts), "facts"    
    if facts:
        print "First fact:", facts[0]

# <codecell>

def get_all_facts(ticker):
    """ Return a list of (date, fact tag, value) for every filing for the given ticker """
    soups = [BeautifulSoup(f) for f in download_filings(ticker)]    
    facts = [[f for f in extract_gaap_facts(get_dates_and_instants(s), s)] for s in soups]
    return [item for sublist in facts for item in sublist]
    
if __name__ == "__main__":
    all_facts = get_all_facts(ticker)
    print "Found", len(all_facts), "all_facts"

# <codecell>

groups = [f for f in groupby(all_facts, lambda x: x[1])]

# <codecell>

all_facts[0:10]

# <codecell>

def get_sp500_tickers():
    import csv
    with open('sp500.csv', 'rU') as f:
        reader = csv.reader(f)
        return [r[1] for r in reader]

if __name__ == "__main__":
    tickers = get_sp500_tickers()
    print "Found", len(tickers), "tickers"
    print tickers[0:10]

# <codecell>

soups = download_filings(tickers[0])
filing_soup = BeautifulSoup(filings[0])
dates_instants = get_dates_and_instants(filing_soup)
# facts = extract_gaap_facts(filing_soup, )

# <codecell>

[len(get_dates_and_instants(BeautifulSoup(f))) for f in filings]

# <codecell>


