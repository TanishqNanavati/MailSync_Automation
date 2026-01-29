"""
Email Categorizer Module
Automatically categorizes emails based on content and sender.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def categorize_email(parsed_email):
    """
    Automatically categorize an email based on subject, sender, and content.
    
    Uses rule-based matching with keywords and sender patterns.
    Falls back to 'Other' if no category matches.
    
    Args:
        parsed_email (dict): Parsed email with 'from', 'subject', 'content' keys
        
    Returns:
        str: Category name (e.g., 'Banking', 'Internship', 'Work', etc.)
    """
    
    sender = parsed_email.get('from','').lower()
    subject = parsed_email.get('subject','').lower()
    content = parsed_email.get('content','').lower()
    
    
    #Combine
    searchable_text = f"{subject} {content} {sender}"
    
    for category,rules in config.CATEGORY_RULES.items():
        # Check for patterns
        sender_patterns = rules.get('senders',[])
        if any(pattern.lower() in sender for pattern in sender_patterns):
            return category
        
        # Check for keywords
        keywords = rules.get('keywords', [])
        if any(keyword.lower() in searchable_text for keyword in keywords):
            return category
        
        
    # Default 
    return 'Other'


def get_importance(category):
    """
    Get importance level for a category.
    
    Args:
        category (str): Email category
        
    Returns:
        int: Importance level (0-5, where 5 is highest)
    """
    
    return config.IMPORTANCE_LEVELS.get(category,2)

def sort_emails_by_importance(emails):
    """
    Sort a list of emails by their importance level.
    
    Args:
        emails (list): List of parsed email dicts
        
    Returns:
        list: Sorted list of emails by importance
    """
    
    return sorted(
        emails,
        key=lambda x:get_importance(x[1]),
        reverse=True
    )
    
    
    
if __name__ == "__main__":
    """Test categorizer with sample emails."""
    print("=" * 60)
    print("Testing Email Categorizer")
    print("=" * 60)
    
    test_emails = [
        {
            'from': 'alerts@hdfcbank.com',
            'subject': 'Account credited with Rs. 5000',
            'content': 'Your account has been credited'
        },
        {
            'from': 'noreply@unstop.com',
            'subject': 'New internship opportunity at Microsoft',
            'content': 'Apply now for summer internship'
        },
        {
            'from': 'promo@amazon.com',
            'subject': 'Flash sale: 50% off on electronics',
            'content': 'Limited time offer'
        },
        {
            'from': 'friend@gmail.com',
            'subject': 'Weekend plans?',
            'content': 'Hey, want to catch up this weekend?'
        }
    ]
    
    print("\nCategorizing test emails:\n")
    
    categorized = []
    for i, email in enumerate(test_emails, 1):
        category = categorize_email(email)
        importance = get_importance(category)
        
        print(f"[{i}] From: {email['from']}")
        print(f"    Subject: {email['subject']}")
        print(f"    → Category: {category}")
        print(f"    → Importance: {importance}/5")
        print()
        
        categorized.append((f"msg_{i}", category))
    
    print("=" * 60)
    print("Testing importance-based sorting")
    print("=" * 60)
    
    sorted_emails = sort_emails_by_importance(categorized)
    
    print("\nSorted by importance (highest first):\n")
    for msg_id, category in sorted_emails:
        importance = get_importance(category)
        print(f"{msg_id}: {category} (Importance: {importance})")
    
    print("\n" + "=" * 60)
    print("✅ Categorizer Test Complete!")
    print("=" * 60)