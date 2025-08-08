#!/usr/bin/env python3
"""
Basic Role-Based Format Competency Extractor
Specialized for role-based documents without CanMEDS framework (9 documents)

Strategy: Role Pattern Detection + Competency Matrix Analysis
Reasoning: These documents use role-based structure without CanMEDS terminology.
Focus on finding clinical competencies, professional roles, and competency matrices.
"""

import PyPDF2
import re
import os
import json
from pathlib import Path

class BasicRoleBasedExtractor:
    def __init__(self):
        self.section_headers = [
            "CLINICAL COMPETENCIES",
            "PROFESSIONAL COMPETENCIES", 
            "COMPETENCIES AND OBJECTIVES",
            "LEARNING AND COMPETENCIES",
            "CLINICAL DOMAINS"
        ]
        
        self.role_indicators = [
            "CLINICAL PRACTICE", "PROFESSIONAL PRACTICE", 
            "PATIENT CARE", "CLINICAL SKILLS",
            "PROFESSIONAL DEVELOPMENT", "LEADERSHIP",
            "COMMUNICATION", "ETHICS", "QUALITY IMPROVEMENT"
        ]
        
        self.section_end_markers = [
            "CONTINUUM OF LEARNING",
            "TEACHING METHODS",
            "ASSESSMENT AND EVALUATION",
            "PROGRAM ROTATIONS"
        ]
        
        # Patterns specific to basic role-based documents
        self.competency_matrix_indicators = [
            "COMPETENCY MATRIX", "COMPETENCY TABLE", 
            "JUNIOR LEVEL", "SENIOR LEVEL",
            "NOVICE", "EXPERT"
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
    
    def find_competency_sections_by_role_patterns(self, pages_text):
        """
        Find competency sections using role pattern detection.
        Strategy: Look for multiple competency-related sections and combine them.
        """
        competency_sections = []
        
        for page_info in pages_text:
            text = page_info['text'].upper()
            
            # Look for competency section headers
            for header in self.section_headers:
                if header in text:
                    # Calculate role indicator density in this page and surrounding pages
                    context_pages = pages_text[max(0, page_info['page_num']-2):page_info['page_num']+3]
                    
                    role_indicators_found = []
                    for ctx_page in context_pages:
                        ctx_text = ctx_page['text'].upper()
                        for indicator in self.role_indicators:
                            if indicator in ctx_text and indicator not in role_indicators_found:
                                role_indicators_found.append(indicator)
                    
                    # If we find multiple role indicators, this is likely a competency section
                    if len(role_indicators_found) >= 2:
                        competency_sections.append({
                            'start_page': page_info['page_num'],
                            'header': header,
                            'role_indicators': role_indicators_found
                        })
                        print(f"Found competency section at page {page_info['page_num']}: '{header}' with {len(role_indicators_found)} role indicators")
        
        return competency_sections
    
    def find_competency_matrices(self, pages_text):
        """
        Find competency matrices which are common in basic role-based documents.
        """
        matrix_pages = []
        
        for page_info in pages_text:
            text = page_info['text'].upper()
            
            # Look for competency matrix indicators
            matrix_indicators_found = 0
            for indicator in self.competency_matrix_indicators:
                if indicator in text:
                    matrix_indicators_found += 1
            
            # Also look for table-like structures (multiple tabs/spaces in lines)
            lines = text.split('\n')
            tabular_lines = sum(1 for line in lines if line.count('\t') > 2 or len(line.split()) > 5)
            
            if matrix_indicators_found > 0 or tabular_lines > 5:
                matrix_pages.append({
                    'page_num': page_info['page_num'],
                    'matrix_indicators': matrix_indicators_found,
                    'tabular_lines': tabular_lines
                })
                print(f"Found potential competency matrix at page {page_info['page_num']}")
        
        return matrix_pages
    
    def determine_extraction_boundaries(self, pages_text, competency_sections, matrix_pages):
        """
        Determine start and end pages for extraction based on found sections and matrices.
        """
        all_competency_pages = []
        
        # Add section start pages
        for section in competency_sections:
            all_competency_pages.append(section['start_page'])
        
        # Add matrix pages
        for matrix in matrix_pages:
            all_competency_pages.append(matrix['page_num'])
        
        if not all_competency_pages:
            return None, None
        
        # Determine overall start and end
        start_page = min(all_competency_pages)
        
        # Find end page by looking for section end markers
        end_page = None
        for page_info in pages_text[start_page:]:
            text = page_info['text'].upper()
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    end_page = page_info['page_num']
                    print(f"Found competency section end at page {end_page} with marker: {end_marker}")
                    break
            
            if end_page:
                break
        
        # If no clear end found, use heuristics
        if not end_page:
            # Look for significant decrease in role indicators
            for i, page_info in enumerate(pages_text[start_page:start_page+15], start_page):
                text = page_info['text'].upper()
                
                role_indicators_in_page = sum(1 for indicator in self.role_indicators if indicator in text)
                
                # If this page has very few role indicators and contains assessment content
                if role_indicators_in_page <= 1 and any(term in text for term in ["ASSESSMENT", "EVALUATION", "TEACHING"]):
                    end_page = page_info['page_num']
                    break
            
            # Default fallback
            if not end_page:
                end_page = min(start_page + 20, len(pages_text))
        
        return start_page, end_page
    
    def extract_competency_content(self, pages_text, start_page, end_page):
        """Extract competency content from identified page range."""
        if not start_page or not end_page:
            return ""
        
        competency_content = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text']
            
            # For first page, try to start from competency section header
            if page_info['page_num'] == start_page:
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
        Validate that extracted content contains expected Basic Role-Based elements.
        """
        if not content:
            return False, "No content extracted"
        
        content_upper = content.upper()
        
        # Count role indicators present
        role_indicators_found = [indicator for indicator in self.role_indicators if indicator in content_upper]
        
        # Check for competency headers
        has_competency_header = any(header in content_upper for header in self.section_headers)
        
        # Check for matrix indicators
        has_matrix_elements = any(indicator in content_upper for indicator in self.competency_matrix_indicators)
        
        # Check for levels or progression indicators
        has_progression = any(term in content_upper for term in ["LEVEL", "JUNIOR", "SENIOR", "NOVICE", "EXPERT"])
        
        validation_score = len(role_indicators_found)
        
        if validation_score >= 2 and has_competency_header:
            return True, f"Valid role-based format ({len(role_indicators_found)} role indicators found)"
        else:
            return False, f"Insufficient role-based content ({len(role_indicators_found)} role indicators found)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function for Basic Role-Based format."""
        print(f"\n=== Processing Basic Role-Based Document: {os.path.basename(pdf_path)} ===")
        
        # Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Find competency sections by role patterns
        competency_sections = self.find_competency_sections_by_role_patterns(pages_text)
        
        # Find competency matrices
        matrix_pages = self.find_competency_matrices(pages_text)
        
        print(f"📊 Found {len(competency_sections)} competency sections and {len(matrix_pages)} potential matrices")
        
        # Determine extraction boundaries
        start_page, end_page = self.determine_extraction_boundaries(pages_text, competency_sections, matrix_pages)
        
        if not start_page:
            print("❌ Could not find competency content")
            return None
        
        print(f"📍 Competency content: Pages {start_page}-{end_page}")
        
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
                f.write(f"Extraction Method: Basic Role-Based Pattern Detection\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"Competency Sections Found: {len(competency_sections)}\n")
                f.write(f"Matrix Pages Found: {len(matrix_pages)}\n")
                f.write(f"Validation: {validation_msg}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            print(f"✅ Competencies extracted to: {output_file}")
            
            return {
                'pdf_path': pdf_path,
                'output_file': output_file,
                'pages_extracted': f"{start_page}-{end_page}",
                'competency_sections_found': len(competency_sections),
                'matrix_pages_found': len(matrix_pages),
                'validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': is_valid
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    """Process all documents in Basic Role-Based category."""
    
    # Paths - corrected to match Extracted_Competencies structure
    category_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Document_Categories/03_Basic_Role_Based_Format"
    output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies/03_Basic_Role_Based_Format"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize extractor
    extractor = BasicRoleBasedExtractor()
    
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
        'category': 'Basic Role-Based Format',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{successful_extractions/len(pdf_files)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 SUMMARY")
    print(f"Category: Basic Role-Based Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
