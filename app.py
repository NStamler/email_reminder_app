from flask import Flask, render_template, request, redirect, url_for, flash
from itsdangerous import URLSafeSerializer
from emailer import send_confirmation_email, send_edit_link
from database import add_user, get_user_by_email, update_user, delete_user, init_db
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

# Auto-initialize the database on startup
init_db()

# Serializer for generating secure tokens
serializer = URLSafeSerializer(app.secret_key)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    days_before = int(request.form['days_before'])
    time_of_day = request.form['time_of_day']
    digest = request.form.get('digest') == 'on'
    digest_day = request.form.get('digest_day')
    digest_time = request.form.get('digest_time')
    digest_range = request.form.get('digest_range')  # "upcoming" or "past"

    user = get_user_by_email(email)
    if user:
        flash("You're already signed up! Sending your edit link.")
        token = serializer.dumps(email)
        send_edit_link(email, token)
        return redirect(url_for('index'))

    add_user(email, days_before, time_of_day, digest, digest_day, digest_time, digest_range)
    token = serializer.dumps(email)
    send_confirmation_email(email, token)
    flash("Signup successful! A confirmation email was sent.")
    return redirect(url_for('index'))

@app.route('/edit/<token>')
def edit(token):
    try:
        email = serializer.loads(token)
        user = get_user_by_email(email)
        if user:
            return render_template('edit.html', user=user, token=token)
    except:
        flash("Invalid or expired link.")
    return redirect(url_for('index'))

@app.route('/update/<token>', methods=['POST'])
def update(token):
    try:
        email = serializer.loads(token)
        days_before = int(request.form['days_before'])
        time_of_day = request.form['time_of_day']
        digest = request.form.get('digest') == 'on'
        digest_day = request.form.get('digest_day')
        digest_time = request.form.get('digest_time')
        digest_range = request.form.get('digest_range')

        update_user(email, days_before, time_of_day, digest, digest_day, digest_time, digest_range)

        # Send confirmation email after update
        send_edit_link(email, token)

        flash("Preferences updated! A confirmation email has been sent.")
        return redirect(url_for('edit', token=token))
    except Exception as e:
        flash(f"Error updating preferences: {str(e)}")
        return redirect(url_for('index'))

@app.route('/unsubscribe/<token>')
def unsubscribe(token):
    try:
        email = serializer.loads(token)
        delete_user(email)
        flash("You've been unsubscribed.")
    except:
        flash("Invalid or expired link.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
