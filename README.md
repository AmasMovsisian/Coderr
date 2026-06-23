# Coderr Backend API

Coderr is a REST API backend for a freelance marketplace platform, built with Django and Django REST Framework.

The platform connects clients with developers. Clients can publish project requests, while developers can offer their services and showcase their expertise. This repository contains the backend implementation, including business logic, data management, authentication, authorization, and REST API endpoints. The frontend application communicates with this backend exclusively through these endpoints.

---

## Features

* Token-based authentication and authorization
* Customer and business user management
* Marketplace workflow for offers, orders, and reviews
* Role-based permissions and access control
* RESTful API architecture
* Data validation and filtering
* Automated test suite
* Clean and maintainable project structure

---

# Installation & Configuration

## 1. Clone the Repository

```bash
git clone https://github.com/AmasMovsisian/Coderr.git
cd Coderr
```

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Create Environment Variables

Create a `.env` file in the project root directory.

Generate a secure Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Add the generated key to your `.env` file:

```env
SECRET_KEY=your_generated_secret_key
DEBUG=True
```

### Local Development

```env
DEBUG=True
```

### Production

```env
DEBUG=False
```

> Never commit your `.env` file to GitHub.

## 5. Apply Database Migrations

```bash
python manage.py migrate
```

## 6. Create a Superuser (Optional)

```bash
python manage.py createsuperuser
```

## 7. Run the Test Suite

Before starting development, verify the installation by running the test suite.

### Standard Test Execution

```bash
python manage.py test
```

### Faster Test Execution (Recommended)

For significantly faster test runs, create a dedicated test settings file that uses an in-memory SQLite database and a lightweight password hasher.

Create the file:

`core/test_settings.py`

```python
from .settings import *  # noqa: F401, F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
```

Run the test suite using the optimized test settings:

```bash
python manage.py test --settings=core.test_settings
```

This setup greatly reduces test execution time by avoiding the development database and using a much faster password hashing algorithm during testing.

### Included Test Coverage

The project includes automated tests covering:

* Registration
* Login
* Profiles
* Offers
* Orders
* Reviews
* Permissions
* API behavior

## 8. Start the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

### Django Admin

```text
http://127.0.0.1:8000/admin/
```

---

# Project Structure

```text
Coderr/
│
├── core/                  # Django project configuration
│   ├── settings.py
│   ├── test_settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/              # User management & authentication
│   └── api/
│
├── profiles/              # Profile management
│   └── api/
│
├── offers/                # Offer management
│   └── api/
│
├── orders/                # Order management
│   └── api/
│
├── reviews/               # Review management
│   └── api/
│
├── api/                   # Platform statistics & base endpoints
│   └── api/
│
├── tests/                 # Shared test configuration
│
├── manage.py
├── requirements.txt
└── .env
```

Each application contains its own API layer including:

* Serializers
* Views
* Permissions
* URL configurations
* Tests

---

# Authentication

Coderr uses **Django REST Framework Token Authentication**.

After successful registration or login, the API returns an authentication token.

### Example Response

```json
{
    "token": "your_token",
    "username": "exampleUser",
    "email": "example@example.com",
    "user_id": 1
}
```

Include the token in all protected requests:

```http
Authorization: Token your_token
```

---

# API Endpoints

## Authentication

| Method | Endpoint             | Description                        | Auth Required |
| ------ | -------------------- | ---------------------------------- | ------------- |
| POST   | `/api/registration/` | Register a new user                | No            |
| POST   | `/api/login/`        | Authenticate user and return token | No            |

## Profiles

| Method | Endpoint                  | Description            | Auth Required |
| ------ | ------------------------- | ---------------------- | ------------- |
| GET    | `/api/profile/<pk>/`      | Retrieve profile       | Yes           |
| PATCH  | `/api/profile/<pk>/`      | Update profile         | Yes           |
| GET    | `/api/profiles/business/` | List business profiles | Yes           |
| GET    | `/api/profiles/customer/` | List customer profiles | Yes           |

## Offers

