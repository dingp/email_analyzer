import requests
import json
from typing import Dict, List
from .config import config

class LLMAnalyzer:
    def __init__(self):
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model
    
    def analyze_email(self, email_data: Dict) -> Dict:
        """Analyze email content using local LLM for lab record classification"""
        
        # Prepare email content for analysis
        email_content = self._prepare_email_content(email_data)
        
        # Create analysis prompt
        prompt = self._create_lab_record_prompt(email_content)
        
        try:
            # Send request to Ollama
            response = self._query_ollama(prompt)
            
            # Parse response
            analysis_result = self._parse_analysis_response(response)
            
            # Add metadata
            analysis_result.update({
                'email_id': email_data['id'],
                'subject': email_data['subject'],
                'from': email_data['from'],
                'date': email_data['date']
            })
            
            return analysis_result
            
        except Exception as e:
            print(f"Error analyzing email {email_data['id']}: {e}")
            return self._create_error_result(email_data, str(e))
    
    def _prepare_email_content(self, email_data: Dict) -> str:
        """Prepare email content for analysis"""
        content = f"""
Subject: {email_data['subject']}
From: {email_data['from']}
To: {email_data['to']}
Date: {email_data['date']}

Body:
{email_data['body'][:2000]}  # Limit body length
"""
        return content
    
    def _create_lab_record_prompt(self, email_content: str) -> str:
        """Create prompt for lab record analysis based on Berkeley Lab definition"""
        prompt = f"""
Analyze the following email to determine if it qualifies as a Berkeley Lab record according to the official definition.

Email Content:
{email_content}

BERKELEY LAB RECORD DEFINITION:
A record is material that has been created or received in the course of Laboratory business, and provides evidence of the Lab's decisions or actions related to a research or operational function.

An email must be marked as a record if its contents include BOTH of the following criteria:
1. Lab business or is related to responsibilities at the Lab; AND
2. Documents an action or decision

IMPORTANT: The following are NOT examples of records and should be classified as NOT lab records:
- Calendar responses: invitations, acceptances, meeting announcements, meeting agendas, Zoom invitations, scheduling notifications
- Formal and informal announcements: system outages, drills, routine IT maintenance work, general notifications
- Personal emails: anything unrelated to Lab business
- Newsletters/Listservs and junk mail: mass communications, promotional content, general information distribution

Please analyze this email and respond with a JSON object containing:
1. "is_lab_record": boolean (true if this email meets BOTH criteria for a lab record AND is not in the exclusion list)
2. "meets_lab_business_criteria": boolean (true if related to lab business/responsibilities)
3. "meets_action_decision_criteria": boolean (true if documents an action or decision)
4. "is_excluded_type": boolean (true if this falls into one of the excluded categories)
5. "exclusion_reason": string (if excluded, specify which exclusion category applies)
6. "confidence_score": number between 0 and 1 (overall confidence in classification)
7. "lab_business_indicators": array of strings (specific phrases indicating lab business)
8. "action_decision_indicators": array of strings (specific phrases indicating actions/decisions)
9. "record_type": string (e.g., "research", "operational", "administrative", "safety", "procurement", "excluded", "none")
10. "summary": brief explanation of why this does or doesn't qualify as a lab record
11. "key_evidence": array of strings (most important phrases that support the classification)

Lab Business Examples (that could be records if they document actions/decisions):
- Research activities, experiments, data analysis results
- Operational functions, facility management decisions
- Administrative duties, departmental work assignments
- Safety procedures, compliance matters, policy implementations
- Equipment procurement, resource allocation decisions
- Berkeley Lab projects, divisions, groups work coordination

Action/Decision Examples:
- Approvals, authorizations, rejections, confirmations of actions
- Implementation of procedures or policies
- Assignment of tasks, resources, or responsibilities
- Budget decisions, procurement actions, contract decisions
- Project planning, milestone setting, deliverable assignments
- Conclusions, recommendations, determinations that affect work
- Problem resolution, corrective actions taken

Exclusion Categories to Check:
1. Calendar/Scheduling: meeting invites, calendar responses, agenda distributions, Zoom links
2. Announcements: system notifications, maintenance alerts, general announcements, drills
3. Personal: non-work related content, personal communications
4. Mass Communications: newsletters, listservs, promotional emails, junk mail

Remember: Even if an email is related to lab business, it must ALSO document an action or decision to be considered a record, AND it must not fall into the excluded categories.

Respond only with valid JSON.
"""
        return prompt
    
    def _query_ollama(self, prompt: str) -> str:
        """Send query to Ollama API"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for consistent analysis
                "top_p": 0.9
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse LLM response into structured data"""
        try:
            # Try to extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback parsing if JSON not found
                return self._fallback_parse(response)
                
        except json.JSONDecodeError:
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict:
        """Fallback parsing when JSON parsing fails"""
        # Simple keyword-based analysis as fallback
        response_lower = response.lower()
        email_content = response_lower  # Use full response for analysis
        
        lab_business_indicators = []
        action_decision_indicators = []
        
        # Check for exclusion categories first
        exclusion_keywords = {
            'calendar': ['meeting', 'calendar', 'invite', 'invitation', 'agenda', 'zoom', 'schedule', 'appointment'],
            'announcement': ['announcement', 'outage', 'maintenance', 'drill', 'notification', 'alert', 'system'],
            'personal': ['personal', 'private', 'family', 'vacation', 'birthday', 'congratulations'],
            'mass_communication': ['newsletter', 'listserv', 'unsubscribe', 'promotional', 'marketing', 'spam']
        }
        
        is_excluded = False
        exclusion_reason = ""
        
        for category, keywords in exclusion_keywords.items():
            if any(keyword in email_content for keyword in keywords):
                is_excluded = True
                exclusion_reason = category.replace('_', ' ')
                break
        
        # Check for lab business indicators
        lab_business_found = any(keyword in email_content for keyword in config.lab_business_keywords)
        if lab_business_found:
            lab_business_indicators.extend([kw for kw in config.lab_business_keywords if kw in email_content])
        
        # Check for action/decision indicators
        action_decision_found = any(keyword in email_content for keyword in config.action_decision_keywords)
        if action_decision_found:
            action_decision_indicators.extend([kw for kw in config.action_decision_keywords if kw in email_content])
        
        # Determine record type
        record_type = "none"
        if is_excluded:
            record_type = "excluded"
        elif lab_business_found and action_decision_found:
            if any(kw in email_content for kw in ['research', 'experiment', 'study', 'analysis']):
                record_type = "research"
            elif any(kw in email_content for kw in ['operational', 'facility', 'equipment']):
                record_type = "operational"
            elif any(kw in email_content for kw in ['administrative', 'department', 'policy']):
                record_type = "administrative"
            elif any(kw in email_content for kw in ['safety', 'compliance', 'procedure']):
                record_type = "safety"
            elif any(kw in email_content for kw in ['purchase', 'procure', 'contract', 'budget']):
                record_type = "procurement"
            else:
                record_type = "general"
        
        # Final determination: must meet both criteria AND not be excluded
        is_lab_record = lab_business_found and action_decision_found and not is_excluded
        
        return {
            "is_lab_record": is_lab_record,
            "meets_lab_business_criteria": lab_business_found,
            "meets_action_decision_criteria": action_decision_found,
            "is_excluded_type": is_excluded,
            "exclusion_reason": exclusion_reason,
            "confidence_score": 0.7 if is_lab_record else (0.8 if is_excluded else 0.3),
            "lab_business_indicators": list(set(lab_business_indicators)),
            "action_decision_indicators": list(set(action_decision_indicators)),
            "record_type": record_type,
            "summary": f"Fallback analysis: {'Excluded - ' + exclusion_reason if is_excluded else ('Qualifies as lab record' if is_lab_record else 'Does not qualify as lab record')} based on keyword matching",
            "key_evidence": list(set(lab_business_indicators + action_decision_indicators))
        }
    
    def _create_error_result(self, email_data: Dict, error_msg: str) -> Dict:
        """Create error result structure"""
        return {
            'email_id': email_data['id'],
            'subject': email_data['subject'],
            'from': email_data['from'],
            'date': email_data['date'],
            'is_lab_record': False,
            'meets_lab_business_criteria': False,
            'meets_action_decision_criteria': False,
            'is_excluded_type': False,
            'exclusion_reason': '',
            'confidence_score': 0.0,
            'lab_business_indicators': [],
            'action_decision_indicators': [],
            'record_type': 'none',
            'summary': f"Analysis failed: {error_msg}",
            'key_evidence': [],
            'error': True
        }
