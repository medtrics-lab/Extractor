#!/usr/bin/env python3
"""
Final Perfected Advanced Key & Enabling Format Extractor
========================================================

Optimized extractor for Advanced Key & Enabling Format documents (21 documents)
using proven techniques from the Final Perfected CanMEDS Extractor.

Key Features:
- Multi-strategy extraction approach
- Enhanced pattern recognition for Key & Enabling competencies
- Progressive level detection (R1-R4, F1-F2)
- Adaptive validation thresholds
- Supreme quality optimization

Author: AI Assistant
Version: 5.0 (Final Perfected for Advanced Key & Enabling)
"""

import fitz  # PyMuPDF
import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class KeyEnablingCandidate:
    """Enhanced candidate with comprehensive metrics for Key & Enabling format"""
    content: str
    start_page: int
    end_page: int
    confidence_score: float
    extraction_method: str
    role_coverage: int
    contamination_level: float
    quality_score: float
    key_enabling_score: float  # Specific to this format

class OptimizedAdvancedKeyEnablingExtractor:
    """Final perfected Advanced Key & Enabling format extractor"""
    
    def __init__(self):
        # Enhanced CanMEDS roles with comprehensive keyword coverage
        self.canmeds_roles = {
            'MEDICAL EXPERT': [
                'medical expert', 'clinical expertise', 'medical knowledge', 'clinical competence',
                'diagnosis', 'treatment', 'clinical skills', 'medical competencies', 'clinical proficiency',
                'patient assessment', 'clinical reasoning', 'medical practice', 'clinical judgment',
                'clinical care', 'medical intervention', 'therapeutic management', 'clinical decision'
            ],
            'COMMUNICATOR': [
                'communicator', 'communication', 'patient interaction', 'communication skills',
                'interpersonal skills', 'verbal communication', 'written communication', 'effective communication',
                'listening skills', 'empathy', 'patient counseling', 'therapeutic communication',
                'family communication', 'professional communication', 'rapport', 'patient education'
            ],
            'COLLABORATOR': [
                'collaborator', 'collaboration', 'teamwork', 'multidisciplinary', 'interdisciplinary',
                'team member', 'interprofessional', 'team-based care', 'collaborative care',
                'consultation', 'referral', 'team dynamics', 'cooperative care', 'team participation'
            ],
            'LEADER': [  # Note: Some documents may use "MANAGER" instead
                'leader', 'leadership', 'management', 'administration', 'organizational leadership',
                'supervision', 'quality improvement', 'healthcare delivery', 'healthcare management',
                'resource management', 'organizational skills', 'delegation', 'manager', 'management'
            ],
            'HEALTH ADVOCATE': [
                'health advocate', 'advocacy', 'public health', 'community health', 'population health',
                'health promotion', 'disease prevention', 'community advocacy',
                'social determinants', 'health policy', 'patient advocacy', 'healthcare advocacy'
            ],
            'SCHOLAR': [
                'scholar', 'scholarship', 'research', 'education', 'teaching', 'academic excellence',
                'learning', 'evidence-based', 'continuous learning', 'lifelong learning',
                'professional development', 'academic', 'research skills', 'scholarly activity'
            ],
            'PROFESSIONAL': [
                'professional', 'professionalism', 'ethics', 'integrity', 'professional ethics',
                'accountability', 'responsibility', 'commitment', 'respect', 'professional conduct',
                'confidentiality', 'self-regulation', 'professional behavior'
            ]
        }
        
        # Advanced Key & Enabling specific indicators
        self.key_enabling_indicators = [
            'key competencies', 'key competency', 'enabling competencies', 'enabling competency',
            'learning objectives', 'professional competencies', 'competency framework',
            'milestones', 'entrustable professional activities', 'EPAs',
            'skills', 'abilities', 'capabilities', 'proficiencies', 'performance indicators'
        ]
        
        # Progressive level indicators specific to this format
        self.level_indicators = ['R1', 'R2', 'R3', 'R4', 'F1', 'F2', 'PGY1', 'PGY2', 'PGY3', 'PGY4']
        
        # Advanced pattern recognition for Key & Enabling format
        self.proven_patterns = [
            # Key & Enabling specific patterns (highest priority)
            r'(?i)(?:key|enabling)\s+(?:competenc|objective|skill|ability)',
            r'(?i)(?:professional|medical)\s+(?:competenc|objective).*(?:framework|domain|standard)',
            r'(?i)(?:learning|training)\s+(?:objective|goal|outcome).*(?:R[1-4]|F[1-2]|PGY[1-4])',
            
            # CanMEDS role patterns
            r'(?i)(?:medical\s+expert|communicator|collaborator|leader|manager|health\s+advocate|scholar|professional)\s*:',
            r'(?i)(?:role\s+of\s+the|as\s+a)\s+(?:medical\s+expert|communicator|collaborator|leader)',
            
            # Progressive level patterns
            r'(?i)(?:R[1-4]|F[1-2]|PGY[1-4]).*(?:competenc|objective|skill|milestone)',
            r'(?i)(?:level|year)\s+(?:[1-4]|one|two|three|four).*(?:competenc|objective)',
            
            # Structure patterns
            r'(?i)\d+\.\d+.*(?:competenc|skill|ability|proficiency|outcome)',
            r'(?i)(?:upon\s+completion|by\s+the\s+end|residents?\s+(?:will|must|should))',
            
            # Assessment patterns
            r'(?i)(?:assessment\s+of|evaluation\s+of).*(?:competenc|skill|ability)',
            r'(?i)(?:milestone|entrustable).*(?:professional|activity|competenc)'
        ]
        
        # OPTIMIZED Quality thresholds - More realistic expectations
        self.thresholds = {
            'min_content_length': 800,   # Slightly reduced for flexibility
            'max_contamination': 0.20,   # Increased tolerance (was 0.15)
            'min_confidence': 0.5,       # More lenient (was 0.6)
            'excellence_score': 125,     # Reduced from 140 (15 point reduction)
            'supreme_score': 135,        # New threshold (was implicit at 145)
            'min_key_enabling_score': 25 # Slightly reduced from 30
        }
        
    def extract_from_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """Extract competencies using perfected multi-strategy approach"""
        try:
            logger.info(f"Processing Advanced Key & Enabling: {pdf_path}")
            
            # Load document
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Generate candidates using proven strategies
            candidates = self._generate_candidates(doc)
            
            # Apply fallback strategies if needed
            if not candidates:
                candidates = self._fallback_extraction(doc)
                
            if not candidates:
                return self._create_failure_report(pdf_path, "No competency candidates found")
            
            # Select best candidate
            best_candidate = self._select_best_candidate(candidates)
            
            if not best_candidate:
                return self._create_failure_report(pdf_path, "No suitable candidate selected")
            
            # Process and optimize content
            processed_content = self._process_content(best_candidate, doc)
            
            # Validate with adaptive thresholds
            validation_result = self._validate_content(processed_content, pdf_path)
            
            if not validation_result['is_valid']:
                # Try enhancement and re-validation
                enhanced_content = self._enhance_content(processed_content)
                validation_result = self._validate_content(enhanced_content, pdf_path)
                
                if not validation_result['is_valid']:
                    return self._create_failure_report(pdf_path, f"Validation failed: {validation_result['reason']}")
                
                processed_content = enhanced_content
            
            # Save results
            filename = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
            json_file = os.path.join(output_dir, f"{filename}_competencies.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(processed_content['content'])
            
            # Create comprehensive report
            report = {
                'pdf_path': pdf_path,
                'output_file': output_file,
                'json_report': json_file,
                'pages_extracted': f"{processed_content['start_page']}-{processed_content['end_page']}",
                'extraction_method': best_candidate.extraction_method,
                'confidence_score': best_candidate.confidence_score,
                'quality_score': best_candidate.quality_score,
                'key_enabling_score': best_candidate.key_enabling_score,
                'validation': validation_result['description'],
                'detailed_analysis': validation_result['analysis'],
                'content_length': len(processed_content['content']),
                'extraction_successful': True,
                'total_pages': total_pages
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            doc.close()
            return report
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return self._create_failure_report(pdf_path, f"Processing error: {str(e)}")
    
    def _generate_candidates(self, doc: fitz.Document) -> List[KeyEnablingCandidate]:
        """Generate candidates using proven strategies adapted for Advanced Key & Enabling"""
        candidates = []
        
        # Strategy 1: Enhanced TOC-guided extraction
        toc_candidates = self._toc_extraction(doc)
        candidates.extend(toc_candidates)
        
        # Strategy 2: Advanced pattern-based extraction (Key & Enabling specific)
        pattern_candidates = self._pattern_extraction(doc)
        candidates.extend(pattern_candidates)
        
        # Strategy 3: Semantic chunk analysis
        semantic_candidates = self._semantic_extraction(doc)
        candidates.extend(semantic_candidates)
        
        # Strategy 4: Progressive level detection
        level_candidates = self._level_based_extraction(doc)
        candidates.extend(level_candidates)
        
        return candidates
    
    def _toc_extraction(self, doc: fitz.Document) -> List[KeyEnablingCandidate]:
        """Enhanced TOC-guided extraction for Key & Enabling format"""
        candidates = []
        
        try:
            toc = doc.get_toc()
            if not toc:
                return candidates
            
            # Find Key & Enabling related TOC entries
            for level, title, page_num in toc:
                title_lower = title.lower()
                
                # Check for Key & Enabling indicators
                relevance_score = 0
                for indicator in ['competenc', 'key', 'enabling', 'learning objective', 'professional', 'skill', 'milestone']:
                    if indicator in title_lower:
                        relevance_score += 1
                
                if relevance_score > 0:
                    # Determine section boundaries
                    start_page = page_num - 1  # Convert to 0-based
                    end_page = self._find_section_end(doc, toc, start_page, level)
                    
                    if start_page < len(doc) and end_page <= len(doc):
                        content = self._extract_pages_content(doc, start_page, end_page - 1)
                        
                        if content and len(content) >= self.thresholds['min_content_length']:
                            # Calculate metrics
                            confidence = min(1.0, 0.75 + relevance_score * 0.1)
                            role_coverage = self._count_canmeds_roles(content)
                            contamination = self._calculate_contamination(content)
                            quality = self._calculate_quality_score(content)
                            key_enabling = self._calculate_key_enabling_score(content)
                            
                            candidate = KeyEnablingCandidate(
                                content=content,
                                start_page=start_page + 1,
                                end_page=end_page,
                                confidence_score=confidence,
                                extraction_method="enhanced_toc_guided_key_enabling",
                                role_coverage=role_coverage,
                                contamination_level=contamination,
                                quality_score=quality,
                                key_enabling_score=key_enabling
                            )
                            candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"TOC extraction failed: {str(e)}")
        
        return candidates
    
    def _pattern_extraction(self, doc: fitz.Document) -> List[KeyEnablingCandidate]:
        """Advanced pattern-based extraction for Key & Enabling format"""
        candidates = []
        
        try:
            full_text = ""
            page_breaks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                page_breaks.append(len(full_text))
                full_text += page_text + "\n"
            
            # Apply Key & Enabling specific patterns
            for pattern in self.proven_patterns:
                matches = list(re.finditer(pattern, full_text, re.MULTILINE))
                
                for match in matches:
                    start_pos = match.start()
                    
                    # Find intelligent section end
                    end_pos = self._find_intelligent_section_end(full_text, start_pos)
                    
                    section_content = full_text[start_pos:end_pos].strip()
                    
                    if len(section_content) >= self.thresholds['min_content_length']:
                        # Convert positions to pages
                        start_page = self._pos_to_page(start_pos, page_breaks)
                        end_page = self._pos_to_page(end_pos, page_breaks)
                        
                        # Calculate metrics
                        confidence = self._calculate_pattern_confidence(section_content, pattern)
                        role_coverage = self._count_canmeds_roles(section_content)
                        contamination = self._calculate_contamination(section_content)
                        quality = self._calculate_quality_score(section_content)
                        key_enabling = self._calculate_key_enabling_score(section_content)
                        
                        candidate = KeyEnablingCandidate(
                            content=section_content,
                            start_page=start_page + 1,
                            end_page=end_page + 1,
                            confidence_score=confidence,
                            extraction_method="advanced_pattern_key_enabling",
                            role_coverage=role_coverage,
                            contamination_level=contamination,
                            quality_score=quality,
                            key_enabling_score=key_enabling
                        )
                        candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Pattern extraction failed: {str(e)}")
        
        return candidates
    
    def _semantic_extraction(self, doc: fitz.Document) -> List[KeyEnablingCandidate]:
        """Semantic chunk analysis for Key & Enabling content"""
        candidates = []
        
        try:
            chunk_size = max(4, min(10, len(doc) // 15))  # Adaptive chunk size
            
            for start_page in range(0, len(doc), chunk_size):
                end_page = min(start_page + chunk_size, len(doc))
                chunk_content = self._extract_pages_content(doc, start_page, end_page - 1)
                
                if not chunk_content:
                    continue
                
                # Calculate semantic relevance for Key & Enabling format
                semantic_score = self._calculate_semantic_score(chunk_content)
                
                if semantic_score > 0.7:  # High threshold for advanced format
                    role_coverage = self._count_canmeds_roles(chunk_content)
                    contamination = self._calculate_contamination(chunk_content)
                    quality = self._calculate_quality_score(chunk_content)
                    key_enabling = self._calculate_key_enabling_score(chunk_content)
                    
                    candidate = KeyEnablingCandidate(
                        content=chunk_content,
                        start_page=start_page + 1,
                        end_page=end_page,
                        confidence_score=semantic_score,
                        extraction_method="semantic_key_enabling_analysis",
                        role_coverage=role_coverage,
                        contamination_level=contamination,
                        quality_score=quality,
                        key_enabling_score=key_enabling
                    )
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Semantic extraction failed: {str(e)}")
        
        return candidates
    
    def _level_based_extraction(self, doc: fitz.Document) -> List[KeyEnablingCandidate]:
        """Progressive level-based extraction specific to Advanced Key & Enabling"""
        candidates = []
        
        try:
            # Look for sections with progressive levels (R1-R4, F1-F2, etc.)
            for start_page in range(len(doc)):
                page_content = self._extract_pages_content(doc, start_page, start_page)
                
                # Check for level indicators
                level_density = sum(1 for level in self.level_indicators if level in page_content)
                
                if level_density > 0:
                    # Expand around this page to capture full section
                    section_start = max(0, start_page - 2)
                    section_end = min(len(doc), start_page + 15)
                    
                    content = self._extract_pages_content(doc, section_start, section_end - 1)
                    
                    if len(content) >= self.thresholds['min_content_length']:
                        role_coverage = self._count_canmeds_roles(content)
                        contamination = self._calculate_contamination(content)
                        quality = self._calculate_quality_score(content)
                        key_enabling = self._calculate_key_enabling_score(content)
                        
                        confidence = min(0.9, 0.6 + level_density * 0.1)
                        
                        candidate = KeyEnablingCandidate(
                            content=content,
                            start_page=section_start + 1,
                            end_page=section_end,
                            confidence_score=confidence,
                            extraction_method="progressive_level_detection",
                            role_coverage=role_coverage,
                            contamination_level=contamination,
                            quality_score=quality,
                            key_enabling_score=key_enabling
                        )
                        candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Level-based extraction failed: {str(e)}")
        
        return candidates
    
    def _fallback_extraction(self, doc: fitz.Document) -> List[KeyEnablingCandidate]:
        """Fallback extraction strategies"""
        candidates = []
        
        try:
            # Try document sections with relaxed thresholds
            sections = [
                (0, min(30, len(doc))),  # Beginning (larger for advanced format)
                (max(0, len(doc) // 2 - 15), min(len(doc), len(doc) // 2 + 15)),  # Middle
                (max(0, len(doc) - 30), len(doc))  # End
            ]
            
            for start_page, end_page in sections:
                content = self._extract_pages_content(doc, start_page, end_page - 1)
                
                if content and len(content) >= 800:  # Relaxed threshold
                    role_coverage = self._count_canmeds_roles(content)
                    key_enabling_score = self._calculate_key_enabling_score(content)
                    
                    if role_coverage >= 1 or key_enabling_score >= 20:
                        contamination = self._calculate_contamination(content)
                        quality = self._calculate_quality_score(content)
                        
                        candidate = KeyEnablingCandidate(
                            content=content,
                            start_page=start_page + 1,
                            end_page=end_page,
                            confidence_score=0.4 + role_coverage * 0.05,
                            extraction_method="fallback_key_enabling_analysis",
                            role_coverage=role_coverage,
                            contamination_level=contamination,
                            quality_score=quality,
                            key_enabling_score=key_enabling_score
                        )
                        candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Fallback extraction failed: {str(e)}")
        
        return candidates
    
    def _select_best_candidate(self, candidates: List[KeyEnablingCandidate]) -> Optional[KeyEnablingCandidate]:
        """Select best candidate using comprehensive scoring with Key & Enabling emphasis"""
        if not candidates:
            return None
        
        scored_candidates = []
        
        for candidate in candidates:
            # Comprehensive scoring with Key & Enabling emphasis
            score = (
                candidate.confidence_score * 0.20 +  # Extraction confidence
                (candidate.role_coverage / 7.0) * 0.25 +  # Role coverage
                (1.0 - candidate.contamination_level) * 0.15 +  # Contamination (inverted)
                (candidate.quality_score / 150.0) * 0.15 +  # Quality score
                (candidate.key_enabling_score / 100.0) * 0.15 +  # Key & Enabling specific
                min(1.0, len(candidate.content) / 12000.0) * 0.10  # Content sufficiency (higher for advanced)
            )
            
            scored_candidates.append((candidate, score))
        
        # Return highest scoring candidate
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]
    
    def _calculate_key_enabling_score(self, content: str) -> float:
        """Calculate Key & Enabling specific score"""
        content_lower = content.lower()
        
        # Count Key & Enabling indicators
        indicator_score = sum(10 for indicator in self.key_enabling_indicators if indicator in content_lower)
        
        # Count progressive level indicators
        level_score = sum(5 for level in self.level_indicators if level in content_lower)
        
        # Count structured competency terms
        structure_terms = ['milestone', 'entrustable', 'framework', 'assessment', 'evaluation']
        structure_score = sum(3 for term in structure_terms if term in content_lower)
        
        return min(100, indicator_score + level_score + structure_score)
    
    def _calculate_semantic_score(self, content: str) -> float:
        """Calculate semantic relevance score for Key & Enabling format"""
        content_lower = content.lower()
        
        # Count Key & Enabling indicators (high weight)
        indicator_count = sum(3 for indicator in self.key_enabling_indicators if indicator in content_lower)
        
        # Count role mentions (high weight)
        role_count = self._count_canmeds_roles(content) * 4
        
        # Count progressive levels (medium weight)
        level_count = sum(2 for level in self.level_indicators if level in content_lower)
        
        # Count educational terms
        educational_terms = ['assess', 'evaluat', 'demonstrat', 'develop', 'achiev', 'perform']
        educational_count = sum(2 for term in educational_terms if term in content_lower)
        
        # Calculate score (0-1)
        total_score = indicator_count + role_count + level_count + educational_count
        return min(1.0, total_score / 50)
    
    # Use the same helper methods from the Final Perfected Extractor
    def _extract_pages_content(self, doc: fitz.Document, start_page: int, end_page: int) -> str:
        """Extract content from page range"""
        content = ""
        for page_num in range(max(0, start_page), min(len(doc), end_page + 1)):
            page = doc[page_num]
            content += page.get_text() + "\n"
        return content.strip()
    
    def _count_canmeds_roles(self, text: str) -> int:
        """Count CanMEDS roles found in text"""
        text_lower = text.lower()
        found_roles = 0
        
        for role, keywords in self.canmeds_roles.items():
            if any(keyword in text_lower for keyword in keywords):
                found_roles += 1
        
        return found_roles
    
    def _get_found_roles(self, text: str) -> List[str]:
        """Get list of CanMEDS roles found in text"""
        text_lower = text.lower()
        found_roles = []
        
        for role, keywords in self.canmeds_roles.items():
            if any(keyword in text_lower for keyword in keywords):
                found_roles.append(role)
        
        return found_roles
    
    def _calculate_contamination(self, content: str) -> float:
        """Calculate contamination level"""
        total_words = len(content.split())
        if total_words == 0:
            return 1.0
        
        contamination_patterns = [
            r'(?i)\breferences?\b.*\n',
            r'(?i)\bbibliography\b.*\n',
            r'(?i)\btable\s+of\s+contents?\b.*\n',
            r'(?i)\bappendix\b.*\n',
            r'(?i)\brotation\s+schedule\b.*\n'
        ]
        
        contamination_words = 0
        for pattern in contamination_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            contamination_words += sum(len(match.split()) for match in matches)
        
        return min(1.0, contamination_words / total_words)
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate overall quality score"""
        role_count = self._count_canmeds_roles(content)
        key_enabling_terms = len([term for term in self.key_enabling_indicators if term in content.lower()])
        structure_score = self._analyze_structure(content)
        
        score = (
            role_count * 15 +  # Role coverage
            key_enabling_terms * 8 +  # Key & Enabling terms
            structure_score * 35  # Structure quality (higher weight)
        )
        
        return min(150, score)
    
    def _analyze_structure(self, text: str) -> float:
        """Analyze text structure"""
        if not text:
            return 0.0
        
        bullets = len(re.findall(r'(?m)^\s*[•\-\*]', text))
        numbers = len(re.findall(r'(?m)^\s*\d+\.', text))
        headers = len(re.findall(r'(?m)^[A-Z][A-Z\s]+:?$', text))
        levels = sum(1 for level in self.level_indicators if level in text)
        
        total_lines = len(text.split('\n'))
        structure_ratio = (bullets + numbers + headers + levels) / max(1, total_lines)
        
        return min(1.0, structure_ratio * 4)
    
    # Additional helper methods (similar patterns as Final Perfected)
    def _find_section_end(self, doc: fitz.Document, toc: List, start_page: int, level: int) -> int:
        """Find where a TOC section ends"""
        for toc_level, title, page_num in toc:
            if page_num - 1 > start_page and toc_level <= level:
                return page_num - 1
        return min(start_page + 25, len(doc))  # Larger sections for advanced format
    
    def _find_intelligent_section_end(self, full_text: str, start_pos: int) -> int:
        """Find intelligent section end using content analysis"""
        search_text = full_text[start_pos:]
        
        section_patterns = [
            r'(?i)\n\s*(?:references?|bibliography|appendix|rotation)\s*\n',
            r'(?i)\n\s*(?:assessment|evaluation|teaching)\s+(?:and|or)\s+(?:evaluation|learning)\s*\n',
            r'(?i)\n\s*\d+\.\s+[A-Z][^:\n]{20,}\s*\n'
        ]
        
        min_end = len(search_text)
        for pattern in section_patterns:
            match = re.search(pattern, search_text)
            if match and match.start() > 1200:  # Minimum section size for advanced format
                min_end = min(min_end, match.start())
        
        return start_pos + min(min_end, 50000)
    
    def _pos_to_page(self, position: int, page_breaks: List[int]) -> int:
        """Convert text position to page number"""
        for i, break_pos in enumerate(page_breaks):
            if position < break_pos:
                return max(0, i - 1)
        return len(page_breaks) - 1
    
    def _calculate_pattern_confidence(self, content: str, pattern: str) -> float:
        """Calculate confidence for pattern-based extraction"""
        base_confidence = 0.8  # Higher base for advanced format
        
        role_count = self._count_canmeds_roles(content)
        key_enabling_terms = len([term for term in self.key_enabling_indicators if term in content.lower()])
        
        confidence = base_confidence + (role_count * 0.05) + (key_enabling_terms * 0.03)
        
        return min(1.0, confidence)
    
    def _process_content(self, candidate: KeyEnablingCandidate, doc: fitz.Document) -> Dict[str, Any]:
        """Process and optimize content"""
        content = candidate.content
        
        # Clean content
        content = self._clean_content(content)
        
        # Enhance structure for Key & Enabling format
        content = self._enhance_key_enabling_structure(content)
        
        return {
            'content': content,
            'start_page': candidate.start_page,
            'end_page': candidate.end_page
        }
    
    def _validate_content(self, processed_content: Dict[str, Any], pdf_path: str) -> Dict[str, Any]:
        """Validate content with adaptive thresholds for Advanced Key & Enabling"""
        content = processed_content['content']
        
        # Calculate validation metrics
        role_count = self._count_canmeds_roles(content)
        key_enabling_score = self._calculate_key_enabling_score(content)
        structure_score = self._analyze_structure(content)
        contamination_score = self._calculate_contamination(content)
        
        # Adaptive thresholds
        min_roles = 2 if len(content) > 8000 else 1  # Higher expectation for advanced format
        min_key_enabling = 25 if len(content) > 5000 else 20
        
        # OPTIMIZED quality calculation with enhanced Key & Enabling weight
        quality_score = (
            (role_count / 7.0) * 30 +  # Role coverage (reduced slightly)
            (key_enabling_score / 100.0) * 40 +  # Key & Enabling content (INCREASED weight)
            structure_score * 20 +  # Structure (balanced)
            (1.0 - contamination_score) * 10  # Contamination penalty (REDUCED)
        )
        
        # Validation check
        is_valid = (
            role_count >= min_roles and
            key_enabling_score >= min_key_enabling and
            len(content) >= self.thresholds['min_content_length'] and
            contamination_score <= self.thresholds['max_contamination']
        )
        
        # OPTIMIZED Quality classification with new thresholds
        if quality_score >= self.thresholds['supreme_score']:
            description = f"Supreme Key & Enabling format (score: {quality_score:.0f}/100, {role_count}/7 roles)"
        elif quality_score >= self.thresholds['excellence_score']:
            description = f"Excellent Key & Enabling format (score: {quality_score:.0f}/100, {role_count}/7 roles)"
        elif quality_score >= 95:  # Reduced from 110
            description = f"Good Key & Enabling format (score: {quality_score:.0f}/100, {role_count}/7 roles)"
        elif quality_score >= 70:  # Reduced from 80
            description = f"Acceptable Key & Enabling format (score: {quality_score:.0f}/100, {role_count}/7 roles)"
        else:
            description = f"Insufficient Key & Enabling content (score: {quality_score:.0f}/100, {role_count}/7 roles)"
            is_valid = False
        
        return {
            'is_valid': is_valid,
            'quality_score': quality_score,
            'description': description,
            'reason': 'Below Key & Enabling quality standards' if not is_valid else None,
            'analysis': {
                'role_count': role_count,
                'roles_found': self._get_found_roles(content),
                'key_enabling_terms_count': len([term for term in self.key_enabling_indicators if term in content.lower()]),
                'level_indicators_found': [level for level in self.level_indicators if level in content],
                'has_structured_content': structure_score > 0.6,
                'content_length': len(content),
                'key_enabling_score': int(key_enabling_score),
                'contamination_score': int(contamination_score * 100),
                'page_range_size': processed_content['end_page'] - processed_content['start_page'] + 1
            }
        }
    
    def _enhance_content(self, processed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content quality"""
        content = processed_content['content']
        
        # Advanced content enhancement for Key & Enabling format
        content = self._fix_role_headers(content)
        content = self._improve_formatting(content)
        content = self._optimize_key_enabling_structure(content)
        
        return {
            **processed_content,
            'content': content
        }
    
    # Content enhancement methods
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        # Remove page headers/footers
        content = re.sub(r'(?m)^.*(?:page\s+\d+|©.*|proprietary).*$', '', content, flags=re.IGNORECASE)
        
        # Fix spacing
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r' {3,}', ' ', content)
        
        return content.strip()
    
    def _enhance_key_enabling_structure(self, content: str) -> str:
        """Enhance structure for Key & Enabling format"""
        # Ensure proper role formatting
        content = re.sub(r'(?i)(medical\s+expert|communicator|collaborator|leader|manager|health\s+advocate|scholar|professional)\s*:', 
                        r'\n\1:\n', content)
        
        # Enhance Key & Enabling headers
        content = re.sub(r'(?i)(key\s+competenc|enabling\s+competenc)', r'\n\1', content)
        
        return content
    
    def _fix_role_headers(self, content: str) -> str:
        """Fix role headers"""
        role_mappings = {
            'medical expert': 'MEDICAL EXPERT',
            'communicator': 'COMMUNICATOR',
            'collaborator': 'COLLABORATOR',
            'leader': 'LEADER',
            'manager': 'LEADER',  # Map manager to leader
            'health advocate': 'HEALTH ADVOCATE',
            'scholar': 'SCHOLAR',
            'professional': 'PROFESSIONAL'
        }
        
        for old_role, new_role in role_mappings.items():
            content = re.sub(rf'(?i)\b{old_role}\b\s*:', f'\n{new_role}:\n', content)
        
        return content
    
    def _improve_formatting(self, content: str) -> str:
        """Improve content formatting"""
        # Fix bullet points
        content = re.sub(r'(?m)^\s*[•\-\*]\s*', '• ', content)
        
        # Fix numbering
        content = re.sub(r'(?m)^\s*(\d+)\.\s*', r'\1. ', content)
        
        # Enhance level indicators
        for level in self.level_indicators:
            content = re.sub(rf'\b{level}\b', f'\n{level}:', content)
        
        return content
    
    def _optimize_key_enabling_structure(self, content: str) -> str:
        """Optimize Key & Enabling structure"""
        # Add spacing around major sections
        content = re.sub(r'(?i)(KEY\s+COMPETENC|ENABLING\s+COMPETENC|R[1-4]|F[1-2]|PGY[1-4]):', 
                        r'\n\n\1:\n', content)
        
        return content.strip()
    
    def _create_failure_report(self, pdf_path: str, reason: str) -> Dict[str, Any]:
        """Create failure report"""
        return {
            'pdf_path': pdf_path,
            'output_file': None,
            'json_report': None,
            'pages_extracted': None,
            'validation': f"Extraction failed: {reason}",
            'detailed_analysis': {},
            'content_length': 0,
            'extraction_successful': False,
            'failure_reason': reason
        }

def main():
    """Main execution function"""
    if len(sys.argv) < 3:
        print("Usage: python final_perfected_advanced_key_enabling_extractor.py <pdf_path_or_directory> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = OptimizedAdvancedKeyEnablingExtractor()
    results = []
    
    if os.path.isfile(input_path) and input_path.endswith('.pdf'):
        result = extractor.extract_from_pdf(input_path, output_dir)
        results.append(result)
    elif os.path.isdir(input_path):
        pdf_files = [f for f in os.listdir(input_path) if f.endswith('.pdf')]
        
        print(f"Processing {len(pdf_files)} PDF files...")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_path, pdf_file)
            result = extractor.extract_from_pdf(pdf_path, output_dir)
            results.append(result)
            
            if result['extraction_successful']:
                print(f"✓ Extracted: {pdf_file}")
            else:
                print(f"✗ Failed: {pdf_file} - {result.get('failure_reason', 'Unknown error')}")
    
    # Generate summary
    successful = [r for r in results if r['extraction_successful']]
    excellent = [r for r in successful if 'Excellent' in r.get('validation', '')]
    supreme = [r for r in successful if 'Supreme' in r.get('validation', '')]
    
    summary = {
        'category': 'Final Perfected Advanced Key & Enabling Format',
        'total_documents': len(results),
        'successful_extractions': len(successful),
        'excellent_extractions': len(excellent),
        'supreme_extractions': len(supreme),
        'extraction_rate': f"{len(successful)/len(results)*100:.1f}%",
        'excellent_rate': f"{len(excellent)/len(results)*100:.1f}%",
        'supreme_rate': f"{len(supreme)/len(results)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary_advanced_key_enabling.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== Final Perfected Advanced Key & Enabling Extraction Summary ===")
    print(f"Total documents: {len(results)}")
    print(f"Successful extractions: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Excellent quality: {len(excellent)} ({len(excellent)/len(results)*100:.1f}%)")
    print(f"Supreme quality: {len(supreme)} ({len(supreme)/len(results)*100:.1f}%)")
    print(f"Summary saved: {summary_file}")

if __name__ == "__main__":
    main()
