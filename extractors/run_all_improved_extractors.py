#!/usr/bin/env python3
"""
Master Improved Extraction Runner
Runs all improved competency extractors and provides comprehensive analysis

This script executes all improved extraction methods and compares results
with the original extraction success rates.
"""

import os
import json
import subprocess
import sys
from datetime import datetime

def run_extractor(script_path, description):
    """Run an extraction script and capture results."""
    print(f"\n{'='*80}")
    print(f"RUNNING: {description}")
    print(f"Script: {script_path}")
    print(f"{'='*80}")
    
    try:
        result = subprocess.run([
            sys.executable, script_path
        ], capture_output=True, text=True, cwd=os.path.dirname(script_path))
        
        if result.returncode == 0:
            print("✅ Extraction completed successfully")
            return True, result.stdout, result.stderr
        else:
            print(f"❌ Extraction failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False, result.stdout, result.stderr
            
    except Exception as e:
        print(f"❌ Error running extractor: {e}")
        return False, "", str(e)

def load_extraction_summary(summary_path):
    """Load extraction summary from JSON file."""
    try:
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load summary from {summary_path}: {e}")
    return None

def compare_results(original_summary, improved_summary, category_name):
    """Compare original and improved results."""
    if not original_summary or not improved_summary:
        return {
            'category': category_name,
            'comparison_available': False,
            'original_success_rate': 'N/A',
            'improved_success_rate': 'N/A',
            'improvement': 'N/A'
        }
    
    original_rate = original_summary.get('successful_extractions', 0) / original_summary.get('total_documents', 1) * 100
    improved_rate = improved_summary.get('successful_extractions', 0) / improved_summary.get('total_documents', 1) * 100
    
    improvement = improved_rate - original_rate
    
    return {
        'category': category_name,
        'comparison_available': True,
        'original_total': original_summary.get('total_documents', 0),
        'original_successful': original_summary.get('successful_extractions', 0),
        'original_success_rate': f"{original_rate:.1f}%",
        'improved_total': improved_summary.get('total_documents', 0),
        'improved_successful': improved_summary.get('successful_extractions', 0),
        'improved_success_rate': f"{improved_rate:.1f}%",
        'improvement': f"{improvement:+.1f}%",
        'improvement_numeric': improvement
    }

def main():
    """Main execution function."""
    print("🚀 MASTER IMPROVED EXTRACTION RUNNER")
    print("=====================================")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    extractors_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/extractors"
    base_output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies"
    
    # Define all improved extractors to run
    extractors = [
        {
            'script': 'extract_advanced_key_enabling_improved.py',
            'description': 'Advanced Key & Enabling (Improved)',
            'category': '01_Advanced_Key_Enabling',
            'original_summary': '01_Advanced_Key_and_Enabling_Format/extraction_summary.json',
            'improved_summary': '01_Advanced_Key_and_Enabling_Format/extraction_summary_improved.json'
        },
        {
            'script': 'extract_standard_canmeds_improved.py',
            'description': 'Standard CanMEDS (Improved)',
            'category': '02_Standard_CanMEDS',
            'original_summary': '02_Standard_CanMEDS_Format/extraction_summary.json',
            'improved_summary': '02_Standard_CanMEDS_Format/extraction_summary_improved.json'
        },
        {
            'script': 'extract_basic_role_based_improved.py',
            'description': 'Basic Role-Based (Improved)', 
            'category': '03_Basic_Role_Based',
            'original_summary': '03_Basic_Role_Based_Format/extraction_summary.json',
            'improved_summary': '03_Basic_Role_Based_Format/extraction_summary_improved.json'
        },
        {
            'script': 'extract_legacy_dotted_toc_improved.py',
            'description': 'Legacy Dotted TOC (Improved)',
            'category': '04_Legacy_Dotted_TOC',
            'original_summary': '04_Legacy_Dotted_TOC/extraction_summary.json',
            'improved_summary': '04_Legacy_Dotted_TOC/extraction_summary_improved.json'
        },
        {
            'script': 'extract_canmeds_without_levels_improved.py', 
            'description': 'CanMEDS Without Levels (Improved)',
            'category': '05_CanMEDS_Without_Levels',
            'original_summary': '05_CanMEDS_Without_Levels/extraction_summary.json',
            'improved_summary': '05_CanMEDS_Without_Levels/extraction_summary_improved.json'
        }
    ]
    
    # Track execution results
    execution_results = []
    comparison_results = []
    
    # Run all extractors
    for extractor in extractors:
        script_path = os.path.join(extractors_dir, extractor['script'])
        
        if not os.path.exists(script_path):
            print(f"⚠️  Script not found: {script_path}")
            execution_results.append({
                'extractor': extractor['description'],
                'status': 'SCRIPT_NOT_FOUND',
                'success': False
            })
            continue
        
        # Run the extractor
        success, stdout, stderr = run_extractor(script_path, extractor['description'])
        
        execution_results.append({
            'extractor': extractor['description'],
            'status': 'SUCCESS' if success else 'FAILED',
            'success': success,
            'stdout_lines': len(stdout.split('\n')) if stdout else 0,
            'stderr_lines': len(stderr.split('\n')) if stderr else 0
        })
        
        # Load and compare summaries
        original_path = os.path.join(base_output_dir, extractor['original_summary'])
        improved_path = os.path.join(base_output_dir, extractor['improved_summary'])
        
        original_summary = load_extraction_summary(original_path)
        improved_summary = load_extraction_summary(improved_path)
        
        comparison = compare_results(original_summary, improved_summary, extractor['description'])
        comparison_results.append(comparison)
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("🎯 COMPREHENSIVE EXTRACTION RESULTS")
    print(f"{'='*80}")
    
    # Execution Summary
    print("\n📊 EXECUTION SUMMARY:")
    print("-" * 50)
    total_executed = len(execution_results)
    successful_executions = sum(1 for r in execution_results if r['success'])
    
    print(f"Total Extractors Run: {total_executed}")
    print(f"Successful Executions: {successful_executions}")
    print(f"Execution Success Rate: {successful_executions/total_executed*100:.1f}%")
    
    for result in execution_results:
        status_emoji = "✅" if result['success'] else "❌"
        print(f"  {status_emoji} {result['extractor']}: {result['status']}")
    
    # Performance Comparison
    print(f"\n📈 PERFORMANCE COMPARISON:")
    print("-" * 80)
    print(f"{'Category':<35} {'Original':<12} {'Improved':<12} {'Change':<12}")
    print("-" * 80)
    
    total_original_docs = 0
    total_original_successful = 0
    total_improved_docs = 0
    total_improved_successful = 0
    
    for comp in comparison_results:
        if comp['comparison_available']:
            original_rate = comp['original_success_rate']
            improved_rate = comp['improved_success_rate']
            change = comp['improvement']
            
            # Add to totals
            total_original_docs += comp.get('original_total', 0)
            total_original_successful += comp.get('original_successful', 0)
            total_improved_docs += comp.get('improved_total', 0)
            total_improved_successful += comp.get('improved_successful', 0)
            
            change_emoji = "📈" if comp['improvement_numeric'] > 0 else "📊" if comp['improvement_numeric'] == 0 else "📉"
            print(f"{comp['category']:<35} {original_rate:<12} {improved_rate:<12} {change_emoji} {change:<9}")
        else:
            print(f"{comp['category']:<35} {'N/A':<12} {'N/A':<12} {'N/A':<12}")
    
    print("-" * 80)
    
    # Calculate overall improvement
    if total_original_docs > 0 and total_improved_docs > 0:
        overall_original_rate = total_original_successful / total_original_docs * 100
        overall_improved_rate = total_improved_successful / total_improved_docs * 100
        overall_improvement = overall_improved_rate - overall_original_rate
        
        print(f"{'OVERALL PERFORMANCE':<35} {overall_original_rate:.1f}%{'':<7} {overall_improved_rate:.1f}%{'':<7} {overall_improvement:+.1f}%")
        print(f"{'DOCUMENT TOTALS':<35} {total_original_successful}/{total_original_docs}{'':<5} {total_improved_successful}/{total_improved_docs}{'':<5}")
    
    # Detailed Results
    print(f"\n📋 DETAILED CATEGORY RESULTS:")
    print("-" * 50)
    for comp in comparison_results:
        if comp['comparison_available']:
            print(f"\n{comp['category']}:")
            print(f"  📄 Documents: {comp['improved_total']}")
            print(f"  📈 Original: {comp['original_successful']}/{comp['original_total']} ({comp['original_success_rate']})")
            print(f"  🔧 Improved: {comp['improved_successful']}/{comp['improved_total']} ({comp['improved_success_rate']})")
            print(f"  📊 Change: {comp['improvement']}")
    
    # Save comprehensive summary
    master_summary = {
        'execution_timestamp': datetime.now().isoformat(),
        'execution_results': execution_results,
        'comparison_results': comparison_results,
        'overall_stats': {
            'total_original_documents': total_original_docs,
            'total_original_successful': total_original_successful,
            'total_improved_documents': total_improved_docs,
            'total_improved_successful': total_improved_successful,
            'overall_original_rate': f"{overall_original_rate:.1f}%" if total_original_docs > 0 else "N/A",
            'overall_improved_rate': f"{overall_improved_rate:.1f}%" if total_improved_docs > 0 else "N/A",
            'overall_improvement': f"{overall_improvement:+.1f}%" if total_original_docs > 0 and total_improved_docs > 0 else "N/A"
        }
    }
    
    summary_file = os.path.join(base_output_dir, 'master_improved_extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(master_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Master summary saved to: {summary_file}")
    print(f"\n✅ Master extraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
