from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class Config(BaseModel):
    # Gmail API settings
    gmail_credentials_path: str = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    gmail_token_path: str = os.getenv('GMAIL_TOKEN_PATH', 'token.json')
    gmail_scopes: List[str] = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # Ollama settings
    ollama_base_url: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    ollama_model: str = os.getenv('OLLAMA_MODEL', 'llama2')
    
    # Email processing settings
    max_emails_per_batch: int = int(os.getenv('MAX_EMAILS_PER_BATCH', '10'))
    days_back: int = int(os.getenv('DAYS_BACK', '7'))
    
    # Lab record criteria keywords
    lab_business_keywords: List[str] = [
        'research', 'experiment', 'laboratory', 'lab', 'project', 'study',
        'analysis', 'data', 'results', 'findings', 'methodology', 'protocol',
        'sample', 'testing', 'measurement', 'calibration', 'equipment',
        'safety', 'compliance', 'quality', 'procedure', 'standard',
        'berkeley lab', 'lbnl', 'department', 'division', 'group',
        'operational', 'administrative', 'facility', 'resource'
    ]
    
    action_decision_keywords: List[str] = [
        'decision', 'approve', 'approved', 'authorize', 'authorized',
        'reject', 'rejected', 'deny', 'denied', 'accept', 'accepted',
        'implement', 'implemented', 'execute', 'executed', 'action',
        'directive', 'instruction', 'order', 'mandate', 'require',
        'assign', 'assigned', 'allocate', 'allocated', 'budget',
        'fund', 'funded', 'purchase', 'procure', 'contract',
        'agreement', 'policy', 'procedure', 'protocol', 'standard',
        'recommendation', 'conclude', 'determine', 'establish',
        'schedule', 'plan', 'strategy', 'milestone', 'deliverable'
    ]
    
    # Exclusion keywords (emails that are NOT records)
    exclusion_keywords: Dict[str, List[str]] = {
        'calendar': [
            'meeting', 'calendar', 'invite', 'invitation', 'agenda', 
            'zoom', 'schedule', 'appointment', 'accepted', 'declined',
            'tentative', 'reschedule', 'room booking', 'conference call'
        ],
        'announcement': [
            'announcement', 'outage', 'maintenance', 'drill', 'notification',
            'alert', 'system', 'broadcast', 'fyi', 'heads up', 'notice',
            'reminder', 'update', 'bulletin'
        ],
        'personal': [
            'personal', 'private', 'family', 'vacation', 'birthday',
            'congratulations', 'condolences', 'wedding', 'baby',
            'retirement', 'farewell', 'social', 'lunch', 'coffee'
        ],
        'mass_communication': [
            'newsletter', 'listserv', 'unsubscribe', 'promotional',
            'marketing', 'spam', 'bulk', 'distribution', 'broadcast',
            'mass email', 'mailing list', 'subscription'
        ]
    }

config = Config()
