"""
Main orchestration script for Gmail to Sheets automation.
Phase 7: Complete workflow implementation.
"""

import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from auth import authenticate
from gmail_service import GmailService
from sheets_service import SheetsService
from email_parser import parse_email
from state_manager import StateManager


def main():
    """
    Main execution function - orchestrates the entire workflow.
    
    Workflow:
    1. Authenticate with Gmail and Sheets APIs
    2. Load state (processed message IDs)
    3. Fetch unread emails from Gmail
    4. Filter out already-processed emails
    5. Parse email data
    6. Append to Google Sheets
    7. Update state
    8. Mark emails as read
    """
    print("=" * 70)
    print("📧 Gmail to Google Sheets Automation")
    print("=" * 70)
    print()
    
    try:
        # =====================================================================
        # Step 1: Authentication
        # =====================================================================
        print("🔐 Step 1: Authenticating with Google APIs...")
        print("-" * 70)
        credentials = authenticate()
        print()
        
        # =====================================================================
        # Step 2: Initialize Services
        # =====================================================================
        print("🔧 Step 2: Initializing services...")
        print("-" * 70)
        
        gmail = GmailService(credentials)
        sheets = SheetsService(credentials)
        state = StateManager()
        
        print()
        
        # =====================================================================
        # Step 3: Ensure Sheet Headers Exist
        # =====================================================================
        print("📋 Step 3: Ensuring spreadsheet headers...")
        print("-" * 70)
        sheets.ensure_headers()
        print()
        
        # =====================================================================
        # Step 4: Fetch Unread Emails
        # =====================================================================
        print("📬 Step 4: Fetching unread emails from Gmail...")
        print("-" * 70)
        
        all_message_ids = gmail.fetch_unread_message_ids()
        
        if not all_message_ids:
            print("✅ No unread emails found. Nothing to process.")
            print()
            print("=" * 70)
            print("✨ Automation Complete!")
            print("=" * 70)
            return
        
        print()
        
        # =====================================================================
        # Step 5: Filter Already-Processed Emails
        # =====================================================================
        print("🔍 Step 5: Filtering out already-processed emails...")
        print("-" * 70)
        
        new_message_ids = state.filter_new_messages(all_message_ids)
        
        if not new_message_ids:
            print("✅ All emails have been processed already. Nothing new to add.")
            print()
            print("=" * 70)
            print("✨ Automation Complete!")
            print("=" * 70)
            return
        
        print(f"🆕 Found {len(new_message_ids)} new email(s) to process")
        print()
        
        # =====================================================================
        # Step 6: Process Each Email
        # =====================================================================
        print("⚙️  Step 6: Processing emails...")
        print("-" * 70)
        
        processed_count = 0
        failed_count = 0
        
        for i, message_id in enumerate(new_message_ids, 1):
            try:
                print(f"\n[{i}/{len(new_message_ids)}] Processing email: {message_id}")
                
                # Fetch full message details
                message = gmail.fetch_message_details(message_id)
                
                # Parse email data
                parsed = parse_email(message)
                
                print(f"   📧 From: {parsed['from']}")
                print(f"   📝 Subject: {parsed['subject'][:50]}...")
                
                # Prepare row for Sheets (matching SHEET_HEADERS order)
                row = [
                    parsed['message_id'],
                    parsed['from'],
                    parsed['subject'],
                    parsed['date'],
                    parsed['content']
                ]
                
                # Append to Google Sheets
                success = sheets.append_row(row)
                
                if success:
                    # Mark as processed in state
                    state.mark_as_processed(message_id)
                    
                    # Mark as read in Gmail
                    gmail.mark_as_read(message_id)
                    print(f"   ✅ Successfully processed and marked as read")
                    
                    processed_count += 1
                else:
                    print(f"   ⚠️  Failed to append to Sheets (will retry next run)")
                    failed_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing email: {e}")
                failed_count += 1
                # Don't mark as processed so it will be retried next run
                continue
        
        print()
        
        # =====================================================================
        # Step 7: Save State
        # =====================================================================
        print("💾 Step 7: Saving state...")
        print("-" * 70)
        state.save_state()
        print()
        
        # =====================================================================
        # Summary
        # =====================================================================
        print("=" * 70)
        print("✨ Automation Complete!")
        print("=" * 70)
        print()
        print("📊 Summary:")
        print(f"   ✅ Successfully processed: {processed_count} email(s)")
        if failed_count > 0:
            print(f"   ⚠️  Failed: {failed_count} email(s) (will retry next run)")
        print()
        
        # Show statistics
        stats = state.get_stats()
        print("📈 All-Time Statistics:")
        print(f"   Total emails processed: {stats['total_processed']}")
        print(f"   Last run: {stats['last_run']}")
        print()
        
        # Show sheet link
        print("🔗 View your Google Sheet:")
        print(f"   https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}/edit")
        print()
        print("=" * 70)
        
    except FileNotFoundError as e:
        print()
        print("=" * 70)
        print("❌ Error: Configuration issue")
        print("=" * 70)
        print()
        print(str(e))
        print()
        sys.exit(1)
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Error: {e}")
        print("=" * 70)
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()