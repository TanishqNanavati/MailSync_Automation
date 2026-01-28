# 📧 Gmail to Google Sheets Automation

A robust, production-ready Python automation that syncs unread Gmail emails to Google Sheets using OAuth 2.0.
Built with modular services, duplicate prevention, retry safety, optional subject filtering, and Docker support.

## Output Format

``` bash
======================================================================
📧 Gmail to Google Sheets Automation
======================================================================

🔐 Step 1: Authenticating with Google APIs...
----------------------------------------------------------------------
🔐 Starting OAuth 2.0 authentication...
📖 A browser window will open for you to grant permissions.
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...
gio: Operation not supported
✅ Authentication successful!
💾 Saving token for future use...
✅ Token saved to: /app/token.json

🔧 Step 2: Initializing services...
----------------------------------------------------------------------
✅ Gmail service initialized
✅ Google Sheets service initialized
📝 No existing state file, creating new one

📋 Step 3: Ensuring spreadsheet headers...
----------------------------------------------------------------------
✅ Headers already exist

📬 Step 4: Fetching unread emails from Gmail...
----------------------------------------------------------------------
📧 Fetching unread emails (max: 10)...
📬 Found 10 unread email(s)

🔍 Step 5: Filtering out already-processed emails...
----------------------------------------------------------------------
🆕 Found 10 new email(s)

⚙️  Step 6: Processing emails...
----------------------------------------------------------------------

[1/10] Processing: msg_001a
   📧 From: notifications@socialnet.example
   📝 Subject: Welcome to your new network
   ⏭️  Skipped (subject keyword filter)

...

[9/10] Processing: msg_009i
   📧 From: noreply@community.example
   📝 Subject: Platform update released
   ⏭️  Skipped (subject keyword filter)

[10/10] Processing: msg_010j
   📧 From: announcements@competitions.example
   📝 Subject: Win prizes in our latest challenge
   ⏭️  Skipped (subject keyword filter)

💾 Step 7: Saving state...
----------------------------------------------------------------------
💾 State saved: 10 total processed

======================================================================
✨ Automation Complete!
======================================================================
✅ Processed: 1

🔗 Google Sheet:
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit
======================================================================

```


## 🚀 Overview

This project automatically:
- Authenticates with Gmail & Google Sheets using OAuth 2.0
- Fetches unread emails from Gmail
- Parses sender, subject, date, and body content
- Converts HTML → plain text safely
- Optionally filters emails by subject keywords
- Appends structured email data into a Google Sheet
- Prevents duplicate processing using persistent state
- Marks successfully processed emails as read
- Retries failed emails safely in future runs
- Designed with clarity, fault tolerance, and extensibility in mind.

## ✨ Features
- 🔐 OAuth 2.0 Authentication (Gmail + Sheets)
- 📥 Fetch unread emails via Gmail API
- 🧠 Intelligent email parsing (plain text, HTML, multipart)
- 🏷️ Subject keyword filtering (optional)
- 📊 Auto-formatted Google Sheets integration
- 🔁 Idempotent processing (no duplicates)
- 💾 Persistent state tracking (JSON)
- ⚠️ Safe retry mechanism for failed writes
- 🧩 Modular service-based architecture
- 🧪 Independent module testing
- 🐳 Dockerized for consistent deployment

## 🏗️ Architecture
```bash
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
```
## 🔧 Tech Stack
- Language: Python 3.9+
- APIs: Gmail API, Google Sheets API
- Authentication: OAuth 2.0 (Installed App flow)
- Libraries: google-api-python-client, google-auth, google-auth-oauthlib
