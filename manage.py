#!/usr/bin/env python
from flask import Flask, jsonify, render_template
from flask_script import Manager
import requests

app = Flask(__name__)
app.debug = True


def getSpares():
    return requests.get('https://job.firstvds.ru/spares.json').json()


def getAlts():
    return requests.get(
        'https://job.firstvds.ru/alternatives.json').json()['alternatives']


@app.route('/')
def index():
    spares, alts = getSpares(), getAlts()
    notEnoughSpares = []
    # Alternatives processing
    for categoryKey, alts in alts.items():
        spares[categoryKey] = {}
        category = spares[categoryKey]
        for alt in alts:
            if alt in spares:
                category['mustbe'] = max(
                    category.get('mustbe', 0),
                    spares[alt]['mustbe'])
                category['count'] = category.get(
                    'count', 0) + spares[alt]['count']
                category['arrive'] = category.get(
                    'arrive', 0) + spares[alt]['arrive']
                del spares[alt]
    # Which not enough
    for spareKey, spare in spares.items():
        if spare['count'] < spare['mustbe']:
            notEnoughSpares.append(spareKey)
    return render_template('index.html',
                           title='fvds_test',
                           spares=spares,
                           notEnoughSpares=notEnoughSpares,
                           sortedSpares=sorted(spares))


@app.route('/json')
def jsonPage():
    spares = getSpares()
    out = {}
    for spareKey, spare in spares.items():
        if spare['count'] + spare['arrive'] < spare['mustbe']:
            out[spareKey] = spare['mustbe'] - spare['count'] + spare['arrive']
    return jsonify(out)


manager = Manager(app)
if __name__ == '__main__':
    manager.run()
