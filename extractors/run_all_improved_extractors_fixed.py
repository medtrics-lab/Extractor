#!/usr/bin/env python3
"""
Master Improved Extraction Runner - Fixed Version
Runs all improved competency extractors with proper CLI arguments and comprehensive error handling

This script executes all improved extraction methods with proper directory handling
and provides comprehensive analysis with better error recovery.
"""

import os
import json
import subprocess
import sys
import argparse
from datetime import datetime
from pathlib import Path

def ensure_dependencies():
    """Check and install required dependencies if missing."""
    missing_deps = []
    
    try:
        import pdfplumber
    except ImportError:
        missing_deps.append('pdfplumber')
    
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append('PyPDF2')
    
    if missing_deps:
        print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Installing missing dependencies...")
        try:
            for dep in missing_deps:
                subprocess.run([sys.executable, '-m', 'pip', 'install', dep], 
                             check=True, capture_output=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    return True

def run_extractor(script_path, input_dir, output_dir, description):
    """Run an extraction script with proper CLI arguments."""
    print(f"\n{'='*80}")
    print(f"RUNNING: {description}")
    print(f"Script: {os.path.basename(script_path)}")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"{'='*80}")
    
    try:
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Build command with proper arguments
        cmd = [
            sys.executable, script_path,
            '--input-dir', input_dir,
            '--output-dir', output_dir
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Extraction completed successfully")
            return True, result.stdout, result.stderr
        else:
            print(f"❌ Extraction failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False, result.stdout, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"❌ Extraction timed out after 5 minutes")
        return False, "", "Timeout after 300 seconds"
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
    
    original_rate = original_summary.get('successful_extractions', 0) / max(original_summary.get('total_documents', 1), 1) * 100
    improved_rate = improved_summary.get('successful_extractions', 0) / max(improved_summary.get('total_documents', 1), 1) * 100
    
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

def validate_paths(base_input_dir, base_output_dir):
    """Validate that required paths exist."""
    if not os.path.exists(base_input_dir):
        print(f"❌ Input directory not found: {base_input_dir}")
        return False
    
    try:
        Path(base_output_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"❌ Cannot create output directory {base_output_dir}: {e}")
        return False
    
    return True

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run all improved extractors with proper CLI arguments")
    parser.add_argument("--input-base", default="/Users/charlesnorris/Downloads/SaudiSCFHS/Document_Categories",
                       help="Base directory containing document category subdirectories")
    parser.add_argument("--output-base", default="/Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies",
                       help="Base directory for extraction outputs")
    parser.add_argument("--check-deps", action="store_true", help="Check and install dependencies if needed")
    
    args = parser.parse_args()
    
    print("🚀 MASTER IMPROVED EXTRACTION RUNNER (FIXED)")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Input Base: {args.input_base}")
    print(f"Output Base: {args.output_base}")
    
    # Check dependencies if requested
    if args.check_deps:
        if not ensure_dependencies():
            print("❌ Dependency installation failed. Continuing anyway...")
    
    # Validate base paths
    if not validate_paths(args.input_base, args.output_base):
        return 1
    
    extractors_dir = Path(__file__).parent
    
    # Define all improved extractors with correct directory mappings
    extractors = [
        {
            'script': 'extract_advanced_key_enabling_improved.py',
            'description': 'Advanced Key & Enabling (Improved)',
            'category': '01_Advanced_Key_Enabling',
            'input_subdir': '01_Advanced_Key_and_Enabling_Format',
            'output_subdir': '01_Advanced_Key_and_Enabling_Format',
            'original_summary': 'extraction_summary.json',
            'improved_summary': 'extraction_summary_improved.json'
        },
        {
            'script': 'extract_standard_canmeds_improved.py',
            'description': 'Standard CanMEDS (Improved)',
            'category': '02_Standard_CanMEDS',
            'input_subdir': '02_Standard_CanMEDS_Format',
            'output_subdir': '02_Standard_CanMEDS_Format',
            'original_summary': 'extraction_summary.json',
            'improved_summary': 'extraction_summary_improved.json'
        },
        {
            'script': 'extract_basic_role_based_improved.py',
            'description': 'Basic Role-Based (Improved)',
            'category': '03_Basic_Role_Based',
            'input_subdir': '03_Basic_Role_Based_Format',
            'output_subdir': '03_Basic_Role_Based_Format',
            'original_summary': 'extraction_summary.json',
            'improved_summary': 'extraction_summary_improved.json'
        },
        {
            'script': 'extract_legacy_dotted_toc_improved.py',
            'description': 'Legacy Dotted TOC (Improved)',
            'category': '04_Legacy_Dotted_TOC',
            'input_subdir': '04_Legacy_Dotted_TOC_Format',
            'output_subdir': '04_Legacy_Dotted_TOC',
            'original_summary': 'extraction_summary.json',
            'improved_summary': 'extraction_summary_improved.json'
        },
        {
            'script': 'extract_canmeds_without_levels_improved.py',
            'description': 'CanMEDS Without Levels (Improved)',
            'category': '05_CanMEDS_Without_Levels',
            'input_subdir': '05_CanMEDS_Without_Levels',
            'output_subdir': '05_CanMEDS_Without_Levels',
            'original_summary': 'extraction_summary.json',
            'improved_summary': 'extraction_summary_improved.json'
        }
    ]
    
    # Track execution results
    execution_results = []
    comparison_results = []
    
    # Run all extractors
    for extractor in extractors:
        script_path = extractors_dir / extractor['script']
        input_dir = os.path.join(args.input_base, extractor['input_subdir'])
        output_dir = os.path.join(args.output_base, extractor['output_subdir'])
        
        # Check if script exists
        if not script_path.exists():
            print(f"⚠️  Script not found: {script_path}")
            execution_results.append({
                'extractor': extractor['description'],
                'status': 'SCRIPT_NOT_FOUND',
                'success': False,
                'input_dir': input_dir,
                'output_dir': output_dir
            })
            continue
        
        # Check if input directory exists
        if not os.path.exists(input_dir):
            print(f"⚠️  Input directory not found: {input_dir}")
            execution_results.append({
                'extractor': extractor['description'],
                'status': 'INPUT_DIR_NOT_FOUND',
                'success': False,
                'input_dir': input_dir,
                'output_dir': output_dir
            })
            continue
        
        # Run the extractor
        success, stdout, stderr = run_extractor(
            str(script_path), input_dir, output_dir, extractor['description']
        )
        
        execution_results.append({
            'extractor': extractor['description'],
            'status': 'SUCCESS' if success else 'FAILED',
            'success': success,
            'input_dir': input_dir,
            'output_dir': output_dir,
            'stdout_lines': len(stdout.split('\n')) if stdout else 0,
            'stderr_lines': len(stderr.split('\n')) if stderr else 0
        })
        
        # Load and compare summaries
        original_path = os.path.join(output_dir, extractor['original_summary'])
        improved_path = os.path.join(output_dir, extractor['improved_summary'])
        
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
    print(f"Execution Success Rate: {successful_executions/max(total_executed,1)*100:.1f}%")
    
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
    
    # Save comprehensive summary
    master_summary = {
        'execution_timestamp': datetime.now().isoformat(),
        'input_base_dir': args.input_base,
        'output_base_dir': args.output_base,
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
    
    summary_file = os.path.join(args.output_base, 'master_improved_extraction_summary_fixed.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(master_summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Master summary saved to: {summary_file}")
    print(f"\n✅ Master extraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return 0 if successful_executions == total_executed else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
