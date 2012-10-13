# -*- coding: utf8 -*- 

"""
Work with the crossref APIs.
"""

from pprint import pprint
import json
import requests

def scrub(value):
    """
    Clean up the incoming queries to remove unfriendly 
    characters that may come from copy and pasted citations.
    """
    from curses import ascii
    if not value:
        return
    n = ''.join([c for c in value.strip() if not ascii.isctrl(c)])
    return n


def fetch_links(query):
    cr = 'http://search.labs.crossref.org/links'
    #Scrub the citation query.
    cleaned = scrub(query)
    #Turn query into a list because the API is expecting a list.
    citations = [cleaned]
    resp = requests.post(cr, data=json.dumps(citations))
    if resp.status_code != 200:
        raise Exception("Crossref request failed")
    match_dict = json.loads(resp.content)
    results = match_dict.get('results')
    ok = match_dict.get('query_ok')
    found = [r for r in results if r.get('match') is True]
    cite_meta = []
    #Lookup the DOIs and get metadata for the located citations.  
    for item in found:
        doi = item.get('doi')
        meta = fetch_doi(doi)
        cite_meta.append(meta)
    out = dict(status=ok, cites=cite_meta)
    return out

def fetch_doi(doi):
    cr = 'http://search.labs.crossref.org/dois'
    resp = requests.get(cr + '?q=' + doi)
    if resp.status_code != 200:
        raise Exception("Crossref request failed.  Error code" + resp.status_code)
    meta = json.loads(resp.content)
    #Some doi lookups are failing.  Not sure why.  
    try:
        first = meta[0]
        return first
    except IndexError:
        return {}

if __name__ == "__main__":
    # d = '10.1021/mp050023q'
    import urllib
    d = '10.1002/1099-0690(200105)2001:10<1903::AID-EJOC1903>3.0.CO;2-W'
    print d
    scrubbed_d = d.replace('/', '%2F')
    meta = fetch_doi(scrubbed_d)
    print meta.get('doi') == d
    print meta.get('title').rfind('Drugs') > 0

#     cite = """
# Dendrimers as drugs: discovery and preclinical and clinical development of dendrimer-based microbicides for HIV and STI prevention
# …, P Karellas, SA Henderson, M Giannis… - Molecular …, 2005 - ACS Publications
# """
#     cites = [cite]
#     pprint(fetch_links(cites))