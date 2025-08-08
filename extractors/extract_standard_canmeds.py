#!/usr/bin/env python3
"""
Standard CanMEDS Format Competency Extractor
Specialized for standard CanMEDS implementation documents (67 documents - largest category)

Strategy: Document Structure Analysis + TOC Parsing
Reasoning: This is the most common format with consistent section numbering and TOC structure.
Focus on Roman numeral sections and CanMEDS role detection for reliable extraction.
"""

import PyPDF2
import re
import os
import json
from pathlib import Path

class StandardCanMEDSExtractor:
    def __init__(self):
        self.section_headers = [
            "LEARNING AND COMPETENCIES",
            "OUTCOMES AND COMPETENCIES",
            "LEARNING OUTCOMES AND COMPETENCIES",
            "PROFESSIONAL COMPETENCIES"
        ]
        
        self.canmeds_roles = [
            "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR", 
            "MANAGER", "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL"
        ]
        
        self.section_end_markers = [
            "CONTINUUM OF LEARNING",
            "ASSESSMENT AND EVALUATION",
            "TEACHING AND LEARNING", 
            "PROGRAM ROTATIONS",
            "CLINICAL ROTATIONS"
        ]
        
        # Roman numeral patterns for section identification
        self.roman_numeral_pattern = re.compile(r'^[IVXLC]+\.\s*', re.MULTILINE)
        
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
    
    def parse_table_of_contents(self, pages_text):
        """
        Extract TOC information to identify competency section location.
        Strategy: Look for section numbers and page references in early pages.
        """
        toc_info = {}
        
        # Check first 10 pages for TOC
        for page_info in pages_text[:10]:
            text = page_info['text']
            lines = text.split('\n')
            
            for line in lines:
                line_upper = line.upper().strip()
                
                # Look for competency section in TOC
                for header in self.section_headers:
                    if header in line_upper:
                        # Try to extract page number
                        page_match = re.search(r'(\d+)$', line.strip())
                        if page_match:
                            page_num = int(page_match.group(1))
                            toc_info['competency_start_page'] = page_num
                            toc_info['competency_header'] = header
                            print(f"Found competency section in TOC: '{header}' at page {page_num}")
                            break
                
                # Look for section end markers in TOC
                for end_marker in self.section_end_markers:
                    if end_marker in line_upper:
                        page_match = re.search(r'(\d+)$', line.strip())
                        if page_match:
                            page_num = int(page_match.group(1))
                            if 'competency_start_page' in toc_info and page_num > toc_info['competency_start_page']:
                                toc_info['competency_end_page'] = page_num
                                print(f"Found competency section end in TOC: '{end_marker}' at page {page_num}")
                                break
        
        return toc_info
    
    def find_competency_section_by_structure(self, pages_text):
        """
        Find competency section using document structure analysis.
        Strategy: Look for section headers and validate with CanMEDS roles.
        """
        start_page = None
        end_page = None
        
        # Find start page - be more flexible
        for page_info in pages_text:
            text = page_info['text'].upper()
            
            # Look for section headers
            for header in self.section_headers:
                if header in text:
                    # Validate by checking for CanMEDS roles in current or next few pages
                    validation_pages = pages_text[max(0, page_info['page_num']-1):page_info['page_num']+5]
                    
                    canmeds_count = 0
                    competency_terms = 0
                    for val_page in validation_pages:
                        val_text = val_page['text'].upper()
                        canmeds_count += sum(1 for role in self.canmeds_roles if role in val_text)
                        competency_terms += sum(1 for term in ["COMPETENC", "OBJECTIVE", "SKILL", "ABILITY"] if term in val_text)
                    
                    # More flexible validation - reduced threshold
                    if canmeds_count >= 2 or competency_terms >= 3:
                        start_page = page_info['page_num']
                        print(f"Found competency section start at page {start_page} with {canmeds_count} CanMEDS roles")
                        break
            
            if start_page:
                break
        
        if not start_page:
            return None, None
        
        # Find end page
        for page_info in pages_text[start_page:]:
            text = page_info['text'].upper()
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    end_page = page_info['page_num']
                    print(f"Found competency section end at page {end_page} with marker: {end_marker}")
                    break
            
            if end_page:
                break
        
        # If no clear end found, estimate based on content
        if not end_page:
            # Look for pages where CanMEDS content significantly decreases
            for i, page_info in enumerate(pages_text[start_page:start_page+20], start_page):
                text = page_info['text'].upper()
                
                canmeds_in_page = sum(1 for role in self.canmeds_roles if role in text)
                
                # If this page has no CanMEDS content and contains other section indicators
                if canmeds_in_page == 0 and any(term in text for term in ["ASSESSMENT", "TEACHING", "ROTATION"]):
                    end_page = page_info['page_num']
                    break
            
            # Default fallback
            if not end_page:
                end_page = min(start_page + 25, len(pages_text))
        
        return start_page, end_page
    
    def extract_competency_content(self, pages_text, start_page, end_page):
        """Extract competency content from identified page range."""
        if not start_page or not end_page:
            return ""
        
        competency_content = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text']
            
            # For Standard CanMEDS format, we want to start from the section header
            if page_info['page_num'] == start_page:
                # Find the actual start of competency content
                text_upper = text.upper()
                for header in self.section_headers:
                    if header in text_upper:
                        header_pos = text_upper.find(header)
                        text = text[header_pos:]
                        break
            
            competency_content.append(f"--- Page {page_info['page_num']} ---\n{text}\n")
        
        return "\n".join(competency_content)
    
    def validate_extraction(self, content):
        """
        Validate that extracted content contains expected Standard CanMEDS elements.
        """
        if not content:
            return False, "No content extracted"
        
        content_upper = content.upper()
        
        # Count CanMEDS roles present
        canmeds_roles_found = [role for role in self.canmeds_roles if role in content_upper]
        
        # Check for other indicators
        has_competency_header = any(header in content_upper for header in self.section_headers)
        has_learning_objectives = "LEARNING OBJECTIVE" in content_upper
        has_competency_levels = any(level in content_upper for level in ["R1", "R2", "R3", "R4", "F1", "F2"])
        
        validation_score = len(canmeds_roles_found)
        
        if validation_score >= 4:  # At least 4 CanMEDS roles should be present
            return True, f"Valid CanMEDS format ({len(canmeds_roles_found)}/7 roles found)"
        else:
            return False, f"Insufficient CanMEDS content ({len(canmeds_roles_found)}/7 roles found)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function for Standard CanMEDS format."""
        print(f"\n=== Processing Standard CanMEDS Document: {os.path.basename(pdf_path)} ===")
        
        # Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Try TOC parsing first
        toc_info = self.parse_table_of_contents(pages_text)
        
        if 'competency_start_page' in toc_info:
            start_page = toc_info['competency_start_page']
            end_page = toc_info.get('competency_end_page')
            print(f"📖 Using TOC information: Pages {start_page}-{end_page or 'TBD'}")
        else:
            print("📖 TOC parsing failed, using structure analysis")
            start_page, end_page = self.find_competency_section_by_structure(pages_text)
        
        if not start_page:
            print("❌ Could not find competency section")
            return None
        
        print(f"📍 Competency section: Pages {start_page}-{end_page}")
        
        # Extract competency content
        content = self.extract_competency_content(pages_text, start_page, end_page)
        
        # Validate extraction
        is_valid, validation_msg = self.validate_extraction(content)
        print(f"🔍 Validation: {validation_msg}")
        
        if not is_valid:
            print("⚠️  Extraction validation failed")
        
        # Save extracted content
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Document: {os.path.basename(pdf_path)}\n")
                f.write(f"Extraction Method: Standard CanMEDS Structure Analysis\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"Validation: {validation_msg}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            print(f"✅ Competencies extracted to: {output_file}")
            
            return {
                'pdf_path': pdf_path,
                'output_file': output_file,
                'pages_extracted': f"{start_page}-{end_page}",
                'validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': is_valid
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    """Process all documents in Standard CanMEDS category."""
    
    # Paths - corrected to match Extracted_Competencies structure
    category_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Document_Categories/02_Standard_CanMEDS_Format"
    output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies/02_Standard_CanMEDS_Format"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize extractor
    extractor = StandardCanMEDSExtractor()
    
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
        'category': 'Standard CanMEDS Format',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{successful_extractions/len(pdf_files)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 SUMMARY")
    print(f"Category: Standard CanMEDS Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
