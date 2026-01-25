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
            return
        
        print()
        
        # =====================================================================
        # Step 5: Filter Already-Processed Emails
        # =====================================================================
        print("🔍 Step 5: Filtering out already-processed emails...")
        print("-" * 70)
        
        new_message_ids = state.filter_new_messages(all_message_ids)
        
        if not new_message_ids:
            print("✅ All emails already processed.")
            return
        
        print(f"🆕 Found {len(new_message_ids)} new email(s)")
        print()
        
        # =====================================================================
        # Step 6: Process Emails
        # =====================================================================
        print("⚙️  Step 6: Processing emails...")
        print("-" * 70)
        
        processed_count = 0
        failed_count = 0
        
        for i, message_id in enumerate(new_message_ids, 1):
            try:
                print(f"\n[{i}/{len(new_message_ids)}] Processing: {message_id}")
                
                message = gmail.fetch_message_details(message_id)
                parsed = parse_email(message)
                
                print(f"   📧 From: {parsed['from']}")
                print(f"   📝 Subject: {parsed['subject'][:60]}...")
                
                # -------------------------------------------------------------
                # Phase 10: Subject Keyword Filtering
                # -------------------------------------------------------------
                if config.SUBJECT_KEYWORDS:
                    subject_lower = parsed['subject'].lower()
                    if not any(k.lower() in subject_lower for k in config.SUBJECT_KEYWORDS):
                        print("   ⏭️  Skipped (subject keyword filter)")
                        gmail.mark_as_read(message_id)
                        state.mark_as_processed(message_id)
                        continue
                
                row = [
                    parsed['message_id'],
                    parsed['from'],
                    parsed['subject'],
                    parsed['date'],
                    parsed['content']
                ]
                
                success = sheets.append_row(row)
                
                if success:
                    state.mark_as_processed(message_id)
                    gmail.mark_as_read(message_id)
                    processed_count += 1
                    print("   ✅ Successfully processed")
                else:
                    failed_count += 1
                    print("   ⚠️  Failed to append (will retry)")
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Error: {e}")
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
        print(f"✅ Processed: {processed_count}")
        if failed_count:
            print(f"⚠️  Failed: {failed_count}")
        print()
        print("🔗 Google Sheet:")
        print(f"https://docs.google.com/spreadsheets/d/{config.SPREADSHEET_ID}/edit")
        print("=" * 70)
        
    except Exception as e:
        print("❌ Fatal error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
