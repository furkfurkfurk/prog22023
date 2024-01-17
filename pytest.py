from flask import Flask, render_template, request, redirect, url_for, session
import json
from datetime import datetime
import plotly.graph_objs as go


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
    

# Datum schöner in einträge.html anzeigen
def format_date(date_str):
    # Annahme: date_str hat das Format 'YYYY-MM-DD'
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    formatted_date = date_obj.strftime('%A %d. %B %Y')
    return formatted_date

eintraege = load_eintraege()
for eintrag in eintraege:
    eintrag['formatted_date'] = format_date(eintrag['date'])

#einträge chronologisch ordnen
eintraege.sort(key=lambda x: x['date'])


    
@app.route('/submit_entry/<int:new_id>', methods=['POST'])
def submit_entry(new_id):
    # Verwende new_id in deiner Funktion
    eintraege = load_eintraege()
    
    eintrag_data = {
        'id': new_id,
        'date': request.form.get('entry_date'),
        'mood': request.form.get('entry_mood'),
        'highlight': request.form.get('entry_highlight'),
        'lowpoint': request.form.get('entry_lowpoint'),
        'content': request.form.get('entry_content')
    }
    
    save_eintrag(eintrag_data)
    session['confirmation_message'] = 'Dein Beitrag wurde erfolgreich erfasst.'
    return redirect(url_for('index'))

app.secret_key = b'my_secret_key_123'


@app.route('/eintrag/<int:eintrag_id>')
def eintrag_detail(eintrag_id):
    eintraege = load_eintraege()
    eintrag = eintraege[eintrag_id - 1]  # Indizes beginnen bei 0, IDs normalerweise bei 1
    return render_template('eintrag_detail.html', eintrag=eintrag)


@app.route('/eintrag_bearbeiten/<int:eintrag_id>', methods=['GET', 'POST'])
def eintrag_bearbeiten(eintrag_id):
    # Lade alle Einträge
    eintraege = load_eintraege()

    # Finde den spezifischen Eintrag mit eintrag_id
    eintrag = next((e for e in eintraege if e['id'] == eintrag_id), None)

    # Überprüfe, ob der Eintrag existiert
    if eintrag is None:
        # Fehlerbehandlung, z.B. Weiterleitung zur Fehlerseite oder Anzeige einer Fehlermeldung
        pass

    if request.method == 'POST':
        # Die aktualisierten Daten aus dem Formular holen
        eintrag['date'] = request.form['date']
        eintrag['mood'] = request.form['mood']
        eintrag['highlight'] = request.form['highlight']
        eintrag['lowpoint'] = request.form['lowpoint']
        eintrag['content'] = request.form['content']

        # Die aktualisierten Einträge speichern
        save_eintraege(eintraege)

        # Weiterleitung zur Übersichtsseite
        return redirect(url_for('eintraege_anzeigen'))

    # Das Bearbeitungsformular mit den vorhandenen Eintragsdaten rendern
    return render_template('eintrag_bearbeiten.html', eintrag=eintrag)


def save_eintraege(eintraege): #aktualisierte beiträge
    try:
        with open(JSON_FILE, 'w') as file:
            json.dump(eintraege, file, indent=4)
    except IOError as e:
        print(f"Beim Speichern der Einträge ist ein Fehler ist aufgetreten : {e}")



@app.route('/')
def gitpy():
    return "Hey Furk"

@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        eintraege = load_eintraege()
        new_id = 1
        new_id = max([eintrag.get('id', 0) for eintrag in eintraege], default=0) + 1
        eintrag_data = {
            'id': new_id,
            'date': request.form['entry_date'],
            'mood': request.form['entry_mood'],
            'highlight': request.form['entry_highlight'],
            'lowpoint': request.form['entry_lowpoint'],
            'content': request.form['entry_content']
        }
        eintraege.append(eintrag_data)
        save_eintraege(eintraege)
        return redirect(url_for('eintraege_anzeigen'))
    else:
        eintraege = load_eintraege()
        new_id = max([eintrag.get('id', 0) for eintrag in eintraege], default=0) + 1
        today = datetime.now().strftime('%Y-%m-%d')
        return render_template('write.html', today=today, new_id=new_id)

#Neuer Chart um stimmungsverlauf der letzten 30 tage anzuzeigen
    

def create_mood_chart():
    eintraege = load_eintraege()  # Laden Sie alle Einträge
    # Sortieren Sie die Einträge nach Datum (vorausgesetzt, 'date' ist im richtigen Format)
    eintraege.sort(key=lambda x: x['date'])

    # Filtern Sie die Einträge auf die letzten 30 Tage
    last_30_days = eintraege[-30:]

    # Erstellen Sie eine Liste der Datenpunkte für das Diagramm
    dates = [entry['date'] for entry in last_30_days]
    moods = [int(entry['mood']) for entry in last_30_days]

    # Stellen Sie die Daten für das Frontend bereit
    chart_data = {
        'x': dates,
        'y': moods,
        'type': 'line',  
        'name': 'Stimmung'
    }

    return chart_data

def calculate_average_mood():
    eintraege = load_eintraege()  # Laden Sie alle Einträge
    last_30_days = eintraege[-30:]  # Filtern Sie die letzten 30 Tage

    if len(last_30_days) > 0:
        sum_mood = sum(int(entry['mood']) for entry in last_30_days)
        average_mood = sum_mood / len(last_30_days)
    else:
        average_mood = 0  # Falls keine Einträge vorhanden sind

    return average_mood


@app.route('/eintraege')
def eintraege_anzeigen():
    average_mood = calculate_average_mood()
    chart_data = create_mood_chart()  # Hier wird das Diagramm erstellt
    filter_date = request.args.get('filter_date')
    filter_mood = request.args.get('filter_mood')
    eintraege = load_eintraege()

    if filter_date:
        eintraege = [e for e in eintraege if e['date'] == filter_date]
    if filter_mood:
        eintraege = [e for e in eintraege if e['mood'] == filter_mood]

    return render_template('eintraege.html', eintraege=eintraege, format_date=format_date, average_mood=average_mood, chart_data=chart_data)


@app.route('/eintrag_loeschen/<int:eintrag_id>', methods=['POST'])
def eintrag_loeschen(eintrag_id):
    # Lade alle Einträge
    eintraege = load_eintraege()

    # Finde den spezifischen Eintrag mit eintrag_id
    eintrag = next((e for e in eintraege if e['id'] == eintrag_id), None)

    # Überprüfe, ob der Eintrag existiert
    if eintrag is None:
        # Fehlerbehandlung, z.B. Weiterleitung zur Fehlerseite oder Anzeige einer Fehlermeldung
        pass

    # Entferne den Eintrag aus der Liste
    eintraege.remove(eintrag)

    # Speichere die aktualisierten Einträge
    save_eintraege(eintraege)

    # Weiterleitung zur Übersichtsseite
    return redirect(url_for('eintraege_anzeigen'))




if __name__ == '__main__':
    app.run(debug=True, port=5000)


