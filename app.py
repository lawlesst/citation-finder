import os
from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template

from crossref import fetch_links

app = Flask(__name__)

@app.route('/<library>/')
@app.route('/')
def index(library=None):
    return render_template('index.html', library=library)

@app.route('/fetch-cite', methods=['POST'])
def fetch_cite():
    if request.method == 'POST':
        cite = request.form.items()[0][0]
        results = fetch_links(cite)
        return jsonify(results)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    params = dict(host='0.0.0.0', port=port)
    if os.environ.get('HOME', '').find('vagrant') > -1:
        params['debug'] = True
    app.run(**params)