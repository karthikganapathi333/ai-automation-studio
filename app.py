from flask import Flask, render_template, request, redirect, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "aistudio_secret"

# --- Create DB if not exists ---
if not os.path.exists("messages.db"):
    with sqlite3.connect("messages.db") as conn:
        conn.execute("CREATE TABLE messages (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        with sqlite3.connect("messages.db") as conn:
            conn.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (name, email, message))
        flash("Message sent successfully! We'll reach out soon 😊")
        return redirect('/contact')
    return render_template('contact.html')

@app.route('/quote', methods=['POST'])
def quote():
    name = request.form['name']
    email = request.form['email']
    service = request.form['service']
    details = request.form['details']

    with sqlite3.connect("messages.db") as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, name TEXT, email TEXT, service TEXT, details TEXT)")
        conn.execute("INSERT INTO quotes (name, email, service, details) VALUES (?, ?, ?, ?)", (name, email, service, details))
    flash("✅ Quote request sent successfully! We'll contact you soon.")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
