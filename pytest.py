from flask import Flask, render_template

app = Flask("ersteapp")

@app.route('/')
def gitpy():
    return "Hey Furk"

@app.route('/write')
def write():
    return render_template('write.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)


