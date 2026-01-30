# 📧 Gmail to Google Sheets Automation

A robust, production-ready Python automation that syncs unread Gmail emails to Google Sheets using OAuth 2.0.
Built with modular services, duplicate prevention, retry safety, optional subject filtering, and Docker support.

## Output Format

``` bash
======================================================================
📧 Gmail to Google Sheets Automation (Full Featured)
======================================================================

🔐 Step 1: Authenticating with Google APIs...
----------------------------------------------------------------------
📋 Loading existing token...
✅ Using existing valid token

🔧 Step 2: Initializing services...
----------------------------------------------------------------------
✅ Gmail service initialized
✅ Google Sheets service initialized
📝 No existing state file, creating new one
✅ Gemini AI summarizer initialized
✅ Google Calendar service initialized

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
   Banking: 3 email(s) [Priority: 5/5]
   Internship: 3 email(s) [Priority: 4/5]
   Work: 1 email(s) [Priority: 3/5]
   Other: 1 email(s) [Priority: 2/5]
   Promotions: 2 email(s) [Priority: 1/5]

⚙️  Step 7: Processing emails (highest importance first)...
----------------------------------------------------------------------

[1/10] Processing: msg-0001
   🏷️  Category: Banking | Importance: 5/5
   📧 From: alerts@bankexample.com
   📝 Subject: Transaction alert: Debit on your account
   🤖 Generating summary...
   📄 Summary: Debit of $25.00 at Grocery Store on 2026-01-30. If unauthorized, contact support.
   ✅ Extracted action items: ['Verify transaction', 'Contact bank if unauthorized']
   📎 Processing attachments... None
   😊 Analyzing sentiment... neutral | Urgency: 0.4
   ✅ Appended to Emails!A72:S72
   ✅ Successfully processed and marked as read

[2/10] Processing: msg-0002
   🏷️  Category: Internship | Importance: 4/5
   📧 From: recruiters@companyexample.com
   📝 Subject: Interview Invitation: Software Engineer Intern
   🤖 Generating summary...
   📄 Summary: Invitation to interview for the Software Engineer Intern role on 2026-02-03.
   ✅ Extracted action items: ['Confirm availability', 'Prepare resume']
   📎 Processing attachments... resume.pdf (downloaded)
   😊 Analyzing sentiment... positive | Urgency: 0.6
   📅 Calendar event: Detected (Dry-run: not created)
   ✅ Appended to Emails!A73:S73
   ✅ Successfully processed and marked as read

[3/10] Processing: msg-0003
   🏷️  Category: Promotions | Importance: 1/5
   📧 From: deals@newsletter.example
   📝 Subject: Weekly Deals and Tips
   🤖 Generating summary...
   📄 Summary: Latest deals and engineering tips from TechUpdates.
   ✅ Extracted action items: []
   📎 Processing attachments... None
   😊 Analyzing sentiment... neutral | Urgency: 0.2
   ✅ Appended to Emails!A74:S74
   ✅ Successfully processed and marked as read

... (remaining messages processed similarly)

💾 Step 8: Saving state...
----------------------------------------------------------------------
💾 State saved: 10 total processed


======================================================================
📊 Generating Email Analytics Report
======================================================================

📊 EMAIL ANALYTICS REPORT
======================================================================

📈 SUMMARY
   Total Emails Processed: 10
   Date Range: 2026-01-25 to 2026-01-30
   Days Span: 6 days

🏷️  EMAILS BY CATEGORY
   Banking: 3 emails
   Internship: 3 emails
   Promotions: 2 emails
   Work: 1 email
   Other: 1 email

📎 ATTACHMENT STATISTICS
   Emails with attachments: 1
   Emails without attachments: 9
   Total attachments: 1

✅ ACTION ITEM STATISTICS
   Emails with action items: 7
   Emails without action items: 3

💾 Report saved to: analytics/email_analytics_report.txt

======================================================================

✨ Automation Complete!
======================================================================

📊 Summary:
   ✅ Successfully processed: 10 email(s)

📈 All-Time Statistics:
   Total emails processed: 10
   Last run: 2026-01-30T07:32:15.148063

🔗 View your Google Sheet:
   https://docs.google.com/spreadsheets/d/1MV6Gbj80zKFjr4RCrVn_EQmNIY_IGYVyoVx6kNnsyXo/edit

🎯 Active Features:
   ✅ Action Items
   ✅ Attachments
   ✅ Analytics
   ✅ Sentiment Analysis
   ✅ Auto-Response (Dry-Run)
   ✅ Calendar Integration (Dry-Run)

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
- ✅ Action item extraction (detects tasks, deadlines)
- 📎 Attachment management (download, metadata, Drive upload optional)
- ✉️ Auto-response system (configurable rules; dry-run mode available)
- 📅 Calendar integration (extract events; dry-run mode available)
- 😊 Sentiment & urgency analysis (JSON output with score)
- 📈 Analytics & reporting (daily volumes, top senders, attachment stats)
- 🔁 Gemini generation fallback handling (uses safe client call patterns)

## 🏗️ Architecture
```bash
mailsync/
├── src/
│   ├── main.py                # Orchestration & workflow
│   ├── auth.py                # OAuth 2.0 authentication
│   ├── gmail_service.py       # Gmail API operations
│   ├── sheets_service.py      # Google Sheets API operations
│   ├── email_parser.py        # Email decoding & parsing
│   ├── state_manager.py       # Persistent state handling
│   ├── categorizer.py         # Email categorization & importance scoring
│   ├── summarizer.py          # AI-powered email summarization (Gemini)
│   ├── action_extractor.py    # Extracts actionable tasks & deadlines
│   ├── analytics.py           # Generates analytics reports
│   ├── attachment_handler.py  # Attachment download & drive upload
│   ├── auto_responder.py      # Auto-response generation & sending (dry-run)
│   ├── calendar_service.py    # Calendar event creation (dry-run)
│   ├── gmail_service.py       # Gmail API wrapper (listed twice for clarity)
│   ├── sentiment_analyzer.py  # Sentiment & urgency analysis
│
├── credentials/
│   └── credentials.json       # Google OAuth credentials

├── token.json                 # OAuth token (auto-generated)
├── state.json                 # Processed email state
├── config.py                  # Central configuration
├── Dockerfile                 # Container definition
└── README.md
```
## 🔧 Tech Stack
- Language: Python 3.9+
- APIs: Gmail API, Google Sheets API, Google Gemini API
- Authentication: OAuth 2.0 (Installed App flow)
- AI/ML: Google Generative AI for email summarization
- Libraries: google-api-python-client, google-auth, google-auth-oauthlib, google-generativeai
