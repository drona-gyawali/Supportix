# Supportix: AI‑Integrated Scalable Customer Support System

> **Note**: This project is currently in development. Core infrastructure and several backend features are implemented, but some modules and integrations may be incomplete or under active development.

Supportix is a high-performance, AI-enabled support ticket platform combining a Django/DRF backend with a modern React frontend. It automates ticket distribution, forecasts load, and dynamically merges teams to optimize resource use.

---

## Table of Contents

- [What is Supportix?](#what-is-supportix)
- [Features](#features)
- [Architecture](#architecture)
- [Ticket Processing Logic](#ticket-processing-logic)
- [Installation](#installation)
- [Setup & Configuration](#setup--configuration)
- [Development](#development)
- [License](#license)


---

## What is Supportix?

Supportix is a scalable support system backend (Django + DRF) paired with a single-page React frontend. It is designed for organizations that need to handle high volumes of support tickets with efficient load distribution, AI-powered traffic forecasting, and dynamic team management.

---

## Features

- **Scalable Ticket Queue**
  - Automatic load distribution across agents (round-robin, least-busy strategies).
- **Role-Based Access Control**
  - JWT authentication with fine-grained permissions for agents and admins.
- **AI‑Driven Traffic Forecasting**
  - Time-series models predict next-hour ticket volume to inform scaling decisions.
- **Automatic Department Merging**
  - Dynamically redistributes tickets from overloaded to underutilized teams.
- **Modern React Frontend**
  - Responsive SPA built with React, Redux/Context API, and Axios.
- **Realtime Communication**
  - WebSockets (Channels/Daphne) for chat and ticket updates.
- **Payment Integrations**
  - Stripe payment intent handling (planned: Esewa, Khalti).
- **Extensible Automation**
  - Rule-based ticket automation using a pluggable architecture.
- **Attachment & Media Support**
  - File and image attachments to support tickets and chat messages.
- **Admin Dashboard**
  - Manage users, roles, tickets, and departments via Django admin.

---

## Architecture

![System Architecture](https://github.com/user-attachments/assets/cd2c9b9e-dc6d-4de0-b18e-dce988370619)

- **Backend**: Django REST Framework, Django Channels (ASGI), Celery, Redis, PostgreSQL
- **Frontend**: React SPA (not included in this repository)
- **Message Broker**: Redis (for Celery and Channels/ASGI)
- **Tasks**: Celery for background ticket processing, auto-assignment, and cleanups
- **Authentication**: JWT with `rest_framework_simplejwt`
- **DevOps**: Docker Compose for local development (Redis, Postgres, Django)

---

## Ticket Processing Logic

When a user creates a ticket:

1. The system identifies the appropriate department based on the issue or request type.
2. It checks the current load of all agents in that department.
3. A load distribution algorithm (round-robin or least-busy) assigns the ticket to the optimal agent.
4. If no agents are available or the department is overloaded:
   - The ticket is placed in a queue for pending processing.
   - A merge suggestion may be triggered if the department exceeds thresholds.
5. Assigned agents can update ticket status; traffic counts are adjusted accordingly.

The goal is fair workload distribution, faster resolution times, and system stability under high load.

![Ticket Processing](https://github.com/user-attachments/assets/c414c5d7-495b-45da-8613-1f9426c6d385)

---

## Installation

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (for local development)
- Node.js + npm (for frontend, if using React SPA)
- Redis & PostgreSQL (set up automatically with Docker Compose)

### Clone the Repository

```bash
git clone https://github.com/drona-gyawali/Supportix.git
cd Supportix/management
```

### Install Python Packages

It’s recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For development tools, also run:

```bash
pip install -r requirements-dev.txt
```

### Docker Compose (Recommended)

To start Postgres and Redis:

```bash
docker-compose up -d
```

---

## Setup & Configuration

1. **Environment Variables**  
   Copy `.env.example` to `.env` and adjust settings (such as secret keys, database URLs, Stripe keys).

2. **Database Migrations**  
   ```bash
   python manage.py migrate
   ```

3. **Create a Superuser**  
   ```bash
   python manage.py createsuperuser
   ```

4. **Start the Development Server**  
   ```bash
   python manage.py runserver
   ```

5. **Start Celery Worker**  
   ```bash
   celery -A main worker -l info
   celery -A main beat -l info  # For scheduled tasks
   ```

6. **(Optional) Run Tests**  
   ```bash
   python manage.py test
   ```

---

## Development

- **Backend**: All Django/DRF and Channels/Celery code is in the `management` directory.
- **Frontend**: The React SPA is referenced but not included in this repository.
- **Admin Panel**: Visit `/admin` to administer users, tickets, departments, and more.
- **API Endpoints**: Auth, chat, tickets, and automation endpoints are documented in the code (`core/api/`, `chat/api/`).

---

## License

Copyright (c) Supportix.

Written in 2025 by Dorna Raj Gyawali <dronarajgyawali@gmail.com>

---

**Note**:  
This README is based on an automated analysis of the repository. For the latest details or updates, refer to the [GitHub repository](https://github.com/drona-gyawali/Supportix).
