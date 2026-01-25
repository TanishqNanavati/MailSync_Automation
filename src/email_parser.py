"""
Email Parser Module
Extracts and formats email data from Gmail API message objects.
"""

import base64
import re
from html import unescape
from datetime import datetime
from email.utils import parsedate_to_datetime


def parse_email(message):
    """
    Parse Gmail message into structured data.
    
    Args:
        message (dict): Gmail API message object containing payload
        
    Returns:
        dict: Parsed email data with keys:
            - message_id: Unique Gmail message ID
            - from: Sender email address
            - subject: Email subject line
            - date: Email date in ISO format (YYYY-MM-DDTHH:MM:SSZ)
            - content: Plain text email body
    """
    try:
        # Extract message ID
        message_id = message.get('id', '')
        
        # Extract headers (From, Subject, Date)
        payload = message.get('payload', {})
        headers = extract_headers(payload)
        
        # Decode email body
        content = decode_body(payload)
        
        # Build structured result
        parsed_data = {
            'message_id': message_id,
            'from': headers.get('from', 'Unknown'),
            'subject': headers.get('subject', '(No Subject)'),
            'date': headers.get('date', ''),
            'content': content
        }
        
        return parsed_data
        
    except Exception as e:
        print(f"⚠️  Warning: Error parsing email: {e}")
        # Return partial data if parsing fails
        return {
            'message_id': message.get('id', 'unknown'),
            'from': 'Parse Error',
            'subject': 'Parse Error',
            'date': '',
            'content': f'Error: {str(e)}'
        }


def extract_headers(payload):
    """
    Extract email headers (From, Subject, Date) from message payload.
    
    Gmail stores headers as a list of {'name': 'Header-Name', 'value': 'header value'} dicts.
    We need to find the ones we care about.
    
    Args:
        payload (dict): Message payload from Gmail API
        
    Returns:
        dict: Dictionary with 'from', 'subject', 'date' keys
    """
    headers = {}
    
    # Get headers list from payload
    header_list = payload.get('headers', [])
    
    # Extract the headers we need
    for header in header_list:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        
        if name == 'from':
            # Extract just email address from "Name <email@example.com>" format
            headers['from'] = extract_email_address(value)
        elif name == 'subject':
            headers['subject'] = value
        elif name == 'date':
            # Convert to ISO format
            headers['date'] = parse_date(value)
    
    return headers


def extract_email_address(from_header):
    """
    Extract email address from "Name <email@example.com>" format.
    
    Examples:
        "John Doe <john@example.com>" -> "john@example.com"
        "john@example.com" -> "john@example.com"
        "<john@example.com>" -> "john@example.com"
    
    Args:
        from_header (str): Raw From header value
        
    Returns:
        str: Clean email address
    """
    # Try to extract email from angle brackets
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1).strip()
    
    # If no angle brackets, assume the whole thing is an email
    return from_header.strip()


def parse_date(date_str):
    """
    Parse email date string to ISO format.
    
    Email dates come in RFC 2822 format like:
    "Mon, 24 Jan 2026 10:30:45 +0000"
    
    We convert to ISO format: "2026-01-24T10:30:45Z"
    
    Args:
        date_str (str): Date string from email header
        
    Returns:
        str: ISO format date string, or original if parsing fails
    """
    try:
        # Parse RFC 2822 date to datetime object
        dt = parsedate_to_datetime(date_str)
        # Convert to ISO format string
        return dt.isoformat()
    except Exception:
        # If parsing fails, return original string
        return date_str


def decode_body(payload):
    """
    Decode email body from base64 and extract plain text.
    
    Email bodies can be structured in different ways:
    1. Simple message: body.data contains base64 encoded text
    2. Multipart message: parts[] array with text/plain and/or text/html
    
    Handles:
    - Multipart emails (text/plain and text/html)
    - Base64 decoding
    - HTML to plain text conversion
    - Nested parts (recursive)
    
    Args:
        payload (dict): Message payload from Gmail API
        
    Returns:
        str: Plain text email content
    """
    content = ""
    
    # Check if this payload has parts (multipart email)
    if 'parts' in payload:
        # Multipart email - recursively process parts
        content = decode_multipart(payload['parts'])
    else:
        # Simple email - decode body directly
        body = payload.get('body', {})
        data = body.get('data', '')
        if data:
            content = decode_base64(data)
    
    # Clean up the content
    content = clean_text(content)
    
    return content if content else "(Empty email body)"


