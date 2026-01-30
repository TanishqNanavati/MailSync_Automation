"""
Auto-Responder Module
Automatically replies to certain emails based on rules.
"""

import sys
import os
import json
import base64
from email.mime.text import MIMEText
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class AutoResponder:
    """Handles automatic email responses."""
    
    def __init__(self, gmail_service=None):
        """
        Initialize auto-responder.
        
        Args:
            gmail_service: GmailService instance for sending emails
        """
        self.gmail_service = gmail_service
        self.response_log = []
        self._load_log()
    
    def should_respond(self, parsed_email, category):
        """
        Determine if email should receive auto-response.
        
        Args:
            parsed_email (dict): Parsed email data
            content (str): Email content
            category (str): Email category
            
        Returns:
            tuple: (should_respond: bool, response_type: str)
        """
        if not config.ENABLE_AUTO_RESPONSE:
            return False, 'disabled'
        
        # Check if category has auto-response rules
        if category not in config.AUTO_RESPONSE_RULES:
            return False, 'no_rule'
        
        rules = config.AUTO_RESPONSE_RULES[category]
        
        # Check if auto-response is enabled for this category
        if not rules.get('enabled', False):
            return False, 'category_disabled'
        
        # Check if already responded to this sender recently
        sender = parsed_email.get('from', '')
        if self._recently_responded_to(sender):
            return False, 'already_responded'
        
        # Check if keywords match
        content = parsed_email.get('content', '').lower()
        subject = parsed_email.get('subject', '').lower()
        combined = f"{subject} {content}"
        
        keywords = rules.get('keywords', [])
        if keywords:
            if not any(kw.lower() in combined for kw in keywords):
                return False, 'keywords_not_matched'
        
        return True, category
    
    def generate_response(self, parsed_email, response_type):
        """
        Generate auto-response content.
        
        Args:
            parsed_email (dict): Parsed email data
            response_type (str): Type of response (category name)
            
        Returns:
            str: Response text
        """
        if response_type not in config.AUTO_RESPONSE_RULES:
            return None
        
        template = config.AUTO_RESPONSE_RULES[response_type]['response_template']
        
        # Extract sender name from email
        sender_email = parsed_email.get('from', '')
        sender_name = self._extract_name(sender_email)
        
        # Fill template
        response = template.format(
            sender_name=sender_name,
            my_name=config.MY_NAME
        )
        
        return response
    
    def send_response(self, message_id, parsed_email, response_text):
        """
        Send auto-response email.
        
        Args:
            message_id (str): Original message ID
            parsed_email (dict): Original email data
            response_text (str): Response content
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.gmail_service:
            print("      ⚠️  Gmail service not available for sending")
            return False
        
        if config.AUTO_RESPONSE_DRY_RUN:
            print(f"      🧪 DRY RUN: Would send response to {parsed_email['from']}")
            print(f"      📝 Response preview: {response_text[:100]}...")
            return True  # Pretend success in dry run
        
        try:
            # Create reply message
            sender = parsed_email.get('from', '')
            subject = parsed_email.get('subject', '')
            
            # Create MIME message
            message = MIMEText(response_text)
            message['to'] = sender
            message['subject'] = f"Re: {subject}"
            message['In-Reply-To'] = message_id
            message['References'] = message_id
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send via Gmail API
            sent_message = self.gmail_service.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            print(f"      ✅ Auto-response sent to {sender}")
            
            # Log the response
            self._log_response(sender, message_id, response_text)
            
            return True
            
        except Exception as e:
            print(f"      ❌ Failed to send auto-response: {e}")
            return False
    
    def _extract_name(self, email_address):
        """Extract name from email address."""
        # Try to get name from "Name <email>" format
        if '<' in email_address:
            name = email_address.split('<')[0].strip()
            if name:
                return name
        
        # Extract from email username
        username = email_address.split('@')[0]
        
        # Convert "john.doe" to "John Doe"
        name_parts = username.replace('.', ' ').replace('_', ' ').split()
        name = ' '.join(word.capitalize() for word in name_parts)
        
        return name if name else 'there'
    
    def _recently_responded_to(self, sender, hours=24):
        """
        Check if we already responded to this sender recently.
        
        Args:
            sender (str): Sender email
            hours (int): Time window in hours
            
        Returns:
            bool: True if recently responded
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        for log_entry in self.response_log:
            if log_entry['sender'] == sender and log_entry['timestamp'] > cutoff_time:
                return True
        
        return False
    
    def _log_response(self, sender, message_id, response_text):
        """Log auto-response for tracking."""
        log_entry = {
            'sender': sender,
            'message_id': message_id,
            'response_preview': response_text[:100],
            'timestamp': datetime.now().timestamp(),
            'date': datetime.now().isoformat()
        }
        
        self.response_log.append(log_entry)
        self._save_log()
    
    def _load_log(self):
        """Load response log from file."""
        if os.path.exists(config.AUTO_RESPONSE_LOG_FILE):
            try:
                with open(config.AUTO_RESPONSE_LOG_FILE, 'r') as f:
                    self.response_log = json.load(f)
            except:
                self.response_log = []
    
    def _save_log(self):
        """Save response log to file."""
        try:
            # Keep only last 1000 entries
            self.response_log = self.response_log[-1000:]
            
            with open(config.AUTO_RESPONSE_LOG_FILE, 'w') as f:
                json.dump(self.response_log, f, indent=2)
        except Exception as e:
            print(f"      ⚠️  Failed to save response log: {e}")


if __name__ == "__main__":
    """Test auto-responder."""
    print("=" * 60)
    print("Testing Auto-Responder")
    print("=" * 60)
    
    responder = AutoResponder()
    
    test_emails = [
        {
            'from': 'hr@techcorp.com',
            'subject': 'Thank you for applying to Software Engineer position',
            'content': 'We have received your application. We will review it and get back to you soon.',
            'category': 'Job'
        },
        {
            'from': 'intern@startups.com',
            'subject': 'Internship Application Received',
            'content': 'Your application for summer internship has been received. Thank you for your interest.',
            'category': 'Internship'
        },
        {
            'from': 'alerts@bank.com',
            'subject': 'Transaction Alert',
            'content': 'Your account has been debited by Rs. 500.',
            'category': 'Banking'
        }
    ]
    
    print("\nTesting auto-response logic:\n")
    
    for i, email in enumerate(test_emails, 1):
        print(f"[{i}] From: {email['from']}")
        print(f"    Category: {email['category']}")
        
        should_respond, response_type = responder.should_respond(email, email['category'])
        
        print(f"    Should Respond: {should_respond}")
        
        if should_respond:
            response = responder.generate_response(email, response_type)
            print(f"    Response Type: {response_type}")
            print(f"    Response Preview:")
            print(f"    {response[:150]}...")
        else:
            print(f"    Reason: {response_type}")
        
        print()
    
    print("=" * 60)
    print("✅ Auto-Responder Test Complete!")
    print("=" * 60)
    print("\n💡 Note: Set AUTO_RESPONSE_DRY_RUN=False to actually send")