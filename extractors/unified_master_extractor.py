#!/usr/bin/env python3
"""
Unified Master CanMEDS Competency Extractor
==========================================

This extractor automatically detects document format and applies the most appropriate
extraction strategy. It combines all specialized extractors into a single unified system.

Key features:
1. Automatic document format detection
2. Dynamic extractor selection based on content analysis
3. Fallback strategies for unknown formats
4. Comprehensive quality assessment
5. Feedback loop for continuous improvement

Author: AI Assistant
Version: 1.0 (Unified Master)
"""

import fitz  # PyMuPDF
import os
import sys
import json
import re
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentFormat(Enum):
    """Supported document formats"""
    ADVANCED_KEY_ENABLING = "Advanced Key & Enabling"
    STANDARD_CANMEDS = "Standard CanMEDS"
    BASIC_ROLE_BASED = "Basic Role-Based"
    LEGACY_DOTTED_TOC = "Legacy Dotted TOC"
    CANMEDS_WITHOUT_LEVELS = "CanMEDS Without Levels"
    UNKNOWN = "Unknown"

@dataclass
class FormatDetectionResult:
    """Result of document format detection"""
    format_type: DocumentFormat
    confidence: float
    indicators: List[str]
    characteristics: Dict[str, Any]

@dataclass
class ExtractionResult:
    """Enhanced extraction result with format information"""
    pdf_path: str
    detected_format: DocumentFormat
    format_confidence: float
    extractor_used: str
    extraction_successful: bool
    quality_score: float
    validation: str
    detailed_analysis: Dict[str, Any]
    content_length: int
    pages_extracted: Optional[str] = None
    output_file: Optional[str] = None
    json_report: Optional[str] = None
    failure_reason: Optional[str] = None

