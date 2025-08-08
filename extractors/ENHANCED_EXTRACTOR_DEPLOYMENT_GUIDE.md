# Enhanced CanMEDS Extractor Deployment Guide

## Overview

This guide covers the deployment and testing of the enhanced CanMEDS competency extractor that addresses significant quality issues identified in the original system.

## Key Improvements Made

### 1. Content Type Classification
- **Problem Solved**: Original system extracted wrong content types (references, program structure) thinking they were competencies
- **Solution**: New `ContentTypeClassifier` that distinguishes between competency frameworks, references, program structure, assessments, and appendices
- **Impact**: Prevents extraction of non-competency content like Document 81 (Periodontics) which only extracted references

### 2. Template Recognition  
- **Problem Solved**: No awareness of SCFHS document patterns and templates
- **Solution**: `SCFHSTemplateRecognizer` that identifies document templates and uses template-specific extraction patterns
- **Impact**: Better extraction accuracy based on document structure understanding

### 3. Multi-Stage Validation Pipeline
- **Problem Solved**: Weak validation that only checked for CanMEDS role presence, not content appropriateness
- **Solution**: Comprehensive validation with content type analysis, contamination detection, and quality scoring
- **Impact**: Better detection of failed extractions and quality assessment

### 4. Enhanced Confidence Scoring
- **Problem Solved**: Scoring based only on keyword presence, not content quality
- **Solution**: Multi-factor scoring including content type, contamination penalties, and structural analysis
- **Impact**: More accurate assessment of extraction quality and success

### 5. Better Section Boundary Detection
- **Problem Solved**: Incorrect page range detection leading to extraction of wrong sections
- **Solution**: Content analysis to validate TOC entries and section boundaries before extraction
- **Impact**: More accurate competency section identification

## Files Created

### Core Enhanced Extractor
- `extract_standard_canmeds_enhanced.py` - Main enhanced extractor with all improvements
- `test_enhanced_extractor.py` - Test script for validation on problematic documents

### Key Classes Added
- `ContentTypeClassifier` - Classifies document sections by content type
- `SCFHSTemplateRecognizer` - Recognizes SCFHS document templates
- `EnhancedStandardCanMEDSExtractor` - Main extractor with enhanced pipeline

## Deployment Steps

### Step 1: Backup Current System
```bash
# Create backup of current extractor
cp extract_standard_canmeds_improved.py extract_standard_canmeds_improved_backup.py
```

### Step 2: Install Enhanced Extractor
```bash
# The enhanced extractor is ready to use
chmod +x extract_standard_canmeds_enhanced.py
chmod +x test_enhanced_extractor.py
```

### Step 3: Test on Problematic Documents
```bash
# Run test suite on known problematic documents
python test_enhanced_extractor.py
```

### Step 4: Review Test Results
- Check outputs in `../Extracted_Competencies/02_Standard_CanMEDS_Format_ENHANCED_TEST/`
- Compare with original extractions
- Look for:
  - Lower contamination scores (< 30)
  - Higher CanMEDS role counts (≥ 3) 
  - More appropriate content extraction
  - Better rejection of non-competency sections

### Step 5: Run Full Enhanced Extraction (Optional)
```bash
# Run enhanced extractor on full Standard CanMEDS dataset
python extract_standard_canmeds_enhanced.py \
  --input-dir "../Document_Categories/02_Standard_CanMEDS_Format" \
  --output-dir "../Extracted_Competencies/02_Standard_CanMEDS_Format_ENHANCED"
```

## Expected Improvements

### Quality Metrics
- **Contamination Reduction**: Documents should have contamination scores < 30
- **Role Coverage**: Documents should identify ≥ 3 CanMEDS roles (vs previous threshold of any roles)
- **Content Appropriateness**: System should reject extraction of non-competency sections
- **Template Awareness**: Better extraction based on document structure understanding

### Specific Document Improvements
- **Document 81 (Periodontics Board)**: Should reject extraction of references section or find actual competencies
- **Document 24 (Diagnostic Neuroradiology)**: Should reject program structure section or find competency content
- **Document 69 (Cardiac Surgery Board)**: Should extract only competency framework, not program structure

## Validation Checklist

### ✅ Content Quality Validation
- [ ] Extracted content contains CanMEDS roles, not references
- [ ] Extracted content contains competency statements, not program logistics
- [ ] Contamination scores are reasonable (< 30)
- [ ] Role coverage is adequate (≥ 3 roles for acceptance)

### ✅ Extraction Accuracy Validation  
- [ ] Page ranges are appropriate and contain competency content
- [ ] Section boundaries are correctly identified
- [ ] Non-competency sections are properly excluded
- [ ] Template recognition works for document categorization

### ✅ System Performance Validation
- [ ] Processing time is reasonable
- [ ] Error handling works properly
- [ ] Output files are properly formatted
- [ ] JSON reports contain detailed analysis

## Integration Options

### Option 1: Replace Current Extractor
Replace `extract_standard_canmeds_improved.py` with the enhanced version after validation.

### Option 2: Update Master Runner
Create new master runner script that uses enhanced extractor:
```python
# Update extractors list in run_all_improved_extractors_fixed.py
{
    'script': 'extract_standard_canmeds_enhanced.py',
    'description': 'Enhanced Standard CanMEDS (multi-stage validation)',
    'category': '02_Standard_CanMEDS_Enhanced',
    # ... other config
}
```

### Option 3: A/B Testing
Run both extractors in parallel and compare results before full deployment.

## Monitoring and Maintenance

### Key Metrics to Monitor
- **Extraction Success Rate**: Should improve from ~77% to 85%+
- **Excellent Extraction Rate**: New metric tracking high-quality extractions
- **Contamination Score Distribution**: Most extractions should have low contamination
- **Template Recognition Accuracy**: Monitor how well document templates are identified

### Regular Validation
- Periodically test on sample documents
- Review extraction quality metrics
- Update template patterns as new document formats are identified
- Adjust validation thresholds based on performance analysis

## Troubleshooting

### Common Issues
1. **High Contamination Scores**: Review content type classification patterns
2. **Low Role Coverage**: Check CanMEDS role detection patterns and synonyms
3. **Template Misclassification**: Update template recognition patterns
4. **Performance Issues**: Optimize content classification if processing is slow

### Debug Mode
The enhanced extractor provides detailed logging:
- Document template identification
- Section candidate analysis  
- Content type classification scores
- Validation step-by-step analysis

## Next Steps

1. **Test the enhanced extractor** on the problematic documents
2. **Review and validate** the improvements
3. **Deploy gradually** - start with Standard CanMEDS format
4. **Monitor performance** and adjust thresholds if needed
5. **Consider applying similar enhancements** to other extractors (Advanced Key & Enabling, Basic Role-Based, etc.)

## Expected Outcomes

The enhanced extractor should significantly improve the quality of competency extraction by:
- Reducing false positive extractions (wrong content types)
- Improving content appropriateness and relevance
- Providing better validation and quality assessment
- Offering more detailed analysis and reporting

This addresses the core issues identified in the collaborative reasoning analysis and should result in more reliable and useful competency extractions for the SCFHS curriculum analysis.
