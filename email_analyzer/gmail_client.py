import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import base64
import email
from email.mime.text import MIMEText
from .config import config

class GmailClient:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API - supports both browser and console mode"""
        creds = None
        
        # Load existing token
        if os.path.exists(config.gmail_token_path):
            with open(config.gmail_token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                creds = self._get_new_credentials()
            
            # Save credentials for next run
            with open(config.gmail_token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def _get_new_credentials(self):
        """Get new credentials with fallback to manual console mode"""
        flow = InstalledAppFlow.from_client_secrets_file(
            config.gmail_credentials_path, config.gmail_scopes)
        
        # Try browser authentication first
        try:
            # Check if we're in a headless environment
            if self._is_headless_environment():
                raise Exception("Headless environment detected")
            
            creds = flow.run_local_server(port=0)
            return creds
            
        except Exception as e:
            print(f"Browser authentication failed: {e}")
            print("Switching to manual console authentication...")
            
            # Manual console authentication
            return self._manual_console_auth(flow)
    
    def _manual_console_auth(self, flow):
        """Manual console authentication for headless environments"""
        print("\n" + "="*60)
        print("MANUAL AUTHENTICATION REQUIRED")
        print("="*60)
        
        # Configure flow for manual mode
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'  # Out-of-band flow
        
        # Get the authorization URL
        auth_url, _ = flow.authorization_url(
            prompt='consent',
            access_type='offline'
        )
        
        print("\n1. Copy and paste this URL into a web browser:")
        print("-" * 50)
        print(auth_url)
        print("-" * 50)
        
        print("\n2. Complete the authentication in your browser")
        print("3. After authorization, Google will display an authorization code")
        print("4. Copy that authorization code and paste it below")
        
        # Get authorization code from user
        while True:
            try:
                auth_code = input("\nEnter the authorization code: ").strip()
                if auth_code:
                    break
                print("Please enter a valid authorization code.")
            except KeyboardInterrupt:
                print("\nAuthentication cancelled.")
                raise
        
        # Exchange code for token
        try:
            flow.fetch_token(code=auth_code)
            print("✅ Authentication successful!")
            return flow.credentials
        except Exception as e:
            print(f"❌ Failed to exchange authorization code: {e}")
            print("Please make sure you copied the complete authorization code.")
            raise
    
    def _is_headless_environment(self):
        """Check if we're running in a headless environment"""
        # Check common indicators of headless environment
        headless_indicators = [
            os.getenv('DISPLAY') is None,  # No X11 display
            os.getenv('SSH_CLIENT') is not None,  # SSH session
            os.getenv('SSH_TTY') is not None,  # SSH TTY
            os.getenv('CI') is not None,  # CI environment
            os.getenv('GITHUB_ACTIONS') is not None,  # GitHub Actions
            os.getenv('FORCE_CONSOLE_AUTH', '').lower() == 'true',  # Force console
        ]
        
        return any(headless_indicators)
    
    def get_recent_emails(self, days_back: int = None) -> List[Dict]:
        """Retrieve recent emails"""
        if days_back is None:
            days_back = config.days_back
        
        try:
            # Calculate date range
            since_date = datetime.now() - timedelta(days=days_back)
            query = f'after:{since_date.strftime("%Y/%m/%d")}'
            
            # Get message list
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=config.max_emails_per_batch
            ).execute()
            
            messages = result.get('messages', [])
            emails = []
            
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict]:
        """Get detailed email information"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload'].get('headers', [])
            
            # Extract header information
            email_data = {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': self._get_header_value(headers, 'Subject'),
                'from': self._get_header_value(headers, 'From'),
                'to': self._get_header_value(headers, 'To'),
                'date': self._get_header_value(headers, 'Date'),
                'body': self._extract_body(message['payload'])
            }
            
            return email_data
            
        except HttpError as error:
            print(f'Error getting email details: {error}')
            return None
    
    def _get_header_value(self, headers: List[Dict], name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _extract_body(self, payload: Dict) -> str:
        """Extract email body text"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html':
                    # Fallback to HTML if no plain text
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
