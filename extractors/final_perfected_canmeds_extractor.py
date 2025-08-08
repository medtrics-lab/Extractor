#!/usr/bin/env python3
"""
Final Perfected CanMEDS Competency Extractor
==========================================

This extractor combines the best proven techniques from all previous versions
to achieve maximum performance:

1. Multi-Strategy Approach (from Advanced AI)
2. Enhanced Pattern Recognition (proven successful)
3. Intelligent Validation (adaptive thresholds)
4. Content Optimization (quality enhancement)
5. Fallback Systems (zero-failure approach)

Author: AI Assistant
Version: 5.0 (Final Perfected)
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
class CompetencyCandidate:
    """Enhanced candidate with comprehensive metrics"""
    content: str
    start_page: int
    end_page: int
    confidence_score: float
    extraction_method: str
    role_coverage: int
    contamination_level: float
    quality_score: float

class FinalPerfectedExtractor:
    """Final perfected CanMEDS competency extractor with maximum performance"""
    
    def __init__(self):
        # Enhanced CanMEDS roles with comprehensive keyword coverage
        self.canmeds_roles = {
            'MEDICAL EXPERT': [
                'medical expert', 'clinical expertise', 'medical knowledge', 'clinical competence',
                'diagnosis', 'treatment', 'clinical skills', 'medical competencies', 'clinical proficiency',
                'patient assessment', 'clinical reasoning', 'medical practice', 'clinical judgment',
                'clinical care', 'medical intervention', 'therapeutic management', 'clinical decision',
                'patient care', 'medical assessment', 'clinical evaluation', 'diagnostic skills'
            ],
            'COMMUNICATOR': [
                'communicator', 'communication', 'patient interaction', 'communication skills',
                'interpersonal skills', 'verbal communication', 'written communication', 'effective communication',
                'listening skills', 'empathy', 'patient counseling', 'therapeutic communication',
                'family communication', 'professional communication', 'rapport', 'patient education',
                'interviewing skills', 'counselling', 'interpersonal competence', 'social skills'
            ],
            'COLLABORATOR': [
                'collaborator', 'collaboration', 'teamwork', 'multidisciplinary', 'interdisciplinary',
                'team member', 'interprofessional', 'team-based care', 'collaborative care',
                'consultation', 'referral', 'team dynamics', 'cooperative care', 'team participation',
                'group work', 'collaborative practice', 'team collaboration', 'professional collaboration'
            ],
            'LEADER': [
                'leader', 'leadership', 'management', 'administration', 'organizational leadership',
                'supervision', 'quality improvement', 'healthcare delivery', 'healthcare management',
                'resource management', 'organizational skills', 'delegation', 'team leadership',
                'quality assurance', 'healthcare systems', 'innovation', 'change management',
                'strategic planning', 'project management', 'healthcare administration'
            ],
            'HEALTH ADVOCATE': [
                'health advocate', 'advocacy', 'public health', 'community health', 'population health',
                'health promotion', 'disease prevention', 'community advocacy',
                'social determinants', 'health policy', 'patient advocacy', 'healthcare advocacy',
                'health equity', 'community engagement', 'social responsibility', 'public advocacy',
                'health awareness', 'community outreach', 'social justice'
            ],
            'SCHOLAR': [
                'scholar', 'scholarship', 'research', 'education', 'teaching', 'academic excellence',
                'learning', 'evidence-based', 'continuous learning', 'lifelong learning',
                'professional development', 'academic', 'research skills', 'scholarly activity',
                'critical appraisal', 'knowledge translation', 'mentoring', 'educational excellence',
                'scientific inquiry', 'research methodology', 'evidence-based practice'
            ],
            'PROFESSIONAL': [
                'professional', 'professionalism', 'ethics', 'integrity', 'professional ethics',
                'accountability', 'responsibility', 'commitment', 'respect', 'professional conduct',
                'confidentiality', 'self-regulation', 'professional behavior',
                'professional standards', 'moral responsibility', 'ethical practice', 'professional integrity',
                'ethical decision-making', 'professional values', 'moral principles'
            ]
        }
        
        # Comprehensive competency indicators
        self.competency_indicators = [
            'competencies', 'competency', 'learning outcomes', 'objectives', 'competency framework',
            'canmeds competencies', 'professional competencies', 'core competencies',
            'milestones', 'entrustable professional activities', 'EPAs', 'competency domains',
            'skills', 'abilities', 'capabilities', 'proficiencies', 'performance indicators',
            'learning goals', 'training objectives', 'expected outcomes', 'key competencies',
            'competency-based', 'competency assessment', 'competency development'
        ]
        
        # Proven pattern recognition (from successful Advanced AI extractor)
        self.proven_patterns = [
            # Primary CanMEDS patterns (highest priority)
            r'(?i)(?:canmeds|can-meds)\s+(?:competenc|role|domain|framework|standard)',
            r'(?i)(?:seven|7)\s+(?:role|competenc|domain).*(?:canmeds|framework)',
            r'(?i)(?:competenc|learning\s+outcome).*(?:framework|matrix|domain|standard)',
            
            # Role detection patterns
            r'(?i)(?:medical\s+expert|communicator|collaborator|leader|health\s+advocate|scholar|professional)\s*:',
            r'(?i)(?:role\s+of\s+the|as\s+a)\s+(?:medical\s+expert|communicator|collaborator)',
            
            # Structure patterns
            r'(?i)\d+\.\d+.*(?:competenc|skill|ability|proficiency|outcome)',
            r'(?i)(?:upon\s+completion|by\s+the\s+end|graduates?\s+(?:will|must|should))',
            r'(?i)(?:assessment\s+of|evaluation\s+of).*(?:competenc|skill|ability)',
            
            # Educational patterns
            r'(?i)(?:training\s+objective|educational\s+objective|learning\s+goal)',
            r'(?i)(?:performance\s+indicator|assessment\s+criteri|evaluation\s+standard)'
        ]
        
        # Quality thresholds (optimized based on Advanced AI success)
        self.thresholds = {
            'min_content_length': 800,
            'max_contamination': 0.20,
            'min_confidence': 0.5,
            'excellence_score': 130
        }
        
    def extract_from_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """Extract competencies using perfected multi-strategy approach"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
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
    
    def _generate_candidates(self, doc: fitz.Document) -> List[CompetencyCandidate]:
        """Generate candidates using proven strategies"""
        candidates = []
        
        # Strategy 1: Enhanced TOC-guided extraction
        toc_candidates = self._toc_extraction(doc)
        candidates.extend(toc_candidates)
        
        # Strategy 2: Advanced pattern-based extraction
        pattern_candidates = self._pattern_extraction(doc)
        candidates.extend(pattern_candidates)
        
        # Strategy 3: Semantic chunk analysis
        semantic_candidates = self._semantic_extraction(doc)
        candidates.extend(semantic_candidates)
        
        # Strategy 4: Density-based discovery
        density_candidates = self._density_extraction(doc)
        candidates.extend(density_candidates)
        
        return candidates
    
    def _toc_extraction(self, doc: fitz.Document) -> List[CompetencyCandidate]:
        """Enhanced TOC-guided extraction"""
        candidates = []
        
        try:
            toc = doc.get_toc()
            if not toc:
                return candidates
            
            # Find competency-related TOC entries
            for level, title, page_num in toc:
                title_lower = title.lower()
                
                # Check for competency indicators
                relevance_score = 0
                for indicator in ['competenc', 'canmeds', 'learning outcome', 'objective', 'skill']:
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
                            confidence = min(1.0, 0.7 + relevance_score * 0.1)
                            role_coverage = self._count_canmeds_roles(content)
                            contamination = self._calculate_contamination(content)
                            quality = self._calculate_quality_score(content)
                            
                            candidate = CompetencyCandidate(
                                content=content,
                                start_page=start_page + 1,
                                end_page=end_page,
                                confidence_score=confidence,
                                extraction_method="enhanced_toc_guided",
                                role_coverage=role_coverage,
                                contamination_level=contamination,
                                quality_score=quality
                            )
                            candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"TOC extraction failed: {str(e)}")
        
        return candidates
    
    def _pattern_extraction(self, doc: fitz.Document) -> List[CompetencyCandidate]:
        """Advanced pattern-based extraction"""
        candidates = []
        
        try:
            full_text = ""
            page_breaks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                page_breaks.append(len(full_text))
                full_text += page_text + "\n"
            
            # Apply proven patterns
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
                        
                        candidate = CompetencyCandidate(
                            content=section_content,
                            start_page=start_page + 1,
                            end_page=end_page + 1,
                            confidence_score=confidence,
                            extraction_method="advanced_pattern_based",
                            role_coverage=role_coverage,
                            contamination_level=contamination,
                            quality_score=quality
                        )
                        candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Pattern extraction failed: {str(e)}")
        
        return candidates
    
    def _semantic_extraction(self, doc: fitz.Document) -> List[CompetencyCandidate]:
        """Semantic chunk analysis"""
        candidates = []
        
        try:
            chunk_size = max(3, min(8, len(doc) // 12))  # Adaptive chunk size
            
            for start_page in range(0, len(doc), chunk_size):
                end_page = min(start_page + chunk_size, len(doc))
                chunk_content = self._extract_pages_content(doc, start_page, end_page - 1)
                
                if not chunk_content:
                    continue
                
                # Calculate semantic relevance
                semantic_score = self._calculate_semantic_score(chunk_content)
                
                if semantic_score > 0.65:  # High threshold
                    role_coverage = self._count_canmeds_roles(chunk_content)
                    contamination = self._calculate_contamination(chunk_content)
                    quality = self._calculate_quality_score(chunk_content)
                    
                    candidate = CompetencyCandidate(
                        content=chunk_content,
                        start_page=start_page + 1,
                        end_page=end_page,
                        confidence_score=semantic_score,
                        extraction_method="semantic_chunk_analysis",
                        role_coverage=role_coverage,
                        contamination_level=contamination,
                        quality_score=quality
                    )
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Semantic extraction failed: {str(e)}")
        
        return candidates
    
    def _density_extraction(self, doc: fitz.Document) -> List[CompetencyCandidate]:
        """Density-based discovery"""
        candidates = []
        
        try:
            # Calculate competency density per page
            page_scores = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                density = self._calculate_competency_density(page_text)
                page_scores.append((page_num, density, page_text))
            
            # Find high-density regions
            regions = self._find_density_regions(page_scores)
            
            for start_page, end_page, avg_density in regions:
                content = self._extract_pages_content(doc, start_page, end_page)
                
                if len(content) >= self.thresholds['min_content_length']:
                    role_coverage = self._count_canmeds_roles(content)
                    contamination = self._calculate_contamination(content)
                    quality = self._calculate_quality_score(content)
                    
                    candidate = CompetencyCandidate(
                        content=content,
                        start_page=start_page + 1,
                        end_page=end_page + 1,
                        confidence_score=min(0.9, avg_density * 1.5),
                        extraction_method="density_based_discovery",
                        role_coverage=role_coverage,
                        contamination_level=contamination,
                        quality_score=quality
                    )
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Density extraction failed: {str(e)}")
        
        return candidates
    
    def _fallback_extraction(self, doc: fitz.Document) -> List[CompetencyCandidate]:
        """Fallback extraction strategies"""
        candidates = []
        
        try:
            # Try document sections with relaxed thresholds
            sections = [
                (0, min(25, len(doc))),  # Beginning
                (max(0, len(doc) // 2 - 10), min(len(doc), len(doc) // 2 + 10)),  # Middle
                (max(0, len(doc) - 25), len(doc))  # End
            ]
            
            for start_page, end_page in sections:
                content = self._extract_pages_content(doc, start_page, end_page - 1)
                
                if content and len(content) >= 500:  # Relaxed threshold
                    role_coverage = self._count_canmeds_roles(content)
                    
                    if role_coverage >= 1:
                        contamination = self._calculate_contamination(content)
                        quality = self._calculate_quality_score(content)
                        
                        candidate = CompetencyCandidate(
                            content=content,
                            start_page=start_page + 1,
                            end_page=end_page,
                            confidence_score=0.4 + role_coverage * 0.05,
                            extraction_method="fallback_section_analysis",
                            role_coverage=role_coverage,
                            contamination_level=contamination,
                            quality_score=quality
                        )
                        candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Fallback extraction failed: {str(e)}")
        
        return candidates
    
    def _select_best_candidate(self, candidates: List[CompetencyCandidate]) -> Optional[CompetencyCandidate]:
        """Select best candidate using comprehensive scoring"""
        if not candidates:
            return None
        
        scored_candidates = []
        
        for candidate in candidates:
            # Comprehensive scoring
            score = (
                candidate.confidence_score * 0.25 +  # Extraction confidence
                (candidate.role_coverage / 7.0) * 0.30 +  # Role coverage
                (1.0 - candidate.contamination_level) * 0.20 +  # Contamination (inverted)
                (candidate.quality_score / 150.0) * 0.15 +  # Quality score
                min(1.0, len(candidate.content) / 10000.0) * 0.10  # Content sufficiency
            )
            
            scored_candidates.append((candidate, score))
        
        # Return highest scoring candidate
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]
    
    def _process_content(self, candidate: CompetencyCandidate, doc: fitz.Document) -> Dict[str, Any]:
        """Process and optimize content"""
        content = candidate.content
        
        # Clean content
        content = self._clean_content(content)
        
        # Enhance structure
        content = self._enhance_structure(content)
        
        return {
            'content': content,
            'start_page': candidate.start_page,
            'end_page': candidate.end_page
        }
    
    def _validate_content(self, processed_content: Dict[str, Any], pdf_path: str) -> Dict[str, Any]:
        """Validate content with adaptive thresholds"""
        content = processed_content['content']
        
        # Calculate validation metrics
        role_count = self._count_canmeds_roles(content)
        competency_score = self._calculate_competency_content_score(content)
        structure_score = self._analyze_structure(content)
        contamination_score = self._calculate_contamination(content)
        
        # Adaptive thresholds based on content characteristics
        min_roles = 1 if len(content) < 5000 else 2
        min_competency = 25 if len(content) < 3000 else 35
        
        # Calculate overall quality
        quality_score = (
            (role_count / 7.0) * 40 +  # Role coverage
            (competency_score / 100.0) * 30 +  # Competency content
            structure_score * 15 +  # Structure
            (1.0 - contamination_score) * 15  # Contamination (inverted)
        ) * 150 / 100
        
        # Validation check
        is_valid = (
            role_count >= min_roles and
            competency_score >= min_competency and
            len(content) >= self.thresholds['min_content_length'] and
            contamination_score <= self.thresholds['max_contamination']
        )
        
        # Quality classification
        if quality_score >= 140:
            description = f"Supreme CanMEDS format (score: {quality_score:.0f}/150, {role_count}/7 roles)"
        elif quality_score >= 130:
            description = f"Excellent CanMEDS format (score: {quality_score:.0f}/150, {role_count}/7 roles)"
        elif quality_score >= 100:
            description = f"Good CanMEDS format (score: {quality_score:.0f}/150, {role_count}/7 roles)"
        elif quality_score >= 70:
            description = f"Acceptable CanMEDS format (score: {quality_score:.0f}/150, {role_count}/7 roles)"
        else:
            description = f"Insufficient CanMEDS content (score: {quality_score:.0f}/150, {role_count}/7 roles)"
            is_valid = False
        
        return {
            'is_valid': is_valid,
            'quality_score': quality_score,
            'description': description,
            'reason': 'Below quality standards' if not is_valid else None,
            'analysis': {
                'role_count': role_count,
                'roles_found': self._get_found_roles(content),
                'competency_terms_count': len(self._find_competency_terms(content)),
                'has_structured_content': structure_score > 0.5,
                'content_length': len(content),
                'competency_type_score': int(competency_score),
                'contamination_score': int(contamination_score * 100),
                'page_range_size': processed_content['end_page'] - processed_content['start_page'] + 1
            }
        }
    
    def _enhance_content(self, processed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance content quality"""
        content = processed_content['content']
        
        # Advanced content enhancement
        content = self._fix_role_headers(content)
        content = self._improve_formatting(content)
        content = self._optimize_structure(content)
        
        return {
            **processed_content,
            'content': content
        }
    
    # Helper methods for all strategies
    
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
            r'(?i)\bappendix\b.*\n'
        ]
        
        contamination_words = 0
        for pattern in contamination_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            contamination_words += sum(len(match.split()) for match in matches)
        
        return min(1.0, contamination_words / total_words)
    
    def _calculate_quality_score(self, content: str) -> float:
        """Calculate overall quality score"""
        role_count = self._count_canmeds_roles(content)
        competency_terms = len(self._find_competency_terms(content))
        structure_score = self._analyze_structure(content)
        
        score = (
            role_count * 15 +  # Role coverage
            competency_terms * 5 +  # Competency terms
            structure_score * 30  # Structure quality
        )
        
        return min(150, score)
    
    def _calculate_semantic_score(self, content: str) -> float:
        """Calculate semantic relevance score"""
        content_lower = content.lower()
        
        # Count competency indicators
        indicator_count = sum(1 for indicator in self.competency_indicators if indicator in content_lower)
        
        # Count role mentions
        role_count = self._count_canmeds_roles(content)
        
        # Count educational terms
        educational_terms = ['assess', 'evaluat', 'demonstrat', 'develop', 'achiev', 'perform']
        educational_count = sum(1 for term in educational_terms if term in content_lower)
        
        # Calculate score (0-1)
        total_score = indicator_count * 3 + role_count * 4 + educational_count * 2
        return min(1.0, total_score / 40)
    
    def _calculate_competency_density(self, text: str) -> float:
        """Calculate competency density"""
        if not text:
            return 0.0
        
        words = text.lower().split()
        if not words:
            return 0.0
        
        competency_words = 0
        for word in words:
            if any(indicator in word for indicator in self.competency_indicators):
                competency_words += 2
            elif any(any(role_term in word for role_term in role_terms) 
                    for role_terms in self.canmeds_roles.values()):
                competency_words += 1
        
        return competency_words / len(words)
    
    def _calculate_pattern_confidence(self, content: str, pattern: str) -> float:
        """Calculate confidence for pattern-based extraction"""
        base_confidence = 0.75
        
        role_count = self._count_canmeds_roles(content)
        competency_terms = len(self._find_competency_terms(content))
        
        confidence = base_confidence + (role_count * 0.05) + (competency_terms * 0.02)
        
        return min(1.0, confidence)
    
    def _find_competency_terms(self, content: str) -> List[str]:
        """Find competency terms in content"""
        content_lower = content.lower()
        found_terms = []
        
        for indicator in self.competency_indicators:
            if indicator in content_lower:
                found_terms.append(indicator)
        
        return found_terms
    
    def _analyze_structure(self, text: str) -> float:
        """Analyze text structure"""
        if not text:
            return 0.0
        
        bullets = len(re.findall(r'(?m)^\s*[•\-\*]', text))
        numbers = len(re.findall(r'(?m)^\s*\d+\.', text))
        headers = len(re.findall(r'(?m)^[A-Z][A-Z\s]+:?$', text))
        
        total_lines = len(text.split('\n'))
        structure_ratio = (bullets + numbers + headers) / max(1, total_lines)
        
        return min(1.0, structure_ratio * 4)
    
    def _calculate_competency_content_score(self, content: str) -> float:
        """Calculate competency content score"""
        content_lower = content.lower()
        
        indicator_score = sum(8 for indicator in self.competency_indicators if indicator in content_lower)
        role_score = self._count_canmeds_roles(content) * 6
        assessment_terms = ['assess', 'evaluat', 'demonstrat', 'develop', 'achiev']
        assessment_score = sum(4 for term in assessment_terms if term in content_lower)
        
        return min(100, indicator_score + role_score + assessment_score)
    
    # Additional helper methods
    
    def _find_section_end(self, doc: fitz.Document, toc: List, start_page: int, level: int) -> int:
        """Find where a TOC section ends"""
        # Look for next section at same or higher level
        for toc_level, title, page_num in toc:
            if page_num - 1 > start_page and toc_level <= level:
                return page_num - 1
        
        # Default: reasonable extension
        return min(start_page + 30, len(doc))
    
    def _find_intelligent_section_end(self, full_text: str, start_pos: int) -> int:
        """Find intelligent section end using content analysis"""
        search_text = full_text[start_pos:]
        
        # Look for section breaks
        section_patterns = [
            r'(?i)\n\s*(?:references?|bibliography|appendix)\s*\n',
            r'(?i)\n\s*\d+\.\s+[A-Z][^:\n]{15,}\s*\n',
            r'(?i)\n\s*[A-Z][A-Z\s]{8,}:\s*\n'
        ]
        
        min_end = len(search_text)
        for pattern in section_patterns:
            match = re.search(pattern, search_text)
            if match and match.start() > 800:  # Minimum section size
                min_end = min(min_end, match.start())
        
        return start_pos + min(min_end, 40000)  # Maximum section size
    
    def _pos_to_page(self, position: int, page_breaks: List[int]) -> int:
        """Convert text position to page number"""
        for i, break_pos in enumerate(page_breaks):
            if position < break_pos:
                return max(0, i - 1)
        return len(page_breaks) - 1
    
    def _find_density_regions(self, page_scores: List[Tuple[int, float, str]]) -> List[Tuple[int, int, float]]:
        """Find high-density regions"""
        regions = []
        high_pages = [p for p, density, _ in page_scores if density > 0.08]
        
        if not high_pages:
            return regions
        
        # Group consecutive high-density pages
        current_region = None
        
        for page_num in high_pages:
            if current_region is None:
                current_region = [page_num, page_num, [page_scores[page_num][1]]]
            elif page_num == current_region[1] + 1:
                current_region[1] = page_num
                current_region[2].append(page_scores[page_num][1])
            else:
                if len(current_region[2]) >= 3:  # Minimum region size
                    avg_density = sum(current_region[2]) / len(current_region[2])
                    regions.append((current_region[0], current_region[1], avg_density))
                
                current_region = [page_num, page_num, [page_scores[page_num][1]]]
        
        # Don't forget the last region
        if current_region and len(current_region[2]) >= 3:
            avg_density = sum(current_region[2]) / len(current_region[2])
            regions.append((current_region[0], current_region[1], avg_density))
        
        return regions
    
    # Content enhancement methods
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        # Remove page headers/footers
        content = re.sub(r'(?m)^.*(?:page\s+\d+|©.*|proprietary).*$', '', content, flags=re.IGNORECASE)
        
        # Fix spacing
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r' {3,}', ' ', content)
        
        return content.strip()
    
    def _enhance_structure(self, content: str) -> str:
        """Enhance content structure"""
        # Ensure proper role formatting
        content = re.sub(r'(?i)(medical\s+expert|communicator|collaborator|leader|health\s+advocate|scholar|professional)\s*:', 
                        r'\n\1:\n', content)
        
        return content
    
    def _fix_role_headers(self, content: str) -> str:
        """Fix role headers"""
        # Standardize role headers
        role_mappings = {
            'medical expert': 'MEDICAL EXPERT',
            'communicator': 'COMMUNICATOR',
            'collaborator': 'COLLABORATOR',
            'leader': 'LEADER',
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
        
        return content
    
    def _optimize_structure(self, content: str) -> str:
        """Optimize content structure"""
        # Add spacing around major sections
        content = re.sub(r'(?i)(MEDICAL EXPERT|COMMUNICATOR|COLLABORATOR|LEADER|HEALTH ADVOCATE|SCHOLAR|PROFESSIONAL):', 
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
        print("Usage: python final_perfected_canmeds_extractor.py <pdf_path_or_directory> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = FinalPerfectedExtractor()
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
        'category': 'Final Perfected CanMEDS Format (maximum performance)',
        'total_documents': len(results),
        'successful_extractions': len(successful),
        'excellent_extractions': len(excellent),
        'supreme_extractions': len(supreme),
        'extraction_rate': f"{len(successful)/len(results)*100:.1f}%",
        'excellent_rate': f"{len(excellent)/len(results)*100:.1f}%",
        'supreme_rate': f"{len(supreme)/len(results)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary_final.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== Final Perfected Extraction Summary ===")
    print(f"Total documents: {len(results)}")
    print(f"Successful extractions: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Excellent quality: {len(excellent)} ({len(excellent)/len(results)*100:.1f}%)")
    print(f"Supreme quality: {len(supreme)} ({len(supreme)/len(results)*100:.1f}%)")
    print(f"Summary saved: {summary_file}")

if __name__ == "__main__":
    main()
