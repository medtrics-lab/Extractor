#!/usr/bin/env python3
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
        print(f"\n=== Processing CanMEDS Without Levels Document: {os.path.basename(pdf_path)} ===")
        
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
            content.append(f"--- Page {page_info['page_num']} ---\n{page_info['text']}\n")
        
        content_text = "\n".join(content)
        
        # Validate
        content_upper = content_text.upper()
        canmeds_found = [role for role in self.canmeds_roles if role in content_upper]
        
        is_valid = len(canmeds_found) >= 4
        validation_msg = f"CanMEDS without levels ({len(canmeds_found)}/7 roles found)"
        
        # Save
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Document: {os.path.basename(pdf_path)}\n")
            f.write(f"Extraction Method: CanMEDS Without Levels Detection\n")
            f.write(f"Pages Extracted: {start_page}-{end_page}\n")
            f.write(f"Validation: {validation_msg}\n")
            f.write("="*80 + "\n\n")
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
    
    print(f"\n🎯 SUMMARY: {successful}/{len(pdf_files)} successful extractions")

if __name__ == "__main__":
    main()
