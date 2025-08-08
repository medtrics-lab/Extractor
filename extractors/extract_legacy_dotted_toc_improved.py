#!/usr/bin/env python3
"""
Improved Legacy Dotted TOC Format Competency Extractor
Enhanced for better dotted TOC parsing, page range detection, and robust validation

Key Improvements:
- Enhanced dotted TOC pattern recognition
- Multiple TOC structure detection methods
- Better competency section boundary detection
- Comprehensive validation with flexible scoring
- Improved content filtering and processing
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

class ImprovedLegacyDottedTOCExtractor:
    def __init__(self):
        # Enhanced dotted TOC patterns to capture more variations
        self.dotted_toc_patterns = [
            # Standard dotted patterns
            r'([A-Z][A-Za-z\s\&\-]+)\s*\.{3,}\s*(\d+)',
            r'([A-Z][A-Za-z\s\&\-]+)\s*\.*\s*(\d+)',
            # Patterns with numbers and dots
            r'(\d+\.\d*\s*[A-Z][A-Za-z\s\&\-]+)\s*\.{2,}\s*(\d+)',
            r'(\d+\s+[A-Z][A-Za-z\s\&\-]+)\s*\.{2,}\s*(\d+)',
            # Space-separated patterns  
            r'([A-Z][A-Za-z\s\&\-]+)\s{5,}(\d+)',
            # Patterns with special characters
            r'([A-Z][A-Za-z\s\&\-\(\)]+)\s*\.{2,}\s*(\d+)',
        ]
        
        self.competency_keywords = [
            "COMPETENCIES", "COMPETENCY", "EDUCATIONAL OBJECTIVES", 
            "OUTCOMES", "CANMEDS", "PROFESSIONAL", "LEARNING OBJECTIVES",
            "SKILLS", "KNOWLEDGE", "ABILITIES", "FRAMEWORK"
        ]
        
        # Enhanced section end indicators
        self.section_end_keywords = [
            "TEACHING AND LEARNING", "LEARNING OPPORTUNITIES", "ASSESSMENT",
            "EVALUATION", "PROGRAM EVALUATION", "CURRICULUM EVALUATION", 
            "ROTATIONS", "SCHEDULE", "BIBLIOGRAPHY", "REFERENCES",
            "APPENDIX", "CLINICAL ROTATIONS", "ACADEMIC ACTIVITIES",
            "ROTATION SCHEDULE", "EVALUATION METHODS"
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
    
    def find_toc_with_enhanced_patterns(self, pages_text):
        """Enhanced TOC detection with multiple pattern recognition strategies."""
        toc_entries = []
        
        # Search for TOC in first 15 pages (expanded range)
        for page_info in pages_text[:15]:
            text = page_info['text']
            page_num = page_info['page_num']
            
            # Skip if page doesn't look like TOC
            text_upper = text.upper()
            if not any(keyword in text_upper for keyword in ["CONTENTS", "TABLE", "INDEX"]):
                continue
            
            print(f"Checking page {page_num} for TOC patterns...")
            
            # Try multiple pattern approaches
            page_toc_entries = []
            
            # Strategy 1: Enhanced dotted patterns
            for pattern in self.dotted_toc_patterns:
                matches = re.findall(pattern, text, re.MULTILINE)
                for match in matches:
                    if len(match) >= 2:
                        entry_title = match[0].strip()
                        try:
                            entry_page = int(match[1])
                            
                            # Validate entry relevance
                            if (any(keyword in entry_title.upper() for keyword in self.competency_keywords) and 
                                5 <= entry_page <= len(pages_text) and
                                len(entry_title) >= 10):
                                
                                page_toc_entries.append({
                                    'title': entry_title,
                                    'page': entry_page,
                                    'pattern': pattern
                                })
                                print(f"  Found: '{entry_title}' -> page {entry_page}")
                        except ValueError:
                            continue
            
            # Strategy 2: Line-by-line analysis for non-standard formats
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or len(line) < 15:
                    continue
                
                # Look for competency-related entries with page numbers
                line_upper = line.upper()
                if any(keyword in line_upper for keyword in self.competency_keywords):
                    # Extract potential page numbers at the end
                    page_match = re.search(r'\b(\d{1,3})\s*$', line)
                    if page_match:
                        try:
                            entry_page = int(page_match.group(1))
                            if 5 <= entry_page <= len(pages_text):
                                entry_title = re.sub(r'\s*\d{1,3}\s*$', '', line).strip()
                                if len(entry_title) >= 10:
                                    page_toc_entries.append({
                                        'title': entry_title,
                                        'page': entry_page,
                                        'pattern': 'line_analysis'
                                    })
                                    print(f"  Found (line analysis): '{entry_title}' -> page {entry_page}")
                        except ValueError:
                            continue
            
            toc_entries.extend(page_toc_entries)
        
        # Remove duplicates and sort by page
        unique_entries = []
        seen_pages = set()
        
        for entry in sorted(toc_entries, key=lambda x: x['page']):
            if entry['page'] not in seen_pages:
                unique_entries.append(entry)
                seen_pages.add(entry['page'])
        
        return unique_entries
    
    def determine_competency_page_range_enhanced(self, toc_entries, pages_text):
        """Enhanced page range determination with multiple validation strategies."""
        if not toc_entries:
            return None, None
        
        # Strategy 1: Direct competency entries
        competency_pages = []
        for entry in toc_entries:
            title_upper = entry['title'].upper()
            if any(keyword in title_upper for keyword in self.competency_keywords):
                competency_pages.append(entry['page'])
        
        if competency_pages:
            start_page = min(competency_pages)
            
            # Find end page by looking at content and next sections
            end_page = self.find_competency_end_page_enhanced(pages_text, start_page, toc_entries)
            return start_page, end_page
        
        # Strategy 2: CanMEDS density analysis in TOC referenced pages
        canmeds_scores = []
        for entry in toc_entries:
            page_num = entry['page']
            if page_num <= len(pages_text):
                page_text = pages_text[page_num - 1]['text'].upper()
                
                # Calculate CanMEDS content score
                score = 0
                score += sum(10 for role in self.canmeds_roles if role in page_text)
                score += page_text.count("COMPETENC") * 5
                score += page_text.count("OBJECTIVE") * 3
                score += page_text.count("CANMEDS") * 8
                
                canmeds_scores.append({
                    'page': page_num,
                    'title': entry['title'],
                    'score': score
                })
        
        # Find best scoring pages
        if canmeds_scores:
            canmeds_scores.sort(key=lambda x: x['score'], reverse=True)
            best_page = canmeds_scores[0]['page']
            
            if canmeds_scores[0]['score'] >= 20:  # Minimum threshold
                end_page = self.find_competency_end_page_enhanced(pages_text, best_page, toc_entries)
                return best_page, end_page
        
        return None, None
    
    def find_competency_end_page_enhanced(self, pages_text, start_page, toc_entries):
        """Enhanced end page detection with multiple strategies."""
        
        # Strategy 1: Look for explicit end markers in TOC
        for entry in toc_entries:
            if entry['page'] > start_page:
                title_upper = entry['title'].upper()
                if any(keyword in title_upper for keyword in self.section_end_keywords):
                    print(f"Found end marker in TOC: '{entry['title']}' at page {entry['page']}")
                    return entry['page']
        
        # Strategy 2: Content analysis - find where competency content drops
        competency_densities = []
        search_range = min(50, len(pages_text) - start_page + 1)  # Extended search range
        
        for i, page_info in enumerate(pages_text[start_page-1:start_page + search_range]):
            text_upper = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Calculate competency content density
            density = 0
            density += sum(15 for role in self.canmeds_roles if role in text_upper)
            density += text_upper.count("COMPETENC") * 8
            density += text_upper.count("OBJECTIVE") * 5
            density += text_upper.count("CANMEDS") * 10
            
            # Penalties for non-competency content
            density -= text_upper.count("ASSESSMENT") * 5
            density -= text_upper.count("EVALUATION") * 5
            density -= text_upper.count("ROTATION") * 3
            
            competency_densities.append({
                'page': page_num,
                'density': density,
                'position': i
            })
        
        # Find significant drop in competency content
        if len(competency_densities) > 5:
            # Use moving average to smooth variations
            window_size = 3
            smoothed_densities = []
            
            for i in range(len(competency_densities)):
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(competency_densities), i + window_size // 2 + 1)
                avg_density = sum(d['density'] for d in competency_densities[start_idx:end_idx]) / (end_idx - start_idx)
                smoothed_densities.append(avg_density)
            
            # Find where density drops significantly
            if smoothed_densities:
                max_density = max(smoothed_densities[:5]) if len(smoothed_densities) >= 5 else max(smoothed_densities)
                threshold = max(max_density * 0.3, 15)  # 70% drop threshold
                
                for i, density in enumerate(smoothed_densities[3:], 3):  # Skip initial pages
                    if density < threshold:
                        print(f"Found content density drop at page {competency_densities[i]['page']} (density: {density:.1f} < {threshold:.1f})")
                        return competency_densities[i]['page']
        
        # Strategy 3: Default reasonable length based on document size
        default_length = min(40, max(20, (len(pages_text) - start_page) // 3))
        return start_page + default_length
    
    def extract_competency_content_enhanced(self, pages_text, start_page, end_page):
        """Enhanced content extraction with improved filtering."""
        if not start_page or not end_page:
            return ""
        
        content_sections = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text']
            page_num = page_info['page_num']
            
            # Clean and process text
            cleaned_text = self.clean_extracted_text_enhanced(text)
            
            if cleaned_text.strip():
                content_sections.append(f"--- Page {page_num} ---\n{cleaned_text}\n")
        
        return "\n".join(content_sections)
    
    def clean_extracted_text_enhanced(self, text):
        """Enhanced text cleaning with better noise removal."""
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove common non-content elements
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip obvious non-content lines
            if (len(line) < 3 or
                line.isdigit() or
                re.match(r'^Page \d+', line) or
                re.match(r'^\d+\s*$', line) or
                line.startswith('©') or
                'COPYRIGHT' in line.upper() or
                'SAUDI COMMISSION' in line.upper() or
                re.match(r'^[a-z\s]+$', line) or  # All lowercase noise
                re.match(r'^\W+$', line)):        # Only punctuation
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def validate_extraction_enhanced(self, content, start_page, end_page, toc_entries_count):
        """Enhanced validation with comprehensive scoring."""
        if not content or len(content.strip()) < 200:
            return False, "Insufficient content extracted"
        
        content_upper = content.upper()
        
        # Core validation metrics
        canmeds_roles_found = [role for role in self.canmeds_roles if role in content_upper]
        competency_count = content_upper.count("COMPETENC")
        objective_count = content_upper.count("OBJECTIVE")
        canmeds_mentions = content_upper.count("CANMEDS")
        
        # Quality indicators
        has_structured_content = bool(re.search(r'\d+\.\d+|\d+\.', content))
        has_professional_elements = any(term in content_upper for term in ["PROFESSIONAL", "ETHICAL", "RESPONSIBILITY"])
        content_length = len(content)
        page_range_reasonable = (end_page - start_page) <= 80  # Reasonable range
        
        # Calculate comprehensive score
        score = 0
        score += len(canmeds_roles_found) * 20     # Up to 140 points (7 roles)
        score += min(competency_count * 8, 64)     # Up to 64 points
        score += min(objective_count * 5, 40)      # Up to 40 points
        score += canmeds_mentions * 12             # Variable points
        score += min(toc_entries_count * 10, 50)   # Up to 50 points for TOC quality
        score += 20 if has_structured_content else 0
        score += 15 if has_professional_elements else 0
        score += 10 if page_range_reasonable else -10
        score += min(content_length / 1000, 30)    # Up to 30 points for length
        
        # Validation thresholds (more flexible for legacy format)
        if score >= 150:
            return True, f"Valid legacy format (score: {score:.0f}/399, {len(canmeds_roles_found)}/7 roles)"
        elif score >= 100 and len(canmeds_roles_found) >= 4:
            return True, f"Acceptable legacy format (score: {score:.0f}/399, {len(canmeds_roles_found)}/7 roles)"
        elif content_length > 5000 and len(canmeds_roles_found) >= 3:
            return True, f"Minimal legacy format (score: {score:.0f}/399, {len(canmeds_roles_found)}/7 roles)"
        else:
            return False, f"Insufficient legacy content (score: {score:.0f}/399, {len(canmeds_roles_found)}/7 roles)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function with enhanced logic."""
        print(f"\n=== Processing Legacy Dotted TOC Document: {os.path.basename(pdf_path)} ===")
        
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        print(f"📄 Document has {len(pages_text)} pages")
        
        # Enhanced TOC detection
        toc_entries = self.find_toc_with_enhanced_patterns(pages_text)
        print(f"📑 Found {len(toc_entries)} relevant TOC entries")
        
        if not toc_entries:
            print("❌ No competency-related TOC entries found")
            return None
        
        # Enhanced page range determination
        start_page, end_page = self.determine_competency_page_range_enhanced(toc_entries, pages_text)
        
        if not start_page or not end_page:
            print("❌ Could not determine competency page range")
            return None
        
        print(f"📍 Competency section: Pages {start_page}-{end_page}")
        
        # Enhanced content extraction
        content = self.extract_competency_content_enhanced(pages_text, start_page, end_page)
        
        # Enhanced validation
        is_valid, validation_msg = self.validate_extraction_enhanced(content, start_page, end_page, len(toc_entries))
        print(f"🔍 Validation: {validation_msg}")
        
        if not is_valid:
            print("⚠️  Extraction validation failed - but saving for review")
        
        # Save content
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Document: {os.path.basename(pdf_path)}\n")
                f.write(f"Extraction Method: Improved Legacy Dotted TOC Detection\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"TOC Entries Found: {len(toc_entries)}\n")
                f.write(f"Validation: {validation_msg}\n")
                f.write("="*80 + "\n\n")
                
                # Add TOC entries for reference
                f.write("TOC ENTRIES USED:\n")
                for entry in toc_entries:
                    f.write(f"  - {entry['title']} -> Page {entry['page']}\n")
                f.write("\n" + "="*80 + "\n\n")
                
                f.write(content)
            
            print(f"✅ Competencies extracted to: {output_file}")
            
            return {
                'pdf_path': pdf_path,
                'output_file': output_file,
                'pages_extracted': f"{start_page}-{end_page}",
                'toc_entries_found': len(toc_entries),
                'validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': is_valid or len(content) > 10000
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Extract competencies (Legacy dotted TOC format, improved)")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to write extracted outputs")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    extractor = ImprovedLegacyDottedTOCExtractor()

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
        'category': 'Legacy Dotted TOC (Improved, layout-aware)',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{successful_extractions/len(pdf_files)*100:.1f}%",
        'results': results
    }

    summary_file = os.path.join(output_dir, 'extraction_summary_improved.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n🎯 IMPROVED SUMMARY")
    print(f"Category: Legacy Dotted TOC")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
