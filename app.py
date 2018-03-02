import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template

from crossref import fetch_links

import py360link

default_sersol_key = 'rl3tp7zf5x'

app = Flask(__name__)

@app.route('/fetch-cite', methods=['POST'])
def fetch_cite():
    if request.method == 'POST':
        cite = request.form.items()[0][0]
        results = fetch_links(cite)
        return jsonify(results)


@app.route('/resolve/<key>/', methods=['GET'])
@app.route('/resolve/', methods=['GET'])
def resolve(key=None):
    raw_query = request.query_string
    #remove http prefix from doi
    query = raw_query.replace('http://dx.doi.org/', '')
    sersol_key = request.view_args.get('key', default_sersol_key)
    #Setup some defaults for the json response.
    d = {}
    d['key'] = sersol_key
    d['library'] = None
    d['error'] = False
    d['url'] = None
    d['provider'] = None
    sersol = py360link.get(query, key=sersol_key, timeout=10)
    resolved = sersol.json()
    try:
        d['library'] = resolved['metadata']['library']
        groups = resolved['records'][0]['links']
        if groups is None:
            groups = []
        #Get the first link to a full text source
        for grp, link in enumerate(groups):
            if link['type'] == 'article':
                d['url'] = link['url']
                d['provider'] = link['anchor']
                break
    except IndexError:
        d['error'] = True
        print('#ERRROR 360Link %s' % query)
    d['query'] = query
    return jsonify(d)


@app.route('/<library>/')
@app.route('/')
def index(library=None):
    ctx = dict(
        ga_tracking_code=os.getenv('GA_TRACKING_CODE'),
        library=library,
    )
    return render_template('index.html', **ctx)


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    params = dict(host='0.0.0.0', port=port)
    if os.environ.get('HOME', '').find('vagrant') > -1:
        params['debug'] = True
    app.run(**params)
