from flask import Flask, render_template, jsonify, request, redirect, url_for
from graph_data import get_data

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route("/data")
def data():
    return jsonify(get_data())


if __name__ == '__main__':
    app.run()