| Method | Endpoint                  | Description            | Auth Required |
| ------ | ------------------------- | ---------------------- | ------------- |
| GET    | `/api/offers/`            | List all offers        | No            |
| POST   | `/api/offers/`            | Create a new offer     | Yes           |
| GET    | `/api/offers/<id>/`       | Retrieve one offer     | Yes           |
| PATCH  | `/api/offers/<id>/`       | Update an offer        | Yes           |
| DELETE | `/api/offers/<id>/`       | Delete an offer        | Yes           |
| GET    | `/api/offerdetails/<id>/` | Retrieve offer details | Yes           |

## Orders

| Method | Endpoint                                         | Description              | Auth Required |
| ------ | ------------------------------------------------ | ------------------------ | ------------- |
| GET    | `/api/orders/`                                   | List user-related orders | Yes           |
| POST   | `/api/orders/`                                   | Create a new order       | Yes           |
| PATCH  | `/api/orders/<id>/`                              | Update an order          | Yes           |
| DELETE | `/api/orders/<id>/`                              | Delete an order          | Yes           |
| GET    | `/api/order-count/<business_user_id>/`           | Count active orders      | Yes           |
| GET    | `/api/completed-order-count/<business_user_id>/` | Count completed orders   | Yes           |

## Reviews

| Method | Endpoint             | Description      | Auth Required |
| ------ | -------------------- | ---------------- | ------------- |
| GET    | `/api/reviews/`      | List all reviews | Yes           |
| POST   | `/api/reviews/`      | Create a review  | Yes           |
| PATCH  | `/api/reviews/<id>/` | Update a review  | Yes           |
| DELETE | `/api/reviews/<id>/` | Delete a review  | Yes           |

## Platform Information

| Method | Endpoint          | Description                    | Auth Required |
| ------ | ----------------- | ------------------------------ | ------------- |
| GET    | `/api/base-info/` | Aggregated platform statistics | No            |

---

# Permissions

## Anonymous Users

Can:

* Register
* Login
* Browse offers
* View platform statistics

## Customer Users

Can:

* Manage their own profile
* Create orders
* Create reviews
* Browse offers
* View business profiles

## Business Users

Can:

* Manage their own profile
* Create offers
* Update their own offers
* Manage orders
* Receive reviews

## Admin Users

Can:

* Access Django Admin
* Perform administrative actions
* Manage platform data

---

# HTTP Status Codes

| Code | Meaning               |
| ---- | --------------------- |
| 200  | OK                    |
| 201  | Created               |
| 204  | No Content            |
| 400  | Bad Request           |
| 401  | Unauthorized          |
| 403  | Forbidden             |
| 404  | Not Found             |
| 500  | Internal Server Error |

---

# Testing

The project includes a comprehensive test suite to ensure reliability and stability.

### Run All Tests

```bash
python manage.py test --settings=core.test_settings
```

### Run Tests for a Specific Application

```bash
python manage.py test accounts --settings=core.test_settings
python manage.py test offers --settings=core.test_settings
python manage.py test orders --settings=core.test_settings
python manage.py test reviews --settings=core.test_settings
```

### Run Tests with Increased Verbosity

```bash
python manage.py test --settings=core.test_settings --verbosity=2
```

### Test Coverage

The test suite validates:

* Authentication flows (registration, login, token generation)
* Profile CRUD operations and permissions
* Offer creation, updates, filtering, and deletion
* Order lifecycle management
* Review system with rating validation
* Role-based permission enforcement
* API response structure and status codes

---

# Frontend

This repository contains the backend application only.

The frontend application is maintained in a separate repository and communicates with this backend through the provided REST API endpoints.

The frontend repository will be available soon.

---

# Project Status

**Development Status:** Completed (Backend)  
**Completion Date:** June 2026

Implemented features include:

- Secure authentication and authorization
- User and profile management
- Offer and order workflows
- Review functionality
- Role-based permissions
- RESTful API endpoints
- Automated test coverage


---

# Author

## Amas Movsisian

**Backend Developer**

Built with **Django** and **Django REST Framework** as part of the **Developer Akademie Full Stack Development Program**.
