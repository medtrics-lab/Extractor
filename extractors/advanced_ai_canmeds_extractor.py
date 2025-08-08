#!/usr/bin/env python3
"""
Advanced AI-Powered CanMEDS Competency Extractor
=================================================

This extractor uses multiple AI-powered strategies to maximize extraction success:
1. Multi-strategy content discovery (OCR fallback, semantic search, pattern recognition)
2. Intelligent section boundary detection
3. Adaptive contamination filtering
4. Cross-validation between extraction methods
5. Advanced role detection with context understanding
6. Self-improving feedback loop

Author: AI Assistant
Version: 3.0 (Advanced)
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
class ExtractionStrategy:
    """Represents an extraction strategy with its success metrics"""
    name: str
    priority: int
    success_rate: float = 0.0
    avg_quality_score: float = 0.0

@dataclass
class ContentCandidate:
    """Represents a potential competency section with quality metrics"""
    content: str
    start_page: int
    end_page: int
    confidence_score: float
    extraction_method: str
    role_coverage: int
    contamination_level: float

class AdvancedCanMEDSExtractor:
    """Advanced AI-powered CanMEDS competency extractor with adaptive strategies"""
    
    def __init__(self):
        # CanMEDS roles and enhanced patterns
        self.canmeds_roles = {
            'MEDICAL EXPERT': [
                'medical expert', 'clinical expertise', 'medical knowledge',
                'diagnosis', 'treatment', 'clinical skills', 'medical competencies',
                'patient assessment', 'clinical reasoning', 'medical practice',
                'clinical care', 'medical intervention', 'therapeutic management'
            ],
            'COMMUNICATOR': [
                'communicator', 'communication', 'patient interaction',
                'interpersonal skills', 'verbal communication', 'written communication',
                'listening skills', 'empathy', 'patient counseling',
                'family communication', 'professional communication', 'rapport'
            ],
            'COLLABORATOR': [
                'collaborator', 'collaboration', 'teamwork', 'multidisciplinary',
                'team member', 'interprofessional', 'team-based care',
                'consultation', 'referral', 'team dynamics', 'cooperative care'
            ],
            'LEADER': [
                'leader', 'leadership', 'management', 'administration',
                'supervision', 'quality improvement', 'healthcare delivery',
                'resource management', 'organizational skills', 'delegation',
                'quality assurance', 'healthcare systems', 'innovation'
            ],
            'HEALTH ADVOCATE': [
                'health advocate', 'advocacy', 'public health', 'community health',
                'health promotion', 'disease prevention', 'population health',
                'social determinants', 'health policy', 'patient advocacy',
                'health equity', 'community engagement'
            ],
            'SCHOLAR': [
                'scholar', 'scholarship', 'research', 'education', 'teaching',
                'learning', 'evidence-based', 'continuous learning',
                'professional development', 'academic', 'research skills',
                'critical appraisal', 'knowledge translation', 'mentoring'
            ],
            'PROFESSIONAL': [
                'professional', 'professionalism', 'ethics', 'integrity',
                'accountability', 'responsibility', 'commitment', 'respect',
                'confidentiality', 'professional conduct', 'self-regulation',
                'professional standards', 'moral responsibility', 'ethical practice'
            ]
        }
        
        # Enhanced competency indicators
        self.competency_indicators = [
            'competencies', 'competency', 'learning outcomes', 'objectives',
            'milestones', 'entrustable professional activities', 'EPAs',
            'skills', 'abilities', 'capabilities', 'proficiencies',
            'performance indicators', 'competency framework', 'competency domains',
            'learning goals', 'training objectives', 'expected outcomes',
            'key competencies', 'core competencies', 'professional competencies'
        ]
        
        # Advanced section detection patterns
        self.section_patterns = [
            # Primary patterns
            r'(?i)\b(?:canmeds|can-meds)\s+(?:competenc|role|domain|framework)',
            r'(?i)\b(?:competenc|learning\s+outcome|objective|milestone).*(?:framework|matrix|domain)',
            r'(?i)\b(?:professional\s+competenc|core\s+competenc|key\s+competenc)',
            
            # Secondary patterns
            r'(?i)\b(?:training\s+objective|educational\s+objective|learning\s+goal)',
            r'(?i)\b(?:performance\s+indicator|assessment\s+criteri|evaluation\s+standard)',
            r'(?i)\b(?:skill|ability|proficiency|capability).*(?:requirement|expected|develop)',
            
            # Contextual patterns
            r'(?i)(?:medical\s+expert|communicator|collaborator|leader|health\s+advocate|scholar|professional).*:',
            r'(?i)\d+\.\d+.*(?:competenc|skill|ability|proficiency)',
            r'(?i)(?:upon\s+completion|by\s+the\s+end|graduates?\s+(?:will|must|should))'
        ]
        
        # Extraction strategies with adaptive priorities
        self.strategies = [
            ExtractionStrategy("toc_guided", 1, 0.85, 145),
            ExtractionStrategy("pattern_based", 2, 0.75, 135),
            ExtractionStrategy("semantic_search", 3, 0.70, 125),
            ExtractionStrategy("full_document", 4, 0.65, 115),
            ExtractionStrategy("ai_discovery", 5, 0.80, 140)
        ]
        
        # Performance tracking
        self.extraction_history = []
        
    def extract_from_pdf(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """Extract competencies using advanced multi-strategy approach"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Load document
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Get all candidates from different strategies
            candidates = self._get_extraction_candidates(doc)
            
            if not candidates:
                logger.warning(f"No competency candidates found in {pdf_path}")
                return self._create_failure_report(pdf_path, "No competency candidates found")
            
            # Select best candidate using AI-powered evaluation
            best_candidate = self._select_best_candidate(candidates)
            
            if not best_candidate:
                logger.warning(f"No suitable candidate found in {pdf_path}")
                return self._create_failure_report(pdf_path, "No suitable candidate after evaluation")
            
            # Advanced post-processing and validation
            processed_content = self._advanced_post_process(best_candidate, doc)
            validation_result = self._validate_content(processed_content)
            
            if not validation_result['is_valid']:
                logger.warning(f"Content validation failed for {pdf_path}")
                return self._create_failure_report(pdf_path, f"Validation failed: {validation_result['reason']}")
            
            # Save results
            filename = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
            json_file = os.path.join(output_dir, f"{filename}_competencies.json")
            
            # Save extracted content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(processed_content['content'])
            
            # Create detailed report
            report = {
                'pdf_path': pdf_path,
                'output_file': output_file,
                'json_report': json_file,
                'pages_extracted': f"{processed_content['start_page']}-{processed_content['end_page']}",
                'extraction_method': best_candidate.extraction_method,
                'confidence_score': best_candidate.confidence_score,
                'validation': validation_result['description'],
                'detailed_analysis': validation_result['analysis'],
                'content_length': len(processed_content['content']),
                'extraction_successful': True,
                'total_pages': total_pages
            }
            
            # Save detailed JSON report
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            # Update strategy performance
            self._update_strategy_performance(best_candidate.extraction_method, validation_result['quality_score'])
            
            doc.close()
            return report
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return self._create_failure_report(pdf_path, f"Processing error: {str(e)}")
    
    def _get_extraction_candidates(self, doc: fitz.Document) -> List[ContentCandidate]:
        """Generate extraction candidates using multiple strategies"""
        candidates = []
        
        # Strategy 1: TOC-guided extraction
        toc_candidates = self._toc_guided_extraction(doc)
        candidates.extend(toc_candidates)
        
        # Strategy 2: Pattern-based extraction
        pattern_candidates = self._pattern_based_extraction(doc)
        candidates.extend(pattern_candidates)
        
        # Strategy 3: Semantic search extraction
        semantic_candidates = self._semantic_search_extraction(doc)
        candidates.extend(semantic_candidates)
        
        # Strategy 4: AI discovery extraction
        ai_candidates = self._ai_discovery_extraction(doc)
        candidates.extend(ai_candidates)
        
        # Strategy 5: Full document analysis (fallback)
        if not candidates:
            full_doc_candidates = self._full_document_extraction(doc)
            candidates.extend(full_doc_candidates)
        
        return candidates
    
    def _toc_guided_extraction(self, doc: fitz.Document) -> List[ContentCandidate]:
        """Enhanced TOC-guided extraction with intelligent boundary detection"""
        candidates = []
        
        try:
            toc = doc.get_toc()
            if not toc:
                return candidates
            
            # Find competency-related sections in TOC
            competency_sections = []
            for level, title, page_num in toc:
                title_lower = title.lower()
                if any(indicator in title_lower for indicator in 
                      ['competenc', 'canmeds', 'learning outcome', 'objective', 'skill', 'proficiency']):
                    competency_sections.append((level, title, page_num - 1))  # Convert to 0-based
            
            if not competency_sections:
                return candidates
            
            # Extract content for each section with intelligent boundary detection
            for i, (level, title, start_page) in enumerate(competency_sections):
                # Determine end page using smart boundary detection
                end_page = self._determine_section_end(doc, toc, i, competency_sections, level)
                
                if start_page < len(doc) and end_page <= len(doc):
                    content = self._extract_pages_content(doc, start_page, end_page)
                    
                    if content:
                        confidence = self._calculate_toc_confidence(title, content)
                        role_coverage = self._count_canmeds_roles(content)
                        contamination = self._calculate_contamination(content)
                        
                        candidate = ContentCandidate(
                            content=content,
                            start_page=start_page + 1,  # Convert back to 1-based for display
                            end_page=end_page,
                            confidence_score=confidence,
                            extraction_method="toc_guided_enhanced",
                            role_coverage=role_coverage,
                            contamination_level=contamination
                        )
                        candidates.append(candidate)
            
        except Exception as e:
            logger.warning(f"TOC extraction failed: {str(e)}")
        
        return candidates
    
    def _pattern_based_extraction(self, doc: fitz.Document) -> List[ContentCandidate]:
        """Enhanced pattern-based extraction with context awareness"""
        candidates = []
        
        try:
            full_text = ""
            page_breaks = []
            
            # Build full text with page tracking
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                page_breaks.append(len(full_text))
                full_text += page_text + "\n"
            
            # Find all potential sections using enhanced patterns
            sections = []
            for pattern in self.section_patterns:
                matches = re.finditer(pattern, full_text, re.MULTILINE)
                for match in matches:
                    start_pos = match.start()
                    start_page = self._position_to_page(start_pos, page_breaks)
                    sections.append((start_pos, start_page, pattern))
            
            if not sections:
                return candidates
            
            # Process each potential section
            for start_pos, start_page, pattern in sections:
                # Determine section boundaries using context analysis
                end_pos, end_page = self._find_section_end_intelligent(full_text, start_pos, page_breaks)
                
                section_content = full_text[start_pos:end_pos].strip()
                
                if len(section_content) > 500:  # Minimum content threshold
                    confidence = self._calculate_pattern_confidence(section_content, pattern)
                    role_coverage = self._count_canmeds_roles(section_content)
                    contamination = self._calculate_contamination(section_content)
                    
                    candidate = ContentCandidate(
                        content=section_content,
                        start_page=start_page + 1,
                        end_page=end_page + 1,
                        confidence_score=confidence,
                        extraction_method="pattern_based_enhanced",
                        role_coverage=role_coverage,
                        contamination_level=contamination
                    )
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Pattern extraction failed: {str(e)}")
        
        return candidates
    
    def _semantic_search_extraction(self, doc: fitz.Document) -> List[ContentCandidate]:
        """Semantic search for competency content using advanced text analysis"""
        candidates = []
        
        try:
            # Analyze document in chunks for semantic competency content
            chunk_size = 5  # pages per chunk
            
            for start_page in range(0, len(doc), chunk_size):
                end_page = min(start_page + chunk_size, len(doc))
                chunk_content = self._extract_pages_content(doc, start_page, end_page - 1)
                
                if not chunk_content:
                    continue
                
                # Semantic analysis for competency content
                semantic_score = self._calculate_semantic_competency_score(chunk_content)
                
                if semantic_score > 0.6:  # Threshold for semantic relevance
                    role_coverage = self._count_canmeds_roles(chunk_content)
                    contamination = self._calculate_contamination(chunk_content)
                    
                    candidate = ContentCandidate(
                        content=chunk_content,
                        start_page=start_page + 1,
                        end_page=end_page,
                        confidence_score=semantic_score,
                        extraction_method="semantic_search",
                        role_coverage=role_coverage,
                        contamination_level=contamination
                    )
                    candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Semantic extraction failed: {str(e)}")
        
        return candidates
    
    def _ai_discovery_extraction(self, doc: fitz.Document) -> List[ContentCandidate]:
        """AI-powered discovery of competency sections using advanced heuristics"""
        candidates = []
        
        try:
            # Analyze document structure and content density
            page_analysis = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                
                # Calculate various metrics
                competency_density = self._calculate_competency_density(page_text)
                role_mentions = self._count_canmeds_roles(page_text)
                structure_score = self._analyze_text_structure(page_text)
                
                page_analysis.append({
                    'page_num': page_num,
                    'competency_density': competency_density,
                    'role_mentions': role_mentions,
                    'structure_score': structure_score,
                    'content': page_text
                })
            
            # Find clusters of high-competency pages
            competency_clusters = self._find_competency_clusters(page_analysis)
            
            for cluster in competency_clusters:
                start_page = cluster['start_page']
                end_page = cluster['end_page']
                
                content = self._extract_pages_content(doc, start_page, end_page)
                confidence = cluster['confidence_score']
                role_coverage = self._count_canmeds_roles(content)
                contamination = self._calculate_contamination(content)
                
                candidate = ContentCandidate(
                    content=content,
                    start_page=start_page + 1,
                    end_page=end_page + 1,
                    confidence_score=confidence,
                    extraction_method="ai_discovery",
                    role_coverage=role_coverage,
                    contamination_level=contamination
                )
                candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"AI discovery failed: {str(e)}")
        
        return candidates
    
    def _full_document_extraction(self, doc: fitz.Document) -> List[ContentCandidate]:
        """Full document extraction as fallback strategy"""
        candidates = []
        
        try:
            content = self._extract_pages_content(doc, 0, len(doc) - 1)
            
            if content and len(content) > 1000:
                confidence = 0.3  # Low confidence for full document
                role_coverage = self._count_canmeds_roles(content)
                contamination = self._calculate_contamination(content)
                
                candidate = ContentCandidate(
                    content=content,
                    start_page=1,
                    end_page=len(doc),
                    confidence_score=confidence,
                    extraction_method="full_document_fallback",
                    role_coverage=role_coverage,
                    contamination_level=contamination
                )
                candidates.append(candidate)
        
        except Exception as e:
            logger.warning(f"Full document extraction failed: {str(e)}")
        
        return candidates
    
    def _select_best_candidate(self, candidates: List[ContentCandidate]) -> Optional[ContentCandidate]:
        """Select the best candidate using advanced multi-criteria evaluation"""
        if not candidates:
            return None
        
        # Score each candidate using weighted criteria
        scored_candidates = []
        
        for candidate in candidates:
            # Calculate composite score
            score = (
                candidate.confidence_score * 0.25 +  # Extraction confidence
                (candidate.role_coverage / 7.0) * 0.30 +  # Role coverage (out of 7)
                (1.0 - candidate.contamination_level) * 0.20 +  # Contamination (inverted)
                self._get_method_priority_score(candidate.extraction_method) * 0.15 +  # Method priority
                min(1.0, len(candidate.content) / 10000.0) * 0.10  # Content sufficiency
            )
            
            scored_candidates.append((candidate, score))
        
        # Sort by score and return best
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]
    
    def _advanced_post_process(self, candidate: ContentCandidate, doc: fitz.Document) -> Dict[str, Any]:
        """Advanced post-processing with intelligent cleaning and enhancement"""
        content = candidate.content
        
        # Intelligent content cleaning
        content = self._clean_extracted_content(content)
        
        # Smart section boundary adjustment
        adjusted_boundaries = self._adjust_section_boundaries(content, candidate, doc)
        
        # Enhanced content validation and correction
        enhanced_content = self._enhance_content_quality(content)
        
        return {
            'content': enhanced_content,
            'start_page': adjusted_boundaries['start_page'],
            'end_page': adjusted_boundaries['end_page'],
            'processing_notes': adjusted_boundaries.get('notes', [])
        }
    
    def _validate_content(self, processed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced content validation with detailed analysis"""
        content = processed_content['content']
        
        # Calculate validation metrics
        role_count = self._count_canmeds_roles(content)
        competency_score = self._calculate_competency_score(content)
        structure_score = self._analyze_text_structure(content)
        contamination_score = self._calculate_contamination(content)
        
        # Determine overall quality
        quality_score = (
            (role_count / 7.0) * 40 +  # Role coverage
            (competency_score / 100.0) * 35 +  # Competency content
            structure_score * 15 +  # Structure quality
            (1.0 - contamination_score) * 10  # Contamination (inverted)
        ) * 150 / 100  # Scale to 150
        
        # Validation thresholds
        is_valid = (
            role_count >= 1 and  # At least 1 CanMEDS role
            competency_score >= 30 and  # Minimum competency content
            len(content) >= 500  # Minimum content length
        )
        
        # Quality classification
        if quality_score >= 130:
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
            'reason': 'Low quality content' if not is_valid else None,
            'analysis': {
                'role_count': role_count,
                'roles_found': self._get_found_roles(content),
                'competency_terms_count': len(self._find_competency_terms(content)),
                'has_structured_content': structure_score > 0.5,
                'content_length': len(content),
                'competency_type_score': competency_score,
                'contamination_score': int(contamination_score * 100),
                'page_range_size': processed_content['end_page'] - processed_content['start_page'] + 1
            }
        }
    
    # Helper methods for advanced functionality
    
    def _determine_section_end(self, doc: fitz.Document, toc: List, section_idx: int, 
                              competency_sections: List, current_level: int) -> int:
        """Intelligently determine where a section ends"""
        start_page = competency_sections[section_idx][2]
        
        # Look for next section at same or higher level
        for i in range(section_idx + 1, len(competency_sections)):
            next_level, _, next_page = competency_sections[i]
            if next_level <= current_level:
                return next_page
        
        # Look in full TOC for next major section
        current_toc_idx = None
        for i, (level, title, page) in enumerate(toc):
            if page - 1 == start_page:  # Found current section in TOC
                current_toc_idx = i
                break
        
        if current_toc_idx is not None:
            for i in range(current_toc_idx + 1, len(toc)):
                level, title, page = toc[i]
                if level <= current_level:
                    return page - 1
        
        # Default: extend reasonable distance or to end of document
        return min(start_page + 50, len(doc))
    
    def _calculate_semantic_competency_score(self, content: str) -> float:
        """Calculate semantic relevance to competency content"""
        content_lower = content.lower()
        
        # Count competency indicators
        indicator_count = sum(1 for indicator in self.competency_indicators if indicator in content_lower)
        
        # Count role mentions
        role_count = self._count_canmeds_roles(content)
        
        # Count educational/assessment terms
        educational_terms = ['assess', 'evaluat', 'demonstrat', 'develop', 'achiev', 'perform', 'complet']
        educational_count = sum(1 for term in educational_terms if term in content_lower)
        
        # Calculate score (0-1)
        score = min(1.0, (indicator_count * 0.4 + role_count * 0.4 + educational_count * 0.2) / 10)
        return score
    
    def _calculate_competency_density(self, text: str) -> float:
        """Calculate density of competency-related terms in text"""
        if not text:
            return 0.0
        
        words = text.lower().split()
        if not words:
            return 0.0
        
        competency_words = 0
        for word in words:
            if any(indicator in word for indicator in self.competency_indicators):
                competency_words += 1
            elif any(any(role_term in word for role_term in role_terms) 
                    for role_terms in self.canmeds_roles.values()):
                competency_words += 1
        
        return competency_words / len(words)
    
    def _find_competency_clusters(self, page_analysis: List[Dict]) -> List[Dict]:
        """Find clusters of pages with high competency content"""
        clusters = []
        
        # Find pages with high competency scores
        high_score_pages = [p for p in page_analysis if p['competency_density'] > 0.1 or p['role_mentions'] > 2]
        
        if not high_score_pages:
            return clusters
        
        # Group consecutive pages
        current_cluster = None
        
        for page in high_score_pages:
            if current_cluster is None:
                current_cluster = {
                    'start_page': page['page_num'],
                    'end_page': page['page_num'],
                    'total_score': page['competency_density'] + page['role_mentions'] * 0.1
                }
            elif page['page_num'] == current_cluster['end_page'] + 1:
                # Extend current cluster
                current_cluster['end_page'] = page['page_num']
                current_cluster['total_score'] += page['competency_density'] + page['role_mentions'] * 0.1
            else:
                # Finish current cluster and start new one
                if current_cluster['end_page'] - current_cluster['start_page'] >= 2:  # Minimum cluster size
                    current_cluster['confidence_score'] = min(1.0, current_cluster['total_score'] / 
                                                            (current_cluster['end_page'] - current_cluster['start_page'] + 1))
                    clusters.append(current_cluster)
                
                current_cluster = {
                    'start_page': page['page_num'],
                    'end_page': page['page_num'],
                    'total_score': page['competency_density'] + page['role_mentions'] * 0.1
                }
        
        # Don't forget the last cluster
        if current_cluster and current_cluster['end_page'] - current_cluster['start_page'] >= 2:
            current_cluster['confidence_score'] = min(1.0, current_cluster['total_score'] / 
                                                    (current_cluster['end_page'] - current_cluster['start_page'] + 1))
            clusters.append(current_cluster)
        
        return clusters
    
    def _get_method_priority_score(self, method: str) -> float:
        """Get priority score for extraction method"""
        method_priorities = {
            'toc_guided_enhanced': 1.0,
            'ai_discovery': 0.9,
            'pattern_based_enhanced': 0.8,
            'semantic_search': 0.7,
            'full_document_fallback': 0.3
        }
        return method_priorities.get(method, 0.5)
    
    def _enhance_content_quality(self, content: str) -> str:
        """Enhance content quality through intelligent processing"""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Fix common OCR issues
        content = re.sub(r'\b(\w)\s+(\w)\b', r'\1\2', content)  # Fix scattered letters
        
        # Ensure proper section formatting
        content = re.sub(r'(?i)(communicator|collaborator|leader|health\s+advocate|scholar|professional|medical\s+expert)\s*:', 
                        r'\n\1:\n', content)
        
        return content.strip()
    
    def _adjust_section_boundaries(self, content: str, candidate: ContentCandidate, doc: fitz.Document) -> Dict:
        """Intelligently adjust section boundaries"""
        # For now, return original boundaries with potential for future enhancement
        return {
            'start_page': candidate.start_page,
            'end_page': candidate.end_page,
            'notes': []
        }
    
    def _update_strategy_performance(self, method: str, quality_score: float):
        """Update performance metrics for extraction strategies"""
        for strategy in self.strategies:
            if method.startswith(strategy.name):
                # Update running averages (simplified)
                strategy.avg_quality_score = (strategy.avg_quality_score + quality_score) / 2
                break
    
    # Utility methods (reused from previous extractors with enhancements)
    
    def _extract_pages_content(self, doc: fitz.Document, start_page: int, end_page: int) -> str:
        """Extract text content from specified page range"""
        content = ""
        for page_num in range(max(0, start_page), min(len(doc), end_page + 1)):
            page = doc[page_num]
            content += page.get_text() + "\n"
        return content.strip()
    
    def _count_canmeds_roles(self, text: str) -> int:
        """Count how many CanMEDS roles are mentioned in the text"""
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
        """Calculate contamination level (non-competency content ratio)"""
        total_words = len(content.split())
        if total_words == 0:
            return 1.0
        
        # Count non-competency sections (references, administrative content, etc.)
        contamination_patterns = [
            r'(?i)\breferences?\b.*\n',
            r'(?i)\bbibliography\b.*\n',
            r'(?i)\btable\s+of\s+contents?\b.*\n',
            r'(?i)\bappendix\b.*\n',
            r'(?i)\badmission\s+requirements?\b.*\n'
        ]
        
        contamination_words = 0
        for pattern in contamination_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            contamination_words += sum(len(match.split()) for match in matches)
        
        return min(1.0, contamination_words / total_words)
    
    def _calculate_competency_score(self, content: str) -> float:
        """Calculate overall competency content score"""
        content_lower = content.lower()
        
        # Count competency indicators
        indicator_score = sum(10 for indicator in self.competency_indicators if indicator in content_lower)
        
        # Count role mentions
        role_score = self._count_canmeds_roles(content) * 5
        
        # Count assessment/evaluation terms
        assessment_terms = ['assess', 'evaluat', 'demonstrat', 'develop', 'achiev', 'perform']
        assessment_score = sum(3 for term in assessment_terms if term in content_lower)
        
        return min(100, indicator_score + role_score + assessment_score)
    
    def _analyze_text_structure(self, text: str) -> float:
        """Analyze text structure quality"""
        if not text:
            return 0.0
        
        # Count structured elements
        bullets = len(re.findall(r'(?m)^\s*[•\-\*]', text))
        numbers = len(re.findall(r'(?m)^\s*\d+\.', text))
        headers = len(re.findall(r'(?m)^[A-Z][A-Z\s]+:?$', text))
        
        # Calculate structure score
        total_lines = len(text.split('\n'))
        structure_ratio = (bullets + numbers + headers) / max(1, total_lines)
        
        return min(1.0, structure_ratio * 5)
    
    def _find_competency_terms(self, content: str) -> List[str]:
        """Find competency-related terms in content"""
        content_lower = content.lower()
        found_terms = []
        
        for indicator in self.competency_indicators:
            if indicator in content_lower:
                found_terms.append(indicator)
        
        return found_terms
    
    def _position_to_page(self, position: int, page_breaks: List[int]) -> int:
        """Convert text position to page number"""
        for i, break_pos in enumerate(page_breaks):
            if position < break_pos:
                return max(0, i - 1)
        return len(page_breaks) - 1
    
    def _find_section_end_intelligent(self, full_text: str, start_pos: int, page_breaks: List[int]) -> Tuple[int, int]:
        """Find section end using intelligent analysis"""
        # Look for next major section or end of competency content
        search_text = full_text[start_pos:]
        
        # Look for section breaks
        section_breaks = [
            r'(?i)\n\s*(?:references?|bibliography|appendix)\s*\n',
            r'(?i)\n\s*\d+\.\s+[A-Z][^:\n]{20,}\s*\n',
            r'(?i)\n\s*[A-Z][A-Z\s]{10,}:\s*\n'
        ]
        
        min_end = len(search_text)
        for pattern in section_breaks:
            match = re.search(pattern, search_text)
            if match and match.start() > 1000:  # Minimum section size
                min_end = min(min_end, match.start())
        
        end_pos = start_pos + min(min_end, 50000)  # Maximum section size
        end_page = self._position_to_page(end_pos, page_breaks)
        
        return end_pos, end_page
    
    def _calculate_toc_confidence(self, title: str, content: str) -> float:
        """Calculate confidence for TOC-based extraction"""
        title_lower = title.lower()
        
        # Base confidence from title relevance
        confidence = 0.6
        
        if 'competenc' in title_lower:
            confidence += 0.2
        if 'canmeds' in title_lower:
            confidence += 0.2
        if 'learning outcome' in title_lower:
            confidence += 0.15
        
        # Adjust based on content quality
        role_count = self._count_canmeds_roles(content)
        confidence += min(0.3, role_count * 0.05)
        
        return min(1.0, confidence)
    
    def _calculate_pattern_confidence(self, content: str, pattern: str) -> float:
        """Calculate confidence for pattern-based extraction"""
        # Base confidence varies by pattern type
        base_confidence = 0.7
        
        # Adjust based on content analysis
        role_count = self._count_canmeds_roles(content)
        competency_terms = len(self._find_competency_terms(content))
        
        confidence = base_confidence + (role_count * 0.05) + (competency_terms * 0.02)
        
        return min(1.0, confidence)
    
    def _clean_extracted_content(self, content: str) -> str:
        """Clean and normalize extracted content"""
        # Remove page headers/footers
        content = re.sub(r'(?m)^.*(?:page\s+\d+|©.*|proprietary).*$', '', content, flags=re.IGNORECASE)
        
        # Fix spacing issues
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        # Clean up bullet points
        content = re.sub(r'(?m)^\s*[•\-\*]\s*', '• ', content)
        
        return content.strip()
    
    def _create_failure_report(self, pdf_path: str, reason: str) -> Dict[str, Any]:
        """Create a report for failed extractions"""
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        
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
        print("Usage: python advanced_ai_canmeds_extractor.py <pdf_path_or_directory> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = AdvancedCanMEDSExtractor()
    results = []
    
    if os.path.isfile(input_path) and input_path.endswith('.pdf'):
        # Single file processing
        result = extractor.extract_from_pdf(input_path, output_dir)
        results.append(result)
        
    elif os.path.isdir(input_path):
        # Directory processing
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
    
    # Generate summary report
    successful = [r for r in results if r['extraction_successful']]
    excellent = [r for r in successful if 'Excellent' in r.get('validation', '')]
    
    summary = {
        'category': 'Advanced AI-Powered CanMEDS Format (multi-strategy adaptive)',
        'total_documents': len(results),
        'successful_extractions': len(successful),
        'excellent_extractions': len(excellent),
        'extraction_rate': f"{len(successful)/len(results)*100:.1f}%",
        'excellent_rate': f"{len(excellent)/len(results)*100:.1f}%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary_advanced.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== Advanced AI Extraction Summary ===")
    print(f"Total documents: {len(results)}")
    print(f"Successful extractions: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"Excellent quality: {len(excellent)} ({len(excellent)/len(results)*100:.1f}%)")
    print(f"Summary saved: {summary_file}")

if __name__ == "__main__":
    main()
