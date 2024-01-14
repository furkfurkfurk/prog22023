from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime

app = Flask("ersteapp")

JSON_FILE = 'eintraege.json'

def save_eintrag(eintrag_data):
    try:
        with open(JSON_FILE, 'r') as file:
            eintraege = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        eintraege = []
    
    eintraege.append(eintrag_data)
    
    with open(JSON_FILE, 'w') as file:
        json.dump(eintraege, file, indent=4)

def load_eintraege():
    try:
        with open(JSON_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
@app.route('/submit_entry', methods=['POST'])
def submit_entry():
    eintrag_data = {
        'date': request.form.get('entry_date'),
        'mood': request.form.get('entry_mood'),
        'highlight': request.form.get('entry_highlight'),
        'lowpoint': request.form.get('entry_lowpoint'),
        'content': request.form.get('entry_content')
    }
    save_eintrag(eintrag_data)
    return redirect(url_for('index'))

@app.route('/eintrag/<int:eintrag_id>')
def eintrag_detail(eintrag_id):
    eintraege = load_eintraege()
    eintrag = eintraege[eintrag_id - 1]  # Indizes beginnen bei 0, IDs normalerweise bei 1
    return render_template('eintrag_detail.html', eintrag=eintrag)




@app.route('/')
def gitpy():
    return "Hey Furk"

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        eintrag_data = {
            'date': request.form['entry_date'],
            'mood': request.form['entry_mood'],
            'highlight': request.form['entry_highlight'],
            'lowpoint': request.form['entry_lowpoint'],
            'content': request.form['entry_content']
        }
        save_eintrag(eintrag_data)
        return redirect(url_for('index'))
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('write.html', today=today)


@app.route('/eintraege')
def eintraege_anzeigen():
    filter_date = request.args.get('filter_date')
    filter_mood = request.args.get('filter_mood')
    eintraege = load_eintraege()

    if filter_date:
        eintraege = [e for e in eintraege if e['date'] == filter_date]
    if filter_mood:
        eintraege = [e for e in eintraege if e['mood'] == filter_mood]

    return render_template('eintraege.html', eintraege=eintraege)






if __name__ == '__main__':
    app.run(debug=True, port=5000)


