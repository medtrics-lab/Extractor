#!/usr/bin/env python3
"""
Enhanced Standard CanMEDS Format Competency Extractor
Major improvements for better content type classification, template recognition, and validation

Key enhancements:
- Content type classification to distinguish competencies from other document sections
- Template recognition for common SCFHS document patterns
- Multi-stage validation pipeline
- Improved confidence scoring based on content quality
- Better section boundary detection with content analysis
"""

import re
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set

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

class ContentTypeClassifier:
    """Classify document sections by content type"""
    
    def __init__(self):
        # Define patterns for different content types
        self.content_patterns = {
            'competency_framework': {
                'headers': [
                    "LEARNING AND COMPETENCIES", "OUTCOMES AND COMPETENCIES",
                    "PROFESSIONAL COMPETENCIES", "COMPETENCIES AND OUTCOMES",
                    "COMPETENCY FRAMEWORK", "TRAINING COMPETENCIES"
                ],
                'indicators': [
                    "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR", "LEADER",
                    "HEALTH ADVOCATE", "SCHOLAR", "PROFESSIONAL", "CANMEDS"
                ],
                'structure_markers': [
                    r'\d+\.\d+\.\d+', r'\d+\.\d+', 'DEMONSTRATE', 'APPLY', 'PERFORM'
                ]
            },
            'program_structure': {
                'headers': [
                    "PROGRAM STRUCTURE", "PROGRAM REQUIREMENTS", "PROGRAM OVERVIEW",
                    "TRAINING STRUCTURE", "PROGRAM ORGANIZATION", "CURRICULUM STRUCTURE"
                ],
                'indicators': [
                    "DURATION", "ROTATION", "REQUIREMENTS", "ADMISSION", "ENTRY"
                ]
            },
            'references': {
                'headers': ["REFERENCES", "BIBLIOGRAPHY", "CITATIONS"],
                'indicators': ["DOI:", "PMID:", "ISBN:", "ET AL", "J.", "VOL."]
            },
            'assessment': {
                'headers': [
                    "ASSESSMENT", "EVALUATION", "EXAMINATION", "TESTING"
                ],
                'indicators': ["MCQ", "OSCE", "EXAM", "GRADE", "PASS", "FAIL"]
            },
            'appendices': {
                'headers': ["APPENDIX", "APPENDICES", "ATTACHMENT"],
                'indicators': ["TABLE", "FORM", "CHECKLIST"]
            }
        }
    
    def classify_section(self, text: str, header: str = "") -> Dict[str, float]:
        """Classify a section and return confidence scores for each content type"""
        text_upper = text.upper()
        header_upper = header.upper()
        scores = {}
        
        for content_type, patterns in self.content_patterns.items():
            score = 0
            
            # Header matching
            for h in patterns['headers']:
                if h in header_upper or h in text_upper[:200]:
                    score += 30
            
            # Indicator matching
            for indicator in patterns['indicators']:
                count = text_upper.count(indicator)
                score += min(count * 3, 15)
            
            # Structure marker matching (for competency framework)
            if content_type == 'competency_framework' and 'structure_markers' in patterns:
                for marker in patterns['structure_markers']:
                    if isinstance(marker, str):
                        if marker in text_upper:
                            score += 5
                    else:  # regex pattern
                        matches = len(re.findall(marker, text))
                        score += min(matches * 2, 10)
            
            scores[content_type] = score
        
        return scores

