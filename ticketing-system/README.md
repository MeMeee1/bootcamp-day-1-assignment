# Support Ticket System (Streamlit + PostgreSQL)

Production-quality support ticket management system using Streamlit, SQLAlchemy ORM, and PostgreSQL (Lakebase compatible).

## Features

- View all tickets in tabular format
- Create new tickets
- View ticket details and all messages (ordered by date)
- Add messages to a ticket
- Update ticket status (`Open`, `In Progress`, `Resolved`)
- Delete ticket with confirmation (cascades to related messages)
- Automatic table creation on startup
- Seed sample data (3 tickets, 2 messages each)

## Project Structure

ticketing-system/
- app.py
- database.py
- models.py
- crud.py
- requirements.txt
- README.md

## Prerequisites

- Python 3.11+
- PostgreSQL / Lakebase-compatible PostgreSQL endpoint
- `DATABASE_URL` environment variable

## DATABASE_URL format

Use SQLAlchemy psycopg driver format:

```bash
postgresql+psycopg://username:password@host:5432/database_name
```

## Setup & Run

1. Clone repo and move into project directory.
2. Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate         # Linux/macOS
# .venv\\Scripts\\activate          # Windows PowerShell
```

3. Install dependencies:

```bash
pip install -r ticketing-system/requirements.txt
```

4. Set environment variable:

```bash
export DATABASE_URL="postgresql+psycopg://username:password@host:5432/database_name"
# Windows PowerShell:
# setx DATABASE_URL "postgresql+psycopg://username:password@host:5432/database_name"
```

5. Run app:

```bash
streamlit run ticketing-system/app.py
```

## Notes

- No credentials are hardcoded.
- SQLAlchemy creates tables automatically if missing.
- Relationships are configured with cascade delete so deleting a ticket also removes its messages.
- Seed data can be added from the **Seed Sample Data** page.
