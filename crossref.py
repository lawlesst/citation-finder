# -*- coding: utf8 -*-

"""
Work with the crossref APIs.
"""
from curses import ascii
from pprint import pprint
import json
import string

import requests

punctuation = set(string.punctuation)

API_URL = 'https://api.crossref.org/works'


def scrub(value):
    """
    Clean up the incoming queries to remove unfriendly
    characters that may come from copy and pasted citations.

    Also remove all punctuation from text.

    """
    if not value:
        return
    n = ''.join([c for c in value.strip() if not ascii.isctrl(c)])
    #Strip newline or \f characters.
    n2 = n.replace('\n', '').replace('\f', '')
    cleaned = ''.join(ch for ch in n2 if ch not in punctuation)
    return cleaned


def fetch_links(query):
    #Scrub the citation query.
    cleaned = scrub(query)
    #Turn query into a list because the API is expecting a list.
    #citations = [cleaned]
    resp = requests.get(API_URL, params={'query': cleaned}, headers={'Content-Type': 'application/json'})
    if resp.status_code != 200:
        print("#ERROR citation lookup failed %s." % cleaned)
        raise Exception("Crossref request failed")
    details = resp.json()
    found = details.get('message', {}).get('items', [])
    if len(found) == 0:
        cite_meta = []
        ok = False
    else:
        #Lookup the DOIs and get metadata for the located citations.
        item = found[0]
        doi = item.get('DOI')
        meta = fetch_doi(doi)
        cite_meta = [meta]
        ok = True
    out = dict(status=ok, cites=cite_meta)
    return out


def fetch_doi(doi):
    #replace / in dois
    resp = requests.get(API_URL + "/doi/" + doi)
    if resp.status_code != 200:
        raise Exception("Crossref request failed.  Error code " + str(resp.status_code))
    meta = resp.json()
    #Some doi lookups are failing.  Not sure why.
    #We could also use the CrossRef OpenURL end point to find these:
    #http://www.crossref.org/openurl/?id=doi:10.1016/0166-0934(91)90005-K&noredirect=true&pid=KEY
    try:
        first = meta['message']
        return first
    except IndexError:
        print("#ERROR DOI lookup failed for %s." % doi)
        return {}

if __name__ == "__main__":
    d = '10.1021/mp050023q'
    meta = fetch_doi(d)
    print(meta.get('doi') == d)
    print(meta.get('title')[0].rfind('Drugs') > 0)

    cite = """
Dendrimers as drugs: discovery and preclinical and clinical development of dendrimer-based microbicides for HIV and STI prevention
…, P Karellas, SA Henderson, M Giannis… - Molecular …, 2005 - ACS Publications
"""
    cites = cite
    pprint(fetch_links(cites))
