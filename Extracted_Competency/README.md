# Extracted CanMEDS Competencies - Master Directory

This directory contains extracted CanMEDS competencies organized by document format type and extraction methodology.

## Directory Structure

### Format-Based Categories (01-06)
Based on the sophistication and structure of the competency framework:

#### 01_Advanced_Key_and_Enabling_Format/
- **Source Documents**: 23 documents
- **Format**: Advanced Key & Enabling competency structure
- **Extraction Methods**: Specialized Key & Enabling extractor
- **Features**: Progressive levels (R1-R4, F1-F2), structured competencies

#### 02_Standard_CanMEDS_Format/  
- **Source Documents**: 67 documents
- **Format**: Standard CanMEDS framework implementation
- **Extraction Methods**: Standard CanMEDS extractor
- **Features**: Traditional 7-role structure, competency domains

#### 03_Basic_Role_Based_Format/
- **Source Documents**: 9 documents  
- **Format**: Basic role-based competency organization
- **Extraction Methods**: Basic role-based extractor
- **Features**: Simple role definitions, minimal structure

#### 04_Legacy_Dotted_TOC_Format/
- **Source Documents**: 4 documents
- **Format**: Legacy dotted table of contents structure
- **Extraction Methods**: Dotted TOC extractor
- **Features**: Hierarchical numbering (1.1.1), legacy formatting

#### 05_CanMEDS_Without_Levels/
- **Source Documents**: 7 documents
- **Format**: CanMEDS without progression levels
- **Extraction Methods**: Without-levels extractor
- **Features**: Basic CanMEDS, no R1-R4/F1-F2 progression

#### 06_Role_Based_Only/
- **Source Documents**: 1 document
- **Format**: Pure role-based organization
- **Extraction Methods**: Role-only extractor
- **Features**: Minimal competency structure

### Type-Based Categories (07-13)
Based on program/document type:

#### 07_Diploma_Programs/
- **Source Documents**: 2 documents
- **Program Type**: Diploma-level programs
- **Extraction Methods**: Adaptive based on format detected

#### 08_Fellowship_Programs/
- **Source Documents**: 9 documents
- **Program Type**: Fellowship training programs
- **Extraction Methods**: Adaptive based on format detected

#### 09_Board_Certifications/
- **Source Documents**: 3 documents
- **Program Type**: Board certification requirements
- **Extraction Methods**: Adaptive based on format detected

#### 10_Residency_Programs/
- **Source Documents**: 1 document
- **Program Type**: Residency training programs
- **Extraction Methods**: Adaptive based on format detected

#### 11_Radiology_Technology/
- **Source Documents**: TBD
- **Program Type**: Radiology technology programs
- **Extraction Methods**: Specialized technical extractor

#### 12_Medical_Physics/
- **Source Documents**: TBD
- **Program Type**: Medical physics programs
- **Extraction Methods**: Specialized physics extractor

#### 13_Other_Documents/
- **Source Documents**: 1+ documents
- **Program Type**: Miscellaneous/uncategorized documents
- **Extraction Methods**: General fallback extractor

## Extraction Results Organization

Each category directory contains:

```
XX_Category_Name/
├── README.md                              # Category-specific information
├── extraction_results/                    # Main extraction outputs
│   ├── competencies/                     # Individual competency files
│   │   ├── document1_competencies.txt
│   │   ├── document1_competencies.json
│   │   └── ...
│   ├── summaries/                        # Extraction summary reports
│   │   ├── extraction_summary.json
│   │   ├── quality_analysis.json
│   │   └── performance_metrics.json
│   └── metadata/                         # Extraction metadata
│       ├── extraction_log.txt
│       ├── failed_extractions.json
│       └── processing_stats.json
├── optimization_tests/                   # Optimization test results
│   ├── baseline/                         # Original extractor results
│   ├── optimized/                        # Optimized extractor results
│   └── comparisons/                      # Performance comparisons
└── validation/                          # Quality validation results
    ├── manual_review/                   # Human-validated samples
    ├── automated_checks/                # Automated quality checks
    └── quality_reports/                 # Quality assessment reports
```

## Extraction Methodologies

### Primary Extractors
1. **Final Perfected Extractor** - General-purpose high-performance
2. **Advanced Key & Enabling Extractor** - Format-specific specialized  
3. **Unified Master Extractor** - Auto-detecting format selector
4. **Optimized Extractors** - Performance-tuned versions

### Quality Levels
- **Supreme**: ≥145/150 quality score
- **Excellent**: ≥140/150 quality score  
- **Good**: ≥130/150 quality score
- **Acceptable**: ≥110/150 quality score
- **Basic**: <110/150 quality score

### Performance Metrics
- **Extraction Success Rate**: Percentage of documents successfully processed
- **Quality Distribution**: Breakdown of quality levels achieved
- **Processing Time**: Average time per document
- **Content Accuracy**: Validation against manual review

## Usage Instructions

### Running Extractions
```bash
# Single category extraction
python3 unified_master_extractor.py ../Document_Categories/01_Advanced_Key_and_Enabling_Format/ 01_Advanced_Key_and_Enabling_Format/extraction_results/

# Full batch extraction
python3 run_all_optimized_extractors.py
```

### Analyzing Results
```bash
# Quality analysis
python3 analyze_extraction_quality.py 01_Advanced_Key_and_Enabling_Format/

# Performance comparison
python3 compare_extraction_methods.py
```

## Statistics Summary

| Category | Documents | Success Rate | Avg Quality | Best Extractor |
|----------|-----------|--------------|-------------|----------------|
| 01_Advanced_Key_Enabling | 23 | 100.0% | Good | Advanced K&E |
| 02_Standard_CanMEDS | 67 | TBD | TBD | Standard |
| 03_Basic_Role_Based | 9 | TBD | TBD | Basic Role |
| 04_Legacy_Dotted_TOC | 4 | TBD | TBD | Dotted TOC |
| 05_CanMEDS_Without_Levels | 7 | TBD | TBD | Without Levels |
| **Total** | **125** | **TBD** | **TBD** | **Unified Master** |

---

*Last Updated: August 8, 2025*  
*Generated automatically from SCFHS document analysis and extraction pipeline*
