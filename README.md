# 📧 Gmail to Google Sheets Automation

A robust, production-ready Python automation that syncs unread Gmail emails to Google Sheets using OAuth 2.0.
Built with modular services, duplicate prevention, retry safety, optional subject filtering, and Docker support.

## Output Format

``` bash
======================================================================
📧 Gmail to Google Sheets Automation (Enhanced)
======================================================================

🔐 Step 1: Authenticating with Google APIs...
----------------------------------------------------------------------
📋 Loading existing token...
✅ Using existing valid token

🔧 Step 2: Initializing services...
----------------------------------------------------------------------
✅ Gmail service initialized
✅ Google Sheets service initialized
📋 Loaded state: 10 processed email(s)
✅ Gemini AI summarizer initialized

📋 Step 3: Ensuring spreadsheet headers...
----------------------------------------------------------------------
✅ Headers already exist

📬 Step 4: Fetching ALL unread emails...
----------------------------------------------------------------------
   📂 Searching: Inbox, Promotions, Social, Updates, Spam
📧 Fetching unread emails (max: 10)...
📬 Found 10 unread email(s)

🔍 Step 5: Filtering out already-processed emails...
----------------------------------------------------------------------
🆕 Found 10 new email(s) to process

🏷️  Step 6: Categorizing and prioritizing emails...
----------------------------------------------------------------------
✅ Emails categorized and sorted by importance

📊 Category Breakdown:
   Banking: 2 email(s) [Priority: 5/5]
   Internship: 7 email(s) [Priority: 4/5]
   Promotions: 1 email(s) [Priority: 1/5]

⚙️  Step 7: Processing emails (highest importance first)...
----------------------------------------------------------------------

[1/10] Processing: 19c042a2bc5db027
   🏷️  Category: Banking | Importance: 5/5
   📧 From: noreply@unstop.news
   📝 Subject: Add a Global Brand Like L'Oréal to Your CV | Brand...
   🤖 Generating summary...
   📄 Summary: Email from noreply@unstop.news: Add a Global Brand...
   ✅ Appended to Emails!A12:H12
   ✅ Successfully processed and marked as read

[2/10] Processing: 19bff7c6f74a04fc
   🏷️  Category: Banking | Importance: 5/5
   📧 From: noreply@unstop.news
   📝 Subject: Tanishq, earn INR 65,000 stipend!...
   🤖 Generating summary...
   📄 Summary: Email from noreply@unstop.news: Tanishq, earn INR...
   ✅ Appended to Emails!A13:H13
   ✅ Successfully processed and marked as read

💾 Step 8: Saving state...
----------------------------------------------------------------------
💾 State saved: 20 total processed

======================================================================
✨ Automation Complete!
======================================================================

📊 Summary:
   ✅ Successfully processed: 10 email(s)

📈 All-Time Statistics:
   Total emails processed: 20
   Last run: 2026-01-29T06:38:21.058481
======================================================================
```


## 🚀 Overview

This project automatically:
- Authenticates with Gmail & Google Sheets using OAuth 2.0
- Fetches unread emails from Gmail across multiple folders (Inbox, Promotions, Social, Updates, Spam)
- Parses sender, subject, date, and body content
- Converts HTML → plain text safely
- Categorizes emails based on content, sender patterns, and keywords
- Assigns importance/priority scores (1-5) to emails
- Generates AI-powered summaries using Google Gemini API
- Appends structured email data into a Google Sheet with category, priority, and summary
- Prevents duplicate processing using persistent state
- Marks successfully processed emails as read
- Prioritizes high-importance emails for processing first
- Retries failed emails safely in future runs
- Designed with clarity, fault tolerance, and extensibility in mind.

## ✨ Features
- 🔐 OAuth 2.0 Authentication (Gmail + Sheets)
- 📥 Fetch unread emails from multiple Gmail folders
- 🧠 Intelligent email parsing (plain text, HTML, multipart)
- 🏷️ Automatic email categorization based on rules & keywords
- ⭐ Dynamic importance scoring (1-5 priority levels)
- 🤖 AI-powered email summarization (Google Gemini API)
- 📊 Auto-formatted Google Sheets integration with category & importance columns
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
│   ├── categorizer.py       # Email categorization & importance scoring
│   ├── summarizer.py        # AI-powered email summarization (Gemini)
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
- APIs: Gmail API, Google Sheets API, Google Gemini API
- Authentication: OAuth 2.0 (Installed App flow)
- AI/ML: Google Generative AI for email summarization
- Libraries: google-api-python-client, google-auth, google-auth-oauthlib, google-generativeai
