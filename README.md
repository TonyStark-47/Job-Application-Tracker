# 💼 Job Application Tracker ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-2.2+-green) ![MIT License](https://img.shields.io/badge/License-MIT-yellow) ![Status](https://img.shields.io/badge/Status-Completed-brightgreen)

> A full-stack job application tracker powered by Flask, AI, and browser automation.

A comprehensive web application to manage and track job applications with AI-powered data extraction and seamless Chrome Extension integration.

[![Live Demo](https://img.shields.io/badge/Demo-Link-blue)](https://job-application-tracker-33ph.onrender.com/)

---

## 🚀 Features

- **Dashboard Management**: Track all job applications with status badges and edit/delete options.
- **AI-Powered Data Extraction**: Automatically extract structured job data (title, company, date, etc.) from raw descriptions using Google Gemini API.
- **Chrome Extension Integration**: One-click job tracking from any job portal website.
- **User Authentication**: Secure registration/login system with OTP verification.
- **Status Visualization**: Colored badges representing application stages like Applied, Interviewed, Offered, etc.

---

## 🛠️ Tech Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login  
- **Frontend**: Bootstrap 5, Jinja2 Templates  
- **AI Integration**: Google Gemini API  
- **Database**: PostgreSQL (Production) / SQLite (Development)  
- **Authentication**: Email-based login with OTP (One Time Password)  

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TonyStark-47/Job-Application-Tracker.git
   cd Job-Application-Tracker
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory and add:
   ```env
   FLASK_SECRET_KEY=your_secret_key
   DB_URI=your_database_url
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. **Initialize the app**
   ```bash
   python main.py
   ```

---

## 🧩 Chrome Extension

A companion Chrome Extension is available for capturing job data from job boards with one click.

### 🔑 Extension Features:

- One-click job tracking from active web pages
- Saves job title, company, content, URL, and date
- Locally stores `user_id` for seamless authentication
- No additional login required if already authenticated

**🔗 Download Extension**: [Extension Repository](https://github.com/TonyStark-47/Extension-Job-Application-Tracker)

---

## 🔧 API Endpoints

### 🔄 Extension Integration

- `POST /save_data` – Accepts job data and saves it after optional AI parsing  
- `POST /login_through_extension` – Authenticates extension users with credentials  

### 🌐 Web Interface

- `GET /` – User dashboard displaying saved jobs  
- `GET /extension` – Information page for installing and using the extension  

---

## 🎨 User Interface

The web dashboard provides a responsive, Bootstrap-powered interface:

- **Status Badges**: Displays application stage using colored labels  
- **Responsive Table**: Lists all saved jobs, sorted by date or status  
- **User Controls**: Includes login/logout, search bar, and job entry forms  

---

## 🤖 AI Data Extraction

Uses **Google Gemini API** (or similar LLM) to extract structured data fields from raw job descriptions or full-text job pages.

### Extracted Fields:

- Job Title  
- Company  
- Application/Test/Interview Date  
- Job Status (e.g., Applied, Offered, Awaiting Interview)  
- Job Location  
- Job Link  

If no date or link is found, it assigns today’s date and a sample link automatically.

---

## 🚀 Usage Guide

1. **Register/Login** through the web dashboard  
2. **Save jobs manually** or use the **Chrome Extension**  
3. View and manage your jobs from the **dashboard**  
4. Receive **daily email reminders** for upcoming interviews/tests  

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🤝 Contributing
Got ideas? 💭 Found a bug? 🐞 Contributions are welcome!  
Submit a pull request or open an issue to collaborate.
