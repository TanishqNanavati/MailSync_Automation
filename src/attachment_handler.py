"""
Attachment Handler Module
Detects, downloads, and manages email attachments.
"""

import os
import sys
import base64

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class AttachmentHandler:
    """Handles email attachments detection and optional download/upload."""
    
    def __init__(self, gmail_service=None):
        """
        Initialize attachment handler.
        
        Args:
            gmail_service: GmailService instance for downloading attachments
        """
        self.gmail_service = gmail_service
        
        # Create attachment directory if downloading locally
        if config.DOWNLOAD_ATTACHMENTS_LOCALLY:
            os.makedirs(config.ATTACHMENT_DIR, exist_ok=True)
    
    def process_attachments(self, message, message_id):
        """
        Process attachments from a Gmail message.
        
        Args:
            message (dict): Gmail API message object
            message_id (str): Gmail message ID
            
        Returns:
            dict: {
                'has_attachments': 'Yes' or 'No',
                'attachment_names': str (comma-separated),
                'attachment_count': int,
                'attachment_links': str (comma-separated) or 'None'
            }
        """
        if not config.ENABLE_ATTACHMENT_HANDLING:
            return {
                'has_attachments': 'No',
                'attachment_names': 'None',
                'attachment_count': 0,
                'attachment_links': 'None'
            }
        
        attachments = self._detect_attachments(message)
        
        if not attachments:
            return {
                'has_attachments': 'No',
                'attachment_names': 'None',
                'attachment_count': 0,
                'attachment_links': 'None'
            }
        
        # Filter by size and type
        valid_attachments = []
        for att in attachments:
            # Check size
            size_mb = att['size'] / (1024 * 1024)
            if size_mb > config.MAX_ATTACHMENT_SIZE_MB:
                print(f"      ⏭️  Skipping large attachment: {att['filename']} ({size_mb:.1f}MB)")
                continue
            
            # Check type (if specified)
            if config.ALLOWED_ATTACHMENT_TYPES:
                if att['mime_type'] not in config.ALLOWED_ATTACHMENT_TYPES:
                    print(f"      ⏭️  Skipping unsupported type: {att['filename']} ({att['mime_type']})")
                    continue
            
            valid_attachments.append(att)
        
        if not valid_attachments:
            return {
                'has_attachments': 'No',
                'attachment_names': 'None',
                'attachment_count': 0,
                'attachment_links': 'None'
            }
        
        # Process valid attachments
        attachment_names = []
        attachment_links = []
        
        for att in valid_attachments:
            attachment_names.append(att['filename'])
            
            # Download locally if enabled
            if config.DOWNLOAD_ATTACHMENTS_LOCALLY:
                try:
                    filepath = self._download_attachment(message_id, att)
                    attachment_links.append(filepath)
                except Exception as e:
                    print(f"      ⚠️  Failed to download {att['filename']}: {e}")
                    attachment_links.append('Download failed')
            
            # Upload to Drive if enabled (placeholder)
            elif config.UPLOAD_ATTACHMENTS_TO_DRIVE:
                # TODO: Implement Drive upload in future
                attachment_links.append('Drive upload not implemented')
        
        return {
            'has_attachments': 'Yes',
            'attachment_names': ', '.join(attachment_names),
            'attachment_count': len(valid_attachments),
            'attachment_links': ', '.join(attachment_links) if attachment_links else 'None'
        }
    
    def _detect_attachments(self, message):
        """
        Detect attachments in message payload.
        
        Args:
            message (dict): Gmail message object
            
        Returns:
            list: List of attachment dicts
        """
        attachments = []
        payload = message.get('payload', {})
        
        # Check if multipart
        if 'parts' in payload:
            for part in payload['parts']:
                attachments.extend(self._extract_attachments_from_part(part))
        else:
            # Single part - check if it's an attachment
            if payload.get('filename'):
                attachments.extend(self._extract_attachments_from_part(payload))
        
        return attachments
    
    def _extract_attachments_from_part(self, part):
        """Recursively extract attachments from message part."""
        attachments = []
        
        filename = part.get('filename', '')
        
        if filename:
            # This part has an attachment
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')
            size = body.get('size', 0)
            mime_type = part.get('mimeType', 'application/octet-stream')
            
            attachments.append({
                'filename': filename,
                'attachment_id': attachment_id,
                'size': size,
                'mime_type': mime_type
            })
        
        # Check nested parts
        if 'parts' in part:
            for subpart in part['parts']:
                attachments.extend(self._extract_attachments_from_part(subpart))
        
        return attachments
    
    def _download_attachment(self, message_id, attachment_info):
        """
        Download attachment from Gmail.
        
        Args:
            message_id (str): Gmail message ID
            attachment_info (dict): Attachment metadata
            
        Returns:
            str: Local file path
        """
        if not self.gmail_service:
            raise Exception("Gmail service not provided to attachment handler")
        
        # Get attachment data
        attachment_id = attachment_info['attachment_id']
        filename = attachment_info['filename']
        
        # Fetch attachment from Gmail API
        att_data = self.gmail_service.service.users().messages().attachments().get(
            userId='me',
            messageId=message_id,
            id=attachment_id
        ).execute()
        
        # Decode data
        file_data = base64.urlsafe_b64decode(att_data['data'])
        
        # Save to local file
        # Create message-specific folder
        message_folder = os.path.join(config.ATTACHMENT_DIR, message_id)
        os.makedirs(message_folder, exist_ok=True)
        
        filepath = os.path.join(message_folder, filename)
        
        with open(filepath, 'wb') as f:
            f.write(file_data)
        
        print(f"      📎 Downloaded: {filename} ({len(file_data)} bytes)")
        
        return filepath


if __name__ == "__main__":
    """Test attachment handler (requires Gmail service)."""
    print("=" * 60)
    print("Testing Attachment Handler")
    print("=" * 60)
    
    # Mock test without actual Gmail connection
    handler = AttachmentHandler()
    
    # Mock message with attachments
    mock_message = {
        'id': 'test_message_123',
        'payload': {
            'parts': [
                {
                    'filename': 'invoice.pdf',
                    'mimeType': 'application/pdf',
                    'body': {
                        'attachmentId': 'att_123',
                        'size': 50000  # 50KB
                    }
                },
                {
                    'filename': 'receipt.jpg',
                    'mimeType': 'image/jpeg',
                    'body': {
                        'attachmentId': 'att_124',
                        'size': 30000000  # 30MB - should be skipped
                    }
                }
            ]
        }
    }
    
    print("\nDetecting attachments in mock message:\n")
    
    result = handler.process_attachments(mock_message, 'test_message_123')
    
    print(f"Has Attachments: {result['has_attachments']}")
    print(f"Attachment Names: {result['attachment_names']}")
    print(f"Attachment Count: {result['attachment_count']}")
    print(f"Attachment Links: {result['attachment_links']}")
    
    print("\n" + "=" * 60)
    print("✅ Attachment Handler Test Complete!")
    print("=" * 60)
    print("\n💡 Note: Actual download requires Gmail service connection")