class UnifiedMasterExtractor:
    """Unified master extractor with automatic format detection"""
    
    def __init__(self):
        # Format detection patterns
        self.format_patterns = {
            DocumentFormat.ADVANCED_KEY_ENABLING: [
                r'(?i)key\s+competenc',
                r'(?i)enabling\s+competenc',
                r'(?i)R[1-4]|F[1-2]|PGY[1-4]',
                r'(?i)entrustable\s+professional\s+activities',
                r'(?i)milestones?',
                r'(?i)competency\s+framework'
            ],
            DocumentFormat.STANDARD_CANMEDS: [
                r'(?i)canmeds\s+competenc',
                r'(?i)(?:medical\s+expert|communicator|collaborator|leader|health\s+advocate|scholar|professional)\s*:',
                r'(?i)seven\s+roles',
                r'(?i)competency\s+domains?',
                r'(?i)professional\s+competenc'
            ],
            DocumentFormat.BASIC_ROLE_BASED: [
                r'(?i)role\s+of\s+the',
                r'(?i)as\s+a\s+(?:medical\s+expert|communicator|collaborator)',
                r'(?i)physician\s+roles?',
                r'(?i)professional\s+roles?'
            ],
            DocumentFormat.LEGACY_DOTTED_TOC: [
                r'(?m)^\s*\d+\.\d+\s+[A-Z]',
                r'(?m)^\s*\d+\.\d+\.\d+\s+',
                r'(?i)table\s+of\s+contents?',
                r'(?m)^\s*\d+\.\s+[A-Z][A-Z\s]+$'
            ],
            DocumentFormat.CANMEDS_WITHOUT_LEVELS: [
                r'(?i)(?:medical\s+expert|communicator|collaborator|leader|health\s+advocate|scholar|professional)',
                r'(?i)canmeds(?!\s+competenc)',  # CanMEDS but not "CanMEDS competencies"
                r'(?i)physician\s+competenc'
            ]
        }
        
        # Format-specific indicators
        self.format_indicators = {
            DocumentFormat.ADVANCED_KEY_ENABLING: [
                'key competencies', 'enabling competencies', 'progressive levels',
                'R1-R4 progression', 'F1-F2 fellowship', 'milestones', 'EPAs'
            ],
            DocumentFormat.STANDARD_CANMEDS: [
                'canmeds framework', 'seven roles', 'competency domains',
                'professional competencies', 'role-based structure'
            ],
            DocumentFormat.BASIC_ROLE_BASED: [
                'simple role structure', 'basic competencies', 'role definitions'
            ],
            DocumentFormat.LEGACY_DOTTED_TOC: [
                'numbered sections', 'hierarchical structure', 'table of contents',
                'dotted numbering system'
            ],
            DocumentFormat.CANMEDS_WITHOUT_LEVELS: [
                'basic canmeds', 'no progression levels', 'simple competencies'
            ]
        }
        
        # Specialized extractors mapping
        self.extractors = {}
        self.extractor_paths = {
            DocumentFormat.ADVANCED_KEY_ENABLING: 'final_perfected_advanced_key_enabling_extractor.py',
            DocumentFormat.STANDARD_CANMEDS: 'final_perfected_canmeds_extractor.py',
            DocumentFormat.BASIC_ROLE_BASED: 'extract_basic_role_based_improved.py',
            DocumentFormat.LEGACY_DOTTED_TOC: 'extract_legacy_dotted_toc_improved.py',
            DocumentFormat.CANMEDS_WITHOUT_LEVELS: 'extract_canmeds_without_levels_improved.py'
        }
        
        # Performance tracking
        self.format_detection_history = []
        self.extraction_performance = {}
        
    def detect_document_format(self, pdf_path: str) -> FormatDetectionResult:
        """Detect the format of a PDF document"""
        try:
            doc = fitz.open(pdf_path)
            
            # Extract sample content for analysis
            sample_content = ""
            sample_pages = min(10, len(doc))  # First 10 pages
            
            for page_num in range(sample_pages):
                page = doc[page_num]
                sample_content += page.get_text() + "\n"
            
            doc.close()
            
            # Analyze content for format indicators
            format_scores = {}
            detected_indicators = {}
            
            for format_type, patterns in self.format_patterns.items():
                score = 0
                indicators = []
                
                for pattern in patterns:
                    matches = re.findall(pattern, sample_content, re.MULTILINE)
                    if matches:
                        score += len(matches) * 10  # Weight by frequency
                        indicators.append(f"Pattern: {pattern[:50]}... ({len(matches)} matches)")
                
                # Additional scoring based on format-specific characteristics
                characteristics = self._analyze_format_characteristics(sample_content, format_type)
                score += characteristics.get('bonus_score', 0)
                
                format_scores[format_type] = score
                detected_indicators[format_type] = indicators + characteristics.get('indicators', [])
            
            # Determine best format match
            if not format_scores or max(format_scores.values()) == 0:
                return FormatDetectionResult(
                    format_type=DocumentFormat.UNKNOWN,
                    confidence=0.0,
                    indicators=[],
                    characteristics={}
                )
            
            best_format = max(format_scores, key=format_scores.get)
            max_score = format_scores[best_format]
            
            # Calculate confidence (0-1)
            total_score = sum(format_scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.0
            
            # Additional confidence boost for strong matches
            if max_score > 50:
                confidence = min(1.0, confidence * 1.2)
            
            return FormatDetectionResult(
                format_type=best_format,
                confidence=confidence,
                indicators=detected_indicators[best_format],
                characteristics=self._analyze_format_characteristics(sample_content, best_format)
            )
            
        except Exception as e:
            logger.error(f"Format detection failed for {pdf_path}: {str(e)}")
            return FormatDetectionResult(
                format_type=DocumentFormat.UNKNOWN,
                confidence=0.0,
                indicators=[],
                characteristics={'error': str(e)}
            )
    
    def _analyze_format_characteristics(self, content: str, format_type: DocumentFormat) -> Dict[str, Any]:
        """Analyze format-specific characteristics"""
        characteristics = {'bonus_score': 0, 'indicators': []}
        content_lower = content.lower()
        
        if format_type == DocumentFormat.ADVANCED_KEY_ENABLING:
            # Look for progressive level indicators
            levels = len(re.findall(r'(?i)(?:R[1-4]|F[1-2]|PGY[1-4])', content))
            if levels > 5:
                characteristics['bonus_score'] += 20
                characteristics['indicators'].append(f'Multiple level indicators ({levels} found)')
            
            # Look for key/enabling competency structure
            key_enabling = len(re.findall(r'(?i)(?:key|enabling)\s+competenc', content))
            if key_enabling > 3:
                characteristics['bonus_score'] += 15
                characteristics['indicators'].append(f'Key/Enabling structure ({key_enabling} instances)')
        
        elif format_type == DocumentFormat.STANDARD_CANMEDS:
            # Look for CanMEDS framework references
            canmeds_refs = len(re.findall(r'(?i)canmeds', content))
            if canmeds_refs > 3:
                characteristics['bonus_score'] += 20
                characteristics['indicators'].append(f'CanMEDS references ({canmeds_refs} found)')
            
            # Check for seven roles structure
            if 'seven roles' in content_lower or '7 roles' in content_lower:
                characteristics['bonus_score'] += 15
                characteristics['indicators'].append('Seven roles structure detected')
        
        elif format_type == DocumentFormat.LEGACY_DOTTED_TOC:
            # Look for hierarchical numbering
            numbered_sections = len(re.findall(r'(?m)^\s*\d+\.\d+', content))
            if numbered_sections > 10:
                characteristics['bonus_score'] += 25
                characteristics['indicators'].append(f'Hierarchical numbering ({numbered_sections} sections)')
        
        return characteristics
    
    def extract_from_pdf(self, pdf_path: str, output_dir: str) -> ExtractionResult:
        """Extract competencies using unified approach"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Step 1: Detect document format
            format_result = self.detect_document_format(pdf_path)
            logger.info(f"Detected format: {format_result.format_type.value} (confidence: {format_result.confidence:.2f})")
            
            # Step 2: Select appropriate extractor
            if format_result.format_type == DocumentFormat.UNKNOWN or format_result.confidence < 0.3:
                logger.warning(f"Low confidence format detection, using fallback strategy")
                return self._fallback_extraction(pdf_path, output_dir, format_result)
            
            # Step 3: Load and use specialized extractor
            extractor = self._get_specialized_extractor(format_result.format_type)
            if not extractor:
                logger.warning(f"No specialized extractor available for {format_result.format_type.value}")
                return self._fallback_extraction(pdf_path, output_dir, format_result)
            
            # Step 4: Perform extraction using appropriate method
            if hasattr(extractor, 'extract_competencies'):
                extraction_report = extractor.extract_competencies(pdf_path, output_dir)
            elif hasattr(extractor, 'extract_from_pdf'):
                extraction_report = extractor.extract_from_pdf(pdf_path, output_dir)
            else:
                logger.error(f"Extractor for {format_result.format_type.value} has no valid extraction method")
                return self._fallback_extraction(pdf_path, output_dir, format_result)
            
            # Step 5: Create unified result
            result = ExtractionResult(
                pdf_path=pdf_path,
                detected_format=format_result.format_type,
                format_confidence=format_result.confidence,
                extractor_used=format_result.format_type.value,
                extraction_successful=extraction_report.get('extraction_successful', False),
                quality_score=extraction_report.get('quality_score', 0),
                validation=extraction_report.get('validation', 'Unknown'),
                detailed_analysis=extraction_report.get('detailed_analysis', {}),
                content_length=extraction_report.get('content_length', 0),
                pages_extracted=extraction_report.get('pages_extracted'),
                output_file=extraction_report.get('output_file'),
                json_report=extraction_report.get('json_report'),
                failure_reason=extraction_report.get('failure_reason')
            )
            
            # Step 6: Update performance tracking
            self._update_performance_tracking(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Unified extraction failed for {pdf_path}: {str(e)}")
            return ExtractionResult(
                pdf_path=pdf_path,
                detected_format=DocumentFormat.UNKNOWN,
                format_confidence=0.0,
                extractor_used="ERROR",
                extraction_successful=False,
                quality_score=0,
                validation=f"Extraction error: {str(e)}",
                detailed_analysis={},
                content_length=0,
                failure_reason=str(e)
            )
    
    def _get_specialized_extractor(self, format_type: DocumentFormat):
        """Get or load specialized extractor for format"""
        if format_type in self.extractors:
            return self.extractors[format_type]
        
        extractor_path = self.extractor_paths.get(format_type)
        if not extractor_path or not os.path.exists(extractor_path):
            return None
        
        try:
            # Dynamically load extractor module
            spec = importlib.util.spec_from_file_location("extractor", extractor_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get extractor class (assuming consistent naming patterns)
            extractor_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if isinstance(obj, type) and 'Extractor' in name and name != 'BaseExtractor':
                    extractor_class = obj
                    break
            
            if extractor_class:
                self.extractors[format_type] = extractor_class()
                return self.extractors[format_type]
            
        except Exception as e:
            logger.error(f"Failed to load extractor for {format_type.value}: {str(e)}")
        
        return None
    
    def _fallback_extraction(self, pdf_path: str, output_dir: str, format_result: FormatDetectionResult) -> ExtractionResult:
        """Fallback extraction when format detection fails or extractor unavailable"""
        logger.info(f"Using fallback extraction for {pdf_path}")
        
        try:
            # Use general-purpose extraction strategy
            doc = fitz.open(pdf_path)
            
            # Extract content from likely competency sections
            content = ""
            for page_num in range(min(50, len(doc))):  # First 50 pages
                page = doc[page_num]
                page_text = page.get_text()
                
                # Look for competency-related content
                if any(term in page_text.lower() for term in 
                      ['competenc', 'canmeds', 'objective', 'skill', 'role', 'professional']):
                    content += page_text + "\n"
            
            doc.close()
            
            if len(content) < 500:
                return ExtractionResult(
                    pdf_path=pdf_path,
                    detected_format=format_result.format_type,
                    format_confidence=format_result.confidence,
                    extractor_used="FALLBACK",
                    extraction_successful=False,
                    quality_score=0,
                    validation="Fallback extraction failed: Insufficient content",
                    detailed_analysis={},
                    content_length=len(content),
                    failure_reason="Insufficient competency content found"
                )
            
            # Save extracted content
            filename = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = os.path.join(output_dir, f"{filename}_competencies.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ExtractionResult(
                pdf_path=pdf_path,
                detected_format=format_result.format_type,
                format_confidence=format_result.confidence,
                extractor_used="FALLBACK",
                extraction_successful=True,
                quality_score=50,  # Basic fallback score
                validation="Fallback extraction completed",
                detailed_analysis={'fallback_used': True, 'content_extracted': True},
                content_length=len(content),
                output_file=output_file
            )
            
        except Exception as e:
            logger.error(f"Fallback extraction failed: {str(e)}")
            return ExtractionResult(
                pdf_path=pdf_path,
                detected_format=format_result.format_type,
                format_confidence=format_result.confidence,
                extractor_used="FALLBACK_ERROR",
                extraction_successful=False,
                quality_score=0,
                validation=f"Fallback extraction error: {str(e)}",
                detailed_analysis={},
                content_length=0,
                failure_reason=str(e)
            )
    
    def _update_performance_tracking(self, result: ExtractionResult):
        """Update performance tracking for continuous improvement"""
        format_type = result.detected_format
        
        if format_type not in self.extraction_performance:
            self.extraction_performance[format_type] = {
                'total_attempts': 0,
                'successful_extractions': 0,
                'average_quality': 0.0,
                'format_detection_accuracy': []
            }
        
        stats = self.extraction_performance[format_type]
        stats['total_attempts'] += 1
        
        if result.extraction_successful:
            stats['successful_extractions'] += 1
            # Update rolling average quality score
            n = stats['successful_extractions']
            stats['average_quality'] = ((stats['average_quality'] * (n-1)) + result.quality_score) / n
        
        stats['format_detection_accuracy'].append(result.format_confidence)
        
        # Keep only recent accuracy scores (last 100)
        if len(stats['format_detection_accuracy']) > 100:
            stats['format_detection_accuracy'] = stats['format_detection_accuracy'][-100:]

def main():
    """Main execution function"""
    if len(sys.argv) < 3:
        print("Usage: python unified_master_extractor.py <pdf_path_or_directory> <output_directory>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    os.makedirs(output_dir, exist_ok=True)
    
    extractor = UnifiedMasterExtractor()
    results = []
    
    if os.path.isfile(input_path) and input_path.endswith('.pdf'):
        result = extractor.extract_from_pdf(input_path, output_dir)
        results.append(result)
    elif os.path.isdir(input_path):
        pdf_files = [f for f in os.listdir(input_path) if f.endswith('.pdf')]
        
        print(f"Processing {len(pdf_files)} PDF files with Unified Master Extractor...")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(input_path, pdf_file)
            result = extractor.extract_from_pdf(pdf_path, output_dir)
            results.append(result)
            
            if result.extraction_successful:
                print(f"✓ Extracted: {pdf_file} [{result.detected_format.value}]")
            else:
                print(f"✗ Failed: {pdf_file} [{result.detected_format.value}] - {result.failure_reason}")
    
    # Generate comprehensive summary
    successful = [r for r in results if r.extraction_successful]
    
    # Group by detected format
    format_breakdown = {}
    for result in results:
        format_name = result.detected_format.value
        if format_name not in format_breakdown:
            format_breakdown[format_name] = {'total': 0, 'successful': 0, 'avg_confidence': 0}
        
        format_breakdown[format_name]['total'] += 1
        format_breakdown[format_name]['avg_confidence'] += result.format_confidence
        
        if result.extraction_successful:
            format_breakdown[format_name]['successful'] += 1
    
    # Calculate averages
    for format_name in format_breakdown:
        stats = format_breakdown[format_name]
        stats['avg_confidence'] = stats['avg_confidence'] / stats['total']
        stats['success_rate'] = (stats['successful'] / stats['total']) * 100
    
    # Convert performance tracking enum keys to strings for JSON serialization
    performance_tracking_serializable = {}
    for format_type, stats in extractor.extraction_performance.items():
        performance_tracking_serializable[format_type.value] = stats
    
    summary = {
        'category': 'Unified Master Extractor',
        'total_documents': len(results),
        'successful_extractions': len(successful),
        'extraction_rate': f"{len(successful)/len(results)*100:.1f}%",
        'format_breakdown': format_breakdown,
        'performance_tracking': performance_tracking_serializable,
        'results': [
            {
                'pdf_path': r.pdf_path,
                'detected_format': r.detected_format.value,
                'format_confidence': f"{r.format_confidence:.2f}",
                'extractor_used': r.extractor_used,
                'extraction_successful': r.extraction_successful,
                'quality_score': r.quality_score,
                'validation': r.validation,
                'content_length': r.content_length,
                'output_file': r.output_file,
                'failure_reason': r.failure_reason
            } for r in results
        ]
    }
    
    summary_file = os.path.join(output_dir, 'unified_extraction_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== Unified Master Extraction Summary ===")
    print(f"Total documents: {len(results)}")
    print(f"Successful extractions: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    
    print(f"\n=== Format Detection Breakdown ===")
    for format_name, stats in format_breakdown.items():
        print(f"{format_name}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.1f}%) - Avg Confidence: {stats['avg_confidence']:.2f}")
    
    print(f"\nSummary saved: {summary_file}")

if __name__ == "__main__":
    main()
