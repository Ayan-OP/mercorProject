# Mercor Time Tracker - Backend API

This repository contains the backend API for the T3 Time Tracker application, designed to replicate the core functionalities of an employee time tracking and management system like Insightful. The API is built with FastAPI and MongoDB, focusing on performance, scalability, and data integrity.

## 🏛️ Architecture & System Design

The backend is built following modern best practices to ensure a clean and maintainable codebase.

* **Core Pattern**: The application uses the **Routes, Services, and Schemas** pattern.
    * **Routes**: Handle incoming HTTP requests and outgoing responses. This layer is kept thin and is only responsible for I/O.
    * **Services**: Contain all the core business logic, validation, and database interactions. This is where the "thinking" happens.
    * **Schemas (Pydantic)**: Define strict data contracts for all API inputs and outputs, ensuring data consistency and providing automatic validation.
* **Database**: **MongoDB** was chosen for its flexibility and scalability.
    * **Data Integrity Tradeoff**: Since MongoDB (a NoSQL database) does not enforce relational integrity, this responsibility was moved to the service layer. The application includes robust validations to prevent data inconsistencies, such as:
        * Preventing deactivated employees from being assigned to projects.
        * Automatically removing deactivated employees from all their project assignments.
        * Ensuring an employee can only be assigned to a task if they are already part of the parent project.
        * Implementing two-way data binding between employees and projects.
* **Authentication**: A **dual-authentication model** is used to secure the API:
    * **Admin Access**: A static **API Key** (sent via the `X-API-Key` header) is used to protect all administrative endpoints (creating/updating/deleting employees, projects, and tasks).
    * **Employee Access**: A standard **JWT (JSON Web Token)** is used for the employee-facing parts of the API. Employees log in from the desktop app to receive a token, which they use to submit time entries and view their assigned work.

## ✨ Features

* **Employee Management**: Invite, update, deactivate, and list employees.
* **Project Management**: Full CRUD (Create, Read, Update, Delete) functionality for projects.
* **Task Management**: Full CRUD functionality for tasks, with validation against parent projects.
* **Time Tracking**: Secure endpoint for the desktop app to submit "time windows".
* **Analytics**: Endpoints to aggregate and analyze time tracking data by project or employee.
* **Custom Authentication Flow**: A complete user lifecycle from email invitation to account activation and login.

## 🚀 Getting Started

### Prerequisites

* Python 3.10+
* MongoDB instance (local or cloud-hosted)
* An email account (like Gmail) with an "App Password" for sending invitations.

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <your-repo-folder>/backend/
```

### 2. Setup Environment
- Create a virtual environment and install the required dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
- Create a ```.env``` file in the ```backend/``` directory.

- Copy the contents of ```.env.example``` into it.

- Fill in the values for your MongoDB connection, JWT secret, Admin API key, and email credentials.

```.env.example``` Template

```Code snippet
# MongoDB Settings
MONGO_CONNECTION_STRING="mongodb://localhost:27017"
MONGO_DB_NAME="t3_db"

# JWT Settings (generate a strong key with `openssl rand -hex 32`)
JWT_SECRET_KEY="your_super_secret_jwt_key"
JWT_ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080 # 7 days

# Admin API Key (generate a strong random string)
ADMIN_API_KEY="your_super_secret_admin_key"

# Email Settings (for Gmail SMTP with an App Password)
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
EMAIL_USERNAME="your-email@gmail.com"
EMAIL_PASSWORD="your-16-character-app-password"
EMAIL_FROM="your-email@gmail.com"
```

### 4. Run the Server
- Start the development server using Uvicorn.

```bash
uvicorn src.main:app --reload
```
- The API will now be running at ```http://127.0.0.1:8000```.




## 📖 API Documentation
- Once the server is running, you can access the interactive Swagger UI documentation in your browser at:
    ```http://127.0.0.1:8000/docs```
- This interface allows you to view and test every available API endpoint directly.
