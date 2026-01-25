📧 Gmail to Google Sheets Automation

A robust Python automation that syncs unread Gmail emails to Google Sheets, with OAuth 2.0 authentication, duplicate prevention, retry safety, and modular, production-ready architecture.

🚀 Overview

This project automatically:

Authenticates with Gmail & Google Sheets using OAuth 2.0

Fetches unread emails from Gmail

Parses sender, subject, date, and body content

Appends structured email data into a Google Sheet

Prevents duplicate processing using a persistent state manager

Marks successfully processed emails as read

Safely retries failed emails in future runs

Designed with clarity, fault-tolerance, and extensibility in mind.

✨ Features

🔐 OAuth 2.0 Authentication (Gmail + Sheets)

📥 Fetch unread emails using Gmail API

🧠 Intelligent email parsing (plain text, HTML, multipart)

📊 Auto-formatted Google Sheets integration

🔁 Idempotent processing (no duplicates)

💾 Persistent state tracking (JSON)

⚠️ Safe retry mechanism for failed writes

🧩 Modular architecture (service-based design)

🧪 Independent module testing support

🏗️ Architecture
mailsync/
├── src/
│   ├── main.py              # Orchestration & workflow
│   ├── auth.py              # OAuth 2.0 authentication
│   ├── gmail_service.py     # Gmail API operations
│   ├── sheets_service.py    # Google Sheets API operations
│   ├── email_parser.py      # Email decoding & parsing
│   ├── state_manager.py     # Persistent state handling
│
├── credentials/
│   └── credentials.json     # Google OAuth credentials
│
├── token.json               # OAuth token (auto-generated)
├── state.json               # Processed email state
├── config.py                # Central configuration
└── README.md

🔧 Tech Stack

Language: Python 3.9+

APIs:

Gmail API

Google Sheets API

Auth: OAuth 2.0

Libraries:

google-api-python-client

google-auth

google-auth-oauthlib

🔐 Authentication Flow

Uses OAuth 2.0 Installed App flow

Opens browser for user consent (first run only)

Stores token locally (token.json)

Automatically refreshes expired tokens

Same credentials shared across Gmail & Sheets APIs

📊 Google Sheet Format
Column	Description
Message ID	Unique Gmail message ID
From	Sender email address
Subject	Email subject
Date	ISO-8601 timestamp
Content	Plain-text email body

⚠️ Email content is safely truncated to avoid Google Sheets’ 50,000 character per cell limit.

▶️ How It Works (Workflow)

Authenticate with Google APIs

Initialize Gmail, Sheets, and State services

Ensure spreadsheet headers exist

Fetch unread Gmail messages

Filter already-processed emails

Parse email content

Append data to Google Sheets

Mark email as read (on success)

Persist state for future runs

🏃 Running the Project
1️⃣ Install Dependencies
pip install google-api-python-client google-auth google-auth-oauthlib

2️⃣ Configure Google Cloud

Enable Gmail API and Google Sheets API

Create OAuth 2.0 credentials

Download credentials.json

Place it in:

credentials/credentials.json

3️⃣ Update Configuration

Edit config.py:

SPREADSHEET_ID = "your_google_sheet_id"
SHEET_NAME = "Emails"

4️⃣ Run the Automation
python3 src/main.py

📈 Sample Output
📧 Gmail to Google Sheets Automation

📬 Found 10 unread email(s)
🆕 Found 10 new email(s) to process
✅ Successfully processed: 6 email(s)
⚠️ Failed: 4 email(s) (will retry next run)

📊 All-Time Statistics:
Total emails processed: 6

🛡️ Error Handling & Reliability

Graceful handling of API failures

Partial failures don’t break the workflow

Emails are only marked read after successful sheet insertion

Failed emails are retried automatically

Atomic state file writes prevent corruption

🧪 Testing

Each module can be tested independently:

python src/auth.py
python src/gmail_service.py
python src/sheets_service.py
python src/email_parser.py
python src/state_manager.py

🔮 Future Enhancements

📎 Attachment handling

🏷️ Label-based Gmail filtering

⏱️ Cron / scheduler support

🗄️ Database-backed state (SQLite)

☁️ Cloud deployment (Cloud Run / Lambda)

📊 Dashboard & analytics