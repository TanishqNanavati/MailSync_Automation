"""
State Manager Module
Handles persistence of processed email IDs to prevent duplicates.
"""

import json
import os
from datetime import datetime
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class StateManager:
    """
    Manages state persistence using JSON file storage.
    
    Tracks which email message IDs have been processed to prevent
    duplicates when the script runs multiple times.
    """
    
    def __init__(self, state_file=None):
        """
        Initialize state manager.
        
        Args:
            state_file (str, optional): Path to state file.
                                       Defaults to config.STATE_FILE
        """
        self.state_file = state_file or config.STATE_FILE
        self.state = {
            'processed_message_ids': [],
            'last_run_timestamp': None,
            'total_emails_processed': 0
        }
        self.load_state()
    
    def load_state(self):
        """
        Load state from JSON file.
        
        If file doesn't exist or is corrupted, initializes empty state.
        This is called automatically on initialization.
        
        Returns:
            dict: Loaded state data
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                print(f"📋 Loaded state: {len(self.state['processed_message_ids'])} processed email(s)")
                return self.state
            except json.JSONDecodeError as e:
                print(f"⚠️  Warning: State file corrupted, creating new one: {e}")
                self._initialize_state()
            except Exception as e:
                print(f"⚠️  Warning: Error loading state: {e}")
                self._initialize_state()
        else:
            print("📝 No existing state file, creating new one")
            self._initialize_state()
        
        return self.state
    
    def _initialize_state(self):
        """Initialize empty state (internal method)."""
        self.state = {
            'processed_message_ids': [],
            'last_run_timestamp': None,
            'total_emails_processed': 0
        }
    
    def save_state(self):
        """
        Save current state to JSON file.
        
        Uses atomic write (write to temp file, then rename) to prevent
        corruption if script crashes during write.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update last run timestamp
            self.state['last_run_timestamp'] = datetime.now().isoformat()
            
            # Write to temporary file first (atomic write)
            temp_file = self.state_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            
            # Rename temp file to actual file (atomic operation)
            os.replace(temp_file, self.state_file)
            
            print(f"💾 State saved: {len(self.state['processed_message_ids'])} total processed")
            return True
            
        except Exception as e:
            print(f"❌ Error saving state: {e}")
            return False
    
    def is_processed(self, message_id):
        """
        Check if a message ID has been processed.
        
        Args:
            message_id (str): Gmail message ID
            
        Returns:
            bool: True if already processed, False if new
        """
        return message_id in self.state['processed_message_ids']
    
    def mark_as_processed(self, message_id):
        """
        Mark a message ID as processed.
        
        Adds to the processed list and increments counter.
        Does NOT save to file automatically - call save_state() after batch.
        
        Args:
            message_id (str): Gmail message ID
        """
        if message_id not in self.state['processed_message_ids']:
            self.state['processed_message_ids'].append(message_id)
            self.state['total_emails_processed'] += 1
    
    def filter_new_messages(self, message_ids):
        """
        Filter out already-processed message IDs from a list.
        
        Args:
            message_ids (list): List of message IDs to filter
            
        Returns:
            list: Only the message IDs that haven't been processed yet
        """
        new_ids = [msg_id for msg_id in message_ids 
                   if not self.is_processed(msg_id)]
        
        if len(new_ids) < len(message_ids):
            skipped = len(message_ids) - len(new_ids)
            print(f"⏭️  Skipping {skipped} already-processed email(s)")
        
        return new_ids
    
    def get_stats(self):
        """
        Get statistics about processed emails.
        
        Returns:
            dict: Statistics with keys:
                - total_processed: Total number processed all-time
                - last_run: Timestamp of last run
                - message_count: Current count in state
        """
        return {
            'total_processed': self.state['total_emails_processed'],
            'last_run': self.state['last_run_timestamp'],
            'message_count': len(self.state['processed_message_ids'])
        }
    
    def clear_state(self):
        """
        Clear all state (reset to empty).
        WARNING: This will cause all emails to be reprocessed!
        Use with caution - mainly for testing.
        
        Returns:
            bool: True if successful
        """
        self._initialize_state()
        return self.save_state()
    
    def remove_old_entries(self, keep_count=1000):
        """
        Remove oldest entries to prevent state file from growing too large.
        
        Keeps only the most recent N message IDs. This is safe because
        emails are marked as read, so old ones won't be refetched anyway.
        
        Args:
            keep_count (int): Number of recent message IDs to keep
            
        Returns:
            int: Number of entries removed
        """
        current_count = len(self.state['processed_message_ids'])
        
        if current_count > keep_count:
            removed = current_count - keep_count
            # Keep only the last N entries
            self.state['processed_message_ids'] = \
                self.state['processed_message_ids'][-keep_count:]
            print(f"🧹 Cleaned up {removed} old state entries")
            return removed
        
        return 0


