from flask import Flask, flash, redirect, render_template, url_for, request, session, abort, Response
import json
from shutil import copyfile
import uuid
from os import listdir, path, remove


app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"
data_file = 'C:/Users/Ben/dev/python/crypo-check/data/crypto_values.json'
chart_file = 'C:/Users/Ben/dev/python/crypo-check/data/crypto_pie.jpg'


@app.route("/")
def index():
    return "web service..."



@app.route("/crypto/coins/")
def crypto():
    crypto_values = json.loads(open(data_file).read())
    flattened = crypto_values['data']
    flattened['timestamp'] = crypto_values['timestamp']
    resp = Response(json.dumps(flattened, indent=2))
    resp.headers['Cache-Control'] = 'private, must-revalidate, max-age=0'
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route("/crypto/coins/<string:coin>/")
def get_chart(coin):
    if len(coin) < 10:
        crypto_values = json.loads(open(data_file).read())
        output = {'timestamp':crypto_values['timestamp']}
        for key, item in crypto_values['data'].items():
            if isinstance(item, dict):
                output[key] = item.get(coin.upper(), None)
            elif isinstance(item, list):
                pass
            else:
                output[key] = item
        resp = Response(json.dumps(output, indent=2))
        resp.headers['Cache-Control'] = 'private, must-revalidate, max-age=0'
        resp.headers['Content-Type'] = 'application/json'
        return resp
    else:
        return 'coin too long'


@app.route("/crypto/chart/")
def chart():
    # copy file
    new_file_name = 'chart/' + str(path.getmtime(chart_file))
    if not path.exists('static/' + new_file_name):
        [remove('static/chart/' + str(f)) for f in listdir('static/chart/')]
        copyfile(chart_file, 'static/' + new_file_name)

    resp = Response(render_template('pie.html', filename=new_file_name))
    resp.headers['Cache-Control'] = 'private, must-revalidate, max-age=0'
    return resp


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=80)
    # app.run(host='83.216.81.199', port=80)
    # context = ('cert.crt', 'key.key')
    app.run(host='192.168.15.36', port=80)#, ssl_context=context)
