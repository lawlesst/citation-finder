"""
Work with the crossref APIs.
"""


import json
import requests

def fetch_links(citations):
    cr = 'http://search.labs.crossref.org/links'
    resp = requests.post(cr, data=json.dumps(citations))
    if resp.status_code != 200:
        raise Exception("Crossref request failed")
    match_dict = json.loads(resp.content)
    results = match_dict.get('results')
    ok = match_dict.get('query_ok')
    return match_dict