def decode_multipart(parts):
    """
    Recursively decode multipart email bodies.
    
    Multipart emails have multiple parts (plain text, HTML, attachments).
    We prefer text/plain over text/html.
    
    Args:
        parts (list): List of message parts from Gmail API
        
    Returns:
        str: Decoded plain text content
    """
    text_plain = ""
    text_html = ""
    
    for part in parts:
        mime_type = part.get('mimeType', '')
        
        # If this part has nested parts, recurse
        if 'parts' in part:
            nested_content = decode_multipart(part['parts'])
            if nested_content:
                return nested_content
        
        # Extract body data
        body = part.get('body', {})
        data = body.get('data', '')
        
        if not data:
            continue
        
        # Decode based on MIME type
        if mime_type == 'text/plain':
            text_plain = decode_base64(data)
        elif mime_type == 'text/html':
            text_html = decode_base64(data)
    
    # Prefer plain text over HTML
    if text_plain:
        return text_plain
    elif text_html:
        # Convert HTML to plain text
        return html_to_text(text_html)
    else:
        return ""


def decode_base64(data):
    """
    Decode base64 URL-safe encoded data.
    
    Gmail API uses URL-safe base64 encoding (RFC 4648).
    Standard base64 uses +/ but URL-safe uses -_
    
    Args:
        data (str): Base64 encoded string
        
    Returns:
        str: Decoded UTF-8 string
    """
    try:
        # Gmail uses URL-safe base64, replace - and _ with + and /
        data = data.replace('-', '+').replace('_', '/')
        
        # Decode from base64
        decoded_bytes = base64.b64decode(data)
        
        # Convert bytes to string
        return decoded_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"⚠️  Warning: Error decoding base64: {e}")
        return ""


def html_to_text(html):
    """
    Convert HTML to plain text.
    
    Simple conversion that:
    - Removes HTML tags
    - Unescapes HTML entities (&nbsp; -> space)
    - Preserves basic structure
    
    Args:
        html (str): HTML content
        
    Returns:
        str: Plain text content
    """
    try:
        # Remove script and style tags and their content
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # Replace <br> and <p> tags with newlines
        html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
        html = re.sub(r'</p>', '\n\n', html, flags=re.IGNORECASE)
        
        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        
        # Unescape HTML entities
        text = unescape(text)
        
        return text
    except Exception as e:
        print(f"⚠️  Warning: Error converting HTML to text: {e}")
        return html


def clean_text(text):
    """
    Clean up text by removing excessive whitespace.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove multiple consecutive blank lines
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # Remove leading/trailing whitespace from entire text
    text = text.strip()
    
    # IMPORTANT: Google Sheets has a 50,000 character limit per cell
    # Truncate content if too long and add notice
    MAX_CONTENT_LENGTH = 45000  # Leave buffer for safety
    if len(text) > MAX_CONTENT_LENGTH:
        text = text[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated - exceeded 45,000 characters]"
    
    return text


if __name__ == "__main__":
    """
    Test the email parser independently.
    Run: python src/email_parser.py
    """
    print("=" * 60)
    print("Testing Email Parser")
    print("=" * 60)
    
    # Import required modules
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from auth import authenticate
    from gmail_service import GmailService
    
    try:
        # Authenticate
        print("\n🔐 Authenticating...")
        creds = authenticate()
        
        # Create Gmail service
        print("\n📧 Fetching a test email...")
        gmail = GmailService(creds)
        
        # Get one unread message
        message_ids = gmail.fetch_unread_message_ids(max_results=1)
        
        if not message_ids:
            print("📭 No unread emails to test with")
            print("   Send yourself a test email and try again!")
            sys.exit(0)
        
        # Fetch message details
        message_id = message_ids[0]
        message = gmail.fetch_message_details(message_id)
        
        # Parse the message
        print("\n" + "=" * 60)
        print("Parsing Email")
        print("=" * 60)
        
        parsed = parse_email(message)
        
        # Display results
        print("\n✅ Parsed Email Data:")
        print("-" * 60)
        print(f"Message ID : {parsed['message_id']}")
        print(f"From       : {parsed['from']}")
        print(f"Subject    : {parsed['subject']}")
        print(f"Date       : {parsed['date']}")
        print(f"Content    : {parsed['content'][:200]}...")
        print("-" * 60)
        
        print("\n" + "=" * 60)
        print("✅ Email Parser Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()