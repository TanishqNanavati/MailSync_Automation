"""
Google Sheets Service Module
Handles all Google Sheets API operations.
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class SheetsService:
    """Service class for Google Sheets API operations."""
    
    def __init__(self, credentials, spreadsheet_id=None, sheet_name=None):
        """
        Initialize Sheets service with authenticated credentials.
        
        Args:
            credentials: OAuth 2.0 credentials object
            spreadsheet_id (str, optional): Google Sheets spreadsheet ID.
                                           Defaults to config.SPREADSHEET_ID
            sheet_name (str, optional): Name of the sheet/tab.
                                       Defaults to config.SHEET_NAME
        """
        self.credentials = credentials
        self.spreadsheet_id = spreadsheet_id or config.SPREADSHEET_ID
        self.sheet_name = sheet_name or config.SHEET_NAME
        self.service = None
        self.build_service()
    
    def build_service(self):
        """
        Build Google Sheets API service client.
        
        Raises:
            Exception: If service building fails
        """
        try:
            self.service = build('sheets', 'v4', credentials=self.credentials)
            print("✅ Google Sheets service initialized")
        except Exception as e:
            raise Exception(f"Failed to build Sheets service: {e}")
    
    def ensure_headers(self, headers=None):
        """
        Check if header row exists, create if missing.
        
        This checks if the first row of the sheet is empty or matches
        our expected headers. If empty, it writes the headers.
        
        Args:
            headers (list, optional): List of column header names.
                                     Defaults to config.SHEET_HEADERS
        
        Returns:
            bool: True if headers exist or were created successfully
        """
        if headers is None:
            headers = config.SHEET_HEADERS
        
        try:
            # Read first row
            range_name = f"{self.sheet_name}!A1:{chr(65 + len(headers) - 1)}1"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            existing_values = result.get('values', [])
            
            if not existing_values or not existing_values[0]:
                # No headers exist, create them
                print("📝 Creating header row...")
                body = {'values': [headers]}
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption='RAW',
                    body=body
                ).execute()
                print("✅ Headers created")
            else:
                print("✅ Headers already exist")
            
            return True
            
        except HttpError as error:
            print(f"❌ Error ensuring headers: {error}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def append_row(self, values):
        """
        Append a new row to the spreadsheet.
        
        This uses the append API which automatically finds the next empty row.
        Values are inserted in order matching the headers.
        
        Args:
            values (list): List of values to append as a row.
                          Order should match SHEET_HEADERS:
                          [message_id, from, subject, date, content]
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Define the range (sheet name with ! to indicate entire sheet)
            range_name = f"{self.sheet_name}!A:S"  # A to E covers 5 columns
            
            # Prepare the request body
            body = {
                'values': [values]  # Wrap in list because append expects 2D array
            }
            
            # Append the row
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',  # Insert exactly as provided
                insertDataOption='INSERT_ROWS',  # Insert new rows
                body=body
            ).execute()
            
            # Get info about what was updated
            updates = result.get('updates', {})
            updated_range = updates.get('updatedRange', '')
            
            print(f"   ✅ Appended to {updated_range}")
            
            return True
            
        except HttpError as error:
            print(f"❌ Error appending row: {error}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def get_all_message_ids(self):
        """
        Get all message IDs currently in the sheet (for duplicate checking).
        
        Reads the first column (Message ID) from all rows except header.
        Returns as a set for fast lookup.
        
        Returns:
            set: Set of message IDs already in the sheet
        """
        try:
            # Read first column (A) from row 2 onwards (skip header)
            range_name = f"{self.sheet_name}!A2:A"
            
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            # Extract message IDs (first column of each row)
            # values is a list of lists: [['id1'], ['id2'], ...]
            message_ids = set()
            for row in values:
                if row and row[0]:  # Check row exists and has a value
                    message_ids.add(row[0])
            
            return message_ids
            
        except HttpError as error:
            print(f"⚠️  Warning: Error reading message IDs from sheet: {error}")
            # Return empty set if error (assume no duplicates)
            return set()
        except Exception as e:
            print(f"⚠️  Warning: Unexpected error: {e}")
            return set()
    
    def get_row_count(self):
        """
        Get the number of rows in the sheet (including header).
        
        Returns:
            int: Number of rows, or 0 if error
        """
        try:
            range_name = f"{self.sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return len(values)
            
        except Exception as e:
            print(f"⚠️  Warning: Error getting row count: {e}")
            return 0
    
    def clear_sheet(self):
        """
        Clear all data from the sheet.
        WARNING: This deletes everything including headers!
        Use with caution - mainly for testing.
        
        Returns:
            bool: True if successful
        """
        try:
            range_name = f"{self.sheet_name}!A:Z"
            self.service.spreadsheets().values().clear(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            print("✅ Sheet cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing sheet: {e}")
            return False


if __name__ == "__main__":
    """
    Test the Sheets service independently.
    Run: python src/sheets_service.py
    """
    print("=" * 60)
    print("Testing Google Sheets Service")
    print("=" * 60)
    
    # Import required modules
    from auth import authenticate
    
    try:
        # Authenticate
        print("\n🔐 Authenticating...")
        creds = authenticate()
        
        # Create Sheets service
        print(f"\n📊 Initializing Sheets service...")
        print(f"   Spreadsheet ID: {config.SPREADSHEET_ID}")
        print(f"   Sheet Name: {config.SHEET_NAME}")
        
        sheets = SheetsService(creds)
        
        # Test 1: Ensure headers exist
        print("\n" + "=" * 60)
        print("Test 1: Ensuring headers exist")
        print("=" * 60)
        sheets.ensure_headers()
        
        # Test 2: Get current row count
        print("\n" + "=" * 60)
        print("Test 2: Getting row count")
        print("=" * 60)
        row_count = sheets.get_row_count()
        print(f"📊 Current rows in sheet: {row_count}")
        
        # Test 3: Get existing message IDs
        print("\n" + "=" * 60)
        print("Test 3: Reading existing message IDs")
        print("=" * 60)
        existing_ids = sheets.get_all_message_ids()
        print(f"📧 Found {len(existing_ids)} existing message ID(s)")
        if existing_ids:
            print(f"   Sample: {list(existing_ids)[:3]}")
        
        # Test 4: Append a test row
        print("\n" + "=" * 60)
        print("Test 4: Appending a test row")
        print("=" * 60)
        
        test_row = [
            "test_message_id_12345",
            "test@example.com",
            "Test Email Subject",
            "2026-01-25T10:30:00Z",
            "This is a test email content for verification."
        ]
        
        print("📝 Appending test row...")
        success = sheets.append_row(test_row)
        
        if success:
            new_row_count = sheets.get_row_count()
            print(f"✅ Row appended successfully")
            print(f"📊 Total rows now: {new_row_count}")
        
        print("\n" + "=" * 60)
        print("✅ Sheets Service Test Complete!")
        print("=" * 60)
        print("\n📝 Check your Google Sheet to verify the test row:")
        print(f"   https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}/edit")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()