from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            hourly_rate REAL NOT NULL,
            hours INTEGER NOT NULL,
            total_payment REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_record():
    name = request.form['name']
    hourly_rate = float(request.form['hourly_rate'])
    hours = int(request.form['hours'])
    total_payment = hourly_rate * hours
    date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO attendance (name, hourly_rate, hours, total_payment, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, hourly_rate, hours, total_payment, date))
    conn.commit()
    conn.close()

    return redirect('/records')

@app.route('/records')
def records():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name, strftime('%Y-%m', date) AS month,
               SUM(hours) as total_hours,
               SUM(total_payment) as total_payment
        FROM attendance
        GROUP BY name, month
        ORDER BY month DESC
    ''')
    data = cursor.fetchall()
    conn.close()
    return render_template('records.html', records=data)

@app.route('/clear', methods=['POST'])
def clear_all():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance")
    conn.commit()
    conn.close()
    return redirect('/records')

@app.route('/clear_month', methods=['POST'])
def clear_month():
    month = request.form['month']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE strftime('%Y-%m', date) = ?", (month,))
    conn.commit()
    conn.close()
    return redirect('/records')

if __name__ == '__main__':
    app.run(debug=True)
