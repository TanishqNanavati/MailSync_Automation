"""
Email Analytics Module
Generates insights and statistics from processed emails.
"""

import sys
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class EmailAnalytics:
    """Generates analytics from processed emails."""
    
    def __init__(self, sheets_service=None, state_manager=None):
        """
        Initialize analytics.
        
        Args:
            sheets_service: SheetsService instance
            state_manager: StateManager instance
        """
        self.sheets_service = sheets_service
        self.state_manager = state_manager
        
        # Create analytics output directory
        os.makedirs(config.ANALYTICS_OUTPUT_DIR, exist_ok=True)
    
    def generate_report(self):
        """
        Generate comprehensive analytics report.
        
        Returns:
            dict: Analytics data
        """
        if not config.ENABLE_ANALYTICS:
            print("⚠️  Analytics disabled in config")
            return None
        
        print("\n" + "=" * 70)
        print("📊 Generating Email Analytics Report")
        print("=" * 70)
        
        # Get data from Google Sheets
        data = self._fetch_sheet_data()
        
        if not data:
            print("⚠️  No data available for analytics")
            return None
        
        # Calculate metrics
        analytics = {
            'total_emails': len(data),
            'by_category': self._count_by_category(data),
            'by_importance': self._count_by_importance(data),
            'by_sender': self._top_senders(data, limit=10),
            'has_attachments': self._count_attachments(data),
            'has_actions': self._count_actions(data),
            'date_range': self._get_date_range(data),
            'daily_volume': self._get_daily_volume(data)
        }
        
        # Display report
        self._display_report(analytics)
        
        # Save to file
        self._save_report(analytics)
        
        return analytics
    
    def _fetch_sheet_data(self):
        """Fetch all email data from Google Sheets."""
        if not self.sheets_service:
            print("⚠️  Sheets service not available")
            return []
        
        try:
            # Read all rows (skip header)
            range_name = f"{config.SHEET_NAME}!A2:N"
            
            result = self.sheets_service.service.spreadsheets().values().get(
                spreadsheetId=config.SPREADSHEET_ID,
                range=range_name
            ).execute()
            
            rows = result.get('values', [])
            
            # Convert to list of dicts
            data = []
            for row in rows:
                # Ensure row has enough columns
                while len(row) < 14:
                    row.append('')
                
                data.append({
                    'message_id': row[0],
                    'from': row[1],
                    'subject': row[2],
                    'date': row[3],
                    'category': row[4] if len(row) > 4 else 'Other',
                    'importance': int(row[5]) if len(row) > 5 and row[5].isdigit() else 2,
                    'summary': row[6] if len(row) > 6 else '',
                    'content': row[7] if len(row) > 7 else '',
                    'action_items': row[8] if len(row) > 8 else 'None',
                    'due_date': row[9] if len(row) > 9 else 'None',
                    'has_attachments': row[10] if len(row) > 10 else 'No',
                    'attachment_names': row[11] if len(row) > 11 else 'None',
                    'attachment_count': int(row[12]) if len(row) > 12 and row[12].isdigit() else 0,
                    'attachment_links': row[13] if len(row) > 13 else 'None'
                })
            
            return data
            
        except Exception as e:
            print(f"⚠️  Error fetching sheet data: {e}")
            return []
    
    def _count_by_category(self, data):
        """Count emails by category."""
        categories = [email['category'] for email in data]
        return dict(Counter(categories))
    
    def _count_by_importance(self, data):
        """Count emails by importance level."""
        importance_counts = Counter([email['importance'] for email in data])
        return dict(sorted(importance_counts.items(), reverse=True))
    
    def _top_senders(self, data, limit=10):
        """Get top N senders by email count."""
        senders = [email['from'] for email in data]
        top = Counter(senders).most_common(limit)
        return dict(top)
    
    def _count_attachments(self, data):
        """Count emails with/without attachments."""
        with_attachments = sum(1 for email in data if email['has_attachments'] == 'Yes')
        without_attachments = len(data) - with_attachments
        return {
            'with_attachments': with_attachments,
            'without_attachments': without_attachments,
            'total_attachments': sum(email['attachment_count'] for email in data)
        }
    
    def _count_actions(self, data):
        """Count emails with/without action items."""
        with_actions = sum(1 for email in data if email['action_items'] != 'None')
        without_actions = len(data) - with_actions
        return {
            'with_actions': with_actions,
            'without_actions': without_actions
        }
    
    def _get_date_range(self, data):
        """Get date range of emails."""
        dates = []
        for email in data:
            try:
                # Parse ISO date
                date_str = email['date']
                if date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    dates.append(date_obj)
            except:
                continue
        
        if dates:
            return {
                'earliest': min(dates).strftime('%Y-%m-%d'),
                'latest': max(dates).strftime('%Y-%m-%d'),
                'days_span': (max(dates) - min(dates)).days
            }
        return {'earliest': 'N/A', 'latest': 'N/A', 'days_span': 0}
    
    def _get_daily_volume(self, data):
        """Get email count per day."""
        daily_counts = defaultdict(int)
        
        for email in data:
            try:
                date_str = email['date']
                if date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    day = date_obj.strftime('%Y-%m-%d')
                    daily_counts[day] += 1
            except:
                continue
        
        # Sort by date
        sorted_daily = dict(sorted(daily_counts.items()))
        return sorted_daily
    
    def _display_report(self, analytics):
        """Display analytics report in console."""
        print("\n📊 EMAIL ANALYTICS REPORT")
        print("=" * 70)
        
        # Summary
        print(f"\n📈 SUMMARY")
        print(f"   Total Emails Processed: {analytics['total_emails']}")
        print(f"   Date Range: {analytics['date_range']['earliest']} to {analytics['date_range']['latest']}")
        print(f"   Days Span: {analytics['date_range']['days_span']} days")
        
        # By Category
        print(f"\n🏷️  EMAILS BY CATEGORY")
        for category in sorted(analytics['by_category'].items(), 
                              key=lambda x: x[1], reverse=True):
            print(f"   {category[0]}: {category[1]} emails")
        
        # By Importance
        print(f"\n⚡ EMAILS BY IMPORTANCE")
        for importance, count in analytics['by_importance'].items():
            print(f"   Priority {importance}/5: {count} emails")
        
        # Top Senders
        print(f"\n📧 TOP 10 SENDERS")
        for i, (sender, count) in enumerate(analytics['by_sender'].items(), 1):
            print(f"   {i}. {sender}: {count} emails")
        
        # Attachments
        att_stats = analytics['has_attachments']
        print(f"\n📎 ATTACHMENT STATISTICS")
        print(f"   Emails with attachments: {att_stats['with_attachments']}")
        print(f"   Emails without attachments: {att_stats['without_attachments']}")
        print(f"   Total attachments: {att_stats['total_attachments']}")
        
        # Actions
        action_stats = analytics['has_actions']
        print(f"\n✅ ACTION ITEM STATISTICS")
        print(f"   Emails with action items: {action_stats['with_actions']}")
        print(f"   Emails without action items: {action_stats['without_actions']}")
        
        # Daily Volume (last 7 days)
        print(f"\n📅 DAILY EMAIL VOLUME (Last 7 Days)")
        daily = list(analytics['daily_volume'].items())[-7:]
        for day, count in daily:
            print(f"   {day}: {count} emails")
        
        print("\n" + "=" * 70)
    
    def _save_report(self, analytics):
        """Save analytics report to file."""
        try:
            report_path = os.path.join(
                config.ANALYTICS_OUTPUT_DIR,
                config.ANALYTICS_REPORT_NAME
            )
            
            with open(report_path, 'w') as f:
                f.write("EMAIL ANALYTICS REPORT\n")
                f.write("=" * 70 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"Total Emails: {analytics['total_emails']}\n")
                f.write(f"Date Range: {analytics['date_range']['earliest']} to {analytics['date_range']['latest']}\n\n")
                
                f.write("BY CATEGORY:\n")
                for cat, count in analytics['by_category'].items():
                    f.write(f"  {cat}: {count}\n")
                
                f.write("\nBY IMPORTANCE:\n")
                for imp, count in analytics['by_importance'].items():
                    f.write(f"  Priority {imp}: {count}\n")
                
                f.write("\nTOP SENDERS:\n")
                for sender, count in list(analytics['by_sender'].items())[:10]:
                    f.write(f"  {sender}: {count}\n")
            
            # Also save as JSON
            json_path = report_path.replace('.txt', '.json')
            with open(json_path, 'w') as f:
                json.dump(analytics, f, indent=2)
            
            print(f"\n💾 Report saved to:")
            print(f"   {report_path}")
            print(f"   {json_path}")
            
        except Exception as e:
            print(f"⚠️  Failed to save report: {e}")


if __name__ == "__main__":
    """Test analytics with mock data."""
    print("=" * 60)
    print("Testing Email Analytics")
    print("=" * 60)
    
    # Note: Requires actual Sheets service for real testing
    print("\n💡 This module requires SheetsService for real testing")
    print("   Run from main.py after processing emails")
    print("\n=" * 60)