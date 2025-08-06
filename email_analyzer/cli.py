#!/usr/bin/env python3
"""
Command-line interface for Berkeley Lab Email Analyzer
"""

import argparse
import sys
import json
from datetime import datetime
from .email_processor import EmailProcessor

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Analyze Gmail emails for Berkeley Lab record classification"
    )
    
    parser.add_argument(
        '--days-back', 
        type=int, 
        default=7,
        help='Number of days back to analyze emails (default: 7)'
    )
    
    parser.add_argument(
        '--confidence', 
        type=float, 
        default=0.5,
        help='Minimum confidence score for lab records (default: 0.5)'
    )
    
    parser.add_argument(
        '--output', 
        type=str,
        help='Output file for results (default: auto-generated timestamp)'
    )
    
    parser.add_argument(
        '--format', 
        choices=['json', 'report', 'both'],
        default='both',
        help='Output format (default: both)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Berkeley Lab Email Analyzer 1.0.0'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize processor
        if args.verbose:
            print("Initializing email processor...")
        
        processor = EmailProcessor()
        
        # Process emails
        if args.verbose:
            print(f"Analyzing emails from the last {args.days_back} days...")
        
        results = processor.process_recent_emails(days_back=args.days_back)
        
        if not results:
            print("No emails found or processed.")
            return 0
        
        # Filter lab records
        lab_records = processor.filter_lab_records(results, min_confidence=args.confidence)
        
        # Generate output filename if not provided
        if not args.output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output = f'email_analysis_{timestamp}'
        
        # Output results
        if args.format in ['json', 'both']:
            json_file = f"{args.output}.json"
            processor.save_results(results, json_file)
            print(f"Results saved to: {json_file}")
        
        if args.format in ['report', 'both']:
            report = processor.generate_report(results)
            report_file = f"{args.output}_report.txt"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"Report saved to: {report_file}")
            
            if args.verbose:
                print("\n" + report)
        
        # Summary
        stats = processor.get_summary_stats(results)
        print(f"\nSummary:")
        print(f"- Total emails analyzed: {stats['total_emails']}")
        print(f"- Lab records identified: {stats['lab_records']}")
        print(f"- Lab record rate: {stats['lab_record_rate']:.1f}%")
        if stats['lab_records'] > 0:
            print(f"- Average confidence: {stats['avg_confidence']:.2f}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
