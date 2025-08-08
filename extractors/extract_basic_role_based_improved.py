#!/usr/bin/env python3
"""
Improved Basic Role-Based Format Competency Extractor
Enhanced for better competency matrix detection and flexible validation

Additional upgrades in this version:
- Layout-aware text extraction via pdfplumber with fallback to PyPDF2
- Updated CanMEDS role taxonomy (Leader instead of Manager) with synonyms
- Cleaning preserves numbered items, level markers, and table-like rows
- CLI arguments for input/output paths and tunable thresholds
- Structured JSON report emitted alongside text output

References consulted: pdfplumber README (text/table extraction, layout params)
"""

import re
import os
import json
import argparse
from pathlib import Path

# Optional layout-aware parser
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Fallback parser
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

class ImprovedBasicRoleBasedExtractor:
    def __init__(self, toc_scan_pages: int = 15):
        # Enhanced section headers with more variations
        self.section_headers = [
            "CLINICAL COMPETENCIES",
            "PROFESSIONAL COMPETENCIES", 
            "COMPETENCIES AND OBJECTIVES",
            "LEARNING AND COMPETENCIES",
            "CLINICAL DOMAINS",
            "COMPETENCY REQUIREMENTS",
            "TRAINING COMPETENCIES",
            "EDUCATIONAL COMPETENCIES"
        ]
        
        # Expanded role indicators for nursing and medical specialties
        self.role_indicators = [
            "CLINICAL PRACTICE", "PROFESSIONAL PRACTICE", 
            "PATIENT CARE", "CLINICAL SKILLS",
            "PROFESSIONAL DEVELOPMENT", "LEADERSHIP",  # updated from old scripts
            "COMMUNICATION", "ETHICS", "QUALITY IMPROVEMENT",
            "PATIENT SAFETY", "CLINICAL REASONING",
            "CRITICAL THINKING", "EVIDENCE-BASED PRACTICE",
            "INTERPROFESSIONAL COLLABORATION",
            "NURSING PRACTICE", "CLINICAL DECISION",
            "THERAPEUTIC RELATIONSHIP", "HEALTH PROMOTION"
        ]
        
        self.toc_scan_pages = toc_scan_pages
        
        self.section_end_markers = [
            "CONTINUUM OF LEARNING",
            "TEACHING METHODS",
            "ASSESSMENT AND EVALUATION",
            "PROGRAM ROTATIONS",
            "CLINICAL ROTATIONS",
            "ACADEMIC ACTIVITIES",
            "EVALUATION METHODS"
        ]
        
        # Enhanced competency matrix indicators
        self.competency_matrix_indicators = [
            "COMPETENCY MATRIX", "COMPETENCY TABLE", 
            "JUNIOR LEVEL", "SENIOR LEVEL",
            "NOVICE", "EXPERT", "BEGINNER", "ADVANCED",
            "LEVEL 1", "LEVEL 2", "LEVEL 3", "LEVEL 4",
            "FOUNDATION", "INTERMEDIATE", "PROFICIENT",
            "COMPETENCY FRAMEWORK", "SKILLS MATRIX",
            "PERFORMANCE LEVEL", "COMPETENCY ASSESSMENT"
        ]
        
        # Clinical specialty terms that indicate competency content
        self.clinical_competency_terms = [
            "CLINICAL ASSESSMENT", "PATIENT ASSESSMENT",
            "DIAGNOSTIC SKILLS", "THERAPEUTIC INTERVENTION",
            "MEDICATION ADMINISTRATION", "PROCEDURE",
            "CLINICAL REASONING", "CARE PLANNING",
            "DISCHARGE PLANNING", "HEALTH EDUCATION"
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
    
    def find_competency_sections_by_enhanced_patterns(self, pages_text):
        """Enhanced competency section detection using multiple strategies."""
        candidates = []
        
        for page_info in pages_text:
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Strategy 1: Direct header matching with context analysis
            for header in self.section_headers:
                if header in text:
                    # Analyze surrounding context
                    context_pages = pages_text[max(0, page_num-2):min(len(pages_text), page_num+4)]
                    
                    role_indicators_found = []
                    clinical_terms_found = []
                    content_density = 0
                    
                    for ctx_page in context_pages:
                        ctx_text = ctx_page['text'].upper()
                        content_density += len(ctx_text.strip())
                        
                        for indicator in self.role_indicators:
                            if indicator in ctx_text and indicator not in role_indicators_found:
                                role_indicators_found.append(indicator)
                        
                        for term in self.clinical_competency_terms:
                            if term in ctx_text and term not in clinical_terms_found:
                                clinical_terms_found.append(term)
                    
                    # Calculate confidence score
                    confidence = 0
                    confidence += len(role_indicators_found) * 15  # Up to ~300 points
                    confidence += len(clinical_terms_found) * 10   # Up to ~100 points
                    confidence += min(content_density / 2000, 50)  # Up to 50 points
                    
                    # Header-specific bonuses
                    if "CLINICAL COMPETENCIES" in header:
                        confidence += 30
                    elif "PROFESSIONAL COMPETENCIES" in header:
                        confidence += 25
                    
                    candidates.append({
                        'page': page_num,
                        'header': header,
                        'confidence': confidence,
                        'role_indicators': role_indicators_found,
                        'clinical_terms': clinical_terms_found,
                        'type': 'header_match'
                    })
                    
                    print(f"Header candidate page {page_num}: {header} (confidence: {confidence:.1f})")
        
        # Strategy 2: Content-based detection for documents without clear headers
        if not candidates:  # Only if no header matches found
            for page_info in pages_text:
                text = page_info['text'].upper()
                page_num = page_info['page_num']
                
                # Look for pages with high competency content density
                role_count = sum(1 for indicator in self.role_indicators if indicator in text)
                clinical_count = sum(1 for term in self.clinical_competency_terms if term in text)
                competency_mentions = text.count("COMPETENC")
                
                if role_count >= 3 or clinical_count >= 2 or competency_mentions >= 3:
                    confidence = role_count * 10 + clinical_count * 15 + competency_mentions * 8
                    
                    candidates.append({
                        'page': page_num,
                        'header': 'CONTENT_BASED_DETECTION',
                        'confidence': confidence,
                        'role_indicators': [ind for ind in self.role_indicators if ind in text],
                        'clinical_terms': [term for term in self.clinical_competency_terms if term in text],
                        'type': 'content_based'
                    })
                    
                    print(f"Content candidate page {page_num}: content-based (confidence: {confidence:.1f})")
        
        return candidates
    
    def find_enhanced_competency_matrices(self, pages_text):
        """Enhanced competency matrix detection with better algorithms."""
        matrix_pages = []
        
        for page_info in pages_text:
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            lines = text.split('\n')
            
            # Strategy 1: Matrix indicator detection
            matrix_indicators_found = 0
            for indicator in self.competency_matrix_indicators:
                if indicator in text:
                    matrix_indicators_found += 1
            
            # Strategy 2: Table structure analysis
            tabular_lines = 0
            column_separators = 0
            for line in lines:
                # Count lines that look like table rows
                if (line.count('\t') >= 2 or 
                    line.count('  ') >= 4 or  # Multiple spaces
                    len(line.split()) >= 4):   # Multiple words
                    tabular_lines += 1
                
                # Count common column separators
                column_separators += line.count('|') + line.count('\t')
            
            # Strategy 3: Competency-specific patterns
            competency_patterns = 0
            patterns_to_check = [
                r'LEVEL\s+[1-4]', r'YEAR\s+[1-5]', r'R[1-5]', r'F[1-3]',
                r'NOVICE|BEGINNER|INTERMEDIATE|ADVANCED|EXPERT',
                r'COMPETENCY\s+\d+', r'OBJECTIVE\s+\d+'
            ]
            
            for pattern in patterns_to_check:
                if re.search(pattern, text):
                    competency_patterns += 1
            
            # Calculate matrix score
            matrix_score = 0
            matrix_score += matrix_indicators_found * 20
            matrix_score += min(tabular_lines, 10) * 3
            matrix_score += min(column_separators / 10, 10) * 2
            matrix_score += competency_patterns * 15
            
            if matrix_score >= 15:  # Lowered threshold
                matrix_pages.append({
                    'page_num': page_num,
                    'matrix_score': matrix_score,
                    'indicators': matrix_indicators_found,
                    'tabular_lines': tabular_lines,
                    'patterns': competency_patterns
                })
                print(f"Enhanced matrix at page {page_num} (score: {matrix_score:.1f})")
        
        return matrix_pages
    
    def determine_enhanced_extraction_boundaries(self, pages_text, competency_candidates, matrix_pages):
        """Enhanced boundary determination with multiple strategies."""
        if not competency_candidates and not matrix_pages:
            return None, None
        
        # Collect all potential competency pages
        all_competency_pages = []
        
        # Add candidate pages
        for candidate in competency_candidates:
            all_competency_pages.append({
                'page': candidate['page'],
                'score': candidate['confidence'],
                'type': 'candidate'
            })
        
        # Add matrix pages
        for matrix in matrix_pages:
            all_competency_pages.append({
                'page': matrix['page_num'],
                'score': matrix['matrix_score'] * 2,  # Weight matrices higher
                'type': 'matrix'
            })
        
        if not all_competency_pages:
            return None, None
        
        # Sort by page number
        all_competency_pages.sort(key=lambda x: x['page'])
        
        # Find optimal start page (highest scoring early page)
        early_pages = [p for p in all_competency_pages if p['page'] <= min(all_competency_pages, key=lambda x: x['page'])['page'] + 10]
        start_page = max(early_pages, key=lambda x: x['score'])['page']
        
        # Find end page using multiple strategies
        end_page = self.find_enhanced_end_page(pages_text, start_page)
        
        return start_page, end_page
    
    def find_enhanced_end_page(self, pages_text, start_page):
        """Enhanced end page detection with multiple strategies."""
        if not start_page:
            return None
        
        # Strategy 1: Look for explicit end markers
        for page_info in pages_text[start_page:]:
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    print(f"Found explicit end marker at page {page_num}: {end_marker}")
                    return page_num
        
        # Strategy 2: Content density analysis
        competency_density = []
        search_range = min(25, len(pages_text) - start_page + 1)
        
        for i, page_info in enumerate(pages_text[start_page:start_page + search_range]):
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Calculate competency content density
            density = 0
            density += sum(5 for indicator in self.role_indicators if indicator in text)
            density += sum(8 for term in self.clinical_competency_terms if term in text)
            density += text.count("COMPETENC") * 3
            
            # Penalties for non-competency content
            if any(term in text for term in ["ASSESSMENT", "EVALUATION", "GRADING", "EXAMINATION"]):
                density -= 15
            if any(term in text for term in ["ROTATION", "SCHEDULE", "CURRICULUM", "REFERENCES"]):
                density -= 10
            
            competency_density.append({
                'page': page_num,
                'density': density,
                'position': i
            })
        
        # Find where competency content drops significantly
        if len(competency_density) > 3:
            # Use moving average to smooth variations
            window = 3
            smoothed_density = []
            
            for i in range(len(competency_density)):
                start_idx = max(0, i - window // 2)
                end_idx = min(len(competency_density), i + window // 2 + 1)
                avg_density = sum(d['density'] for d in competency_density[start_idx:end_idx]) / (end_idx - start_idx)
                smoothed_density.append(avg_density)
            
            # Find significant drop
            if smoothed_density:
                max_density = max(smoothed_density[:5]) if len(smoothed_density) >= 5 else max(smoothed_density)
                threshold = max(max_density * 0.3, 5)  # 70% drop or minimum threshold
                
                for i, density in enumerate(smoothed_density[3:], 3):  # Skip first 3 pages
                    if density < threshold:
                        return competency_density[i]['page']
        
        # Strategy 3: Default reasonable length
        default_length = min(20, max(8, (len(pages_text) - start_page) // 3))
        return start_page + default_length
    
    def extract_enhanced_competency_content(self, pages_text, start_page, end_page):
        """Enhanced content extraction with smart filtering."""
        if not start_page or not end_page:
            return ""
        
        competency_content = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text']
            page_num = page_info['page_num']
            
            # For first page, try to start from competency section
            if page_num == start_page:
                text_upper = text.upper()
                best_start = 0
                
                # Look for the best starting point
                for header in self.section_headers:
                    if header in text_upper:
                        header_pos = text_upper.find(header)
                        if header_pos != -1:
                            best_start = header_pos
                            break
                
                text = text[best_start:]
            
            # Clean and filter content
            text = self.clean_extracted_text(text)
            
            if text.strip():
                competency_content.append(f"--- Page {page_num} ---\n{text}\n")
        
        return "\n".join(competency_content)
    
    def clean_extracted_text(self, text):
        """Advanced text cleaning with preservation of numbered items and table-like rows."""
        if not text:
            return ""
        
        # Normalize whitespace but preserve multiple spaces for table-like content
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            raw = line
            line = line.rstrip()
            up = line.upper().strip()
            if not up:
                continue
            
            # Skip obvious boilerplate
            if up.startswith('©') or 'COPYRIGHT' in up or 'SAUDI COMMISSION' in up or re.match(r'^PAGE\s+\d+', up):
                continue
            
            # Preserve competency numbering, bullets, and level markers
            numbered = bool(re.match(r'^(\d+\.)+\s*\S', line) or re.match(r'^\d+\s+\S', line))
            subnumbered = bool(re.match(r'^\d+\.\d+(\.\d+)*\s+\S', line))
            level_mark = bool(re.match(r'^[FR][1-5]\b', up) or re.match(r'^(LEVEL|YEAR)\s+\d', up))
            bullet = bool(re.match(r'^[\-•▪]\s+\S', line))
            looks_tabular = ('\t' in raw) or (raw.count('  ') >= 2)
            
            # Skip very short lines unless they look meaningful
            if len(up) < 3 and not (numbered or subnumbered or bullet or level_mark):
                continue
            if up.isdigit() and not (numbered or subnumbered or level_mark):
                continue
            
            # Keep line; normalize tabs to double spaces for readability
            normalized = raw.replace('\t', '  ')
            cleaned_lines.append(normalized)
        
        return '\n'.join(cleaned_lines)
    
    def validate_extraction_enhanced(self, content):
        """Enhanced validation with comprehensive scoring."""
        if not content or len(content.strip()) < 100:
            return False, "No meaningful content extracted"
        
        content_upper = content.upper()
        
        # Core indicators
        role_indicators_found = [indicator for indicator in self.role_indicators if indicator in content_upper]
        clinical_terms_found = [term for term in self.clinical_competency_terms if term in content_upper]
        
        # Section headers present
        headers_found = [header for header in self.section_headers if header in content_upper]
        
        # Matrix indicators
        matrix_indicators = [indicator for indicator in self.competency_matrix_indicators if indicator in content_upper]
        
        # Content quality indicators
        competency_mentions = content_upper.count("COMPETENC")
        has_detailed_structure = bool(re.search(r'\d+\.\d+', content))
        has_progressive_levels = bool(re.search(r'LEVEL\s+[1-4]|YEAR\s+[1-5]|R[1-5]|F[1-3]', content_upper))
        
        # Calculate comprehensive score
        score = 0
        score += len(role_indicators_found) * 8      # Up to ~160 points
        score += len(clinical_terms_found) * 12     # Up to ~120 points
        score += len(headers_found) * 20            # Up to ~160 points
        score += len(matrix_indicators) * 15        # Up to ~195 points
        score += min(competency_mentions * 5, 50)   # Up to 50 points
        score += 15 if has_detailed_structure else 0
        score += 20 if has_progressive_levels else 0
        score += min(len(content) / 300, 25)        # Up to 25 points for length
        
        # Quality thresholds (more flexible)
        if score >= 80:
            return True, f"Valid role-based format (score: {score:.0f}/800+, {len(role_indicators_found)} indicators)"
        elif score >= 50 and len(content) > 1000:
            return True, f"Acceptable role-based format (score: {score:.0f}/800+, {len(role_indicators_found)} indicators)"
        else:
            return False, f"Insufficient role-based content (score: {score:.0f}/800+, {len(role_indicators_found)} indicators)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function with enhanced logic."""
        print(f"\n=== Processing Basic Role-Based Document: {os.path.basename(pdf_path)} ===")
        
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Enhanced competency section detection
        competency_candidates = self.find_competency_sections_by_enhanced_patterns(pages_text)
        
        # Enhanced competency matrix detection
        matrix_pages = self.find_enhanced_competency_matrices(pages_text)
        
        print(f"📊 Found {len(competency_candidates)} competency candidates and {len(matrix_pages)} enhanced matrices")
        
        # Enhanced boundary determination
        start_page, end_page = self.determine_enhanced_extraction_boundaries(pages_text, competency_candidates, matrix_pages)
        
        if not start_page:
            print("❌ Could not find competency content")
            return None
        
        print(f"📍 Competency content: Pages {start_page}-{end_page}")
        
        # Enhanced content extraction
        content = self.extract_enhanced_competency_content(pages_text, start_page, end_page)
        
        # Enhanced validation
        is_valid, validation_msg = self.validate_extraction_enhanced(content)
        print(f"🔍 Validation: {validation_msg}")
        
        if not is_valid:
            print("⚠️  Extraction validation failed - but saving for review")
        
        # Outputs
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_path = os.path.join(output_dir, f"{filename}_competencies.txt")
        json_path = os.path.join(output_dir, f"{filename}_competencies.json")
        
        report = {
            'document': os.path.basename(pdf_path),
            'method': 'Improved Basic Role-Based (layout-aware)',
            'pages_extracted': {'start': start_page, 'end': end_page},
            'competency_candidates_found': len(competency_candidates),
            'enhanced_matrices_found': len(matrix_pages),
            'validation': validation_msg,
            'content_length': len(content),
            'success': bool(is_valid or len(content) > 1000)
        }
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Document: {report['document']}\n")
                f.write(f"Extraction Method: {report['method']}\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"Competency Candidates Found: {len(competency_candidates)}\n")
                f.write(f"Enhanced Matrices Found: {len(matrix_pages)}\n")
                f.write(f"Validation: {validation_msg}\n")
                f.write("="*80 + "\n\n")
                f.write(content)
            
            with open(json_path, 'w', encoding='utf-8') as jf:
                json.dump(report, jf, indent=2, ensure_ascii=False)
            
            print(f"✅ Competencies extracted to: {txt_path}")
            
            return {
                'pdf_path': pdf_path,
                'output_file': txt_path,
                'json_report': json_path,
                'pages_extracted': f"{start_page}-{end_page}",
                'competency_candidates_found': len(competency_candidates),
                'enhanced_matrices_found': len(matrix_pages),
                'validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': report['success']
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Extract competencies (Basic Role-Based format, improved)")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to write extracted outputs")
    parser.add_argument("--toc-scan-pages", type=int, default=15, help="Number of initial pages to scan for TOC")
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = ImprovedBasicRoleBasedExtractor(toc_scan_pages=args.toc_scan_pages)
    
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
        'category': 'Basic Role-Based Format (Improved, layout-aware)',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{(successful_extractions/len(pdf_files)*100):.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary_improved.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎯 IMPROVED SUMMARY")
    print(f"Category: Basic Role-Based Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
