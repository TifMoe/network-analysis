from flask import Flask, render_template, jsonify, request, redirect, url_for
from src.features.fetch_data import fetch_data
import os

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('admin'))
    return render_template('landing.html', error=error)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


@app.route("/admin")
def admin():
    return render_template("index.html")


@app.route("/data")
def data():
    return jsonify(fetch_data(.3))


if __name__ == '__main__':
    app.run()