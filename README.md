# Using GPT-OSS to label emails with .LBNL.record

This repository contains a Python package for analyzing Gmail emails using local Large Language Models (LLMs) via Ollama to automatically identify and classify Berkeley Lab records according to official LBNL record management policies.

## Overview

The email analyzer automatically processes Gmail emails to determine if they qualify as Berkeley Lab records based on the official definition:

> A record is material, in any media, that has been created or received in the course of Laboratory business, and provides evidence of the Lab's decisions or actions related to a research or operational function.

An email qualifies as a lab record if it meets **BOTH** criteria:
1. **Lab business**: Related to responsibilities at the Lab
2. **Action/Decision**: Documents an action or decision

The system also excludes emails that are explicitly **NOT** records:
- Calendar responses (invitations, acceptances, meeting announcements, agendas, Zoom invitations)
- Formal and informal announcements (system outages, drills, routine IT maintenance)
- Personal emails (anything unrelated to Lab business)
- Newsletters/Listservs and junk mail

## Features

- **Automated Gmail Integration**: Connects to Gmail API to retrieve recent emails
- **Local LLM Analysis**: Uses Ollama to run GPT-OSS locally for privacy and security
- **Berkeley Lab Specific**: Tailored to LBNL record management requirements
- **Headless Authentication**: Supports server environments without GUI
- **Comprehensive Reporting**: Generates detailed analysis reports and JSON outputs
- **Configurable**: Customizable time ranges, confidence thresholds, and analysis parameters

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gmail API     │────│  Email Analyzer  │────│   Ollama/GPT    │
│   (OAuth 2.0)   │    │     Package      │    │   (Local LLM)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Recent Emails   │    │ Analysis Results │    │ Record          │
│ (Last N days)   │    │ (JSON/Reports)   │    │ Classification  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Using Gmail API

### Enabling Gmail API Client and Download Credentials

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Project name suggestion: "Berkeley Lab Email Analyzer"

2. **Enable Gmail API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill required fields:
     - App name: "Berkeley Lab Email Analyzer"
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes: `https://www.googleapis.com/auth/gmail.readonly`
   - Add test users (your email address)

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - **Important**: Choose "Desktop application" (not web application)
   - Name: "Email Analyzer Desktop Client"
   - Download the JSON file and save as `credentials.json`

### Headless Authentication

For server environments without GUI access, the package supports console-based authentication:

1. **Automatic Detection**: The system automatically detects headless environments (SSH sessions, no DISPLAY variable)

2. **Manual Console Flow**:
   - System generates an authorization URL
   - Copy URL and open in any browser (phone, laptop, etc.)
   - Complete Google authentication
   - Copy the authorization code back to terminal

3. **Force Console Mode**: Set environment variable `FORCE_CONSOLE_AUTH=true`

**Example Authentication Flow**:
```bash
# System detects headless environment and shows:
MANUAL AUTHENTICATION REQUIRED
============================================================

1. Copy and paste this URL into a web browser:
------------------------------------------------------------
https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...
------------------------------------------------------------

2. Complete the authentication in your browser
3. After authorization, Google will display an authorization code
4. Copy that authorization code and paste it below

Enter the authorization code: [paste code here]
```

## Install the Package

### Prerequisites

- Python 3.8 or higher
- Internet connection for Gmail API
- Ollama installed and running locally

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd email_analyzer_package
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv email_analyzer_env
   
   # Activate virtual environment
   # On Linux/Mac:
   source email_analyzer_env/bin/activate
   # On Windows:
   email_analyzer_env\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Install in development mode
   pip install -e .
   
   # Or install dependencies directly
   pip install -r requirements.txt
   ```

4. **Set Up Configuration**
   ```bash
   # Copy your Gmail credentials
   cp /path/to/downloaded/credentials.json ./credentials.json
   
   # Create environment configuration
   cat > .env << EOF
   GMAIL_CREDENTIALS_PATH=credentials.json
   GMAIL_TOKEN_PATH=token.json
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=gpt-oss:120b
   MAX_EMAILS_PER_BATCH=10
   DAYS_BACK=7
   FORCE_CONSOLE_AUTH=true
   EOF
   ```

### Package Structure
```
email_analyzer_package/
├── credentials.json          # Gmail API credentials (you provide)
├── token.json               # Auto-generated after first auth
├── .env                     # Configuration file
├── requirements.txt         # Python dependencies
├── setup.py                # Package installation
├── README.md               # This file
├── example_usage.py        # Example script
├── authenticate_manual.py  # Standalone auth script
└── email_analyzer/         # Main package
    ├── __init__.py
    ├── config.py           # Configuration management
    ├── gmail_client.py     # Gmail API interface
    ├── llm_analyzer.py     # LLM analysis logic
    ├── email_processor.py  # Main processing logic
    └── cli.py             # Command-line interface
```

## Pull and Serve GPT-OSS Locally with Ollama

Ref: [run gpt-oss locally cookbook](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama)

### Install and Run Ollama

```bash
# Download and install Ollama
curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz
tar -C $CFS/nstaff/$USER/ollama -xzf ollama-linux-amd64.tgz

# Set up environment variables
export PATH=$CFS/nstaff/$USER/ollama/bin:$PATH
export LD_LIBRARY_PATH=$CFS/nstaff/$USER/ollama/lib:$LD_LIBRARY_PATH
export OLLAMA_MODELS=$SCRATCH/ollama-models

