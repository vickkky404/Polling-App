# Polling App

A **full-featured polling web application** built with **Python Flask** and **SQLite**, allowing users to create polls, vote, view results, and manage polls. The app includes user authentication, poll expiry, categories, real-time charts, and a gradient UI.

---

## Features

- **User Authentication**: Register, login, and logout.
- **Create Polls**: Add poll questions with multiple options, category, and expiry date.
- **Vote**: Users can vote once per poll.
- **Poll Results**: Display results using dynamic **Chart.js** bar charts.
- **Delete Polls**: Users can delete their polls.
- **Gradient UI**: Modern and responsive UI using **Bootstrap**.
- **SQLite Database**: Lightweight and easy-to-manage database.

**Planned Advanced Features (future updates)**:

- Admin dashboard
- Export poll results as CSV/PDF
- Poll comments
- Multi-language (i18n) support
- Real-time live vote updates

---

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML, Bootstrap 5, Chart.js
- **Password Security**: Werkzeug password hashing

---

## Folder Structure
polling_app/
│
├── app.py # Main Flask application
├── models.py # Database setup and connection
├── polls.db # SQLite database file
├── templates/ # HTML templates
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── create_poll.html
│ ├── poll.html
│ └── results.html
├── static/
│ └── styles.css # Optional custom CSS
└── README.md # Project documentation

