#!/usr/bin/env python3
"""
Extraction Quality Testing and Validation Utility
Tests individual extractors with detailed debugging and quality metrics

This utility helps validate improvements and debug extraction issues.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    try:
        import pdfplumber
    except ImportError:
        missing.append('pdfplumber')
    
    try:
        import PyPDF2
    except ImportError:
        missing.append('PyPDF2')
    
    return missing

def run_single_extractor_test(script_path, input_dir, output_dir, max_files=3):
    """Run a single extractor on a limited set of files for testing."""
    print(f"\n{'='*60}")
    print(f"TESTING: {os.path.basename(script_path)}")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Max files: {max_files}")
    print(f"{'='*60}")
    
    # Check if directories exist
    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}")
        return None
    
    # Get PDF files in input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f"❌ No PDF files found in {input_dir}")
        return None
    
    # Limit to first N files for testing
    test_files = pdf_files[:max_files]
    print(f"Found {len(pdf_files)} PDF files, testing with {len(test_files)}: {test_files}")
    
    # Create a temporary input directory with just the test files
    test_input_dir = output_dir + "_test_input"
    Path(test_input_dir).mkdir(parents=True, exist_ok=True)
    
    # Copy test files to temporary directory
    import shutil
    for test_file in test_files:
        src_path = os.path.join(input_dir, test_file)
        dst_path = os.path.join(test_input_dir, test_file)
        shutil.copy2(src_path, dst_path)
    
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        # Run the extractor
        cmd = [
            sys.executable, script_path,
            '--input-dir', test_input_dir,
            '--output-dir', output_dir
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Clean up temporary input directory
        shutil.rmtree(test_input_dir)
        
        if result.returncode == 0:
            print("✅ Extraction completed successfully")
            
            # Check for output files
            output_files = list(Path(output_dir).glob("*"))
            print(f"Generated {len(output_files)} output files")
            
            # Load summary if available
            summary_files = [f for f in output_files if 'summary' in f.name.lower() and f.suffix == '.json']
            if summary_files:
                with open(summary_files[0], 'r') as f:
                    summary = json.load(f)
                    success_rate = summary.get('successful_extractions', 0) / summary.get('total_documents', 1) * 100
                    print(f"Success rate: {success_rate:.1f}%")
            
            return {
                'success': True,
                'output_files': len(output_files),
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            print(f"❌ Extraction failed with return code {result.returncode}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return {
                'success': False,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
    except subprocess.TimeoutExpired:
        print("❌ Extraction timed out after 2 minutes")
        shutil.rmtree(test_input_dir)
        return {'success': False, 'error': 'timeout'}
    except Exception as e:
        print(f"❌ Error running extractor: {e}")
        if os.path.exists(test_input_dir):
            shutil.rmtree(test_input_dir)
        return {'success': False, 'error': str(e)}

def analyze_extraction_outputs(output_dir):
    """Analyze the quality of extraction outputs."""
    output_path = Path(output_dir)
    if not output_path.exists():
        print(f"Output directory not found: {output_dir}")
        return
    
    print(f"\n📊 ANALYZING OUTPUTS IN: {output_dir}")
    print("-" * 50)
    
    txt_files = list(output_path.glob("*.txt"))
    json_files = list(output_path.glob("*.json"))
    
    print(f"Text files: {len(txt_files)}")
    print(f"JSON files: {len(json_files)}")
    
    if txt_files:
        print("\nText file analysis:")
        for txt_file in txt_files[:3]:  # Analyze first 3 files
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"  {txt_file.name}: {len(content)} chars, {len(lines)} lines")
                
                # Quick quality indicators
                canmeds_roles = ['MEDICAL EXPERT', 'COMMUNICATOR', 'COLLABORATOR', 'LEADER', 'HEALTH ADVOCATE', 'SCHOLAR', 'PROFESSIONAL']
                role_count = sum(1 for role in canmeds_roles if role in content.upper())
                numbered_items = len([l for l in lines if l.strip() and l.strip()[0].isdigit() and '.' in l[:5]])
                
                print(f"    CanMEDS roles found: {role_count}/7")
                print(f"    Numbered items: {numbered_items}")

def main():
    parser = argparse.ArgumentParser(description="Test and validate extraction improvements")
    parser.add_argument("--base-dir", default="/Users/charlesnorris/Downloads/SaudiSCFHS",
                       help="Base directory containing extractors and documents")
    parser.add_argument("--max-files", type=int, default=3,
                       help="Maximum number of files to test per extractor")
    parser.add_argument("--extractor", help="Specific extractor script to test (optional)")
    parser.add_argument("--check-deps", action="store_true", help="Check dependencies")
    
    args = parser.parse_args()
    
    print("🧪 EXTRACTION QUALITY TESTING UTILITY")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies
    if args.check_deps:
        missing = check_dependencies()
        if missing:
            print(f"⚠️  Missing dependencies: {', '.join(missing)}")
            print("Install with: pip install " + " ".join(missing))
        else:
            print("✅ All dependencies are installed")
    
    extractors_dir = os.path.join(args.base_dir, "extractors")
    document_categories = os.path.join(args.base_dir, "Document_Categories")
    extracted_competencies = os.path.join(args.base_dir, "Extracted_Competencies")
    
    # Define test configurations
    test_configs = [
        {
            'script': 'extract_standard_canmeds_improved.py',
            'input_subdir': '02_Standard_CanMEDS_Format',
            'output_subdir': '02_Standard_CanMEDS_Format_TEST',
        },
        {
            'script': 'extract_basic_role_based_improved.py',
            'input_subdir': '03_Basic_Role_Based_Format',
            'output_subdir': '03_Basic_Role_Based_Format_TEST',
        },
        {
            'script': 'extract_advanced_key_enabling_improved.py',
            'input_subdir': '01_Advanced_Key_and_Enabling_Format',
            'output_subdir': '01_Advanced_Key_and_Enabling_Format_TEST',
        }
    ]
    
    # Filter to specific extractor if requested
    if args.extractor:
        test_configs = [c for c in test_configs if args.extractor in c['script']]
        if not test_configs:
            print(f"❌ Extractor not found: {args.extractor}")
            return
    
    results = []
    
    for config in test_configs:
        script_path = os.path.join(extractors_dir, config['script'])
        input_dir = os.path.join(document_categories, config['input_subdir'])
        output_dir = os.path.join(extracted_competencies, config['output_subdir'])
        
        if not os.path.exists(script_path):
            print(f"⚠️  Script not found: {script_path}")
            continue
            
        result = run_single_extractor_test(script_path, input_dir, output_dir, args.max_files)
        if result:
            result['config'] = config
            results.append(result)
            
            # Analyze outputs if successful
            if result['success']:
                analyze_extraction_outputs(output_dir)
    
    # Summary
    print(f"\n🎯 TEST SUMMARY")
    print("-" * 30)
    successful_tests = sum(1 for r in results if r['success'])
    print(f"Tests run: {len(results)}")
    print(f"Successful: {successful_tests}")
    print(f"Success rate: {successful_tests/max(len(results),1)*100:.1f}%")
    
    if results:
        print("\nDetailed results:")
        for result in results:
            status = "✅" if result['success'] else "❌"
            extractor_name = result['config']['script']
            print(f"  {status} {extractor_name}")
            if not result['success'] and 'error' in result:
                print(f"      Error: {result['error']}")

if __name__ == "__main__":
    main()
