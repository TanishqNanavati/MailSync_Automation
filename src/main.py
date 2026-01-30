"""
Main orchestration script - Phase 1 Enhanced
Includes: Action Items, Attachments, Analytics
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from auth import authenticate
from gmail_service import GmailService
from sheets_service import SheetsService
from email_parser import parse_email
from state_manager import StateManager
from categorizer import categorize_email, get_importance
from summarizer import EmailSummarizer
from action_extractor import ActionExtractor  # NEW
from attachment_handler import AttachmentHandler  # NEW
from analytics import EmailAnalytics  # NEW


def main():
    """Enhanced main workflow with Phase 1 features."""
    print("=" * 70)
    print("📧 Gmail to Google Sheets Automation (Phase 1 Enhanced)")
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
        summarizer = EmailSummarizer()
        action_extractor = ActionExtractor(use_llm=True)  # NEW
        attachment_handler = AttachmentHandler(gmail_service=gmail)  # NEW
        analytics = EmailAnalytics(sheets_service=sheets, state_manager=state)  # NEW
        
        print()
        
        # =================================================================
        # Step 3: Ensure Sheet Headers
        # =================================================================
        print("📋 Step 3: Ensuring spreadsheet headers...")
        print("-" * 70)
        sheets.ensure_headers()
        print()
        
        # =================================================================
        # Step 4: Fetch ALL Unread Emails
        # =================================================================
        print("📬 Step 4: Fetching ALL unread emails...")
        print("-" * 70)
        print("   📂 Searching: Inbox, Promotions, Social, Updates, Spam")
        
        all_message_ids = gmail.fetch_unread_message_ids()
        
        if not all_message_ids:
            print("✅ No unread emails found.")
            print()
            # Generate analytics even if no new emails
            if config.ENABLE_ANALYTICS:
                analytics.generate_report()
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
            print("✅ All emails already processed.")
            print()
            # Generate analytics
            if config.ENABLE_ANALYTICS:
                analytics.generate_report()
            print("=" * 70)
            print("✨ Automation Complete!")
            print("=" * 70)
            return
        
        print(f"🆕 Found {len(new_message_ids)} new email(s) to process")
        print()
        
        # =================================================================
        # Step 6: Categorize and Sort by Importance
        # =================================================================
        print("🏷️  Step 6: Categorizing and prioritizing emails...")
        print("-" * 70)
        
        email_categories = []
        
        for msg_id in new_message_ids:
            try:
                message = gmail.fetch_message_details(msg_id)
                parsed = parse_email(message)
                category = categorize_email(parsed)
                email_categories.append((msg_id, category, parsed, message))
            except Exception as e:
                print(f"   ⚠️  Error categorizing {msg_id}: {e}")
                email_categories.append((msg_id, 'Other', None, None))
        
        # Sort by importance
        sorted_emails = sorted(
            email_categories,
            key=lambda x: get_importance(x[1]),
            reverse=True
        )
        
        print(f"✅ Emails categorized and sorted by importance")
        print()
        
        # Display category breakdown
        category_counts = {}
        for _, category, _, _ in sorted_emails:
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
        # Step 7: Process Emails (ENHANCED with Phase 1 features)
        # =================================================================
        print("⚙️  Step 7: Processing emails (highest importance first)...")
        print("-" * 70)
        
        processed_count = 0
        failed_count = 0
        
        for i, (message_id, category, cached_parsed, message) in enumerate(sorted_emails, 1):
            try:
                importance = get_importance(category)
                
                print(f"\n[{i}/{len(sorted_emails)}] Processing: {message_id}")
                print(f"   🏷️  Category: {category} | Importance: {importance}/5")
                
                # Use cached data
                if cached_parsed:
                    parsed = cached_parsed
                else:
                    message = gmail.fetch_message_details(message_id)
                    parsed = parse_email(message)
                
                print(f"   📧 From: {parsed['from']}")
                print(f"   📝 Subject: {parsed['subject'][:50]}...")
                
                # AI Summary
                print(f"   🤖 Generating summary...")
                summary = summarizer.summarize_email(parsed)
                print(f"   📄 Summary: {summary[:60]}...")
                
                # PHASE 1 Feature 1: Extract Action Items
                print(f"   ✅ Extracting action items...")
                actions = action_extractor.extract(parsed)
                if actions['actions'] != 'None':
                    print(f"   📋 Actions: {actions['actions'][:50]}...")
                    if actions['due_date'] != 'None':
                        print(f"   📅 Due: {actions['due_date']}")
                
                # PHASE 1 Feature 2: Process Attachments
                print(f"   📎 Processing attachments...")
                attachments = attachment_handler.process_attachments(message, message_id)
                if attachments['has_attachments'] == 'Yes':
                    print(f"   📎 Found {attachments['attachment_count']} attachment(s): {attachments['attachment_names'][:50]}...")
                
                # Prepare row with PHASE 1 columns (14 total)
                row = [
                    parsed['message_id'],      # A
                    parsed['from'],            # B
                    parsed['subject'],         # C
                    parsed['date'],            # D
                    category,                  # E
                    str(importance),           # F
                    summary,                   # G
                    parsed['content'],         # H
                    actions['actions'],        # I - NEW
                    actions['due_date'],       # J - NEW
                    attachments['has_attachments'],    # K - NEW
                    attachments['attachment_names'],   # L - NEW
                    str(attachments['attachment_count']),  # M - NEW
                    attachments['attachment_links']    # N - NEW
                ]
                
                # Append to Sheets
                success = sheets.append_row(row)
                
                if success:
                    state.mark_as_processed(message_id)
                    gmail.mark_as_read(message_id)
                    print(f"   ✅ Successfully processed and marked as read")
                    processed_count += 1
                else:
                    print(f"   ⚠️  Failed to append to Sheets (will retry next run)")
                    failed_count += 1
                
                # Rate limiting for Gemini
                if i < len(sorted_emails):
                    time.sleep(4)  # 15 req/min for Gemini Pro
                
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
        # Step 9: Generate Analytics (PHASE 1 Feature 3)
        # =================================================================
        if config.ENABLE_ANALYTICS and processed_count > 0:
            analytics.generate_report()
        
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
        
        # Sheet link
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