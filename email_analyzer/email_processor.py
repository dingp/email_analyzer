from typing import List, Dict
import json
from datetime import datetime
from .gmail_client import GmailClient
from .llm_analyzer import LLMAnalyzer
from .config import config

class EmailProcessor:
    def __init__(self):
        self.gmail_client = GmailClient()
        self.llm_analyzer = LLMAnalyzer()
    
    def process_recent_emails(self, days_back: int = None) -> List[Dict]:
        """Process recent emails and analyze them for lab record classification"""
        print("Retrieving recent emails...")
        emails = self.gmail_client.get_recent_emails(days_back)
        
        if not emails:
            print("No emails found.")
            return []
        
        print(f"Found {len(emails)} emails. Analyzing for lab record classification...")
        
        results = []
        for i, email in enumerate(emails, 1):
            print(f"Analyzing email {i}/{len(emails)}: {email['subject'][:50]}...")
            
            analysis = self.llm_analyzer.analyze_email(email)
            results.append(analysis)
        
        return results
    
    def filter_lab_records(self, analysis_results: List[Dict], 
                          min_confidence: float = 0.5) -> List[Dict]:
        """Filter results to only include emails that qualify as lab records"""
        return [
            result for result in analysis_results
            if result.get('is_lab_record', False) and 
               result.get('confidence_score', 0) >= min_confidence
        ]
    
    def generate_report(self, analysis_results: List[Dict]) -> str:
        """Generate a summary report for lab record analysis"""
        total_emails = len(analysis_results)
        lab_records = self.filter_lab_records(analysis_results)
        
        # Criteria breakdown
        meets_lab_business = sum(1 for r in analysis_results if r.get('meets_lab_business_criteria', False))
        meets_action_decision = sum(1 for r in analysis_results if r.get('meets_action_decision_criteria', False))
        excluded_emails = sum(1 for r in analysis_results if r.get('is_excluded_type', False))
        
        # Record type counts
        record_type_counts = {}
        for result in lab_records:
            record_type = result.get('record_type', 'unknown')
            record_type_counts[record_type] = record_type_counts.get(record_type, 0) + 1
        
        # Exclusion reason counts
        exclusion_counts = {}
        for result in analysis_results:
            if result.get('is_excluded_type', False):
                reason = result.get('exclusion_reason', 'unknown')
                exclusion_counts[reason] = exclusion_counts.get(reason, 0) + 1
        
        report = f"""
Berkeley Lab Email Record Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
- Total emails analyzed: {total_emails}
- Lab records identified: {len(lab_records)}
- Lab record rate: {len(lab_records)/total_emails*100:.1f}%

CRITERIA ANALYSIS:
- Emails meeting lab business criteria: {meets_lab_business} ({meets_lab_business/total_emails*100:.1f}%)
- Emails meeting action/decision criteria: {meets_action_decision} ({meets_action_decision/total_emails*100:.1f}%)
- Emails meeting BOTH criteria (lab records): {len(lab_records)} ({len(lab_records)/total_emails*100:.1f}%)
- Excluded emails: {excluded_emails} ({excluded_emails/total_emails*100:.1f}%)

RECORD TYPE BREAKDOWN:
"""
        
        for record_type, count in record_type_counts.items():
            report += f"- {record_type.replace('_', ' ').title()}: {count}\n"
        
        if exclusion_counts:
            report += "\nEXCLUSION REASONS:\n"
            for reason, count in exclusion_counts.items():
                report += f"- {reason.replace('_', ' ').title()}: {count}\n"
        
        report += "\nDETAILED LAB RECORDS:\n"
        report += "=" * 60 + "\n"
        
        for result in lab_records:
            report += f"""
Subject: {result.get('subject', 'N/A')}
From: {result.get('from', 'N/A')}
Date: {result.get('date', 'N/A')}
Record Type: {result.get('record_type', 'N/A').title()}
Confidence: {result.get('confidence_score', 0):.2f}

Lab Business Indicators: {', '.join(result.get('lab_business_indicators', []))}
Action/Decision Indicators: {', '.join(result.get('action_decision_indicators', []))}

Summary: {result.get('summary', 'N/A')}

Key Evidence: {', '.join(result.get('key_evidence', []))}

{'-' * 60}
"""
        
        return report
    
    def save_results(self, analysis_results: List[Dict], filename: str = None):
        """Save analysis results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'lab_record_analysis_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(analysis_results, f, indent=2, default=str)
        
        print(f"Results saved to: {filename}")
    
    def analyze_specific_emails(self, email_ids: List[str]) -> List[Dict]:
        """Analyze specific emails by their IDs"""
        results = []
        
        for email_id in email_ids:
            try:
                # Get email details
                email_data = self.gmail_client._get_email_details(email_id)
                if email_data:
                    # Analyze email
                    analysis = self.llm_analyzer.analyze_email(email_data)
                    results.append(analysis)
                else:
                    print(f"Could not retrieve email: {email_id}")
            except Exception as e:
                print(f"Error analyzing email {email_id}: {e}")
        
        return results
    
    def get_summary_stats(self, analysis_results: List[Dict]) -> Dict:
        """Get summary statistics from analysis results"""
        total_emails = len(analysis_results)
        
        if total_emails == 0:
            return {
                'total_emails': 0,
                'lab_records': 0,
                'lab_record_rate': 0.0,
                'avg_confidence': 0.0,
                'record_types': {},
                'exclusion_reasons': {}
            }
        
        lab_records = self.filter_lab_records(analysis_results)
        
        # Calculate average confidence for lab records
        lab_record_confidences = [r.get('confidence_score', 0) for r in lab_records]
        avg_confidence = sum(lab_record_confidences) / len(lab_record_confidences) if lab_record_confidences else 0.0
        
        # Count record types
        record_types = {}
        for result in lab_records:
            record_type = result.get('record_type', 'unknown')
            record_types[record_type] = record_types.get(record_type, 0) + 1
        
        # Count exclusion reasons
        exclusion_reasons = {}
        for result in analysis_results:
            if result.get('is_excluded_type', False):
                reason = result.get('exclusion_reason', 'unknown')
                exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
        
        return {
            'total_emails': total_emails,
            'lab_records': len(lab_records),
            'lab_record_rate': len(lab_records) / total_emails * 100,
            'avg_confidence': avg_confidence,
            'record_types': record_types,
            'exclusion_reasons': exclusion_reasons
        }
