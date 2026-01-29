"""
Main orchestration script for Gmail to Sheets automation.
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
from categorizer import categorize_email, get_importance, sort_emails_by_importance
from summarizer import EmailSummarizer


def main():
    """
    Main execution function - orchestrates the entire workflow.
    
    Enhanced workflow:
    1. Authenticate
    2. Initialize services (including AI summarizer)
    3. Fetch ALL unread emails (not just inbox)
    4. Filter already-processed emails
    5. Categorize emails
    6. Sort by importance (process high-priority first)
    7. For each email:
       - Parse content
       - Generate AI summary
       - Append to Sheets with category, importance, summary
       - Update state
       - Mark as read
    """
    print("=" * 70)
    print("📧 Gmail to Google Sheets Automation (Enhanced)")
    print("=" * 70)
    print()
    
    try:
        # =================================================================
        # Step 1: Authentication
        # =================================================================
        print("🔐 Step 1: Authenticating with Google APIs...")
        print("-" * 70)
        credentials = authenticate()
        print()
        
        # =================================================================
        # Step 2: Initialize Services
        # =================================================================
        print("🔧 Step 2: Initializing services...")
        print("-" * 70)
        
        gmail = GmailService(credentials)
        sheets = SheetsService(credentials)
        state = StateManager()
        summarizer = EmailSummarizer()  # NEW: AI summarizer
        
        print()
        
        # =================================================================
        # Step 3: Ensure Sheet Headers
        # =================================================================
        print("📋 Step 3: Ensuring spreadsheet headers...")
        print("-" * 70)
        sheets.ensure_headers()
        print()
        
        # =================================================================
        # Step 4: Fetch ALL Unread Emails (Enhanced)
        # =================================================================
        print("📬 Step 4: Fetching ALL unread emails...")
        print("-" * 70)
        print("   📂 Searching: Inbox, Promotions, Social, Updates, Spam")
        
        all_message_ids = gmail.fetch_unread_message_ids()
        
        if not all_message_ids:
            print("✅ No unread emails found. Nothing to process.")
            print()
            print("=" * 70)
            print("✨ Automation Complete!")
            print("=" * 70)
            return
        
        print()
        
        # =================================================================
        # Step 5: Filter Already-Processed Emails
        # =================================================================
        print("🔍 Step 5: Filtering out already-processed emails...")
        print("-" * 70)
        
        new_message_ids = state.filter_new_messages(all_message_ids)
        
        if not new_message_ids:
            print("✅ All emails have been processed already.")
            print()
            print("=" * 70)
            print("✨ Automation Complete!")
            print("=" * 70)
            return
        
        print(f"🆕 Found {len(new_message_ids)} new email(s) to process")
        print()
        
        # =================================================================
        # Step 6: Categorize and Sort by Importance (NEW)
        # =================================================================
        print("🏷️  Step 6: Categorizing and prioritizing emails...")
        print("-" * 70)
        
        # Quick pass to categorize (fetch minimal details)
        email_categories = []
        
        for msg_id in new_message_ids:
            try:
                # Fetch email
                message = gmail.fetch_message_details(msg_id)
                
                # Quick parse for categorization
                parsed = parse_email(message)
                
                # Categorize
                category = categorize_email(parsed)
                
                email_categories.append((msg_id, category, parsed))
                
            except Exception as e:
                print(f"   ⚠️  Error categorizing {msg_id}: {e}")
                # Add with default category
                email_categories.append((msg_id, 'Other', None))
        
        # Sort by importance
        sorted_emails = sorted(
            email_categories,
            key=lambda x: get_importance(x[1]),
            reverse=True  # Highest importance first
        )
        
        print(f"✅ Emails categorized and sorted by importance")
        print()
        
        # Display priority breakdown
        category_counts = {}
        for _, category, _ in sorted_emails:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("📊 Category Breakdown:")
        for category in sorted(category_counts.keys(), 
                              key=lambda c: get_importance(c), 
                              reverse=True):
            count = category_counts[category]
            importance = get_importance(category)
            print(f"   {category}: {count} email(s) [Priority: {importance}/5]")
        
        print()
        
        # =================================================================
        # Step 7: Process Emails (in importance order)
        # =================================================================
        print("⚙️  Step 7: Processing emails (highest importance first)...")
        print("-" * 70)
        
        processed_count = 0
        failed_count = 0
        
        for i, (message_id, category, cached_parsed) in enumerate(sorted_emails, 1):
            try:
                importance = get_importance(category)
                
                print(f"\n[{i}/{len(sorted_emails)}] Processing: {message_id}")
                print(f"   🏷️  Category: {category} | Importance: {importance}/5")
                
                # Use cached parsed data if available
                if cached_parsed:
                    parsed = cached_parsed
                else:
                    message = gmail.fetch_message_details(message_id)
                    parsed = parse_email(message)
                
                print(f"   📧 From: {parsed['from']}")
                print(f"   📝 Subject: {parsed['subject'][:50]}...")
                
                # NEW: Generate AI summary
                print(f"   🤖 Generating summary...")
                summary = summarizer.summarize_email(parsed)
                print(f"   📄 Summary: {summary[:60]}...")
                
                # Prepare row with NEW columns
                row = [
                    parsed['message_id'],
                    parsed['from'],
                    parsed['subject'],
                    parsed['date'],
                    category,           # NEW
                    str(importance),    # NEW (as string for Sheets)
                    summary,            # NEW
                    parsed['content']
                ]
                
                # Append to Sheets
                success = sheets.append_row(row)
                
                if success:
                    # Mark as processed
                    state.mark_as_processed(message_id)
                    
                    # Mark as read
                    gmail.mark_as_read(message_id)
                    
                    print(f"   ✅ Successfully processed and marked as read")
                    processed_count += 1
                else:
                    print(f"   ⚠️  Failed to append to Sheets (will retry next run)")
                    failed_count += 1
                
            except Exception as e:
                print(f"   ❌ Error processing email: {e}")
                failed_count += 1
                continue
        
        print()
        
        # =================================================================
        # Step 8: Save State
        # =================================================================
        print("💾 Step 8: Saving state...")
        print("-" * 70)
        state.save_state()
        print()
        
        # =================================================================
        # Summary
        # =================================================================
        print("=" * 70)
        print("✨ Automation Complete!")
        print("=" * 70)
        print()
        print("📊 Summary:")
        print(f"   ✅ Successfully processed: {processed_count} email(s)")
        if failed_count > 0:
            print(f"   ⚠️  Failed: {failed_count} email(s) (will retry next run)")
        print()
        
        # Statistics
        stats = state.get_stats()
        print("📈 All-Time Statistics:")
        print(f"   Total emails processed: {stats['total_processed']}")
        print(f"   Last run: {stats['last_run']}")
        print()
        
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