# Start Ollama server
ollama serve
```

**Note**: Keep this terminal session running. Ollama must be serving for the email analyzer to work.

### Pull and Run the Model

On the same node where `ollama serve` is running, open a second terminal and pull the model:

```bash
# Set up environment (same as above)
export PATH=$CFS/nstaff/$USER/ollama/bin:$PATH
export LD_LIBRARY_PATH=$CFS/nstaff/$USER/ollama/lib:$LD_LIBRARY_PATH

# Pull the GPT-OSS model (this may take time - model is large)
ollama pull gpt-oss:120b

# Verify model is available
ollama list

# Test the model (optional)
ollama run gpt-oss:120b
```

### Alternative Models

If `gpt-oss:120b` is too large or unavailable, you can use alternative models:

```bash
# Smaller alternatives
ollama pull llama2:13b      # Good balance of size/performance
ollama pull mistral:7b      # Faster, smaller model
ollama pull codellama:13b   # Good for structured output

# Update your .env file accordingly
echo "OLLAMA_MODEL=llama2:13b" >> .env
```

## Setup the Package and Run

### Quick Start

1. **Verify Prerequisites**
   ```bash
   # Check Python version
   python --version  # Should be 3.8+
   
   # Check Ollama is running
   curl http://localhost:11434/api/tags
   ```

2. **First-Time Authentication**
   ```bash
   # Run authentication (will open browser or show console instructions)
   python authenticate_manual.py
   ```

3. **Run Email Analysis**
   ```bash
   # Basic usage - analyze last 7 days
   python example_usage.py
   
   # Custom time range
   python -c "
   from email_analyzer import EmailProcessor
   processor = EmailProcessor()
   results = processor.process_recent_emails(days_back=30)
   print(f'Analyzed {len(results)} emails')
   "
   ```

### Command Line Interface

The package includes a CLI for advanced usage:

```bash
# Install with CLI support
pip install -e .

# Basic analysis
email-analyzer --days-back 7 --confidence 0.5

# Verbose output with custom settings
email-analyzer --days-back 30 --confidence 0.7 --verbose --format both

# Help
email-analyzer --help
```

### Example Usage Script

```python
#!/usr/bin/env python3
"""
Example: Analyze recent emails for lab records
"""

from email_analyzer import EmailProcessor
import json

def main():
    # Initialize processor
    processor = EmailProcessor()
    
    # Analyze recent emails
    results = processor.process_recent_emails(days_back=14)
    
    # Filter high-confidence lab records
    lab_records = processor.filter_lab_records(results, min_confidence=0.7)
    
    # Generate report
    report = processor.generate_report(results)
    print(report)
    
    # Save results
    processor.save_results(results, 'analysis_results.json')
    
    # Summary statistics
    stats = processor.get_summary_stats(results)
    print(f"\nSummary: {stats['lab_records']}/{stats['total_emails']} emails are lab records")

if __name__ == "__main__":
    main()
```

### Configuration Options

Customize analysis via `.env` file:

```bash
# Email processing
MAX_EMAILS_PER_BATCH=50     # Process more emails at once
DAYS_BACK=30                # Look further back

# LLM settings  
OLLAMA_MODEL=gpt-oss:120b   # Use specific model
OLLAMA_BASE_URL=http://localhost:11434

# Authentication
FORCE_CONSOLE_AUTH=true     # Always use console auth
GMAIL_CREDENTIALS_PATH=./credentials.json
```

### Output Files

The analyzer generates several output files:

- `email_analysis_results.json` - Complete analysis with all details
- `lab_records_only.json` - Only emails classified as lab records  
- `email_analysis_YYYYMMDD_HHMMSS_report.txt` - Human-readable summary report
- `token.json` - Gmail authentication token (auto-generated)

### Troubleshooting

**Common Issues and Solutions:**

1. **"Ollama connection failed"**
   ```bash
   # Check if Ollama is running
   ps aux | grep ollama
   # Restart if needed
   ollama serve
   ```

2. **"Gmail authentication failed"**
   ```bash
   # Delete token and re-authenticate
   rm token.json
   python authenticate_manual.py
   ```

3. **"No emails found"**
   - Check date range (`DAYS_BACK` setting)
   - Verify Gmail account has emails in the specified period
   - Check Gmail API quotas in Google Cloud Console

4. **"Model not found"**
   ```bash
   # List available models
   ollama list
   # Pull required model
   ollama pull gpt-oss:120b
   ```

5. **"Permission denied"**
   ```bash
   # Check file permissions
   chmod 600 credentials.json token.json
   ```

### Performance Notes

- **Model Size**: `gpt-oss:120b` requires significant RAM (~80GB). Use smaller models for resource-constrained environments.
- **Processing Speed**: Analysis time depends on model size and number of emails. Expect 2-5 seconds per email.
- **Gmail API Limits**: Google imposes rate limits. The package includes automatic throttling.

### Security Considerations

- **Credentials**: Keep `credentials.json` and `token.json` secure and private
- **Local Processing**: All email content is processed locally via Ollama - no data sent to external LLM services
- **Read-Only Access**: The package only requests read-only Gmail permissions
- **Token Management**: Tokens are automatically refreshed; manual intervention rarely needed

For additional support or questions, refer to the troubleshooting section or check the project's issue tracker.
