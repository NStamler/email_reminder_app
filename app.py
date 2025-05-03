from flask import Flask, render_template, request, redirect, url_for, flash
from itsdangerous import URLSafeSerializer
from emailer import send_confirmation_email, send_edit_link
from database import add_user, get_user_by_email, update_user, delete_user
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super-secret-key")  # Replace in prod

# Token serializer for email links
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
    digest_range = request.form.get('digest_range')  # past or upcoming

    user = get_user_by_email(email)
    if user:
        flash("You're already signed up! Sending edit link to your email.")
        send_edit_link(email, serializer.dumps(email))
        return redirect(url_for('index'))

    add_user(email, days_before, time_of_day, digest, digest_day, digest_time, digest_range)
    token = serializer.dumps(email)
    send_confirmation_email(email, token)
    flash("Signup successful! Please check your email to confirm and manage preferences.")
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
        send_edit_link(email, token)  # confirmation
        flash("Preferences updated! A confirmation email was sent.")
        return redirect(url_for('edit', token=token))
    except:
        flash("Something went wrong.")
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
