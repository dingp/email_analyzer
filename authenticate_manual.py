#!/usr/bin/env python3
"""
Standalone authentication script for headless environments
Fixed redirect_uri issue
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

def manual_authenticate():
    """Manual authentication for headless environments"""
    
    # Configuration
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE = 'token.json'
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    print("Gmail API Manual Authentication")
    print("=" * 40)
    
    # Check credentials file
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"❌ Error: {CREDENTIALS_FILE} not found!")
        print("Please download your OAuth 2.0 credentials from Google Cloud Console")
        return False
    
    # Create flow
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    
    # Set redirect URI for out-of-band flow
    flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
    
    # Get authorization URL
    auth_url, _ = flow.authorization_url(
        prompt='consent',
        access_type='offline'
    )
    
    print("\n📋 AUTHENTICATION STEPS:")
    print("1. Copy the URL below and open it in any web browser")
    print("2. Sign in to your Google account")
    print("3. Grant permissions to the application")
    print("4. Google will display an authorization code")
    print("5. Copy that code and paste it below")
    
    print(f"\n🔗 AUTHORIZATION URL:")
    print("-" * 60)
    print(auth_url)
    print("-" * 60)
    
    print(f"\n📝 After authorization, Google will show you a page with:")
    print("'Please copy this code, switch to your application and paste it there:'")
    print("followed by an authorization code.")
    
    # Get authorization code
    while True:
        try:
            print(f"\n🔑 Enter the authorization code:")
            auth_code = input("Code: ").strip()
            
            if not auth_code:
                print("❌ Please enter a valid code")
                continue
                
            break
            
        except KeyboardInterrupt:
            print("\n❌ Authentication cancelled")
            return False
    
    # Exchange code for credentials
    try:
        print("\n🔄 Exchanging code for credentials...")
        flow.fetch_token(code=auth_code)
        
        # Save credentials
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(flow.credentials, token)
        
        print(f"✅ Success! Credentials saved to {TOKEN_FILE}")
        print("🚀 You can now run the email analyzer")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("💡 Make sure you copied the complete authorization code")
        return False

if __name__ == "__main__":
    manual_authenticate()
