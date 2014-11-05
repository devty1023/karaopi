import glob
import os
import requests
import urllib
from flask import Flask, render_template, url_for, jsonify, request

from codec_skym import Skym
from kmsearch import km_search

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get("query", "").encode('cp949')
        qtype = request.form.get("qtype", "")
        page =  request.form.get("page", 1)
        if query:
            query = urllib.parse.unquote_to_bytes(query)
            print(query)
            query = urllib.parse.quote(query)
            songs = km_search(query=query, page=page, qtype=qtype)
            page = int(page)
            return render_template("search.html", songs=songs, query=query, qtype=qtype, next_page=(page+1))
    return render_template("index.html")


@app.route('/show/<song>')
def show(song):
    files = glob.glob('static/audio/*')
    songs = [file.split('/')[-1].split('.')[0] for file in files]

    if song not in songs:
        return render_template("loading.html", sid=song)

    else:
        return render_template("show.html", sid=song)

@app.route('/src/<song>')
def audio(song):
    return app.send_static_file(os.path.join('audio', song))

@app.route('/data/<sid>')
def timing(sid):
    spath = os.path.join('static/audio', '{}.skym'.format(sid))
    print(spath)
    sk = Skym.open(spath) 
    return sk.toJson()

@app.route('/download/<sid>')
def download_audio(sid):
    ROOT_URL = "http://cyms.chorus.co.kr/cykara_dl2.asp?song_id={0}"
    PATH = 'static/audio'

    target = ROOT_URL.format(sid)
    destination = os.path.join(PATH, "{0}.skym".format(sid))

    try:
        r = requests.get(target, stream=True)
        if r.status_code == requests.codes.ok:
            with open(destination, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return jsonify(status=True)
    except Exception as e:
        try:
            os.remove(destination)
        except:
            pass
   
    return jsonify(status=False)

@app.route('/loading/<sid>')
def loading(sid):
    return render_template("loading.html", sid=sid)

if __name__ == "__main__":
    app.run(debug=False)

