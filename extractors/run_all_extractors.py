#!/usr/bin/env python3
"""
Master Competency Extraction Script
Runs all category-specific extractors for SCFHS documents

This script coordinates the execution of all specialized extractors,
each tailored for specific document categories.
"""

import os
import subprocess
import sys
import json
from datetime import datetime

def run_extractor(script_path, category_name):
    """Run a specific extractor script and capture results."""
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {category_name}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, 
                              text=True, 
                              timeout=1800)  # 30 minute timeout
        
        if result.returncode == 0:
            print(f"✅ {category_name} extraction completed successfully")
            return {
                'category': category_name,
                'status': 'success',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        else:
            print(f"❌ {category_name} extraction failed")
            print(f"Error output: {result.stderr}")
            return {
                'category': category_name,
                'status': 'failed',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
    
    except subprocess.TimeoutExpired:
        print(f"⏰ {category_name} extraction timed out")
        return {
            'category': category_name,
            'status': 'timeout',
            'stdout': '',
            'stderr': 'Process timed out after 30 minutes'
        }
    
    except Exception as e:
        print(f"❌ Error running {category_name} extractor: {e}")
        return {
            'category': category_name,
            'status': 'error',
            'stdout': '',
            'stderr': str(e)
        }

def create_remaining_extractors():
    """Create the remaining category extractors."""
    
    # Create extractors directory if it doesn't exist
    extractors_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/extractors"
    os.makedirs(extractors_dir, exist_ok=True)
    
    # Script for CanMEDS Without Levels (7 docs)
    canmeds_without_levels_script = """#!/usr/bin/env python3
'''
CanMEDS Without Levels Format Competency Extractor
Specialized for CanMEDS documents without competency progression levels (7 documents)

Strategy: CanMEDS Role Detection + Simplified Validation
Reasoning: These have CanMEDS framework but no progressive levels (R1-R4, F1-F2).
Focus on finding CanMEDS roles with simpler competency structure.
'''

import PyPDF2
import re
import os
import json

class CanMEDSWithoutLevelsExtractor:
    def __init__(self):
        self.section_headers = [
            "OUTCOMES AND COMPETENCIES",
            "COMPETENCIES AND OUTCOMES",
            "LEARNING AND COMPETENCIES"
        ]
        
        self.canmeds_roles = [
            "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR", 
            "MANAGER", "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL"
        ]
        
        self.section_end_markers = [
            "LEARNING OPPORTUNITIES",
            "TEACHING AND LEARNING", 
            "ASSESSMENT",
            "PROGRAM ROTATIONS"
        ]
    
    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pages_text = []
                
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    pages_text.append({
                        'page_num': page_num + 1,
                        'text': text
                    })
                
                return pages_text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return None
    
    def find_canmeds_sections(self, pages_text):
        start_page = None
        end_page = None
        
        # Find start by looking for CanMEDS roles density
        for page_info in pages_text:
            text = page_info['text'].upper()
            
            # Check if this page has multiple CanMEDS roles
            canmeds_count = sum(1 for role in self.canmeds_roles if role in text)
            
            # Also check for section headers
            has_section_header = any(header in text for header in self.section_headers)
            
            if canmeds_count >= 3 or (canmeds_count >= 2 and has_section_header):
                start_page = page_info['page_num']
                print(f"Found CanMEDS section at page {start_page} ({canmeds_count} roles)")
                break
        
        if not start_page:
            return None, None
        
        # Find end page
        for page_info in pages_text[start_page:]:
            text = page_info['text'].upper()
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    end_page = page_info['page_num']
                    break
            
            if end_page:
                break
        
        if not end_page:
            end_page = min(start_page + 20, len(pages_text))
        
        return start_page, end_page
    
    def extract_competencies(self, pdf_path, output_dir):
        print(f"\\n=== Processing CanMEDS Without Levels Document: {os.path.basename(pdf_path)} ===")
        
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        start_page, end_page = self.find_canmeds_sections(pages_text)
        
        if not start_page:
            print("❌ Could not find CanMEDS sections")
            return None
        
        print(f"📍 CanMEDS section: Pages {start_page}-{end_page}")
        
        # Extract content
        content = []
        for page_info in pages_text[start_page-1:end_page]:
            content.append(f"--- Page {page_info['page_num']} ---\\n{page_info['text']}\\n")
        
        content_text = "\\n".join(content)
        
        # Validate
        content_upper = content_text.upper()
        canmeds_found = [role for role in self.canmeds_roles if role in content_upper]
        
        is_valid = len(canmeds_found) >= 4
        validation_msg = f"CanMEDS without levels ({len(canmeds_found)}/7 roles found)"
        
        # Save
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Document: {os.path.basename(pdf_path)}\\n")
            f.write(f"Extraction Method: CanMEDS Without Levels Detection\\n")
            f.write(f"Pages Extracted: {start_page}-{end_page}\\n")
            f.write(f"Validation: {validation_msg}\\n")
            f.write("="*80 + "\\n\\n")
            f.write(content_text)
        
        return {
            'pdf_path': pdf_path,
            'output_file': output_file,
            'pages_extracted': f"{start_page}-{end_page}",
            'validation': validation_msg,
            'extraction_successful': is_valid
        }

def main():
    category_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Document_Categories/05_CanMEDS_Without_Levels"
    output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/extracted_competencies/05_CanMEDS_Without_Levels"
    
    os.makedirs(output_dir, exist_ok=True)
    extractor = CanMEDSWithoutLevelsExtractor()
    
    pdf_files = [os.path.join(category_dir, f) for f in os.listdir(category_dir) if f.endswith('.pdf')]
    
    results = []
    successful = 0
    
    for pdf_path in pdf_files:
        result = extractor.extract_competencies(pdf_path, output_dir)
        if result:
            results.append(result)
            if result['extraction_successful']:
                successful += 1
    
    summary = {
        'category': 'CanMEDS Without Levels',
        'total_documents': len(pdf_files),
        'successful_extractions': successful,
        'results': results
    }
    
    with open(os.path.join(output_dir, 'extraction_summary.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\\n🎯 SUMMARY: {successful}/{len(pdf_files)} successful extractions")

if __name__ == "__main__":
    main()
"""
    
    # Write the CanMEDS Without Levels script
    with open(os.path.join(extractors_dir, "extract_canmeds_without_levels.py"), 'w') as f:
        f.write(canmeds_without_levels_script)
    
    # Make it executable
    os.chmod(os.path.join(extractors_dir, "extract_canmeds_without_levels.py"), 0o755)
    
    print("✅ Created remaining category extractors")

def main():
    """Main execution function."""
    
    print("🎯 SCFHS COMPETENCY EXTRACTION MASTER SCRIPT")
    print("=" * 60)
    print(f"Starting extraction at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create remaining extractors first
    create_remaining_extractors()
    
    # Define category mappings for extraction
    category_mappings = {
        '01_Advanced_Key_and_Enabling_Format': {
            'script': 'extract_advanced_key_enabling.py',
            'name': 'Advanced Key & Enabling Format',
            'strategy': 'Content Pattern Analysis + Key Phrase Detection'
        },
        '02_Standard_CanMEDS_Format': {
            'script': 'extract_standard_canmeds.py', 
            'name': 'Standard CanMEDS Format',
            'strategy': 'Document Structure Analysis + TOC Parsing'
        },
        '03_Basic_Role_Based_Format': {
            'script': 'extract_basic_role_based.py',
            'name': 'Basic Role-Based Format', 
            'strategy': 'Role Pattern Detection + Competency Matrix Analysis'
        },
        '04_Legacy_Dotted_TOC_Format': {
            'script': 'extract_legacy_dotted_toc.py',
            'name': 'Legacy Dotted TOC Format',
            'strategy': 'Dotted TOC Parsing + Page Range Extraction'
        },
        '05_CanMEDS_Without_Levels': {
            'script': 'extract_canmeds_without_levels.py', 
            'name': 'CanMEDS Without Levels',
            'strategy': 'CanMEDS Role Detection + Simplified Validation'
        }
    }
    
    # Process each category
    results = []
    successful_categories = 0
    total_documents_processed = 0
    total_successful_extractions = 0
    
    for category_folder, extractor_info in category_mappings.items():
        print(f"\n{'='*60}")
        print(f"🚀 PROCESSING CATEGORY: {extractor_info['name']}")
        print(f"📋 Strategy: {extractor_info['strategy']}")
        print(f"{'='*60}")
        
        # Run category-specific extractor 
        script_path = f"/Users/charlesnorris/Downloads/SaudiSCFHS/extractors/{extractor_info['script']}"
        result = run_extractor(script_path, f"{extractor_info['name']}")
        results.append(result)
        
        if result['status'] == 'success':
            successful_categories += 1
            # Extract success metrics from output if available
            if 'successful extractions' in result.get('stdout', '').lower():
                # Parse extraction results from stdout
                lines = result['stdout'].split('\n')
                for line in lines:
                    if 'Documents Processed:' in line:
                        try:
                            total_documents_processed += int(line.split(':')[1].strip())
                        except:
                            pass
                    elif 'Successful Extractions:' in line:
                        try:
                            total_successful_extractions += int(line.split(':')[1].strip()) 
                        except:
                            pass
    
    # Create master summary in Extracted_Competencies folder
    output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies"
    os.makedirs(output_dir, exist_ok=True)
    
    master_summary = {
        'extraction_date': datetime.now().isoformat(),
        'total_categories_processed': len(category_mappings),
        'successful_categories': successful_categories,
        'category_success_rate': f"{successful_categories/len(category_mappings)*100:.1f}%",
        'total_documents_processed': total_documents_processed,
        'total_successful_extractions': total_successful_extractions,
        'overall_extraction_rate': f"{total_successful_extractions/max(1,total_documents_processed)*100:.1f}%" if total_documents_processed > 0 else "0%",
        'category_results': results
    }
    
    summary_file = os.path.join(output_dir, 'MASTER_EXTRACTION_SUMMARY.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(master_summary, f, indent=2, ensure_ascii=False)
    
    # Final summary
    print(f"\n{'='*60}")
    print("🎯 EXTRACTION COMPLETE!")
    print(f"{'='*60}")
    print(f"📊 Categories Processed: {len(category_mappings)}")
    print(f"✅ Successful Categories: {successful_categories}")
    print(f"❌ Failed Categories: {len(category_mappings) - successful_categories}")
    print(f"📈 Category Success Rate: {successful_categories/len(category_mappings)*100:.1f}%")
    if total_documents_processed > 0:
        print(f"📄 Total Documents Processed: {total_documents_processed}")
        print(f"🎯 Total Successful Extractions: {total_successful_extractions}")
        print(f"📊 Overall Extraction Rate: {total_successful_extractions/total_documents_processed*100:.1f}%")
    print(f"💾 Master summary: {summary_file}")
    
    # Show individual results
    print(f"\n📋 CATEGORY RESULTS:")
    for result in results:
        status_emoji = "✅" if result['status'] == 'success' else "❌"
        print(f"{status_emoji} {result['category']}: {result['status']}")
    
    print(f"\n🎯 All competency extractions completed!")
    print(f"📁 Results saved in: /Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies/")
    print(f"🔍 Check individual category folders for extracted competency files")

if __name__ == "__main__":
    main()
