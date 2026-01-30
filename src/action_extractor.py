"""
Action Item Extractor Module
Detects actionable tasks and deadlines from email content.
"""

import re
import sys
import os
from datetime import datetime, timedelta
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class ActionExtractor:
    """Extracts action items and deadlines from email content."""
    
    def __init__(self, use_llm=True):
        """
        Initialize action extractor.
        
        Args:
            use_llm (bool): Use LLM for extraction (more accurate but slower)
        """
        self.use_llm = use_llm and GEMINI_AVAILABLE and config.GEMINI_API_KEY
        
        if self.use_llm:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            except Exception as e:
                print(f"⚠️  Failed to initialize LLM for actions: {e}")
                self.use_llm = False
    
    def extract(self, parsed_email):
        """
        Extract action items and deadlines from email.
        
        Args:
            parsed_email (dict): Parsed email with 'subject', 'content'
            
        Returns:
            dict: {
                'actions': str (comma-separated) or "None",
                'due_date': str (YYYY-MM-DD) or "None"
            }
        """
        if not config.ENABLE_ACTION_EXTRACTION:
            return {'actions': 'None', 'due_date': 'None'}
        
        subject = parsed_email.get('subject', '')
        content = parsed_email.get('content', '')[:2000]  # Limit for LLM
        
        # Try LLM extraction first
        if self.use_llm:
            try:
                return self._extract_with_llm(subject, content)
            except Exception as e:
                print(f"      ⚠️  LLM action extraction failed: {str(e)[:50]}")
                # Fall back to rule-based
        
        # Rule-based extraction
        return self._extract_with_rules(subject, content)
    
    def _extract_with_llm(self, subject, content):
        """Extract using Gemini LLM."""
        prompt = config.ACTION_EXTRACTION_PROMPT.format(
            subject=subject,
            content=content
        )
        
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse JSON response
        # Remove markdown code blocks if present
        result_text = re.sub(r'```json\s*|\s*```', '', result_text)
        
        try:
            result = json.loads(result_text)
            actions = result.get('actions', [])
            deadlines = result.get('deadlines', [])
            
            # Format output
            actions_str = '; '.join(actions) if actions else 'None'
            due_date = deadlines[0] if deadlines and deadlines[0] != 'None' else 'None'
            
            return {
                'actions': actions_str[:500],  # Limit length for Sheets
                'due_date': due_date
            }
        except json.JSONDecodeError:
            # LLM returned invalid JSON, fall back
            return self._extract_with_rules(subject, content)
    
    def _extract_with_rules(self, subject, content):
        """Extract using rule-based pattern matching."""
        combined_text = f"{subject} {content}".lower()
        
        # Find action items
        actions = []
        sentences = re.split(r'[.!?]+', combined_text)
        
        for sentence in sentences:
            # Check if sentence contains action keywords
            if any(keyword in sentence for keyword in config.ACTION_KEYWORDS):
                # Clean and add
                cleaned = sentence.strip()
                if len(cleaned) > 10 and len(cleaned) < 200:
                    actions.append(cleaned.capitalize())
        
        # Find deadlines
        deadline = self._extract_deadline(combined_text)
        
        # Format output
        if actions:
            actions_str = '; '.join(actions[:3])  # Max 3 actions
        else:
            actions_str = 'None'
        
        return {
            'actions': actions_str[:500],
            'due_date': deadline
        }
    
    def _extract_deadline(self, text):
        """Extract deadline from text using patterns."""
        
        # Pattern 1: Specific dates (Jan 5, January 5th, 01/05/2026)
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # 01/05/2026, 1-5-26
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}(?:st|nd|rd|th)?(?:,? \d{4})?)',
            r'(\d{1,2}(?:st|nd|rd|th)? (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:,? \d{4})?)'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Try to parse the date
                    date_str = matches[0]
                    parsed_date = self._parse_date_string(date_str)
                    if parsed_date:
                        return parsed_date.strftime('%Y-%m-%d')
                except:
                    continue
        
        # Pattern 2: Relative dates (by Friday, by end of week, by tomorrow)
        relative_patterns = {
            r'\b(?:by |before |until )?(?:this )?friday\b': 'friday',
            r'\b(?:by |before |until )?(?:this )?monday\b': 'monday',
            r'\b(?:by |before |until )?(?:this )?tuesday\b': 'tuesday',
            r'\b(?:by |before |until )?(?:this )?wednesday\b': 'wednesday',
            r'\b(?:by |before |until )?(?:this )?thursday\b': 'thursday',
            r'\b(?:by |before |until )?tomorrow\b': 'tomorrow',
            r'\b(?:by |before |until )?(?:this )?week(?:end)?\b': 'week',
            r'\b(?:by |before |until )?(?:end of |this )?month\b': 'month'
        }
        
        for pattern, relative_type in relative_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return self._get_relative_date(relative_type)
        
        return 'None'
    
    def _parse_date_string(self, date_str):
        """Parse various date string formats."""
        formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%d/%m/%Y', '%d-%m-%Y',
            '%m/%d/%y', '%m-%d-%y',
            '%B %d, %Y', '%B %d %Y', '%b %d, %Y', '%b %d %Y',
            '%d %B %Y', '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        
        return None
    
    def _get_relative_date(self, relative_type):
        """Convert relative date to actual date."""
        today = datetime.now()
        
        if relative_type == 'tomorrow':
            target = today + timedelta(days=1)
        elif relative_type in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            target_day = days.index(relative_type)
            current_day = today.weekday()
            days_ahead = (target_day - current_day) % 7
            if days_ahead == 0:
                days_ahead = 7
            target = today + timedelta(days=days_ahead)
        elif relative_type == 'week':
            target = today + timedelta(days=7)
        elif relative_type == 'month':
            # End of current month
            if today.month == 12:
                target = datetime(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                target = datetime(today.year, today.month + 1, 1) - timedelta(days=1)
        else:
            return 'None'
        
        return target.strftime('%Y-%m-%d')


if __name__ == "__main__":
    """Test action extractor."""
    print("=" * 60)
    print("Testing Action Item Extractor")
    print("=" * 60)
    
    extractor = ActionExtractor(use_llm=True)
    
    test_emails = [
        {
            'subject': 'Please submit your assignment',
            'content': 'Hi, Please submit your final assignment by Friday, Feb 5th. Make sure to include all references.'
        },
        {
            'subject': 'Interview Scheduled',
            'content': 'Your interview is scheduled for Jan 30, 2026. Please confirm your availability and bring your resume.'
        },
        {
            'subject': 'Payment Due',
            'content': 'Your invoice #12345 is due. Please pay Rs. 5000 by end of this month to avoid late fees.'
        },
        {
            'subject': 'Meeting Reminder',
            'content': 'Reminder: Team meeting tomorrow at 10 AM. Please review the project proposal before the meeting.'
        }
    ]
    
    print("\nExtracting actions from test emails:\n")
    
    for i, email in enumerate(test_emails, 1):
        print(f"[{i}] Subject: {email['subject']}")
        
        result = extractor.extract(email)
        
        print(f"    Actions: {result['actions']}")
        print(f"    Due Date: {result['due_date']}")
        print()
    
    print("=" * 60)
    print("✅ Action Extractor Test Complete!")
    print("=" * 60)