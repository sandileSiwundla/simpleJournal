from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

entryList = []   

@app.route('/')
def index():
    entry1 = {"date" : "23/03/2024" }
    entry2 = {"date" : "24/03/2024"}
    entryList.append(entry1)
    entryList.append(entry2)
    entries = [{"title": "...", "content": "..."}]
    return render_template("index.html")


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    if request.method == 'POST':
        date = request.form.get("date")
        content = request.form.get("content")
        return f'{date}: {content}'
    return render_template('add.html')


if __name__ == '__main__':
    app.run()