class SCFHSTemplateRecognizer:
    """Recognize common SCFHS document templates and patterns"""
    
    def __init__(self):
        self.template_patterns = {
            'standard_canmeds': {
                'toc_patterns': [
                    r'LEARNING AND COMPETENCIES.*?(\d+)',
                    r'OUTCOMES AND COMPETENCIES.*?(\d+)',
                    r'PROFESSIONAL COMPETENCIES.*?(\d+)'
                ],
                'section_flow': [
                    "INTRODUCTION", "PROGRAM", "LEARNING", "COMPETENCIES",
                    "ASSESSMENT", "REFERENCES"
                ],
                'competency_markers': [
                    "MEDICAL EXPERT", "COMMUNICATOR", "COLLABORATOR"
                ]
            },
            'advanced_key_enabling': {
                'toc_patterns': [
                    r'KEY COMPETENCIES.*?(\d+)',
                    r'ENABLING COMPETENCIES.*?(\d+)'
                ],
                'competency_markers': [
                    "KEY COMPETENCIES", "ENABLING COMPETENCIES"
                ]
            }
        }
    
    def identify_template(self, pages_text: List[Dict]) -> str:
        """Identify the document template type"""
        full_text = " ".join([p.get('text', '') for p in pages_text[:10]]).upper()
        
        for template_name, patterns in self.template_patterns.items():
            score = 0
            
            # Check for template-specific markers
            for marker in patterns.get('competency_markers', []):
                if marker in full_text:
                    score += 1
            
            # Check TOC patterns
            for pattern in patterns.get('toc_patterns', []):
                if re.search(pattern, full_text):
                    score += 2
            
            if score >= 2:
                return template_name
        
        return 'unknown'

