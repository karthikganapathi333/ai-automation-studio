from flask import Flask, render_template, request, redirect, flash
from flask_mail import Mail, Message
import sqlite3
import os

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'aiautomationstudio30@gmail.com'
app.config['MAIL_PASSWORD'] = 'vnwrjfeadeoaeioi'
app.config['MAIL_DEFAULT_SENDER'] = ('AI Automation Studio', 'YOUR_EMAIL@gmail.com')

mail = Mail(app)

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
        msg = Message(
    subject=f"📩 New Contact from {name}",
    recipients=['YOUR_EMAIL@gmail.com'],
    body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")
        mail.send(msg)

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
    msg = Message(
    subject=f"💬 New Quote Request from {name}",
    recipients=['YOUR_EMAIL@gmail.com'],
    body=f"Service: {service}\n\nDetails:\n{details}\n\nEmail: {email}")
    mail.send(msg)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
