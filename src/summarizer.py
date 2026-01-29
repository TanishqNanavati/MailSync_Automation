"""
Email Summarizer Module
Uses Google Gemini API to generate concise email summaries.
"""


import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Warning: google-generativeai not installed. Summaries will be disabled.")
    
class EmailSummarizer:
    """Handles AI-powered email summarization using Gemini."""
    
    def __init__(self,api_key=None):
        """
        Initialize the summarizer.
        
        Args:
            api_key (str, optional): Gemini API key. 
            Defaults to config.GEMINI_API_KEY
        """
        
        self.api_key = api_key or config.GEMINI_API_KEY
        
        self.model = None
        
        if not GEMINI_AVAILABLE:
            print("⚠️  Gemini API unavailable - summaries will be skipped")
            return
        
        if not self.api_key:
            print("⚠️  Gemini API key not configured - summaries will be skipped")
            return
        
        try:
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            print("✅ Gemini AI summarizer initialized")
            
        except Exception as e:
            print(f"⚠️  Failed to initialize Gemini: {e}")
            self.model = None
            
    def summarize_email(self,parsed_email):
        """
        Generate a concise summary of an email.
        
        Args:
            parsed_email (dict): Parsed email with 'from', 'subject', 'content'
            
        Returns:
            str: AI-generated summary (1-2 sentences), or fallback message
        """
        
        if not self.model:
            return self._fallback_summary(parsed_email)
        
        try:
            # Truncate content to avoid token limits (first 2000 chars)
            content_snippet = parsed_email.get('content', '')[:2000]
            
            prompt = config.SUMMARY_PROMPT_TEMPLATE.format(
                subject=parsed_email.get('subject', ''),
                sender=parsed_email.get('from', ''),
                content=content_snippet
            )
            
            # Generate summary
            response = self.model.generate_content(prompt)
            
            # Extract text
            summary = response.text.strip()
            
            if len(summary) > 200:
                summary = summary[:197] + "..."
            
            return summary
        
        except Exception as e:
            print(f"   ⚠️  Summary generation failed: {e}")
            return self._fallback_summary(parsed_email)
        
    def _fallback_summary(self, parsed_email):
        """
        Create a simple fallback summary when AI is unavailable.
        
        Args:
            parsed_email (dict): Parsed email
            
        Returns:
            str: Simple summary based on subject
        """
        
        subject = parsed_email.get('subject', '(No Subject)')
        sender = parsed_email.get('from', 'Unknown')
        
        # Use first 100 chars of subject as summary
        if len(subject) > 100:
            return f"Email from {sender}: {subject[:97]}..."
        else:
            return f"Email from {sender}: {subject}"
        
        
if __name__ == "__main__":
    """Test the summarizer."""
    print("=" * 60)
    print("Testing Email Summarizer")
    print("=" * 60)
    
    # Initialize summarizer
    summarizer = EmailSummarizer()
    
    # Test email
    test_email = {
        'from': 'alerts@hdfcbank.com',
        'subject': 'Transaction Alert: Your account has been debited',
        'content': '''Dear Customer,
        
        Your account XXXX1234 has been debited with Rs. 2,500.00 on 25-Jan-2026.
        
        Transaction details:
        - Merchant: Amazon India
        - Reference: TXN20260125ABC123
        - Available Balance: Rs. 45,000.00
        
        If you did not authorize this transaction, please contact us immediately.
        
        Regards,
        HDFC Bank Customer Service
        
        This is an automated message. Please do not reply.
        '''
    }
    
    print("\nTest Email:")
    print(f"From: {test_email['from']}")
    print(f"Subject: {test_email['subject']}")
    print()
    
    print("Generating summary...")
    summary = summarizer.summarize(test_email)
    
    print("\n" + "=" * 60)
    print("Generated Summary:")
    print("=" * 60)
    print(summary)
    print()
    
    print("=" * 60)
    print("✅ Summarizer Test Complete!")
    print("=" * 60)
    print()
            

            