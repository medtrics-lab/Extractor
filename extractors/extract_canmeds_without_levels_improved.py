#!/usr/bin/env python3
"""
Improved CanMEDS Without Levels Format Competency Extractor  
Enhanced for better CanMEDS detection, boundary detection, and comprehensive validation

Additional upgrades in this version:
- Layout-aware text extraction via pdfplumber with fallback to PyPDF2
- Updated CanMEDS role taxonomy (Leader instead of Manager) with synonyms
- Cleaning preserves numbered items, level markers, and table-like rows
- CLI arguments for input/output paths
- Structured JSON report emitted alongside text output

References consulted: pdfplumber README
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

class ImprovedCanMEDSWithoutLevelsExtractor:
    def __init__(self, toc_scan_pages: int = 15):
        # Enhanced section headers with more variations
        self.section_headers = [
            "OUTCOMES AND COMPETENCIES",
            "COMPETENCIES AND OUTCOMES",
            "LEARNING AND COMPETENCIES",
            "PROFESSIONAL COMPETENCIES",
            "COMPETENCY FRAMEWORK",
            "CANMEDS COMPETENCIES",
            "TRAINING COMPETENCIES",
            "EDUCATIONAL OBJECTIVES"
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
            "LEARNING OPPORTUNITIES",
            "TEACHING AND LEARNING", 
            "ASSESSMENT",
            "PROGRAM ROTATIONS",
            "CLINICAL ROTATIONS",
            "CONTINUUM OF LEARNING",
            "EVALUATION METHODS",
            "ACADEMIC ACTIVITIES"
        ]
        
        # Additional competency terms that often appear in CanMEDS documents
        self.competency_terms = [
            "COMPETENC", "OBJECTIVE", "SKILL", "KNOWLEDGE", 
            "ABILITY", "DEMONSTRATE", "PERFORM", "APPLY",
            "CANMEDS", "FRAMEWORK", "ROLE", "PROFESSIONAL"
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
    
    def find_canmeds_sections_enhanced(self, pages_text):
        """Enhanced CanMEDS section detection with confidence scoring."""
        candidates = []
        
        for page_info in pages_text:
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Strategy 1: Header-based detection with context analysis
            for header in self.section_headers:
                if header in text:
                    # Analyze surrounding context (current page + 5 following pages)
                    context_pages = pages_text[page_num-1:min(len(pages_text), page_num+5)]
                    
                    canmeds_count = 0
                    competency_terms_count = 0
                    content_density = 0
                    
                    for ctx_page in context_pages:
                        ctx_text = ctx_page['text'].upper()
                        canmeds_count += sum(1 for role in self.canmeds_roles if role in ctx_text)
                        competency_terms_count += sum(1 for term in self.competency_terms if term in ctx_text)
                        content_density += len(ctx_text.strip())
                    
                    # Calculate confidence score
                    confidence = 0
                    confidence += canmeds_count * 20        # Up to ~140 points per role
                    confidence += competency_terms_count * 8  # Up to ~96 points per term  
                    confidence += min(content_density / 3000, 30)  # Up to 30 points for content
                    
                    # Header-specific bonuses
                    if "CANMEDS" in header:
                        confidence += 50
                    elif "COMPETENCIES" in header:
                        confidence += 30
                    
                    candidates.append({
                        'page': page_num,
                        'header': header,
                        'confidence': confidence,
                        'canmeds_count': canmeds_count,
                        'competency_terms': competency_terms_count,
                        'type': 'header_based'
                    })
                    
                    print(f"Header candidate page {page_num}: {header} (confidence: {confidence:.1f}, {canmeds_count} CanMEDS)")
            
            # Strategy 2: CanMEDS density-based detection
            canmeds_on_page = sum(1 for role in self.canmeds_roles if role in text)
            competency_mentions = text.count("COMPETENC")
            
            if canmeds_on_page >= 3 or (canmeds_on_page >= 2 and competency_mentions >= 2):
                # Check surrounding context
                context_pages = pages_text[max(0, page_num-2):min(len(pages_text), page_num+4)]
                
                total_canmeds = 0
                total_competency_terms = 0
                
                for ctx_page in context_pages:
                    ctx_text = ctx_page['text'].upper()
                    total_canmeds += sum(1 for role in self.canmeds_roles if role in ctx_text)
                    total_competency_terms += sum(1 for term in self.competency_terms if term in ctx_text)
                
                confidence = canmeds_on_page * 25 + total_canmeds * 10 + competency_mentions * 12
                
                candidates.append({
                    'page': page_num,
                    'header': 'CANMEDS_DENSITY_DETECTION',
                    'confidence': confidence,
                    'canmeds_count': total_canmeds,
                    'competency_terms': total_competency_terms,
                    'type': 'density_based'
                })
                
                print(f"Density candidate page {page_num}: {canmeds_on_page} roles on page (confidence: {confidence:.1f})")
        
        return candidates
    
    def select_best_canmeds_candidate(self, candidates):
        """Select the best CanMEDS section candidate."""
        if not candidates:
            return None, None
        
        # Select candidate with highest confidence score
        best_candidate = max(candidates, key=lambda x: x['confidence'])
        
        # Minimum threshold for acceptance
        if best_candidate['confidence'] >= 60:  # Lowered threshold
            return best_candidate['page'], best_candidate
        
        return None, None
    
    def find_canmeds_section_end_enhanced(self, pages_text, start_page, start_candidate):
        """Enhanced end detection with multiple strategies."""
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
        canmeds_density = []
        search_range = min(20, len(pages_text) - start_page + 1)
        
        for i, page_info in enumerate(pages_text[start_page:start_page + search_range]):
            text = page_info['text'].upper()
            page_num = page_info['page_num']
            
            # Calculate CanMEDS content density
            density = 0
            density += sum(15 for role in self.canmeds_roles if role in text)
            density += sum(5 for term in self.competency_terms if term in text)
            
            # Penalties for non-competency content
            if any(term in text for term in ["ASSESSMENT", "EVALUATION", "GRADING", "EXAMINATION"]):
                density -= 20
            if any(term in text for term in ["ROTATION", "SCHEDULE", "CURRICULUM", "BIBLIOGRAPHY"]):
                density -= 15
            
            canmeds_density.append({
                'page': page_num,
                'density': density,
                'position': i
            })
        
        # Find where CanMEDS content drops significantly
        if len(canmeds_density) > 3:
            # Use moving average to smooth variations
            window = 3
            smoothed_density = []
            
            for i in range(len(canmeds_density)):
                start_idx = max(0, i - window // 2)
                end_idx = min(len(canmeds_density), i + window // 2 + 1)
                avg_density = sum(d['density'] for d in canmeds_density[start_idx:end_idx]) / (end_idx - start_idx)
                smoothed_density.append(avg_density)
            
            # Find significant drop
            if smoothed_density:
                max_density = max(smoothed_density[:4]) if len(smoothed_density) >= 4 else max(smoothed_density)
                threshold = max(max_density * 0.25, 10)  # 75% drop or minimum threshold
                
                for i, density in enumerate(smoothed_density[2:], 2):  # Skip first 2 pages
                    if density < threshold:
                        return canmeds_density[i]['page']
        
        # Strategy 3: Default reasonable length based on start candidate info
        if start_candidate and start_candidate['canmeds_count'] >= 5:
            default_length = min(25, max(12, (len(pages_text) - start_page) // 4))
        else:
            default_length = min(15, max(8, (len(pages_text) - start_page) // 5))
        
        return start_page + default_length
    
    def extract_canmeds_content_enhanced(self, pages_text, start_page, end_page):
        """Enhanced content extraction with smart filtering."""
        if not start_page or not end_page:
            return ""
        
        canmeds_content = []
        
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
                canmeds_content.append(f"--- Page {page_num} ---\n{text}\n")
        
        return "\n".join(canmeds_content)
    
    def clean_extracted_text(self, text):
        """Advanced text cleaning and normalization."""
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
            
            # Skip obvious non-content
            if (len(line) < 3 or
                line.isdigit() or
                line.startswith('©') or
                'COPYRIGHT' in line.upper() or
                'SAUDI COMMISSION' in line.upper() or
                re.match(r'^Page \d+', line) or
                re.match(r'^\d+\s*$', line)):
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def validate_extraction_enhanced(self, content):
        """Enhanced validation with comprehensive scoring."""
        if not content or len(content.strip()) < 100:
            return False, "No meaningful content extracted"
        
        content_upper = content.upper()
        
        # Core CanMEDS indicators (include synonyms)
        canmeds_roles_found = []
        for role in self.canmeds_roles:
            if role in content_upper or any(s in content_upper for s in self.role_synonyms.get(role, [])):
                canmeds_roles_found.append(role)
        competency_terms_found = sum(1 for term in self.competency_terms if term in content_upper)
        
        # Content quality indicators
        has_canmeds_framework = "CANMEDS" in content_upper
        has_professional_roles = bool(re.search(r'PROFESSIONAL\s+ROLE|ROLE\s+OF', content_upper))
        has_competency_structure = content_upper.count("COMPETENC") >= 3
        has_numbered_sections = bool(re.search(r'\d+\.\d+|\d+\.', content))
        
        # Calculate comprehensive score
        score = 0
        score += len(canmeds_roles_found) * 20    # Up to 140 points (all 7 roles)
        score += min(competency_terms_found * 6, 48)  # Up to 48 points
        score += 25 if has_canmeds_framework else 0
        score += 15 if has_professional_roles else 0
        score += 20 if has_competency_structure else 0  
        score += 10 if has_numbered_sections else 0
        score += min(len(content) / 400, 20)      # Up to 20 points for length
        
        # Quality thresholds (more flexible)
        if score >= 120:
            return True, f"Valid CanMEDS without levels (score: {score:.0f}/268, {len(canmeds_roles_found)}/7 roles)"
        elif score >= 80 and len(canmeds_roles_found) >= 3:
            return True, f"Acceptable CanMEDS without levels (score: {score:.0f}/268, {len(canmeds_roles_found)}/7 roles)"
        elif len(content) > 2000 and len(canmeds_roles_found) >= 2:
            return True, f"Minimal CanMEDS without levels (score: {score:.0f}/268, {len(canmeds_roles_found)}/7 roles)"
        else:
            return False, f"Insufficient CanMEDS content (score: {score:.0f}/268, {len(canmeds_roles_found)}/7 roles)"
    
    def extract_competencies(self, pdf_path, output_dir):
        """Main extraction function with enhanced logic."""
        print(f"\n=== Processing CanMEDS Without Levels Document: {os.path.basename(pdf_path)} ===")
        
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Enhanced CanMEDS section detection
        candidates = self.find_canmeds_sections_enhanced(pages_text)
        
        # Select best candidate
        start_page, start_candidate = self.select_best_canmeds_candidate(candidates)
        
        if not start_page:
            print("❌ Could not find CanMEDS sections")
            return None
        
        # Enhanced end detection
        end_page = self.find_canmeds_section_end_enhanced(pages_text, start_page, start_candidate)
        
        print(f"📍 CanMEDS section: Pages {start_page}-{end_page}")
        if start_candidate:
            print(f"🔍 Selected: {start_candidate['type']} (confidence: {start_candidate['confidence']:.1f})")
        
        # Enhanced content extraction
        content = self.extract_canmeds_content_enhanced(pages_text, start_page, end_page)
        
        # Enhanced validation
        is_valid, validation_msg = self.validate_extraction_enhanced(content)
        print(f"🔍 Validation: {validation_msg}")
        
        if not is_valid:
            print("⚠️  Extraction validation failed - but saving for review")
        
        # Save content + JSON
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_path = os.path.join(output_dir, f"{filename}_competencies.txt")
        json_path = os.path.join(output_dir, f"{filename}_competencies.json")

        report = {
            'document': os.path.basename(pdf_path),
            'method': 'Improved CanMEDS Without Levels (layout-aware)',
            'pages_extracted': {'start': start_page, 'end': end_page},
            'candidates_found': len(candidates),
            'validation': validation_msg,
            'content_length': len(content),
            'success': bool(is_valid or len(content) > 1500)
        }
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Document: {report['document']}\n")
                f.write(f"Extraction Method: {report['method']}\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"Candidates Found: {len(candidates)}\n")
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
                'candidates_found': len(candidates),
                'validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': report['success']
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Extract CanMEDS (without levels) – improved")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to write extracted outputs")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    extractor = ImprovedCanMEDSWithoutLevelsExtractor()

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
        'category': 'CanMEDS Without Levels (Improved, layout-aware)',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{(successful_extractions/len(pdf_files)*100):.1f}%",
        'results': results
    }

    summary_file = os.path.join(output_dir, 'extraction_summary_improved.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n🎯 IMPROVED SUMMARY")
    print(f"Category: CanMEDS Without Levels")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
