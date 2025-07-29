from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

entryList = []   

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        userName = request.form.get("username")
        password = request.form.get("password")

    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        date = request.form.get("date")
        content = request.form.get("content")
        return f'{date}: {content}'
    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)