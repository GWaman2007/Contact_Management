# 📇 Contacts Store - Flask REST API & Dashboard

A secure, full-stack **Contact Management REST API** built with **Flask**, **SQLite**, **Flask-Bcrypt**, **Flask-JWT-Extended**, and a responsive JavaScript frontend.

Includes full CRUD operations, JWT authentication, user ownership isolation, and a unique **Secret Hidden Contacts** feature.

---

## ✨ Features

- 🔐 **User Authentication**: Secure user registration and login using **Flask-Bcrypt** for password hashing and **JWT Access Tokens** for session management.
- 📇 **Full Contact CRUD**: Create, read, update, and delete contacts attached to your user account.
- 🕵️ **Secret Hidden Contacts**: Assign a custom `hide_code` to sensitive contacts. Hidden contacts are filtered out of standard search results and list views unless unlocked with the matching hide code.
- 🖼️ **Profile Images & Professions**: Store contact details including Name, Phone Number, Email, Company, Relation / Profession, and Profile Image URL.
- 📱 **Responsive Frontend**: Clean, responsive UI with alphabetical grouping, profile avatars, live search, and modal forms.
- 🛡️ **Resource Ownership & Security**: Endpoints strictly enforce user-level authorization checks.
- ⚠️ **Custom Error Handling Pages**: Renders custom `404 Page Not Found` and `500 Server Error` HTML templates for browser navigation, and structured JSON responses for API requests.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy, Flask-Bcrypt, Flask-JWT-Extended
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla ES6 Fetch API), Bootstrap 5 Icons

---

## 📂 Project Structure

```text
Contacts-Store/
├── app.py                  # Flask application factory, page routes & error handlers
├── config.py               # Application configuration (DB URI, JWT secret keys)
├── extensions.py           # SQLAlchemy, Bcrypt, and JWT instances
├── models.py               # User and Contact SQLAlchemy database models
├── routes/
│   ├── auth_routes.py      # User Authentication endpoints (/api/auth/*)
│   └── contact_routes.py   # Contact CRUD & Search endpoints (/create, /get, /search, etc.)
├── templates/
│   ├── index.html          # Main Dashboard page
│   ├── login_.html         # Login page
│   ├── Register.html       # Registration page
│   ├── 404.html            # Custom 404 Not Found error template
│   └── 500.html            # Custom 500 Server Error template
├── static/
│   ├── js/                 # Client-side JavaScript (script.js, login.js, Register.js)
│   └── style/              # Custom stylesheets (style.css, login_.css, Register.css, error.css)
└── requirements.txt        # Python package dependencies
```

---

## 🚀 Quick Start & Setup

### 1. Clone Repository
```bash
git clone https://github.com/GWaman2007/Contact_Management.git
cd Contact_Management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application Server
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 🔌 API Endpoints Summary

### Authentication
| Method | Endpoint | Description | Payload |
|--------|----------|-------------|---------|
| `POST` | `/api/auth/register` | Register new user account | `{"name": "...", "email": "...", "password": "..."}` |
| `POST` | `/api/auth/login` | Authenticate & get JWT token | `{"email": "...", "password": "..."}` |
| `GET`  | `/api/auth/me` | Fetch logged-in user profile | Bearer Token |

### Contact Management
| Method | Endpoint | Description | Authorization | Parameters |
|--------|----------|-------------|---------------|------------|
| `POST` | `/create` | Create a new contact | Bearer Token | JSON body with contact details |
| `GET`  | `/get` | List normal contacts | Bearer Token | `code` *(Optional: pass to reveal hidden contacts)* |
| `GET`  | `/get/<c_id>` | Fetch single contact | Bearer Token | `code` *(Required if contact is hidden)* |
| `GET`  | `/search` | Search contacts | Bearer Token | `q` *(Search query)*, `code` *(Secret code)* |
| `PUT`  | `/update/<c_id>` | Update existing contact | Bearer Token | JSON body with updated fields |
| `DELETE` | `/delete/<c_id>` | Delete contact by ID | Bearer Token | Path parameter `c_id` |

---

## 📜 License
Distributed under the MIT License.
