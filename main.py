from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, String
from flask_login import UserMixin, LoginManager, login_user, current_user, logout_user

from forms import JobApplicationForm, RegisterForm, LoginForm, OTPForm

import random
from smtplib import SMTP
from datetime import datetime

from flask_apscheduler import APScheduler

import json
import re

from agent import get_response


import os
import dotenv


dotenv.load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
Bootstrap5(app)


# for scheduling task/job
scheduler = APScheduler()
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URI', "sqlite:///blog.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class JobDetails(db.Model):
    __tablename__ = 'job_details'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(200))
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    link: Mapped[str] = mapped_column(String(500))

    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates='job_details')


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)

    job_details = relationship('JobDetails', back_populates='user')



with app.app_context():
    db.create_all()


# Decorator
def loggedin(func):
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return func(*args, **kwargs)
        else:
            # return abort(403)
            return redirect(url_for('home'))
    decorated_function.__name__ = func.__name__
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user:
            flash('You already signed up with that email.')
            return redirect(url_for('login'))
        # Generate OTP
        otp = random.randint(1000, 9999)
        session['otp'] = otp
        session['email'] = form.email.data
        session['password'] = form.password.data
        session['name'] = form.name.data

        # Send OTP to the user's email
        print(f"Sending OTP: {otp}")  # For debugging purposes
        message = f"Subject:OTP for email verification\n\nHere is your OTP for your email verification on Job APPlication Tracker\nOTP:{session['otp']}"
        message_sent = send_email(message, form.email.data)
        if not message_sent:
            flash('Failed to send OTP. Please try again.')
            return redirect(url_for('register'))

        # Redirect to OTP verification page
        return redirect(url_for('get_verify_otp'))

    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if user.password == password:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash('Wrong Password, Try Again!')
                return redirect(url_for('login'))
        else:
            flash("User doesn't exist. Register this email first.")
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route('/logout')
@loggedin
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/home')
@app.route('/')
def home():
    if current_user.is_authenticated:
        jobs = db.session.execute(db.select(JobDetails).where(JobDetails.user_id == current_user.id)).scalars().all()
        for job in jobs:
            if isinstance(job.date, str):  # Only convert if stored as string
                job_date = datetime.strptime(job.date, "%Y-%m-%d")
                job.date = job_date.strftime("%B %d, %Y")
    else:
        jobs = {'id': 0, "job_title": "(Dummy) Sustainability Intern", "company": "Sonoma Holdings", 
                "status": "Awaiting Interview", "location": "Singapore",
                "date": "2025-03-04", "link": "www.linkedin.com"},
    return render_template('index.html', jobs=jobs)



@app.route('/add', methods=['GET', 'POST'])
@loggedin
def add_application():
    form = JobApplicationForm()
    if form.validate_on_submit():
        new_job_details = JobDetails(
            user_id=current_user.id,
            job_title=form.job_title.data,
            company=form.company.data,
            status=form.status.data,
            location=form.location.data,
            date=form.date.data,
            link=form.link.data
        )

        db.session.add(new_job_details)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('job_form.html', form=form)



@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
@loggedin
def edit_job(job_id):
    job = db.session.execute(db.select(JobDetails).where(JobDetails.id == job_id)).scalar()
    form = JobApplicationForm(obj=job)

    if form.validate_on_submit():
        job.user_id = current_user.id
        job.job_title = form.job_title.data
        job.company = form.company.data
        job.status = form.status.data
        job.location = form.location.data
        job.date = form.date.data
        job.link = form.link.data

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('job_form.html', form=form, job_id=job_id)


@app.route('/delete/<int:job_id>')
@loggedin
def delete_job(job_id):
    job = db.session.execute(db.select(JobDetails).where(JobDetails.id == job_id)).scalar()
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    text = request.form.get('search', '').strip()
    if not text:
        return redirect(url_for('home'))
    search_text = f"%{text.lower()}%"
    result = db.session.execute(
        db.select(JobDetails).where(
            db.and_(
                JobDetails.user_id == current_user.id,
                db.or_(
                    JobDetails.job_title.ilike(search_text),
                    JobDetails.company.ilike(search_text),
                    JobDetails.status.ilike(search_text),
                    JobDetails.location.ilike(search_text),
                    JobDetails.date.ilike(search_text),
                    JobDetails.link.ilike(search_text)
                )
            )
        )
    ).scalars().all()
    # if not result:
    #     flash('Search result not found.')

    return render_template('index.html', jobs=result)


