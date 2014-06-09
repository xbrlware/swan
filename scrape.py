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

# Download all the filings from edgar
ticker = 'AAPL'
requests_cache.install_cache("/data/swan/%s" % ticker)

edgar_search_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type={0}&output=atom&CIK={1}&count=100&start=0"
entries = BeautifulSoup(requests.get(edgar_search_url.format("10", ticker)).text).find_all('entry')
page_urls = [entry.find('filing-href').text for entry in entries if entry.find('xbrl_href')]
pages = [requests.get(url).text for url in page_urls]
regex = re.compile("href=\"(.*xml)\"")
urls = ["http://www.sec.gov{0}".format(regex.findall(p)[0]) for p in pages]
filings = [requests.get(url).text for url in urls]
print "Found", len(filings), "filings"

# <codecell>

# Find all the unique instant's and their associated contexts
s = BeautifulSoup(filings[0])
instants = [c for c in s("context") if c("instant")]
unique_instants = [(k, [i.attrs['id'] for i in list(v)]) for k, v in groupby(instants, lambda x: x.period.instant.text)]

# [((i[0], s.find_all(contextref=re.compile(c))) for c in i[1]) for i in unique_instants]

instant_entities = [((i[0], [e for e in s.find_all(contextref=re.compile(c))]) for c in i[1]) for i in unique_instants]

# instant_entities = [(i[0], [e for e in s.find_all(contextref=re.compile(str(c))) for c in i[1]]) for i in unique_instants]
# instant_facts = [(i[0], list(set([(f.name, f.string) for f in i[1]]))) for i in instant_entities]

# <codecell>

def extract_gaap_entities(instants):
    for instant in instants:
        for context in instant[1]:
            for e in s.find_all(contextref=re.compile(context)):
                if  "xsi:nil" not in e.attrs and e.name.startswith("us-gaap"):
                    yield((instant[0], e.name, float(e.contents[0])))

gaap_instant_facts = extract_gaap_entities(unique_instants)

print gaap_instant_facts.next()
print gaap_instant_facts.next()

