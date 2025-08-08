#!/usr/bin/env python3
"""
Legacy Dotted TOC Format Competency Extractor
Specialized for documents with dotted table of contents (4 documents)

Strategy: Dotted TOC Parsing + Page Range Extraction
Reasoning: These documents have unique dotted TOC format that requires special parsing.
Extract page numbers from dotted lines, then navigate to competency sections.
"""

import PyPDF2
import re
import os
import json
from pathlib import Path

class LegacyDottedTOCExtractor:
    def __init__(self):
        self.dotted_competency_patterns = [
            r"COMPETENC.*?\.{3,}.*?(\d+)",
            r"LEARNING.*?COMPETENC.*?\.{3,}.*?(\d+)",
            r"PROFESSIONAL.*?COMPETENC.*?\.{3,}.*?(\d+)",
            r"OUTCOMES.*?COMPETENC.*?\.{3,}.*?(\d+)"
        ]
        
        self.canmeds_roles = [
            "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR", 
            "MANAGER", "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL"
        ]
        
        self.section_end_patterns = [
            r"TEACHING.*?LEARNING.*?\.{3,}.*?(\d+)",
            r"ASSESSMENT.*?\.{3,}.*?(\d+)",
            r"EVALUATION.*?\.{3,}.*?(\d+)"
        ]
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF with page tracking."""
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
    
    def parse_dotted_toc(self, pages_text):
        """
        Parse the dotted table of contents to find competency section pages.
        Strategy: Look for dotted lines with competency keywords and extract page numbers.
        """
        toc_entries = []
        
        # Check first 15 pages for dotted TOC
        for page_info in pages_text[:15]:
            text = page_info['text']
            lines = text.split('\n')
            
            for line in lines:
                line_clean = line.strip()
                
                # Skip empty lines or lines without dots
                if not line_clean or '.' not in line_clean:
                    continue
                
                # Look for competency-related dotted entries
                for pattern in self.dotted_competency_patterns:
                    match = re.search(pattern, line_clean, re.IGNORECASE)
                    if match:
                        page_num = int(match.group(1))
                        toc_entries.append({
                            'type': 'competency_start',
                            'page': page_num,
                            'text': line_clean,
                            'source_page': page_info['page_num']
                        })
                        print(f"Found competency section in dotted TOC: Page {page_num} - {line_clean[:50]}...")
                        break
                
                # Look for section end markers
                for pattern in self.section_end_patterns:
                    match = re.search(pattern, line_clean, re.IGNORECASE)
                    if match:
                        page_num = int(match.group(1))
                        toc_entries.append({
                            'type': 'section_end',
                            'page': page_num,
                            'text': line_clean,
                            'source_page': page_info['page_num']
                        })
                        print(f"Found potential section end in dotted TOC: Page {page_num} - {line_clean[:50]}...")
                        break
        
        return toc_entries
    
    def determine_competency_page_range(self, toc_entries):
        """
        Determine the page range for competency sections from TOC entries.
        """
        competency_starts = [entry for entry in toc_entries if entry['type'] == 'competency_start']
        section_ends = [entry for entry in toc_entries if entry['type'] == 'section_end']
        
        if not competency_starts:
            return None, None
        
        # Use the first competency section found
        start_page = competency_starts[0]['page']
        
        # Find the nearest section end after the competency start
        end_page = None
        for end_entry in section_ends:
            if end_entry['page'] > start_page:
                end_page = end_entry['page']
                break
        
        # If no explicit end found, estimate based on typical section length
        if not end_page:
            # Look for any subsequent major section
            all_pages = [entry['page'] for entry in toc_entries if entry['page'] > start_page]
            if all_pages:
                end_page = min(all_pages)
            else:
                end_page = start_page + 30  # Default estimate
        
        return start_page, end_page
    
    def validate_competency_pages(self, pages_text, start_page, end_page):
        """
        Validate that the identified pages actually contain competency content.
        """
        if not start_page or not end_page:
            return False, "No page range identified"
        
        # Check pages in the range for CanMEDS content
        canmeds_pages = 0
        total_pages_checked = 0
        
        for page_info in pages_text[start_page-1:min(start_page+10, end_page)]:
            text = page_info['text'].upper()
            total_pages_checked += 1
            
            # Count CanMEDS roles in this page
            canmeds_in_page = sum(1 for role in self.canmeds_roles if role in text)
            if canmeds_in_page > 0:
                canmeds_pages += 1
        
        # At least 30% of pages should contain CanMEDS content
        if total_pages_checked > 0 and (canmeds_pages / total_pages_checked) >= 0.3:
            return True, f"Valid competency range ({canmeds_pages}/{total_pages_checked} pages with CanMEDS content)"
        else:
            return False, f"Insufficient competency content ({canmeds_pages}/{total_pages_checked} pages with CanMEDS content)"
    
    def extract_competency_content(self, pages_text, start_page, end_page):
        """Extract competency content from the identified page range."""
        if not start_page or not end_page:
            return ""
        
        competency_content = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text']
            competency_content.append(f"--- Page {page_info['page_num']} ---\n{text}\n")
        
        return "\n".join(competency_content)
    
    def validate_extraction(self, content):
        """
        Validate that extracted content contains expected Legacy Dotted TOC elements.
        """
        if not content:
            return False, "No content extracted"
        
        content_upper = content.upper()
        
        # Count CanMEDS roles present
        canmeds_roles_found = [role for role in self.canmeds_roles if role in content_upper]
        
        # Check for competency-related terms
        has_competency_terms = any(term in content_upper for term in [
            "COMPETENC", "LEARNING OBJECTIVE", "PROFESSIONAL"
        ])
        
        # Check for legacy format indicators
        has_legacy_indicators = any(term in content_upper for term in [
            "ROTATION", "OBJECTIVES", "TRAINING"
        ])
        
        validation_score = len(canmeds_roles_found)
        
        if validation_score >= 3 and has_competency_terms:
            return True, f"Valid legacy format ({len(canmeds_roles_found)}/7 CanMEDS roles found)"
        else:
            return False, f"Insufficient legacy content ({len(canmeds_roles_found)}/7 CanMEDS roles found)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function for Legacy Dotted TOC format."""
        print(f"\n=== Processing Legacy Dotted TOC Document: {os.path.basename(pdf_path)} ===")
        
        # Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Parse dotted TOC
        toc_entries = self.parse_dotted_toc(pages_text)
        
        if not toc_entries:
            print("❌ Could not parse dotted TOC")
            return None
        
        print(f"📋 Found {len(toc_entries)} TOC entries")
        
        # Determine competency page range
        start_page, end_page = self.determine_competency_page_range(toc_entries)
        
        if not start_page:
            print("❌ Could not determine competency page range")
            return None
        
        print(f"📍 Competency section (from TOC): Pages {start_page}-{end_page}")
        
        # Validate the page range contains competency content
        is_valid_range, range_msg = self.validate_competency_pages(pages_text, start_page, end_page)
        print(f"🔍 Page range validation: {range_msg}")
        
        # Extract competency content
        content = self.extract_competency_content(pages_text, start_page, end_page)
        
        # Validate extraction
        is_valid, validation_msg = self.validate_extraction(content)
        print(f"🔍 Content validation: {validation_msg}")
        
        overall_valid = is_valid_range and is_valid
        
        if not overall_valid:
            print("⚠️  Extraction validation failed")
        
        # Save extracted content
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Document: {os.path.basename(pdf_path)}\n")
                f.write(f"Extraction Method: Legacy Dotted TOC Parsing\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"TOC Entries Found: {len(toc_entries)}\n")
                f.write(f"Page Range Validation: {range_msg}\n")
                f.write(f"Content Validation: {validation_msg}\n")
                f.write("="*80 + "\n\n")
                
                # Include TOC entries for reference
                f.write("DOTTED TOC ENTRIES FOUND:\n")
                f.write("-" * 40 + "\n")
                for entry in toc_entries:
                    f.write(f"{entry['type'].upper()}: Page {entry['page']} - {entry['text']}\n")
                f.write("\n" + "="*80 + "\n\n")
                
                f.write("EXTRACTED COMPETENCY CONTENT:\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            print(f"✅ Competencies extracted to: {output_file}")
            
            return {
                'pdf_path': pdf_path,
                'output_file': output_file,
                'pages_extracted': f"{start_page}-{end_page}",
                'toc_entries_found': len(toc_entries),
                'page_range_validation': range_msg,
                'content_validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': overall_valid
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    """Process all documents in Legacy Dotted TOC category."""
    
    # Paths
    category_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Document_Categories/04_Legacy_Dotted_TOC_Format"
    output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/extracted_competencies/04_Legacy_Dotted_TOC"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize extractor
    extractor = LegacyDottedTOCExtractor()
    
    # Find all PDF files in category
    pdf_files = []
    for file in os.listdir(category_dir):
        if file.endswith('.pdf'):
            pdf_files.append(os.path.join(category_dir, file))
    
    if not pdf_files:
        print("No PDF files found in category directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each document
    results = []
    successful_extractions = 0
    
    for pdf_path in pdf_files:
        result = extractor.extract_competencies(pdf_path, output_dir)
        if result:
            results.append(result)
            if result['extraction_successful']:
                successful_extractions += 1
    
    # Save summary
    summary = {
        'category': 'Legacy Dotted TOC Format',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{successful_extractions/len(pdf_files)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 SUMMARY")
    print(f"Category: Legacy Dotted TOC Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
