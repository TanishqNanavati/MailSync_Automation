"""
Calendar Service Module
Integrates with Google Calendar to create events from emails.
"""

import sys
import os
import re
import json
from datetime import datetime, timedelta
from googleapiclient.discovery import build

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class CalendarService:
    """Handles Google Calendar operations."""
    
    def __init__(self, credentials, use_llm=True):
        """
        Initialize calendar service.
        
        Args:
            credentials: OAuth 2.0 credentials
            use_llm (bool): Use LLM for event extraction
        """
        self.credentials = credentials
        self.service = None
        self.use_llm = use_llm and GEMINI_AVAILABLE and config.GEMINI_API_KEY
        
        if self.use_llm:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            except Exception as e:
                print(f"⚠️  Failed to initialize LLM for calendar: {e}")
                self.use_llm = False
        
        self._build_service()
    
    def _build_service(self):
        """Build Google Calendar API service."""
        try:
            self.service = build('calendar', 'v3', credentials=self.credentials)
            print("✅ Google Calendar service initialized")
        except Exception as e:
            print(f"⚠️  Failed to build Calendar service: {e}")
            self.service = None
    
    def should_create_event(self, parsed_email, category):
        """
        Determine if email contains calendar event.
        
        Args:
            parsed_email (dict): Parsed email data
            category (str): Email category
            
        Returns:
            bool: True if should create event
        """
        if not config.ENABLE_CALENDAR_INTEGRATION:
            return False
        
        if not self.service:
            return False
        
        # Check for calendar keywords
        subject = parsed_email.get('subject', '').lower()
        content = parsed_email.get('content', '').lower()
        combined = f"{subject} {content}"
        
        # Check if email contains event indicators
        for event_type, keywords in config.CALENDAR_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                return True
        
        return False
    
    def extract_event_details(self, parsed_email):
        """
        Extract event details from email.
        
        Args:
            parsed_email (dict): Parsed email data
            
        Returns:
            dict or None: Event details or None if extraction failed
        """
        subject = parsed_email.get('subject', '')
        content = parsed_email.get('content', '')[:2000]
        
        # Try LLM extraction first
        if self.use_llm:
            try:
                return self._extract_with_llm(subject, content)
            except Exception as e:
                print(f"      ⚠️  LLM event extraction failed: {str(e)[:50]}")
                # Fall back to rules
        
        # Rule-based extraction
        return self._extract_with_rules(subject, content)
    
    def _extract_with_llm(self, subject, content):
        """Extract event using Gemini LLM."""
        prompt = config.CALENDAR_EXTRACTION_PROMPT.format(
            subject=subject,
            content=content
        )
        
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse JSON
        result_text = re.sub(r'```json\s*|\s*```', '', result_text)
        
        try:
            result = json.loads(result_text)
            
            if not result.get('has_event', False):
                return None
            
            # Validate and format event
            event_details = {
                'title': result.get('event_title', subject),
                'date': result.get('event_date'),
                'time': result.get('event_time', '09:00'),
                'duration': result.get('duration_minutes', config.DEFAULT_EVENT_DURATION_MINUTES),
                'location': result.get('location', 'Online'),
                'description': result.get('description', content[:500])
            }
            
            # Validate date format
            if event_details['date']:
                datetime.strptime(event_details['date'], '%Y-%m-%d')
            else:
                return None
            
            return event_details
            
        except (json.JSONDecodeError, ValueError):
            return self._extract_with_rules(subject, content)
    
    def _extract_with_rules(self, subject, content):
        """Extract event using rule-based patterns."""
        combined = f"{subject} {content}".lower()
        
        # Try to extract date
        event_date = self._extract_date(combined)
        if not event_date:
            return None
        
        # Try to extract time
        event_time = self._extract_time(combined)
        
        # Determine event type and title
        event_title = subject
        if 'interview' in combined:
            event_title = f"Interview: {subject}"
        elif 'meeting' in combined:
            event_title = f"Meeting: {subject}"
        
        return {
            'title': event_title[:100],
            'date': event_date,
            'time': event_time or '09:00',
            'duration': config.DEFAULT_EVENT_DURATION_MINUTES,
            'location': 'Online' if 'zoom' in combined or 'teams' in combined else 'TBD',
            'description': content[:500]
        }
    
    def _extract_date(self, text):
        """Extract date from text."""
        # Pattern 1: Specific dates
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?(?:,? \d{4})?)',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    date_str = matches[0]
                    parsed = self._parse_date_string(date_str)
                    if parsed:
                        return parsed.strftime('%Y-%m-%d')
                except:
                    continue
        
        # Pattern 2: Relative dates
        if 'tomorrow' in text:
            return (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'next week' in text:
            return (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        return None
    
    def _extract_time(self, text):
        """Extract time from text."""
        # Patterns: 10:00, 10:30 AM, 2 PM, etc.
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',
            r'(\d{1,2})\s*(am|pm)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    if len(matches[0]) == 3:  # HH:MM AM/PM
                        hour, minute, period = matches[0]
                        hour = int(hour)
                        minute = int(minute)
                        
                        if period and period.lower() == 'pm' and hour < 12:
                            hour += 12
                        elif period and period.lower() == 'am' and hour == 12:
                            hour = 0
                        
                        return f"{hour:02d}:{minute:02d}"
                    elif len(matches[0]) == 2:  # H AM/PM
                        hour, period = matches[0]
                        hour = int(hour)
                        
                        if period.lower() == 'pm' and hour < 12:
                            hour += 12
                        elif period.lower() == 'am' and hour == 12:
                            hour = 0
                        
                        return f"{hour:02d}:00"
                except:
                    continue
        
        return None
    
    def _parse_date_string(self, date_str):
        """Parse date string to datetime."""
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%m/%d/%y', '%m-%d-%y',
            '%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    
    def create_event(self, event_details):
        """
        Create Google Calendar event.
        
        Args:
            event_details (dict): Event information
            
        Returns:
            str: Event link or 'DryRun' or 'Failed'
        """
        if config.CALENDAR_DRY_RUN:
            print(f"      🧪 DRY RUN: Would create event '{event_details['title']}'")
            print(f"      📅 Date: {event_details['date']} at {event_details['time']}")
            return 'DryRun'
        
        try:
            # Build start and end times
            start_datetime = datetime.strptime(
                f"{event_details['date']} {event_details['time']}",
                '%Y-%m-%d %H:%M'
            )
            
            end_datetime = start_datetime + timedelta(minutes=event_details['duration'])
            
            # Create event object
            event = {
                'summary': event_details['title'],
                'location': event_details['location'],
                'description': event_details['description'],
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',  # Adjust to your timezone
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId=config.DEFAULT_CALENDAR_ID,
                body=event
            ).execute()
            
            event_link = created_event.get('htmlLink', 'Created')
            
            print(f"      ✅ Calendar event created: {event_details['title']}")
            
            return event_link
            
        except Exception as e:
            print(f"      ❌ Failed to create calendar event: {e}")
            return 'Failed'


if __name__ == "__main__":
    """Test calendar service."""
    print("=" * 60)
    print("Testing Calendar Service")
    print("=" * 60)
    
    # Note: Requires actual credentials for real testing
    print("\n💡 This module requires Calendar API credentials for real testing")
    print("   Run from main.py after processing emails")
    print("\n=" * 60)