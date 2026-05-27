

# Medical Clinic Management System

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web-000000?style=flat&logo=flask&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-11-003545?style=flat&logo=mariadb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)

A complete management system for a medical clinic, built with Python (Flask) on
top of a normalized MariaDB relational database. Beyond a standard CRUD
application, the project implements critical business logic directly at the
database level through stored procedures and triggers, encrypts sensitive data,
segments access by role, and measures query performance before and after
indexing, as described in more detail in the [Features](#features) section.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Features](#features)
- [Usage and Examples](#usage-and-examples)
- [Database Schema](#database-schema)
- [Notes](#notes)
- [Contributions](#contributions)

## Introduction

This project models the full operational flow of a medical clinic: users and
roles, doctors and patients, medical records, appointments, consultations,
service-based invoicing, prescriptions and medication, notifications, and an
activity audit trail. The data is organized across 13 normalized tables linked
by foreign keys with explicit referential integrity rules.

The emphasis falls on database engineering. Instead of keeping all logic in the
application layer, the project moves the critical operations into the SQL
server through stored procedures and triggers, hardens the database with
hashing and encryption, and treats performance as a measurable property rather
than an assumption.

## Installation

### Prerequisites

- Python 3.10 or newer
- Docker and Docker Compose

### Steps

1. **Clone the repository**

```
git clone <repository-url>
cd <repository-name>
```

2. **Configure the environment variables**

Create a `.env` file in the project root:

```
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=clinica_medicala

AES_KEY=a_32_character_key______________
AES_IV=a_16_char_iv____
```

3. **Start the database**

```
docker compose up -d
```

4. **Install the Python dependencies**

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Initialize, seed, and secure the database**

```
python -m scripts.init_db
python -m scripts.seed
python -m scripts.security_setup
```

6. **Run the web application**

```
python -m app.web
```

The application is then available at `http://127.0.0.1:5001`.

### Notes

- Make sure the database container is fully started before running the
initialization scripts.
- On first run, if no users exist, visit the `/seed-admin` route to create a
demo administrator account.
- The `AES_KEY` must be exactly 32 characters and the `AES_IV` exactly 16
characters.

## Features

- **Database Initialization** — Build the relational schema from scratch

  - Connects to the MariaDB instance defined in the environment file.

  - Reads `schema.sql` and creates the 13 normalized tables.

  - Applies foreign-key constraints with explicit `ON DELETE CASCADE` and `ON DELETE SET NULL` rules.

- **Synthetic Data Seeding** — Populate the database with realistic test data

  - Uses the `Faker` library configured with the `ro_RO` locale.

  - Generates users, doctors, patients, appointments, consultations, and related records.

  - Inserts the records in an order that respects referential integrity.

- **Web Application (CRUD)** — Manage every entity through a web interface

  - Exposes a Flask interface for all 13 tables from a single central configuration.

  - Renders list, create, and edit views dynamically per table.

  - Builds foreign-key dropdowns automatically from the related tables.

  - Performs safe deletion by first clearing dependent child rows.

- **Stored Procedure — Finalize Consultation** — Close a consultation and issue its invoice

  - Inserts the consultation record for a given appointment.

  - Receives the rendered services as a JSON array and parses them in a loop.

  - Inserts one invoice line per service into the dependent table.

  - Computes the cumulative total cost across all lines.

  - Updates the consultation header with the final cost, all in one transaction.

- **Stored Procedure — Manage Appointment** — Handle the full appointment lifecycle

  - Accepts an action parameter: create, cancel, or reschedule.

  - Branches accordingly and applies the corresponding change.

  - Returns the affected appointment identifier.

- **Triggers** — Enforce business rules directly at the database level

  - Rejects any appointment scheduled in the past by raising `SIGNAL SQLSTATE '45000'`.

  - Logs every appointment status change into the audit table.

  - Automatically marks an appointment as completed when its consultation is inserted.

- **Security Hardening** — Protect credentials and sensitive personal data

  - Re-hashes all user passwords with `bcrypt` using a per-user salt.

  - Encrypts patient national ID numbers with `AES-256-CBC` before storage.

  - Creates four database accounts with differentiated, least-privilege `GRANT`s.

- **Performance Benchmarking** — Measure and optimize query execution speed

  - Runs each test query 30 times to obtain stable measurements.

  - Computes the mean and standard deviation of the execution times.

  - Applies 8 strategic indexes on the most frequently filtered columns.

  - Re-runs the benchmark and generates a before/after comparison chart.

- **SQL Injection Lab** — Demonstrate the difference between safe and unsafe queries

  - Runs the same search in both parameterized and concatenated mode.

  - Validates table and field names against a whitelist before execution.

  - Returns both result sets so the risk of concatenation is clearly visible.

- **Automated Reporting** — Generate analytical PDF reports

  - Queries aggregated statistics from the database.

  - Renders charts with `matplotlib`.

  - Builds a formatted PDF document with `reportlab`.

  - Can run on a fixed schedule for repeated reporting cycles.

- **CSV Import and Export** — Move data in and out of the database

  - Validates the requested table name against a whitelist.

  - Exports the table rows to a CSV file, or imports them back into the table.

## Usage and Examples

After the database is running and seeded, each part of the system is exercised
through a dedicated script.

- `python -m scripts.init_db` — Create the database schema

```
python -m scripts.init_db
```

- `python -m scripts.seed` — Populate the database with synthetic data

```
python -m scripts.seed
```

- `python -m scripts.security_setup` — Create DB accounts and encrypt sensitive data

```
python -m scripts.security_setup
```

- `python -m scripts.add_indexes` — Apply the optimization indexes

```
python -m scripts.add_indexes
```

- `python -m scripts.perf_bench` — Run the performance benchmark

```
python -m scripts.perf_bench
```

- `python -m scripts.consultation_service` — Test the stored procedures end to end

```
python -m scripts.consultation_service
```

- `python -m scripts.export_csv` — Export a table to a CSV file

```
python -m scripts.export_csv
```

- `python -m app.web` — Start the web application

```
python -m app.web
```

## Database Schema

The schema is normalized and consists of 13 tables connected by foreign keys.

```
utilizator ──┬─< medic ──────< programare >──── pacient ──┬─< dosar_medical
             │                     │                      │
             ├─< user_log          └─< consultatie ──┬─< factura >── servicii_medicale
             │                                       │
             └─< notificare                          └─< reteta ──< reteta_medicament >── medicament
```



## Notes

- The system uses **MariaDB 11**, run through Docker for a reproducible
environment.
- All application queries are **parameterized**; the unsafe query path exists
only inside the SQL Injection Lab, isolated and clearly labelled for
educational purposes.
- Generated artifacts such as performance charts, reports, and CSV exports are
written to dedicated output folders.

## Contributions

Any contributions to the project are welcomed and appreciated. Whether you are
fixing bugs, improving the documentation, or implementing new features, your
efforts to improve this project are held in high regard.