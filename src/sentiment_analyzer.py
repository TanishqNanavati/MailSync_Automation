"""
Sentiment Analyzer Module
Detects emotional tone and urgency of emails.
"""

import sys
import os
import re
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class SentimentAnalyzer:
    """Analyzes sentiment and urgency of emails."""
    
    def __init__(self, use_llm=True):
        """
        Initialize sentiment analyzer.
        
        Args:
            use_llm (bool): Use LLM for analysis (more accurate)
        """
        self.use_llm = use_llm and GEMINI_AVAILABLE and config.GEMINI_API_KEY
        
        if self.use_llm:
            try:
                genai.configure(api_key=config.GEMINI_API_KEY)
                self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            except Exception as e:
                print(f"⚠️  Failed to initialize LLM for sentiment: {e}")
                self.use_llm = False
    
    def analyze(self, parsed_email):
        """
        Analyze sentiment and urgency of email.
        
        Args:
            parsed_email (dict): Parsed email with 'subject', 'content', 'from'
            
        Returns:
            dict: {
                'sentiment': str ('positive'/'neutral'/'negative'/'urgent'),
                'urgency_score': float (0.0-1.0)
            }
        """
        if not config.ENABLE_SENTIMENT_ANALYSIS:
            return {
                'sentiment': 'neutral',
                'urgency_score': 0.5
            }
        
        subject = parsed_email.get('subject', '')
        content = parsed_email.get('content', '')[:1500]  # Limit for LLM
        sender = parsed_email.get('from', '')
        
        # Try LLM analysis first
        if self.use_llm:
            try:
                return self._analyze_with_llm(subject, content, sender)
            except Exception as e:
                print(f"      ⚠️  LLM sentiment analysis failed: {str(e)[:50]}")
                # Fall back to rule-based
        
        # Rule-based analysis
        return self._analyze_with_rules(subject, content)
    
    def _analyze_with_llm(self, subject, content, sender):
        """Analyze using Gemini LLM."""
        prompt = config.SENTIMENT_PROMPT.format(
            subject=subject,
            sender=sender,
            content=content
        )
        
        response = self.model.generate_content(prompt)
        result_text = response.text.strip()
        
        # Parse JSON response
        result_text = re.sub(r'```json\s*|\s*```', '', result_text)
        
        try:
            result = json.loads(result_text)
            
            sentiment = result.get('sentiment', 'neutral').lower()
            urgency_score = float(result.get('urgency_score', 0.5))
            
            # Validate sentiment
            valid_sentiments = ['positive', 'neutral', 'negative', 'urgent']
            if sentiment not in valid_sentiments:
                sentiment = 'neutral'
            
            # Clamp urgency score
            urgency_score = max(0.0, min(1.0, urgency_score))
            
            return {
                'sentiment': sentiment,
                'urgency_score': round(urgency_score, 2)
            }
            
        except (json.JSONDecodeError, ValueError):
            # LLM returned invalid format, fall back
            return self._analyze_with_rules(subject, content)
    
    def _analyze_with_rules(self, subject, content):
        """Analyze using rule-based patterns."""
        combined_text = f"{subject} {content}".lower()
        
        # Urgency indicators
        urgent_keywords = [
            'urgent', 'asap', 'immediately', 'emergency', 'critical',
            'time-sensitive', 'deadline', 'expires', 'last chance',
            'act now', 'hurry', 'quick', 'fast', 'important'
        ]
        
        # Negative indicators
        negative_keywords = [
            'problem', 'issue', 'error', 'failed', 'rejected',
            'denied', 'declined', 'cancelled', 'suspended',
            'overdue', 'late', 'missed', 'wrong', 'mistake'
        ]
        
        # Positive indicators
        positive_keywords = [
            'congratulations', 'approved', 'accepted', 'selected',
            'success', 'completed', 'confirmed', 'thank you',
            'great', 'excellent', 'wonderful', 'pleased'
        ]
        
        # Calculate scores
        urgency_count = sum(1 for kw in urgent_keywords if kw in combined_text)
        negative_count = sum(1 for kw in negative_keywords if kw in combined_text)
        positive_count = sum(1 for kw in positive_keywords if kw in combined_text)
        
        # Determine sentiment
        if urgency_count >= 2:
            sentiment = 'urgent'
            urgency_score = 0.9
        elif negative_count > positive_count:
            sentiment = 'negative'
            urgency_score = 0.6
        elif positive_count > negative_count:
            sentiment = 'positive'
            urgency_score = 0.3
        else:
            sentiment = 'neutral'
            urgency_score = 0.5
        
        # Adjust urgency based on patterns
        if '!' in subject or '!!' in combined_text:
            urgency_score = min(1.0, urgency_score + 0.2)
        
        if 'by tomorrow' in combined_text or 'by today' in combined_text:
            urgency_score = min(1.0, urgency_score + 0.3)
        
        return {
            'sentiment': sentiment,
            'urgency_score': round(urgency_score, 2)
        }


if __name__ == "__main__":
    """Test sentiment analyzer."""
    print("=" * 60)
    print("Testing Sentiment Analyzer")
    print("=" * 60)
    
    analyzer = SentimentAnalyzer(use_llm=True)
    
    test_emails = [
        {
            'subject': 'URGENT: System Down - Immediate Action Required!',
            'content': 'Our production system is down. Please fix this immediately. Critical issue affecting all users.',
            'from': 'ops@company.com'
        },
        {
            'subject': 'Congratulations! Your application has been approved',
            'content': 'We are pleased to inform you that your application has been approved. Welcome aboard!',
            'from': 'hr@company.com'
        },
        {
            'subject': 'Payment Failed - Account Suspended',
            'content': 'Your payment has failed. Your account will be suspended if not resolved within 24 hours.',
            'from': 'billing@service.com'
        },
        {
            'subject': 'Weekly Newsletter - January 2026',
            'content': 'Here is your weekly update with the latest news and articles from our blog.',
            'from': 'newsletter@blog.com'
        }
    ]
    
    print("\nAnalyzing sentiment of test emails:\n")
    
    for i, email in enumerate(test_emails, 1):
        print(f"[{i}] Subject: {email['subject']}")
        
        result = analyzer.analyze(email)
        
        print(f"    Sentiment: {result['sentiment']}")
        print(f"    Urgency Score: {result['urgency_score']}/1.0")
        
        # Visual urgency indicator
        urgency_bar = '█' * int(result['urgency_score'] * 10)
        print(f"    Urgency: [{urgency_bar:10}]")
        print()
    
    print("=" * 60)
    print("✅ Sentiment Analyzer Test Complete!")
    print("=" * 60)