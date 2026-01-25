"""
Gmail Service Module
Handles all Gmail API operations including fetching and marking emails.
Phase 3 Implementation.
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class GmailService:
    """Service class for Gmail API operations."""
    
    def __init__(self, credentials):
        """
        Initialize Gmail service with authenticated credentials.
        
        Args:
            credentials: OAuth 2.0 credentials object
        """
        self.credentials = credentials
        self.service = None
        self.build_service()
    
    def build_service(self):
        """
        Build Gmail API service client.
        
        Raises:
            Exception: If service building fails
        """
        try:
            self.service = build('gmail', 'v1', credentials=self.credentials)
            print("✅ Gmail service initialized")
        except Exception as e:
            raise Exception(f"Failed to build Gmail service: {e}")
    
    def fetch_unread_message_ids(self, max_results=None):
        """
        Fetch list of unread email message IDs from inbox.
        
        This is a lightweight operation that only fetches message IDs,
        not the full message content. Use fetch_message_details() to get content.
        
        Args:
            max_results (int, optional): Maximum number of messages to fetch.
                                        Defaults to config.MAX_RESULTS
        
        Returns:
            list: List of message ID strings (e.g., ['18d4f2a1b3c5e6f7', ...])
            
        Raises:
            HttpError: If Gmail API request fails
        """
        if max_results is None:
            max_results = config.MAX_RESULTS
        
        try:
            print(f"📧 Fetching unread emails (max: {max_results})...")
            
            # Call Gmail API to list messages
            # Query: 'is:unread in:inbox' - only unread emails in inbox
            results = self.service.users().messages().list(
                userId='me',
                q=config.GMAIL_QUERY,
                maxResults=max_results
            ).execute()
            
            # Extract messages from response
            messages = results.get('messages', [])
            
            if not messages:
                print("📭 No unread emails found")
                return []
            
            # Extract just the IDs
            message_ids = [msg['id'] for msg in messages]
            
            print(f"📬 Found {len(message_ids)} unread email(s)")
            
            return message_ids
            
        except HttpError as error:
            print(f"❌ Gmail API error: {error}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error fetching messages: {e}")
            raise
    
    def fetch_message_details(self, message_id):
        """
        Fetch full message details for a given message ID.
        
        This retrieves the complete message including headers and body.
        The format is set to 'full' to get all message parts.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            dict: Complete message object with structure:
                {
                    'id': 'message_id',
                    'threadId': 'thread_id',
                    'labelIds': ['INBOX', 'UNREAD'],
                    'snippet': 'preview text...',
                    'payload': {
                        'headers': [...],
                        'body': {...},
                        'parts': [...]
                    }
                }
                
        Raises:
            HttpError: If Gmail API request fails
        """
        try:
            # Fetch complete message
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'  # Get full message including body
            ).execute()
            
            return message
            
        except HttpError as error:
            print(f"❌ Error fetching message {message_id}: {error}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise
    
    def mark_as_read(self, message_id):
        """
        Mark an email as read by removing the UNREAD label.
        
        This is done by modifying the message's labels.
        We remove 'UNREAD' from the labelIds list.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Modify message to remove UNREAD label
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
            
        except HttpError as error:
            print(f"❌ Error marking message {message_id} as read: {error}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def get_message_count(self):
        """
        Get total count of unread messages in inbox.
        Useful for reporting and verification.
        
        Returns:
            int: Number of unread messages
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=config.GMAIL_QUERY
            ).execute()
            
            return results.get('resultSizeEstimate', 0)
            
        except Exception as e:
            print(f"❌ Error getting message count: {e}")
            return 0


if __name__ == "__main__":
    """
    Test the Gmail service independently.
    Run: python src/gmail_service.py
    """
    print("=" * 60)
    print("Testing Gmail Service")
    print("=" * 60)
    
    # Import auth module
    from auth import authenticate
    
    try:
        # Authenticate
        print("\n🔐 Authenticating...")
        creds = authenticate()
        
        # Create Gmail service
        print("\n📧 Initializing Gmail service...")
        gmail = GmailService(creds)
        
        # Test: Fetch unread message IDs
        print("\n" + "=" * 60)
        print("Test 1: Fetching unread message IDs")
        print("=" * 60)
        message_ids = gmail.fetch_unread_message_ids(max_results=5)
        
        if message_ids:
            print(f"\n✅ Successfully fetched {len(message_ids)} message ID(s):")
            for i, msg_id in enumerate(message_ids[:3], 1):
                print(f"   {i}. {msg_id}")
            if len(message_ids) > 3:
                print(f"   ... and {len(message_ids) - 3} more")
            
            # Test: Fetch details of first message
            print("\n" + "=" * 60)
            print("Test 2: Fetching message details")
            print("=" * 60)
            print(f"\nFetching details for message: {message_ids[0]}")
            message = gmail.fetch_message_details(message_ids[0])
            
            print("\n✅ Message details retrieved:")
            print(f"   ID: {message['id']}")
            print(f"   Thread ID: {message['threadId']}")
            print(f"   Labels: {', '.join(message.get('labelIds', []))}")
            print(f"   Snippet: {message['snippet'][:100]}...")
            
        else:
            print("\nℹ️  No unread emails to test with")
        
        print("\n" + "=" * 60)
        print("✅ Gmail Service Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)