class EnhancedStandardCanMEDSExtractor:
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
        
        # Initialize new components
        self.classifier = ContentTypeClassifier()
        self.template_recognizer = SCFHSTemplateRecognizer()

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

    def analyze_document_structure(self, pages_text: List[Dict]) -> Dict:
        """Pre-analyze document to understand its structure and template"""
        analysis = {
            'template': self.template_recognizer.identify_template(pages_text),
            'section_candidates': [],
            'document_length': len(pages_text)
        }
        
        print(f"📋 Document template identified: {analysis['template']}")
        
        # Find all potential competency sections
        for page_info in pages_text:
            text = page_info.get('text', '')
            page_num = page_info['page_num']
            
            for header in self.section_headers:
                if header in text.upper():
                    # Analyze the section
                    section_start = text.upper().find(header)
                    section_text = text[section_start:section_start+2000]  # Sample
                    
                    # Classify content type
                    classification = self.classifier.classify_section(section_text, header)
                    
                    candidate = {
                        'page': page_num,
                        'header': header,
                        'start_position': section_start,
                        'classification': classification,
                        'competency_confidence': classification.get('competency_framework', 0)
                    }
                    analysis['section_candidates'].append(candidate)
                    
                    print(f"🔍 Found section candidate at page {page_num}: {header} "
                          f"(competency confidence: {candidate['competency_confidence']:.1f})")
        
        return analysis

    def parse_table_of_contents_enhanced(self, pages_text, document_analysis):
        """Enhanced TOC parsing with template awareness and content validation"""
        toc_info = {}
        template = document_analysis['template']
        
        # Use template-specific patterns if available
        if template in self.template_recognizer.template_patterns:
            toc_patterns = self.template_recognizer.template_patterns[template]['toc_patterns']
        else:
            toc_patterns = [
                rf'{header}.*?(\d+)' for header in self.section_headers
            ]
        
        # Check first N pages for TOC
        for page_info in pages_text[:self.toc_scan_pages]:
            text = page_info['text'] or ""
            lines = text.split('\n')

            for line in lines:
                line_clean = line.strip()
                line_upper = line_clean.upper()

                if not line_clean:
                    continue

                # Try template-specific patterns first
                for pattern in toc_patterns:
                    match = re.search(pattern, line_upper)
                    if match:
                        page_num = int(match.group(1))
                        if 5 <= page_num <= len(pages_text):
                            # Validate that this page actually contains competencies
                            target_page = pages_text[page_num - 1]
                            target_text = target_page.get('text', '')
                            
                            # Use classifier to validate content type
                            classification = self.classifier.classify_section(target_text)
                            competency_score = classification.get('competency_framework', 0)
                            
                            if competency_score >= 20:  # Minimum threshold for competency content
                                toc_info['competency_start_page'] = page_num
                                toc_info['competency_header'] = line_clean
                                toc_info['validation_score'] = competency_score
                                print(f"✅ Found validated competency section in TOC: Page {page_num} "
                                      f"(validation score: {competency_score:.1f})")
                                break
                
                if 'competency_start_page' in toc_info:
                    # Find end page
                    for end_marker in self.section_end_markers:
                        if end_marker in line_upper:
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
                                    end_page_num = int(page_match.group(1))
                                    if end_page_num > toc_info['competency_start_page'] and end_page_num <= len(pages_text):
                                        toc_info['competency_end_page'] = end_page_num
                                        print(f"✅ Found competency section end in TOC: Page {end_page_num}")
                                        break
                            if 'competency_end_page' in toc_info:
                                break
        
        return toc_info

    def find_competency_section_by_structure_enhanced(self, pages_text, document_analysis):
        """Enhanced structure-based search with content type classification"""
        candidates = document_analysis['section_candidates']
        
        if not candidates:
            print("❌ No section candidates found during document analysis")
            return None
        
        # Score and rank candidates
        for candidate in candidates:
            page_num = candidate['page']
            validation_range = pages_text[max(0, page_num-1):min(len(pages_text), page_num+6)]
            
            # Enhanced scoring based on content analysis
            canmeds_count = 0
            competency_terms_count = 0
            content_quality = 0
            
            for val_page in validation_range:
                val_text = (val_page['text'] or "").upper()
                
                # Count structured CanMEDS roles
                for role in self.canmeds_roles:
                    role_hits = role in val_text
                    synonym_hits = any(s in val_text for s in self.role_synonyms.get(role, []))
                    if role_hits or synonym_hits:
                        canmeds_count += 1
                        
                competency_terms_count += sum(1 for term in self.competency_terms if term in val_text)
                
                # Quality indicators
                if any(indicator in val_text for indicator in ["1.1", "1.2", "2.1", "2.2"]):
                    content_quality += 10
                if "CANMEDS" in val_text:
                    content_quality += 15
                if len(val_text.strip()) > 1000:
                    content_quality += 5
            
            # Content type penalty/bonus
            content_scores = candidate['classification']
            competency_bonus = content_scores.get('competency_framework', 0)
            structure_penalty = content_scores.get('program_structure', 0) * -0.5
            reference_penalty = content_scores.get('references', 0) * -1.0
            
            # Calculate final confidence
            confidence = 0
            confidence += canmeds_count * 12
            confidence += competency_terms_count * 5
            confidence += content_quality
            confidence += competency_bonus
            confidence += structure_penalty
            confidence += reference_penalty
            
            # Header bonus
            if candidate['header'] == "LEARNING AND COMPETENCIES":
                confidence += 20
            elif candidate['header'] == "OUTCOMES AND COMPETENCIES":
                confidence += 25
            
            candidate['final_confidence'] = confidence
            
            print(f"📊 Candidate page {page_num}: {candidate['header']} "
                  f"(confidence: {confidence:.1f}, CanMEDS: {canmeds_count}/7)")
        
        # Select best candidate
        best_candidate = max(candidates, key=lambda x: x['final_confidence'])
        
        if best_candidate['final_confidence'] >= 30:  # Raised threshold
            return best_candidate['page']
        else:
            print(f"⚠️  Best candidate confidence too low: {best_candidate['final_confidence']:.1f}")
            return None

    def find_competency_section_end_enhanced(self, pages_text, start_page):
        """Enhanced end detection with content analysis"""
        if not start_page:
            return None
            
        # Look for explicit end markers first
        for page_info in pages_text[start_page:]:
            text = (page_info['text'] or "").upper()
            page_num = page_info['page_num']
            
            for end_marker in self.section_end_markers:
                if end_marker in text:
                    # Validate that this actually ends the competency section
                    remaining_text = text[text.find(end_marker):]
                    if len(remaining_text) > 500:  # Substantial content after marker
                        classification = self.classifier.classify_section(remaining_text)
                        competency_score = classification.get('competency_framework', 0)
                        if competency_score < 10:  # Low competency content after marker
                            print(f"✅ Found validated end marker at page {page_num}: {end_marker}")
                            return page_num
                    else:
                        print(f"✅ Found end marker at page {page_num}: {end_marker}")
                        return page_num

        # Fallback to density analysis
        competency_density = []
        search_range = min(25, len(pages_text) - start_page + 1)
        
        for i, page_info in enumerate(pages_text[start_page:start_page + search_range]):
            text = (page_info['text'] or "").upper()
            page_num = page_info['page_num']

            # Calculate competency content density
            density = 0
            for role in self.canmeds_roles:
                if role in text or any(s in text for s in self.role_synonyms.get(role, [])):
                    density += 8
            density += sum(3 for term in self.competency_terms if term in text)

            # Content type analysis
            classification = self.classifier.classify_section(text)
            density += classification.get('competency_framework', 0) * 0.5
            density -= classification.get('assessment', 0) * 0.3
            density -= classification.get('references', 0) * 0.5

            competency_density.append({'page': page_num, 'density': density, 'position': i})

        if len(competency_density) > 3:
            # Find where density drops significantly
            window = 3
            for i in range(window, len(competency_density) - window):
                current_avg = sum(d['density'] for d in competency_density[i-window:i+window+1]) / (2*window + 1)
                if competency_density[i]['density'] < current_avg * 0.4:  # Significant drop
                    return competency_density[i]['page']
                    
        # Default fallback
        default_length = min(20, max(8, (len(pages_text) - start_page) // 4))
        return start_page + default_length

    def validate_extraction_comprehensive(self, content: str, start_page: int, end_page: int, pages_text: List[Dict]) -> Tuple[bool, str, Dict]:
        """Comprehensive validation with detailed analysis"""
        if not content or len(content.strip()) < 50:
            return False, "No meaningful content extracted", {}
        
        up = content.upper()
        
        # Basic metrics
        role_hits = set()
        for role in self.canmeds_roles:
            if role in up or any(s in up for s in self.role_synonyms.get(role, [])):
                role_hits.add(role)
        
        competency_terms_count = sum(1 for term in self.competency_terms if term in up)
        has_numbered_sections = bool(re.search(r'\d+\.\d+', content))
        has_canmeds_framework = "CANMEDS" in up
        has_progressive_levels = bool(re.search(r'\b[FR][1-5]\b', up))
        content_length = len(content)
        has_detailed_competencies = up.count("COMPETENC") >= 3
        
        # Content type analysis
        classification = self.classifier.classify_section(content)
        competency_score = classification.get('competency_framework', 0)
        contamination_score = (
            classification.get('references', 0) + 
            classification.get('program_structure', 0) + 
            classification.get('appendices', 0)
        )
        
        # Calculate comprehensive score
        score = 0
        score += min(len(role_hits) * 12, 84)  # Up to 84 points for all 7 roles
        score += min(competency_terms_count * 3, 18)  # Up to 18 points
        score += 15 if has_numbered_sections else 0
        score += 10 if has_canmeds_framework else 0
        score += 8 if has_progressive_levels else 0
        score += min(content_length / 300, 12)  # Up to 12 points for length
        score += 10 if has_detailed_competencies else 0
        score += min(competency_score * 0.3, 15)  # Content type bonus
        score -= min(contamination_score * 0.2, 10)  # Contamination penalty
        
        # Detailed analysis
        analysis = {
            'role_count': len(role_hits),
            'roles_found': list(role_hits),
            'competency_terms_count': competency_terms_count,
            'has_structured_content': has_numbered_sections,
            'content_length': content_length,
            'competency_type_score': competency_score,
            'contamination_score': contamination_score,
            'page_range_size': end_page - start_page + 1 if end_page else 1
        }
        
        # Validation thresholds
        if score >= 80 and len(role_hits) >= 5:
            return True, f"Excellent CanMEDS format (score: {score:.0f}/150, {len(role_hits)}/7 roles)", analysis
        elif score >= 60 and len(role_hits) >= 4:
            return True, f"Good CanMEDS format (score: {score:.0f}/150, {len(role_hits)}/7 roles)", analysis
        elif score >= 45 and content_length > 1500:
            return True, f"Acceptable CanMEDS format (score: {score:.0f}/150, {len(role_hits)}/7 roles)", analysis
        else:
            return False, f"Insufficient CanMEDS content (score: {score:.0f}/150, {len(role_hits)}/7 roles)", analysis

    def clean_extracted_text(self, text):
        """Advanced text cleaning and normalization with preservation of structure"""
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
            
            # Filter out very short non-meaningful content
            if len(up) < 3 and not (numbered or subnumbered or bullet or level_mark):
                continue
            if up.isdigit() and not (numbered or subnumbered or level_mark):
                continue
            
            # Normalize internal spacing while preserving structure
            if '\t' in raw:
                normalized = re.sub(r'\t+', '  ', raw)
            elif raw.count('  ') >= 3:
                normalized = re.sub(r'  +', '  ', raw)
            else:
                normalized = raw
            
            cleaned_lines.append(normalized)
        
        return '\n'.join(cleaned_lines)

    def extract_competency_content_enhanced(self, pages_text, start_page, end_page):
        """Enhanced content extraction with better boundary detection"""
        if not start_page or not end_page:
            return ""
            
        competency_content = []
        
        for page_info in pages_text[start_page-1:end_page]:
            text = page_info['text'] or ""
            page_num = page_info['page_num']
            
            if page_num == start_page:
                # Find the actual start of competency content
                text_upper = text.upper()
                best_start = 0
                for header in self.section_headers:
                    if header in text_upper:
                        header_pos = text_upper.find(header)
                        if header_pos != -1:
                            best_start = header_pos
                            break
                text = text[best_start:]
            
            # Clean and validate page content
            cleaned_text = self.clean_extracted_text(text)
            
            if cleaned_text.strip():
                # Quick content validation
                classification = self.classifier.classify_section(cleaned_text)
                competency_score = classification.get('competency_framework', 0)
                contamination_score = (
                    classification.get('references', 0) + 
                    classification.get('appendices', 0)
                )
                
                # Include page only if it has reasonable competency content
                if competency_score >= 5 or contamination_score < 20:
                    competency_content.append(f"--- Page {page_num} ---\n{cleaned_text}\n")
                else:
                    print(f"⚠️  Skipping page {page_num} - low competency content (score: {competency_score:.1f})")
        
        return "\n".join(competency_content)

    def extract_competencies(self, pdf_path, output_dir):
        """Enhanced extraction with comprehensive analysis pipeline"""
        print(f"\n=== Processing Enhanced Standard CanMEDS Document: {os.path.basename(pdf_path)} ===")
        
        # Step 1: Extract text
        pages_text = self.extract_text_from_pdf(pdf_path)
        if not pages_text:
            return None
        
        # Step 2: Analyze document structure
        document_analysis = self.analyze_document_structure(pages_text)
        
        # Step 3: Enhanced TOC parsing with validation
        toc_info = self.parse_table_of_contents_enhanced(pages_text, document_analysis)
        start_page = toc_info.get('competency_start_page')
        end_page = toc_info.get('competency_end_page')
        
        if start_page:
            print(f"📖 Using validated TOC information: Pages {start_page}-{end_page or 'TBD'}")
        else:
            print("📖 TOC parsing failed, using enhanced structure analysis")
            start_page = self.find_competency_section_by_structure_enhanced(pages_text, document_analysis)
        
        if not start_page:
            print("❌ Could not find competency section")
            return None
        
        if not end_page:
            end_page = self.find_competency_section_end_enhanced(pages_text, start_page)
        
        print(f"📍 Competency section: Pages {start_page}-{end_page}")
        
        # Step 4: Extract content with validation
        content = self.extract_competency_content_enhanced(pages_text, start_page, end_page)
        
        # Step 5: Comprehensive validation
        is_valid, validation_msg, detailed_analysis = self.validate_extraction_comprehensive(
            content, start_page, end_page, pages_text
        )
        
        print(f"🔍 Validation: {validation_msg}")
        
        if not is_valid:
            print("⚠️  Extraction validation failed - reviewing...")
            
            # Additional validation details
            if detailed_analysis.get('contamination_score', 0) > 30:
                print("⚠️  High contamination score detected - may contain non-competency content")
            if detailed_analysis.get('role_count', 0) < 3:
                print("⚠️  Insufficient CanMEDS roles found")

        # Step 6: Generate outputs
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        txt_path = os.path.join(output_dir, f"{filename}_competencies.txt")
        json_path = os.path.join(output_dir, f"{filename}_competencies.json")
        
        report = {
            'document': os.path.basename(pdf_path),
            'method': 'Enhanced Standard CanMEDS (multi-stage validation)',
            'template': document_analysis['template'],
            'pages_extracted': {'start': start_page, 'end': end_page},
            'validation': validation_msg,
            'detailed_analysis': detailed_analysis,
            'content_length': len(content),
            'success': is_valid or (len(content) > 1000 and detailed_analysis.get('role_count', 0) >= 3)
        }
        
        try:
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"Document: {report['document']}\n")
                f.write(f"Extraction Method: {report['method']}\n")
                f.write(f"Template: {report['template']}\n")
                f.write(f"Pages Extracted: {start_page}-{end_page}\n")
                f.write(f"Validation: {validation_msg}\n")
                f.write(f"Roles Found: {', '.join(detailed_analysis.get('roles_found', []))}\n")
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
                'detailed_analysis': detailed_analysis,
                'content_length': len(content),
                'extraction_successful': report['success']
            }
            
        except Exception as e:
            print(f"❌ Error saving extraction: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Extract CanMEDS competencies (Enhanced Standard format)")
    parser.add_argument("--input-dir", required=True, help="Directory containing PDF files")
    parser.add_argument("--output-dir", required=True, help="Directory to write extracted outputs")
    parser.add_argument("--toc-scan-pages", type=int, default=15, help="Number of initial pages to scan for TOC")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    extractor = EnhancedStandardCanMEDSExtractor(toc_scan_pages=args.toc_scan_pages)

    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in input directory")
        return

    print(f"Found {len(pdf_files)} PDF files to process")

    results = []
    successful_extractions = 0
    excellent_extractions = 0
    
    for pdf_path in pdf_files:
        result = extractor.extract_competencies(pdf_path, output_dir)
        if result:
            results.append(result)
            if result['extraction_successful']:
                successful_extractions += 1
                if 'Excellent' in result['validation']:
                    excellent_extractions += 1

    summary = {
        'category': 'Enhanced Standard CanMEDS Format (multi-stage validation)',
        'total_documents': len(pdf_files),
        'successful_extractions': successful_extractions,
        'excellent_extractions': excellent_extractions,
        'extraction_rate': f"{(successful_extractions/len(pdf_files)*100):.1f}%",
        'excellent_rate': f"{(excellent_extractions/len(pdf_files)*100):.1f}%",
        'results': results
    }

    summary_file = os.path.join(output_dir, 'extraction_summary_enhanced.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n🎯 ENHANCED SUMMARY")
    print(f"Category: Enhanced Standard CanMEDS Format")
    print(f"Documents Processed: {len(pdf_files)}")
    print(f"Successful Extractions: {successful_extractions}")
    print(f"Excellent Extractions: {excellent_extractions}")
    print(f"Success Rate: {successful_extractions/len(pdf_files)*100:.1f}%")
    print(f"Excellence Rate: {excellent_extractions/len(pdf_files)*100:.1f}%")
    print(f"Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
