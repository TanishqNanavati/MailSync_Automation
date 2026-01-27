📧 Gmail to Google Sheets Automation

A robust, production-ready Python automation that syncs unread Gmail emails to Google Sheets using OAuth 2.0.
Built with modular services, duplicate prevention, retry safety, optional subject filtering, and Docker support.

🚀 Overview

This project automatically:

Authenticates with Gmail & Google Sheets using OAuth 2.0

Fetches unread emails from Gmail

Parses sender, subject, date, and body content

Converts HTML → plain text safely

Optionally filters emails by subject keywords

Appends structured email data into a Google Sheet

Prevents duplicate processing using persistent state

Marks successfully processed emails as read

Retries failed emails safely in future runs

Designed with clarity, fault tolerance, and extensibility in mind.

✨ Features

🔐 OAuth 2.0 Authentication (Gmail + Sheets)

📥 Fetch unread emails via Gmail API

🧠 Intelligent email parsing (plain text, HTML, multipart)

🏷️ Subject keyword filtering (optional)

📊 Auto-formatted Google Sheets integration

🔁 Idempotent processing (no duplicates)

💾 Persistent state tracking (JSON)

⚠️ Safe retry mechanism for failed writes

🧩 Modular service-based architecture

🧪 Independent module testing

🐳 Dockerized for consistent deployment

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
├── Dockerfile               # Container definition
└── README.md

🔧 Tech Stack

Language

Python 3.9+

APIs

Gmail API

Google Sheets API

Authentication

OAuth 2.0 (Installed App flow)

Libraries

google-api-python-client

google-auth

google-auth-oauthlib

🔐 Authentication Flow

Uses OAuth 2.0 Installed App flow

Browser opens for consent on first run

Access token stored locally (token.json)

Expired tokens refresh automatically

Same credentials shared across Gmail & Sheets APIs

📊 Google Sheet Format
Column	Description
Message ID	Unique Gmail message ID
From	Sender email address
Subject	Email subject
Date	ISO-8601 timestamp
Content	Plain-text email body

⚠️ Email content is automatically truncated to stay within Google Sheets’ 50,000-character cell limit.

▶️ Workflow

Authenticate with Google APIs

Initialize Gmail, Sheets, and State services

Ensure spreadsheet headers exist

Fetch unread Gmail messages

Filter already-processed emails

Apply subject keyword filtering (if enabled)

Parse email content

Append data to Google Sheets

Mark email as read on success

Persist state for future runs

🏃 Running the Project (Local)
1️⃣ Install Dependencies
pip install google-api-python-client google-auth google-auth-oauthlib

2️⃣ Configure Google Cloud

Enable Gmail API and Google Sheets API

Create OAuth 2.0 credentials

Download credentials.json

Place it at:

credentials/credentials.json

3️⃣ Update Configuration

Edit config.py:

SPREADSHEET_ID = "your_google_sheet_id"
SHEET_NAME = "Emails"

# Optional subject filtering
SUBJECT_KEYWORDS = ["invoice", "job", "internship"]

4️⃣ Run the Automation
python3 src/main.py

🐳 Running with Docker
Build the Image
docker build -t mailsync .

Run the Container
docker run -it \
  -v $(pwd)/credentials:/app/credentials \
  -v $(pwd)/token.json:/app/token.json \
  -v $(pwd)/state.json:/app/state.json \
  mailsync


🔐 On first run, OAuth will open a browser for authentication.
Subsequent runs reuse the saved token.

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

Partial failures don’t stop execution

Emails marked read only after successful insertion

Failed emails retry automatically

Atomic state file writes prevent corruption

🧪 Testing

Each module can be tested independently:

python src/auth.py
python src/gmail_service.py
python src/sheets_service.py
python src/email_parser.py
python src/state_manager.py
