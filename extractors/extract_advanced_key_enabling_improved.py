#!/usr/bin/env python3
"""
Improved Advanced Key & Enabling Format Competency Extractor
Enhanced for better content extraction with flexible validation and robust boundary detection

Key Improvements:
- More flexible validation thresholds
- Better end boundary detection
- Enhanced content pattern analysis
- Robust fallback mechanisms
"""

import re
import os
import json
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

class ImprovedAdvancedKeyEnablingExtractor:
    def __init__(self, toc_scan_pages: int = 15):
        self.key_indicators = [
            "LEARNING AND COMPETENCIES",
            "PROFESSIONAL COMPETENCIES", 
            "KEY COMPETENCIES",
            "ENABLING COMPETENCIES",
            "COMPETENCIES AND OBJECTIVES",
            "TRAINING OBJECTIVES"
        ]
        
        self.canmeds_roles = [
            "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR", 
            "LEADER", "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL"
        ]
        self.role_synonyms = {
            "LEADER": ["LEADER", "LEADERSHIP", "MANAGER"],
            "HEALTH ADVOCATE": ["HEALTH ADVOCATE", "ADVOCACY"],
            "PROFESSIONAL": ["PROFESSIONAL", "PROFESSIONALISM"],
        }
        
        self.section_end_markers = [
            "CONTINUUM OF LEARNING",
            "ASSESSMENT AND EVALUATION", 
            "TEACHING AND LEARNING",
            "PROGRAM ROTATIONS",
            "CLINICAL ROTATIONS",
            "RESEARCH OBJECTIVES",
            "EVALUATION METHODS"
        ]
        
        self.competency_terms = [
            "COMPETENC", "OBJECTIVE", "SKILL", "KNOWLEDGE", 
            "ABILITY", "PROFICIENCY", "DEMONSTRATE", "PERFORM"
        ]
        
    def _extract_with_pdfplumber(self, pdf_path: str):
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text(layout=True) or ""
                pages_text.append({"page_num": page.page_number, "text": txt})
        return pages_text

    def _extract_with_pypdf2(self, pdf_path: str):
        if PyPDF2 is None:
            return None
        pages_text = []
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                pages_text.append({"page_num": i + 1, "text": txt})
        return pages_text

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF using pdfplumber if available, fallback to PyPDF2."""
        try:
            pages_text = None
            if pdfplumber is not None:
                pages_text = self._extract_with_pdfplumber(pdf_path)
            if not pages_text or all(not (p.get("text") or "").strip() for p in pages_text):
                pages_text = self._extract_with_pypdf2(pdf_path)
            return pages_text
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return None
    
    def find_competency_section_start(self, pages_text):
        """Find the start of competency section with improved pattern matching."""
        candidates = []
        
        for page_info in pages_text:
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Check for key indicators
            for indicator in self.key_indicators:
                if indicator in text:
                    # Calculate confidence score based on surrounding content
                    validation_pages = pages_text[max(0, page_num-2):min(len(pages_text), page_num+4)]
                    
                    canmeds_count = 0
                    competency_terms_count = 0
                    content_density = 0
                    
                    for val_page in validation_pages:
                        val_text = val_page['text'].upper()
                        canmeds_count += sum(1 for role in self.canmeds_roles if role in val_text)
                        competency_terms_count += sum(1 for term in self.competency_terms if term in val_text)
                        content_density += len(val_text.strip())
                    
                    # Calculate confidence score
                    confidence = 0
                    confidence += min(canmeds_count * 15, 60)  # Up to 60 points for CanMEDS roles
                    confidence += min(competency_terms_count * 8, 40)  # Up to 40 points for competency terms
                    confidence += min(content_density / 1000, 20)  # Up to 20 points for content density
                    
                    # Bonus points for specific indicators
                    if "KEY COMPETENC" in text:
                        confidence += 25
                    if "ENABLING COMPETENC" in text:
                        confidence += 25
                    
                    candidates.append({
                        'page': page_num,
                        'indicator': indicator,
                        'confidence': confidence,
                        'canmeds_count': canmeds_count,
                        'competency_terms': competency_terms_count
                    })
                    
                    print(f"Candidate start page {page_num}: {indicator} (confidence: {confidence:.1f})")
        
        # Select best candidate
        if candidates:
            best_candidate = max(candidates, key=lambda x: x['confidence'])
            if best_candidate['confidence'] >= 30:  # Lowered threshold
                return best_candidate['page'], best_candidate['indicator']
        
        return None, None
    
    def find_competency_section_end(self, pages_text, start_page):
        """Find the end of competency section with improved heuristics."""
        if not start_page:
            return None
            
        end_candidates = []
        
        # Look for explicit end markers first
        for page_info in pages_text[start_page:]:
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    end_candidates.append({
                        'page': page_num,
                        'marker': end_marker,
                        'type': 'explicit'
                    })
                    print(f"Found explicit end marker at page {page_num}: {end_marker}")
                    break
        
        # If explicit markers found, use the first one
        if end_candidates:
            return min(end_candidates, key=lambda x: x['page'])['page']
        
        # Use content analysis to find implicit end
        competency_scores = []
        search_range = min(30, len(pages_text) - start_page + 1)  # Look ahead up to 30 pages
        
        for i, page_info in enumerate(pages_text[start_page:start_page + search_range]):
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Calculate competency content score
            score = 0
            score += sum(5 for role in self.canmeds_roles if role in text)
            score += sum(2 for term in self.competency_terms if term in text)
            
            # Penalty for assessment/evaluation content (indicates section end)
            if any(term in text for term in ["ASSESSMENT", "EVALUATION", "EXAMINATION", "GRADING"]):
                score -= 10
            
            competency_scores.append({
                'page': page_num,
                'score': score,
                'relative_pos': i
            })
        
        # Find where competency content drops significantly
        if competency_scores:
            # Use moving average to smooth out variations
            window_size = 3
            smoothed_scores = []
            
            for i in range(len(competency_scores)):
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(competency_scores), i + window_size // 2 + 1)
                avg_score = sum(s['score'] for s in competency_scores[start_idx:end_idx]) / (end_idx - start_idx)
                smoothed_scores.append(avg_score)
            
            # Find significant drop
            max_score = max(smoothed_scores[:5]) if len(smoothed_scores) >= 5 else max(smoothed_scores)
            threshold = max_score * 0.3  # 70% drop threshold
            
            for i, score in enumerate(smoothed_scores[2:], 2):  # Skip first 2 pages
                if score < threshold and i < len(competency_scores):
                    return competency_scores[i]['page']
        
        # Fallback: reasonable default based on document length
        reasonable_length = min(25, max(10, (len(pages_text) - start_page) // 3))
        return start_page + reasonable_length
    
    def extract_competency_content(self, pages_text, start_page, end_page):
        """Extract competency content with smart content filtering."""
        if not start_page or not end_page:
            return ""
        
        competency_content = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text']
            page_num = page_info['page_num']
            
            # For first page, try to start from the competency section
            if page_num == start_page:
                text_upper = text.upper()
                best_start = 0
                
                for indicator in self.key_indicators:
                    if indicator in text_upper:
                        indicator_pos = text_upper.find(indicator)
                        if indicator_pos != -1:
                            best_start = indicator_pos
                            break
                
                text = text[best_start:]
            
            # Clean up the text
            text = self.clean_extracted_text(text)
            
            if text.strip():  # Only add non-empty pages
                competency_content.append(f"--- Page {page_num} ---\n{text}\n")
        
        return "\n".join(competency_content)
    
    def clean_extracted_text(self, text):
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove page numbers and headers/footers that are clearly not content
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip obvious page numbers, copyright notices, etc.
            if (len(line) < 5 or 
                line.isdigit() or 
                line.startswith('©') or
                line.upper().startswith('COPYRIGHT') or
                'SAUDI COMMISSION' in line.upper()):
                continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def validate_extraction(self, content):
        """Enhanced validation with more flexible criteria."""
        if not content or len(content.strip()) < 100:
            return False, "No meaningful content extracted"
        
        content_upper = content.upper()
        
        # Count various indicators
        canmeds_roles_found = sum(1 for role in self.canmeds_roles if role in content_upper)
        key_competencies = "KEY COMPETENC" in content_upper
        enabling_competencies = "ENABLING COMPETENC" in content_upper
        competency_terms = sum(1 for term in self.competency_terms if term in content_upper)
        
        # Progressive levels (F1, F2, R1-R5)
        has_progressive_levels = bool(re.search(r'\b[FR][1-5]\b', content_upper))
        
        # Calculate validation score
        validation_score = 0
        validation_score += min(canmeds_roles_found * 10, 40)  # Up to 40 points
        validation_score += 20 if key_competencies else 0
        validation_score += 20 if enabling_competencies else 0
        validation_score += min(competency_terms * 2, 20)  # Up to 20 points
        validation_score += 20 if has_progressive_levels else 0
        
        # Length bonus
        validation_score += min(len(content) / 500, 10)  # Up to 10 points for length
        
        if validation_score >= 50:  # Lowered threshold
            return True, f"Valid advanced format (score: {validation_score:.0f}/100, {canmeds_roles_found}/7 CanMEDS roles)"
        else:
            return False, f"Insufficient validation (score: {validation_score:.0f}/100, {canmeds_roles_found}/7 CanMEDS roles)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function."""
        print(f"\n=== Processing Advanced Key & Enabling Document: {os.path.basename(pdf_path)} ===")
        
        # Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Find competency section boundaries
        start_page, start_indicator = self.find_competency_section_start(pages_text)
        
        if not start_page:
            print("❌ Could not find competency section start")
            return None
        
        end_page = self.find_competency_section_end(pages_text, start_page)
        
        print(f"📍 Competency section: Pages {start_page}-{end_page}")
        if start_indicator:
            print(f"🔍 Start indicator: {start_indicator}")
        
        # Extract competency content
        content = self.extract_competency_content(pages_text, start_page, end_page)
        
        # Validate extraction
        is_valid, validation_msg = self.validate_extraction(content)
        print(f"🔍 Validation: {validation_msg}")
        
        if not is_valid:
            print("⚠️  Extraction validation failed - but saving anyway for review")
        
        # Save extracted content
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Document: {os.path.basename(pdf_path)}\n")
                f.write(f"Extraction Method: Improved Advanced Key & Enabling Pattern Analysis\n")
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
                'extraction_successful': is_valid or len(content) > 500  # Save if reasonable content
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Extract competencies (Advanced Key & Enabling format, improved)")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to write extracted outputs")
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    extractor = ImprovedAdvancedKeyEnablingExtractor()
    
    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    results = []
    successful_extractions = 0
    
    for pdf_path in pdf_files:
        result = extractor.extract_competencies(pdf_path, output_dir)
        if result:
            results.append(result)
            if result['extraction_successful']:
                successful_extractions += 1
    
    summary = {
        'category': 'Advanced Key & Enabling Format (Improved, layout-aware)',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{(successful_extractions/len(pdf_files)*100):.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary_improved.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 IMPROVED SUMMARY")
    print(f"Category: Advanced Key & Enabling Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
