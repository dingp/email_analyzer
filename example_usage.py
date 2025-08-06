# example_first_run.py
from email_analyzer import EmailProcessor

def main():
    print("Starting first-time authentication...")
    
    try:
        # This will trigger the authentication flow
        processor = EmailProcessor()
        print("✓ Authentication successful!")
        
        # Test with a small batch
        results = processor.process_recent_emails(days_back=1)
        print(f"✓ Successfully analyzed {len(results)} emails")
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")

if __name__ == "__main__":
    main()