@app.route('/otp', methods=['GET', 'POST'])
def get_verify_otp():
    form = OTPForm()
    if form.validate_on_submit():
        entered_otp = form.otp.data
        if 'otp' in session and int(entered_otp) == session['otp']:
            # OTP is correct, register the user
            new_user = User(
                email=session['email'],
                password=session['password'],
                name=session['name']
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)

                # Clear session data
                session.pop('otp', None)
                session.pop('email', None)
                session.pop('password', None)
                session.pop('name', None)

                return redirect(url_for('home'))
            except:
                flash('You already signed up with that email.')
                return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')

    return render_template('otp.html', form=form)

@app.route('/secret/hehehe')
def show_all_job_application():
    jobs = db.session.execute(db.select(JobDetails)).scalars().all()
    return render_template('index.html', jobs=jobs)


@app.route('/save_data', methods=["GET", "POST"])
def save_data():
    data = request.json
    print("Received data:", data)

    today_date = datetime.today().strftime('%Y-%m-%d')

    prompt = f"""
    You are an intelligent job data extractor.

    I will provide you with raw extracted text from a job portal. Your task is to parse the text and extract job-related information. 
    Your response must be in **pure JSON format** with the following keys:

    - "job_title" (str): Title of the job role  
    - "company" (str): Name of the company  
    - "status" (str): Application status. Choose from the following:
    - "Applied", "Interviewed", "Rejected", "Offered", "Awaiting Interview"
    - If no exact match, return a best-guess such as "Hiring Challenge"
    - "location" (str): Use short, city-level names (1–2 words only)
    - "date" (str): Date of apply/test/interview in `YYYY-MM-DD` format  
    - If no date is found in the text, use today’s date: "{today_date}"
    - "link" (str): Link to the job posting  
    - If not found, use a placeholder like `"https://sample-job-link.com"`

    Additional Instructions:
    - Do **not** include any keys with `null`, `None`, or empty values.
    - If multiple jobs are present in the text, return only the one(s) I have applied for.
    - Output must be in **valid JSON** and nothing else — no explanations, no extra text.

    Here is the extracted data:
    {data}
    """
   
    job_details_raw = get_response(prompt)
    print(job_details_raw)

    # Try to extract JSON object from the raw string
    match = re.search(r'\{.*\}', job_details_raw, re.DOTALL)

    if match:
        json_str = match.group(0)
        job_details = json.loads(json_str)
        print(job_details)  # Clean Python dict
    else:
        print("No valid JSON object found.") 
  
   
    # try:
    new_job_details = JobDetails(
        user_id=1,
        job_title=job_details["job_title"],
        company=job_details["company"],
        status=job_details["status"],
        location=job_details["location"],
        date=job_details["date"],
        link=job_details["link"]
    )
    # except Exception as e:
    #     print(f"Error parsing job details: {e}\n Users already exists")
    #     return jsonify({"status": "error", "message": "Failed to parse job details"}), 400

    db.session.add(new_job_details)
    db.session.commit()
    # return redirect(url_for('home'))
    return jsonify({"status": "success", "recieved": data, "job_details": job_details})


def send_email(message, to_email):
    MY_EMAIL = os.getenv('MY_EMAIL')
    MY_PASSWORD = os.getenv('MY_PASSWORD')

    try:
        with SMTP(host='smtp.gmail.com', port=587) as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(from_addr=MY_EMAIL, to_addrs=to_email, msg=message)
            print(f'message sent {message} to {to_email}')
            return True
    except:
        print('message not sent.')
        return False

@scheduler.task('cron', id='send notification', hour='16', minute=0, timezone='Asia/Kolkata')
def send_notification():
    with app.app_context():
        print('yes, notification is on the way...')
        today_date = datetime.now().strftime("%Y-%m-%d")
        jobs = db.session.execute(db.select(JobDetails).where(JobDetails.date == today_date)).scalars().all()
        for job in jobs:
            email = job.user.email
            message = f"Subject:Upcoming Interview Reminder: {job.job_title} at {job.company}\n\nYour interview for {job.job_title} at {job.company} is scheduled on {job.date}.\nYour status of the application is: {job.status}\n Best of luck!"
            send_email(message, email)


if __name__ == '__main__':
    app.run(debug=True, port=5000)