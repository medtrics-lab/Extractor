#!/usr/bin/env python3
"""
Improved Standard CanMEDS Format Competency Extractor
Enhanced for better TOC parsing, content boundary detection, and robust fallback mechanisms

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
    import pdfplumber  # https://github.com/jsvine/pdfplumber
except ImportError:  # graceful fallback
    pdfplumber = None

# Fallback parser
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

class ImprovedStandardCanMEDSExtractor:
    def __init__(self, keep_short_numbered: bool = True, toc_scan_pages: int = 15):
        self.section_headers = [
            "LEARNING AND COMPETENCIES",
            "OUTCOMES AND COMPETENCIES",
            "LEARNING OUTCOMES AND COMPETENCIES",
            "PROFESSIONAL COMPETENCIES",
            "COMPETENCIES AND OUTCOMES"
        ]

        # Updated roles: LEADER instead of MANAGER; include synonyms and legacy
        self.canmeds_roles = [
            "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR",
            "LEADER", "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL"
        ]
        self.role_synonyms = {
            "LEADER": ["LEADER", "LEADERSHIP", "MANAGER"],  # include legacy wording
            "HEALTH ADVOCATE": ["HEALTH ADVOCATE", "ADVOCACY"],
            "PROFESSIONAL": ["PROFESSIONAL", "PROFESSIONALISM"],
        }

        self.section_end_markers = [
            "CONTINUUM OF LEARNING",
            "ASSESSMENT AND EVALUATION",
            "TEACHING AND LEARNING",
            "PROGRAM ROTATIONS",
            "CLINICAL ROTATIONS",
            "RESEARCH AND SCHOLARLY ACTIVITY",
            "EVALUATION METHODS",
            "REFERENCES", "BIBLIOGRAPHY"
        ]

        self.competency_terms = [
            "COMPETENC", "OBJECTIVE", "SKILL", "KNOWLEDGE",
            "ABILITY", "DEMONSTRATE", "PERFORM", "APPLY"
        ]

        self.keep_short_numbered = keep_short_numbered
        self.toc_scan_pages = toc_scan_pages

    def _extract_with_pdfplumber(self, pdf_path: str):
        pages_text = []
        # Conservative laparams; allow default layout analysis
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                # Try to preserve layout to keep columns/tables closer to original
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
        """Extract text from PDF with page tracking using pdfplumber if available."""
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return None
            
        try:
            pages_text = None
            extraction_method = "unknown"
            
            # Try pdfplumber first (layout-aware)
            if pdfplumber is not None:
                try:
                    pages_text = self._extract_with_pdfplumber(pdf_path)
                    extraction_method = "pdfplumber"
                except Exception as e:
                    print(f"pdfplumber extraction failed: {e}")
                    pages_text = None
            
            # Fallback to PyPDF2 if needed
            if not pages_text or all(not (p.get("text") or "").strip() for p in pages_text):
                print("Falling back to PyPDF2 extraction...")
                try:
                    pages_text = self._extract_with_pypdf2(pdf_path)
                    extraction_method = "PyPDF2"
                except Exception as e:
                    print(f"PyPDF2 extraction also failed: {e}")
                    return None
            
            if pages_text:
                print(f"Successfully extracted {len(pages_text)} pages using {extraction_method}")
            
            return pages_text
            
        except Exception as e:
            print(f"Critical error reading PDF {pdf_path}: {e}")
            return None

    def parse_table_of_contents_enhanced(self, pages_text):
        """Enhanced TOC parsing with multiple pattern recognition strategies."""
        toc_info = {}
        # Check first N pages for TOC
        for page_info in pages_text[: self.toc_scan_pages]:
            text = page_info['text'] or ""
            lines = text.split('\n')

            for line in lines:
                line_clean = line.strip()
                line_upper = line_clean.upper()

                if not line_clean:
                    continue

                for header in self.section_headers:
                    if header in line_upper:
                        page_patterns = [
                            r'(\d+)$',
                            r'\.{3,}\s*(\d+)',
                            r'\.{2,}\s*(\d+)',
                            r'\s+(\d+)\s*$',
                            r'.*?(\d+)\s*$'
                        ]
                        for pattern in page_patterns:
                            page_match = re.search(pattern, line_clean)
                            if page_match:
                                page_num = int(page_match.group(1))
                                if 5 <= page_num <= len(pages_text):
                                    toc_info['competency_start_page'] = page_num
                                    toc_info['competency_header'] = header
                                    print(f"Found competency section in TOC: '{header}' at page {page_num}")
                                    break
                        if 'competency_start_page' in toc_info:
                            break

                if 'competency_start_page' in toc_info:
                    for end_marker in self.section_end_markers:
                        if end_marker in line_upper:
                            for pattern in page_patterns:
                                page_match = re.search(pattern, line_clean)
                                if page_match:
                                    page_num = int(page_match.group(1))
                                    if page_num > toc_info['competency_start_page'] and page_num <= len(pages_text):
                                        toc_info['competency_end_page'] = page_num
                                        print(f"Found competency section end in TOC: '{end_marker}' at page {page_num}")
                                        break
                            if 'competency_end_page' in toc_info:
                                break
        return toc_info

    def find_competency_section_by_structure_enhanced(self, pages_text):
        candidates = []
        for page_info in pages_text:
            text = (page_info['text'] or "").upper()
            page_num = page_info['page_num']

            for header in self.section_headers:
                if header in text:
                    validation_range = pages_text[max(0, page_num-1):min(len(pages_text), page_num+6)]

                    canmeds_count = 0
                    competency_terms_count = 0
                    content_quality = 0

                    for val_page in validation_range:
                        val_text = (val_page['text'] or "").upper()
                        # Count roles and synonyms
                        for role in self.canmeds_roles:
                            role_hits = role in val_text
                            synonym_hits = any(s in val_text for s in self.role_synonyms.get(role, []))
                            if role_hits or synonym_hits:
                                canmeds_count += 1
                        competency_terms_count += sum(1 for term in self.competency_terms if term in val_text)

                        if any(indicator in val_text for indicator in ["1.1", "1.2", "2.1", "2.2"]):
                            content_quality += 10
                        if "CANMEDS" in val_text:
                            content_quality += 15
                        if len(val_text.strip()) > 1000:
                            content_quality += 5

                    confidence = 0
                    confidence += canmeds_count * 12
                    confidence += competency_terms_count * 5
                    confidence += content_quality

                    if header == "LEARNING AND COMPETENCIES":
                        confidence += 20
                    elif header == "OUTCOMES AND COMPETENCIES":
                        confidence += 25

                    candidates.append({
                        'page': page_num,
                        'header': header,
                        'confidence': confidence,
                        'canmeds_count': canmeds_count,
                        'competency_terms': competency_terms_count
                    })
                    print(f"Structure candidate page {page_num}: {header} (confidence: {confidence:.1f})")
        if candidates:
            best_candidate = max(candidates, key=lambda x: x['confidence'])
            if best_candidate['confidence'] >= 25:
                return best_candidate['page']
        return None

    def find_competency_section_end_enhanced(self, pages_text, start_page):
        if not start_page:
            return None
        for page_info in pages_text[start_page:]:
            text = (page_info['text'] or "").upper()
            page_num = page_info['page_num']
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    print(f"Found explicit end marker at page {page_num}: {end_marker}")
                    return page_num

        competency_density = []
        search_range = min(25, len(pages_text) - start_page + 1)
        for i, page_info in enumerate(pages_text[start_page:start_page + search_range]):
            text = (page_info['text'] or "").upper()
            page_num = page_info['page_num']

            density = 0
            for role in self.canmeds_roles:
                if role in text or any(s in text for s in self.role_synonyms.get(role, [])):
                    density += 8
            density += sum(3 for term in self.competency_terms if term in text)

            if any(term in text for term in ["ASSESSMENT", "EVALUATION", "GRADING", "EXAMINATION"]):
                density -= 15
            if any(term in text for term in ["ROTATION", "SCHEDULE", "CURRICULUM"]):
                density -= 10

            competency_density.append({'page': page_num, 'density': density, 'position': i})

        if len(competency_density) > 3:
            window = 3
            smoothed_density = []
            for i in range(len(competency_density)):
                start_idx = max(0, i - window // 2)
                end_idx = min(len(competency_density), i + window // 2 + 1)
                avg_density = sum(d['density'] for d in competency_density[start_idx:end_idx]) / (end_idx - start_idx)
                smoothed_density.append(avg_density)
            if smoothed_density:
                max_density = max(smoothed_density[:5]) if len(smoothed_density) >= 5 else max(smoothed_density)
                threshold = max(max_density * 0.25, 5)
                for i, density in enumerate(smoothed_density[2:], 2):
                    if density < threshold:
                        return competency_density[i]['page']
        default_length = min(20, max(8, (len(pages_text) - start_page) // 4))
        return start_page + default_length

    def clean_extracted_text(self, text):
        """Advanced text cleaning and normalization with preservation of numbered items and table-like rows."""
        if not text:
            return ""
        
        # Normalize excessive whitespace but preserve meaningful spacing
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
            boilerplate_patterns = [
                r'^©',
                r'COPYRIGHT',
                r'SAUDI COMMISSION',
                r'^PAGE\s+\d+',
                r'^\s*\d+\s*$',  # lone page numbers
                r'^SCFHS\s*$',   # common header abbreviation
            ]
            if any(re.search(pattern, up) for pattern in boilerplate_patterns):
                continue
            
            # Identify content patterns to preserve
            numbered = bool(re.match(r'^(\d+\.)+\s*\S', line) or re.match(r'^\d+\s+\S', line))
            subnumbered = bool(re.match(r'^\d+\.\d+(\.\d+)*\s+\S', line))
            level_mark = bool(re.match(r'^[FR][1-5]\b', up) or re.match(r'^(LEVEL|YEAR)\s+\d', up))
            bullet = bool(re.match(r'^[\-•▪]\s+\S', line))
            header = bool(re.match(r'^[A-Z][A-Z\s]+:?\s*$', up) and len(up.split()) <= 5)
            looks_tabular = ('\t' in raw) or (raw.count('  ') >= 2)
            
            # Filter out very short non-meaningful content
            if len(up) < 3 and not (numbered or subnumbered or bullet or level_mark):
                continue
            if up.isdigit() and not (numbered or subnumbered or level_mark):
                continue
            
            # Normalize internal spacing while preserving column-like structures
            if '\t' in raw:
                # Convert tabs to consistent spacing
                normalized = re.sub(r'\t+', '  ', raw)
            elif raw.count('  ') >= 3:
                # Preserve column-like spacing but make it consistent
                normalized = re.sub(r'  +', '  ', raw)
            else:
                normalized = raw
            
            cleaned_lines.append(normalized)
        
        return '\n'.join(cleaned_lines)

    def extract_competency_content_enhanced(self, pages_text, start_page, end_page):
        if not start_page or not end_page:
            return ""
        competency_content = []
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text'] or ""
            page_num = page_info['page_num']
            if page_num == start_page:
                text_upper = text.upper()
                best_start = 0
                for header in self.section_headers:
                    if header in text_upper:
                        header_pos = text_upper.find(header)
                        if header_pos != -1:
                            best_start = header_pos
                            break
                text = text[best_start:]
            text = self.clean_extracted_text(text)
            if text.strip():
                competency_content.append(f"--- Page {page_num} ---\n{text}\n")
        return "\n".join(competency_content)

    def validate_extraction_enhanced(self, content):
        if not content or len(content.strip()) < 50:
            return False, "No meaningful content extracted"
        up = content.upper()
        # Count roles including synonyms
        role_hits = 0
        for role in self.canmeds_roles:
            if role in up or any(s in up for s in self.role_synonyms.get(role, [])):
                role_hits += 1
        competency_terms_count = sum(1 for term in self.competency_terms if term in up)
        has_numbered_sections = bool(re.search(r'\d+\.\d+', content))
        has_canmeds_framework = "CANMEDS" in up
        has_progressive_levels = bool(re.search(r'\b[FR][1-5]\b', up))
        content_length = len(content)
        has_detailed_competencies = up.count("COMPETENC") >= 3

        score = 0
        score += min(role_hits * 12, 48)
        score += min(competency_terms_count * 4, 24)
        score += 15 if has_numbered_sections else 0
        score += 10 if has_canmeds_framework else 0
        score += 8 if has_progressive_levels else 0
        score += min(content_length / 200, 15)
        score += 10 if has_detailed_competencies else 0

        if score >= 60:
            return True, f"Valid CanMEDS format (score: {score:.0f}/130, {role_hits}/7 roles)"
        elif score >= 40 and content_length > 1000:
            return True, f"Acceptable CanMEDS format (score: {score:.0f}/130, {role_hits}/7 roles)"
        else:
            return False, f"Insufficient CanMEDS content (score: {score:.0f}/130, {role_hits}/7 roles)"

    def extract_competencies(self, pdf_path, output_dir):
        print(f"\n=== Processing Standard CanMEDS Document: {os.path.basename(pdf_path)} ===")
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        toc_info = self.parse_table_of_contents_enhanced(pages_text)
        start_page = toc_info.get('competency_start_page')
        end_page = toc_info.get('competency_end_page')
        if start_page:
            print(f"📖 Using TOC information: Pages {start_page}-{end_page or 'TBD'}")
        else:
            print("📖 TOC parsing failed, using structure analysis")
            start_page = self.find_competency_section_by_structure_enhanced(pages_text)
        if not start_page:
            print("❌ Could not find competency section")
            return None
        if not end_page:
            end_page = self.find_competency_section_end_enhanced(pages_text, start_page)
        print(f"📍 Competency section: Pages {start_page}-{end_page}")
        content = self.extract_competency_content_enhanced(pages_text, start_page, end_page)
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
            'method': 'Improved Standard CanMEDS (layout-aware)',
            'pages_extracted': {'start': start_page, 'end': end_page},
            'validation': validation_msg,
            'content_length': len(content),
            'success': bool(is_valid or len(content) > 800)
        }
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Document: {report['document']}\n")
                f.write(f"Extraction Method: {report['method']}\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
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
                'validation': validation_msg,
                'content_length': len(content),
                'extraction_successful': report['success']
            }
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description="Extract CanMEDS competencies (Standard format, improved)")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to write extracted outputs")
    parser.add_argument("--toc-scan-pages", type=int, default=15, help="Number of initial pages to scan for TOC")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    extractor = ImprovedStandardCanMEDSExtractor(toc_scan_pages=args.toc_scan_pages)

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
        'category': 'Standard CanMEDS Format (Improved, layout-aware)',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'extraction_rate': f"{(successful_extractions/len(pdf_files)*100):.1f}%",
        'results': results
    }

    summary_file = os.path.join(output_dir, 'extraction_summary_improved.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n🎯 IMPROVED SUMMARY")
    print(f"Category: Standard CanMEDS Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
