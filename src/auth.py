"""
OAuth 2.0 Authentication Module
Handles authentication for both Gmail and Google Sheets APIs.
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def authenticate():
    """
    Authenticate using OAuth 2.0 and return credentials.
    
    This function:
    1. Checks if token.json exists (from previous authentication)
    2. If exists and valid, uses it
    3. If expired, refreshes it automatically
    4. If doesn't exist, initiates OAuth flow (opens browser)
    
    The same credentials object can be used for both Gmail and Sheets APIs
    because we request all necessary scopes upfront.
    
    Returns:
        Credentials: Authenticated credentials object for API access
        
    Raises:
        FileNotFoundError: If credentials.json is missing
        Exception: If authentication fails
    """
    creds = None
    
    # Check if we have a token from previous authentication
    if os.path.exists(config.TOKEN_FILE):
        print("📋 Loading existing token...")
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES)
    
    # If credentials don't exist or are invalid
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Token expired but we have refresh token - auto refresh
            print("🔄 Token expired. Refreshing...")
            try:
                creds.refresh(Request())
                print("✅ Token refreshed successfully")
            except Exception as e:
                print(f"❌ Token refresh failed: {e}")
                print("🔐 Re-authenticating...")
                creds = None
        
        # If still no valid credentials, run OAuth flow
        if not creds:
            # Check if credentials.json exists
            if not os.path.exists(config.CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"❌ Credentials file not found at: {config.CREDENTIALS_FILE}\n"
                    f"Please download credentials.json from Google Cloud Console and "
                    f"place it in the credentials/ folder."
                )
            
            print("🔐 Starting OAuth 2.0 authentication...")
            print("📖 A browser window will open for you to grant permissions.")
            
            try:
                # Create OAuth flow
                flow = InstalledAppFlow.from_client_secrets_file(
                    config.CREDENTIALS_FILE,
                    config.SCOPES
                )
                
                # Run local server for OAuth callback
                # This will open a browser window
                creds = flow.run_local_server(port=0)
                
                print("✅ Authentication successful!")
                
            except Exception as e:
                raise Exception(f"❌ Authentication failed: {e}")
        
        # Save credentials for next run
        print("💾 Saving token for future use...")
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
        print(f"✅ Token saved to: {config.TOKEN_FILE}")
    
    else:
        print("✅ Using existing valid token")
    
    return creds


def revoke_token():
    """
    Revoke the current token and delete local token file.
    Use this if you want to re-authenticate or change Google account.
    """
    if os.path.exists(config.TOKEN_FILE):
        os.remove(config.TOKEN_FILE)
        print("✅ Token revoked and deleted")
    else:
        print("ℹ️  No token file found")


if __name__ == "__main__":
    """
    Test the authentication module independently.
    Run: python src/auth.py
    """
    print("=" * 60)
    print("Testing OAuth 2.0 Authentication")
    print("=" * 60)
    
    try:
        creds = authenticate()
        print("\n" + "=" * 60)
        print("✅ Authentication test successful!")
        print("=" * 60)
        print(f"\nToken info:")
        print(f"  - Valid: {creds.valid}")
        print(f"  - Expired: {creds.expired if hasattr(creds, 'expired') else 'N/A'}")
        print(f"  - Scopes: {', '.join(config.SCOPES)}")
        print("\n✅ Ready to use Gmail and Sheets APIs")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Authentication failed: {e}")
        print("=" * 60)