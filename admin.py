from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "admin_secret_key"

@app.route('/')
def home_redirect():
    return redirect('/admin')

# --- ADMIN LOGIN PAGE ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash("❌ Invalid login credentials")
            return redirect('/admin')

    return render_template('admin_login.html')


# --- ADMIN DASHBOARD ---
@app.route('/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin')

    conn = sqlite3.connect('messages.db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, name TEXT, email TEXT, message TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS quotes (id INTEGER PRIMARY KEY, name TEXT, email TEXT, service TEXT, details TEXT)")
    messages = conn.execute("SELECT * FROM messages").fetchall()
    quotes = conn.execute("SELECT * FROM quotes").fetchall()
    conn.close()

    return render_template('admin_dashboard.html', messages=messages, quotes=quotes)


# --- ADMIN LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Logged out successfully")
    return redirect('/admin')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
