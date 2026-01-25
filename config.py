"""
Configuration file for Gmail to Google Sheets automation.
Contains all constants and settings used across the application.
"""

import os


SCOPES = [
    # Gmail scopes
    'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
    'https://www.googleapis.com/auth/gmail.modify',    # Mark emails as read
    
    # Google Sheets scope
    'https://www.googleapis.com/auth/spreadsheets'     # Read/write to sheets
]


# SPREADSHEET ="https://docs.google.com/spreadsheets/d/1Jn2QL_q2gWCHAwZ_Iu0_iD3Awd4-8sWgVdVKeBr_kEg/edit?hl=id&gid=0#gid=0"


SPREADSHEET_ID = '1Jn2QL_q2gWCHAwZ_Iu0_iD3Awd4-8sWgVdVKeBr_kEg'
# https://docs.google.com/spreadsheets/d/1Jn2QL_q2gWCHAwZ_Iu0_iD3Awd4-8sWgVdVKeBr_kEg/edit?hl=id&gid=0#gid=0

# The name of the sheet/tab within the spreadsheet
SHEET_NAME = 'Emails'

# =============================================================================
# File Paths
# =============================================================================
# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Credentials directory
CREDENTIALS_DIR = os.path.join(BASE_DIR, 'credentials')

# Path to OAuth credentials downloaded from Google Cloud Console
CREDENTIALS_FILE = os.path.join(CREDENTIALS_DIR, 'credentials.json')

# Path where OAuth token will be stored after first authentication
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')

# Path to state file for tracking processed emails
STATE_FILE = os.path.join(BASE_DIR, 'state.json')

# =============================================================================
# Application Settings
# =============================================================================
# Maximum number of emails to fetch per run (prevents API quota issues)
MAX_RESULTS = 10

# Gmail query to filter emails (only unread inbox emails)
GMAIL_QUERY = 'is:unread in:inbox'

# =============================================================================
# Google Sheets Column Headers
# =============================================================================
# These will be used as the header row in Google Sheets
SHEET_HEADERS = [
    'Message ID',
    'From',
    'Subject',
    'Date',
    'Content'
]

# API_KEY = "AIzaSyAhCsYbByOdy_j-1v1JLwZmKUMigCFJ6uA"