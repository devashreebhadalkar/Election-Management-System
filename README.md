# 🗳️ Election Management System

A web-based **Election Management System** built using Python, Streamlit, and MySQL to demonstrate the digital management of election-related activities through a centralized interface.

## 🌐 Live Website

**Try the application here:**  
👉 https://election-management-system-2ethmb7tnxlzsm94d3zt42.streamlit.app/

## 📂 GitHub Repository

**Source code:**  
👉 https://github.com/devashreebhadalkar/Election-Management-System

## 📌 About the Project

The Election Management System is an academic project designed to simplify and organize election-related administrative operations. It provides a user-friendly dashboard and separate modules for managing election information and related records.

The project demonstrates how a Python-based web application can interact with a database to support structured data management.

## ✨ Features

- **Login System** – Login interface with role-based demo accounts.
- **Dashboard** – Overview of election management activities.
- **Election Management** – Interface for election-related records.
- **Voter Management** – Module for voter record management.
- **Candidate Management** – Module for candidate information.
- **Other Management Modules** – Dedicated pages for election administration, including claim and objection management.
- **Database Integration** – MySQL connectivity through Python.
- **Interactive Interface** – Multi-page web application built with Streamlit.

*The availability of each feature depends on the current implementation and database configuration.*

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Web interface |
| MySQL | Database management |
| MySQL Connector/Python | Python–MySQL connectivity |
| Pandas | Data handling |
| Plotly | Interactive visualizations |
| CSS | Interface styling |
| Git and GitHub | Version control and source code hosting |
| Streamlit Community Cloud | Application deployment |

## 🏗️ Project Structure

```text
Election-Management-System/
│
├── app.py
├── database.py
├── requirements.txt
├── test_db.py
│
├── css/
│   └── style.css
│
├── pages/
│   ├── 1_Dashboard.py
│   ├── ...
│   └── 9_Claim_Objection_Management.py
│
├── services/
│   ├── auth.py
│   └── ui.py
│
└── README.md
```

## 🚀 Run the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/devashreebhadalkar/Election-Management-System.git
```

### 2. Open the project directory

```bash
cd Election-Management-System
```

### 3. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure the database

Install and configure MySQL, create the required database and tables, and set the database connection details using environment variables in a local `.env` file.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=election_management_system
```

Replace the example values with your own local MySQL settings. Never commit your `.env` file or database password to GitHub.

### 6. Start the application

```bash
streamlit run app.py
```

The application will display a local URL in your terminal.

## 🔐 Demo Login Accounts

The application currently includes demo login accounts for testing:

| Role | Username | Password |
|---|---|---|
| Administrator | `admin` | `Admin@123` |
| Electoral Officer | `officer` | `Officer@123` |
| Booth Level Officer | `blo` | `BLO@123` |
| Voter | `voter` | `Voter@123` |

**Note:** These are demonstration credentials, not production-secure accounts. Replace them with secure authentication before any real-world use.

## 🗄️ Database

The project uses MySQL as its relational database. The Python application connects to the configured database through `mysql-connector-python`.

Database configuration and connectivity must be completed separately when running the project locally or deploying it to a cloud environment.

## ☁️ Deployment

The application is hosted on **Streamlit Community Cloud**, making it accessible through a public web URL.

🔗 **Live application:**  
https://election-management-system-2ethmb7tnxlzsm94d3zt42.streamlit.app/

## 🎯 Project Objectives

- Demonstrate a database-driven web application.
- Organize election-related information into dedicated modules.
- Provide an interactive interface for different demo user roles.
- Practice Python, SQL, database connectivity, and web application deployment.
- Apply DBMS concepts to a practical academic project.

## ⚠️ Disclaimer

This is an academic demonstration project. It is not an official election platform and is not intended for conducting real elections or storing real voter information. The demo credentials and authentication implementation should not be considered production-grade security.

## 👩‍💻 Author

**Devashree D. Bhadalkar**

GitHub: https://github.com/devashreebhadalkar

---

⭐ If you find this project useful, consider starring the repository on GitHub.
# Election-Management-System
Python Streamlit and MySQL Election Management System
