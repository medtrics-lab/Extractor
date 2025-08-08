#!/usr/bin/env python3
"""
Advanced Key & Enabling Format Competency Extractor
Specialized for documents with sophisticated competency frameworks (21 documents)

Strategy: Content Pattern Analysis + Key Phrase Detection
Reasoning: These documents have the most structured format with clear "Key Competencies" 
and "Enabling Competencies" markers, making pattern-based extraction most reliable.
"""

import PyPDF2
import re
import os
import json
from pathlib import Path

class AdvancedKeyEnablingExtractor:
    def __init__(self):
        self.key_indicators = [
            "LEARNING AND COMPETENCIES",
            "PROFESSIONAL COMPETENCIES", 
            "KEY COMPETENCIES",
            "ENABLING COMPETENCIES"
        ]
        
        self.canmeds_roles = [
            "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR", 
            "MANAGER", "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL"
        ]
        
        self.section_end_markers = [
            "CONTINUUM OF LEARNING",
            "ASSESSMENT AND EVALUATION", 
            "TEACHING AND LEARNING",
            "PROGRAM ROTATIONS"
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
    
    def find_competency_section_boundaries(self, pages_text):
        """
        Find start and end of competency section using pattern analysis.
        Strategy: Look for key indicators followed by CanMEDS roles pattern.
        """
        start_page = None
        end_page = None
        start_position = None
        
        # Find start of competency section
        for page_info in pages_text:
            text = page_info['text'].upper()
            
            # Check for key indicators
            for indicator in self.key_indicators:
                if indicator in text:
                    # Validate by checking for CanMEDS roles or competency content in this and next few pages
                    validation_pages = pages_text[max(0, page_info['page_num']-1):page_info['page_num']+5]
                    
                    canmeds_count = 0
                    competency_terms = 0
                    for val_page in validation_pages:
                        val_text = val_page['text'].upper()
                        canmeds_count += sum(1 for role in self.canmeds_roles if role in val_text)
                        competency_terms += sum(1 for term in ["COMPETENC", "OBJECTIVE", "SKILL", "KNOWLEDGE"] if term in val_text)
                    
                    # More flexible validation - accept if has CanMEDS OR competency terms
                    if canmeds_count >= 1 or competency_terms >= 3:
                        start_page = page_info['page_num']
                        start_position = indicator
                        print(f"Found competency section start at page {start_page} with indicator: {indicator}")
                        break
            
            if start_page:
                break
        # Find end of competency section
        for page_info in pages_text[start_page:]:  # Start searching from competency section
            text = page_info['text'].upper()
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    end_page = page_info['page_num']
                    print(f"Found competency section end at page {end_page} with marker: {end_marker}")
                    break
            
            if end_page:
                break
        
        # If no clear end found, estimate based on content pattern changes
        if not end_page and start_page:
            # Look for significant pattern change or last page with competency content
            for i, page_info in enumerate(pages_text[start_page:start_page+10], start_page):
                text = page_info['text'].upper()
                
                # If we find assessment/evaluation content, this might be the end
                if any(term in text for term in ["ASSESSMENT", "EVALUATION", "ROTATION"]):
                    end_page = page_info['page_num']
                    break
            
            # Default to reasonable section length if still no end found
            if not end_page:
                end_page = min(start_page + 15, len(pages_text))
        
        return start_page, end_page, start_position
    
    def extract_competency_content(self, pages_text, start_page, end_page, start_position):
        """Extract the actual competency content from identified pages."""
        competency_content = []
        
        if not start_page or not end_page:
            return ""
        
        for page_info in pages_text[start_page-1:end_page]:
            if page_info['page_num'] == start_page and start_position:
                # For first page, start from the identified position
                text = page_info['text'][start_position:]
            else:
                text = page_info['text']
            
            competency_content.append(f"--- Page {page_info['page_num']} ---\n{text}\n")
        
        return "\n".join(competency_content)
    
    def validate_extraction(self, content):
        """
        Validate that extracted content contains expected Advanced Key & Enabling elements.
        """
        if not content:
            return False, "No content extracted"
        
        content_upper = content.upper()
        
        # Check for key indicators
        has_key_competencies = "KEY COMPETENC" in content_upper
        has_enabling_competencies = "ENABLING COMPETENC" in content_upper
        has_canmeds = any(role in content_upper for role in self.canmeds_roles)
        
        # Advanced format should have structured competency breakdown
        has_progressive_levels = any(level in content_upper for level in ["R1", "R2", "R3", "R4", "F1", "F2"])
        
        validation_score = sum([
            has_key_competencies,
            has_enabling_competencies, 
            has_canmeds,
            has_progressive_levels
        ])
        
        if validation_score >= 2:  # At least 2 indicators should be present
            return True, f"Valid advanced format (score: {validation_score}/4)"
        else:
            return False, f"Insufficient advanced format indicators (score: {validation_score}/4)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function for Advanced Key & Enabling format."""
        print(f"\n=== Processing Advanced Key & Enabling Document: {os.path.basename(pdf_path)} ===")
        
        # Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Find competency section boundaries
        start_page, end_page, start_position = self.find_competency_section_boundaries(pages_text)
        
        if not start_page:
            print("❌ Could not find competency section boundaries")
            return None
        
        print(f"📍 Competency section: Pages {start_page}-{end_page}")
        
        # Extract competency content
        content = self.extract_competency_content(pages_text, start_page, end_page, start_position)
        
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
                f.write(f"Extraction Method: Advanced Key & Enabling Pattern Analysis\n")
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
    """Process all documents in Advanced Key & Enabling category."""
    
    # Paths - corrected to match Extracted_Competencies structure
    category_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Document_Categories/01_Advanced_Key_and_Enabling_Format"
    output_dir = "/Users/charlesnorris/Downloads/SaudiSCFHS/Extracted_Competencies/01_Advanced_Key_and_Enabling_Format"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize extractor
    extractor = AdvancedKeyEnablingExtractor()
    
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
        'category': 'Advanced Key & Enabling Format',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{successful_extractions/len(pdf_files)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 SUMMARY")
    print(f"Category: Advanced Key & Enabling Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