if __name__ == "__main__":
    """
    Test the state manager independently.
    Run: python src/state_manager.py
    """
    print("=" * 60)
    print("Testing State Manager")
    print("=" * 60)
    
    try:
        # Test 1: Initialize state manager
        print("\n" + "=" * 60)
        print("Test 1: Initialize State Manager")
        print("=" * 60)
        
        state = StateManager()
        print(f"✅ State manager initialized")
        print(f"   State file: {config.STATE_FILE}")
        
        # Test 2: Check initial stats
        print("\n" + "=" * 60)
        print("Test 2: Get Statistics")
        print("=" * 60)
        
        stats = state.get_stats()
        print(f"📊 Statistics:")
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   Message count: {stats['message_count']}")
        print(f"   Last run: {stats['last_run']}")
        
        # Test 3: Mark messages as processed
        print("\n" + "=" * 60)
        print("Test 3: Mark Messages as Processed")
        print("=" * 60)
        
        test_message_ids = [
            "test_msg_001",
            "test_msg_002",
            "test_msg_003"
        ]
        
        print(f"📝 Marking {len(test_message_ids)} test messages as processed...")
        for msg_id in test_message_ids:
            state.mark_as_processed(msg_id)
        
        print(f"✅ Marked {len(test_message_ids)} messages")
        
        # Test 4: Check if processed
        print("\n" + "=" * 60)
        print("Test 4: Check if Messages are Processed")
        print("=" * 60)
        
        for msg_id in test_message_ids[:2]:
            is_proc = state.is_processed(msg_id)
            print(f"   {msg_id}: {'✅ Processed' if is_proc else '❌ New'}")
        
        new_msg = "test_msg_999"
        is_proc = state.is_processed(new_msg)
        print(f"   {new_msg}: {'✅ Processed' if is_proc else '🆕 New'}")
        
        # Test 5: Filter new messages
        print("\n" + "=" * 60)
        print("Test 5: Filter New Messages")
        print("=" * 60)
        
        mixed_messages = [
            "test_msg_001",  # Already processed
            "test_msg_004",  # New
            "test_msg_002",  # Already processed
            "test_msg_005",  # New
        ]
        
        print(f"📥 Input: {len(mixed_messages)} message IDs")
        new_messages = state.filter_new_messages(mixed_messages)
        print(f"📤 Output: {len(new_messages)} new message IDs")
        print(f"   New IDs: {new_messages}")
        
        # Test 6: Save state
        print("\n" + "=" * 60)
        print("Test 6: Save State")
        print("=" * 60)
        
        state.save_state()
        
        # Test 7: Reload and verify
        print("\n" + "=" * 60)
        print("Test 7: Reload State")
        print("=" * 60)
        
        state2 = StateManager()
        stats2 = state2.get_stats()
        print(f"📊 Reloaded Statistics:")
        print(f"   Total processed: {stats2['total_processed']}")
        print(f"   Message count: {stats2['message_count']}")
        
        # Verify persistence
        if state2.is_processed("test_msg_001"):
            print("✅ State persisted correctly!")
        else:
            print("❌ State persistence failed!")
        
        print("\n" + "=" * 60)
        print("✅ State Manager Test Complete!")
        print("=" * 60)
        print(f"\n💡 Check the state file: {config.STATE_FILE}")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()