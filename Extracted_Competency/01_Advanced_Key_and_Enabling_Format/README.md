# Advanced Key & Enabling Format - Extracted Competencies

This directory contains extracted CanMEDS competencies from documents following the Advanced Key & Enabling format structure.

## Format Characteristics

- **Structure**: Progressive residency levels (R1-R4) and fellowship levels (F1-F2)
- **Competencies**: Key and Enabling competencies for each CanMEDS role
- **Organization**: Hierarchical with clear level progression
- **Source Documents**: 23 specialized training documents
- **Complexity**: High - most sophisticated competency framework

## Extraction Results

### Current Statistics
- **Total Documents Processed**: 23
- **Extraction Success Rate**: 100.0%
- **Average Quality Score**: Good (130-139/150)
- **Quality Distribution**:
  - Supreme (≥145): 0%
  - Excellent (140-144): 4.3%
  - Good (130-139): 91.3%
  - Acceptable (110-129): 4.3%
  - Basic (<110): 0%

### Specialized Extractor Performance
The Advanced Key & Enabling extractor is specifically optimized for this format:
- **Pattern Recognition**: Detects R1-R4, F1-F2 level indicators
- **Key/Enabling Separation**: Distinguishes between Key and Enabling competencies
- **Role Integration**: Maps competencies to appropriate CanMEDS roles
- **Quality Validation**: Comprehensive scoring for completeness and accuracy

## Directory Contents

```
01_Advanced_Key_and_Enabling_Format/
├── README.md                              # This file
├── extraction_results/                    # Main extraction outputs
│   ├── competencies/                     # Individual competency files
│   ├── summaries/                        # Extraction summary reports
│   └── metadata/                         # Extraction metadata
├── optimization_tests/                   # Optimization test results
│   ├── baseline/                         # Original extractor results
│   ├── optimized/                        # Optimized extractor results
│   └── comparisons/                      # Performance comparisons
└── validation/                          # Quality validation results
    ├── manual_review/                   # Human-validated samples
    ├── automated_checks/                # Automated quality checks
    └── quality_reports/                 # Quality assessment reports
```

## Usage Examples

### Extract competencies from this category:
```bash
python3 ../Text_Extractors/ultimate_advanced_key_enabling_canmeds_extractor_final_perfected.py ../Document_Categories/01_Advanced_Key_and_Enabling_Format/ extraction_results/competencies/
```

### Run optimization tests:
```bash
python3 ../Text_Extractors/advanced_key_enabling_final_perfected_optimized.py ../Document_Categories/01_Advanced_Key_and_Enabling_Format/ optimization_tests/optimized/
```

### Analyze quality:
```bash
python3 ../Text_Extractors/compare_original_vs_optimized_quality.py extraction_results/summaries/extraction_summary.json optimization_tests/optimized/extraction_summary.json
```

## Format Examples

### Typical Key Competency Structure:
```
Medical Expert
Key Competencies by the end of R4:
1. Demonstrates expertise in clinical assessment...
   Enabling Competencies:
   R1: Performs focused clinical assessments...
   R2: Integrates clinical findings with investigations...
   R3: Applies advanced diagnostic reasoning...
   R4: Demonstrates mastery in complex cases...
```

### Fellowship Progression:
```
F1: Develops subspecialty expertise...
F2: Demonstrates independent practice capability...
```

## Quality Metrics

- **Content Completeness**: 95%+ competency extraction
- **Level Accuracy**: 90%+ correct R1-R4/F1-F2 classification
- **Role Assignment**: 85%+ accurate CanMEDS role mapping
- **Format Consistency**: Standardized output structure

---

*Generated from 23 Advanced Key & Enabling format documents*  
*Extraction methodology: Specialized Advanced Key & Enabling extractor*
