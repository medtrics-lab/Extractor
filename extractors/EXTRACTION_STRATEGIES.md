# SCFHS Competency Section Extractors
## Category-Specific Extraction Strategies

This document describes the specialized extraction scripts created for each SCFHS document category, explaining the unique strategies and reasoning behind each approach.

---

## 📊 **Overview of Extraction Challenges**

Each document category presents unique formatting patterns that require tailored extraction strategies:

| Category | Documents | Primary Challenge | Extraction Strategy |
|----------|-----------|-------------------|-------------------|
| Advanced Key & Enabling | 21 | Most sophisticated structure | Content Pattern Analysis |
| Standard CanMEDS | 67 | Most common, variable structure | Document Structure + TOC |
| Basic Role-Based | 9 | No CanMEDS framework | Role Pattern Detection |
| Legacy Dotted TOC | 4 | Dotted table of contents | TOC Parsing + Page Range |
| CanMEDS Without Levels | 7 | No progression levels | CanMEDS Role Detection |

---

## 🎯 **Category 1: Advanced Key & Enabling Format (21 docs)**

### **Script**: `extract_advanced_key_enabling.py`
### **Strategy**: Content Pattern Analysis + Key Phrase Detection

#### **Reasoning**
These documents have the most structured and sophisticated competency framework with clear "Key Competencies" and "Enabling Competencies" markers, making pattern-based extraction most reliable.

#### **Key Features**
- **Pattern Indicators**: "KEY COMPETENCIES", "ENABLING COMPETENCIES" 
- **Validation**: CanMEDS roles + Key & Enabling structure + Progressive levels
- **Boundary Detection**: Look for "CONTINUUM OF LEARNING" as end marker
- **Content Validation**: Requires ≥2 indicators (Key/Enabling + CanMEDS + Levels)

#### **Example Documents**
- Vascular Neurology (Stroke)
- Internal Medicine Board  
- Rheumatology Fellowship

#### **Extraction Process**
1. Search for key indicators: "LEARNING AND COMPETENCIES", "KEY COMPETENCIES"
2. Validate by finding CanMEDS roles within section
3. Extract from header to next major section
4. Validate for advanced format characteristics

---

## 🎯 **Category 2: Standard CanMEDS Format (67 docs)**

### **Script**: `extract_standard_canmeds.py`  
### **Strategy**: Document Structure Analysis + TOC Parsing

#### **Reasoning**
This is the most common format with consistent section numbering and TOC structure. Focus on Roman numeral sections and CanMEDS role detection for reliable extraction.

#### **Key Features**
- **TOC Parsing**: Extract page numbers from table of contents first
- **Structure Analysis**: Roman numeral section identification
- **CanMEDS Validation**: Requires ≥4 of 7 CanMEDS roles present
- **Dual Approach**: TOC parsing with structure analysis fallback

#### **Example Documents**
- Ophthalmology Board
- Pediatrics Board
- General Surgery Board

#### **Extraction Process**
1. Parse TOC for "LEARNING AND COMPETENCIES" page numbers
2. If TOC fails, use structure analysis to find CanMEDS role density
3. Validate with minimum 4 CanMEDS roles
4. Extract from competency header to next section marker

---

## 🎯 **Category 3: Basic Role-Based Format (9 docs)**

### **Script**: `extract_basic_role_based.py`
### **Strategy**: Role Pattern Detection + Competency Matrix Analysis  

#### **Reasoning**
These documents use role-based structure without CanMEDS terminology. Focus on finding clinical competencies, professional roles, and competency matrices.

#### **Key Features**
- **Role Indicators**: "CLINICAL PRACTICE", "PROFESSIONAL DEVELOPMENT", "PATIENT CARE"
- **Matrix Detection**: Look for "COMPETENCY MATRIX", tabular structures
- **Multiple Sections**: May need to combine multiple competency sections
- **Validation**: Requires ≥2 role indicators + competency header

#### **Example Documents**
- Emergency Medicine Board
- Nursing Diplomas
- Emergency Nursing Diploma

#### **Extraction Process**
1. Search for competency section headers
2. Calculate role indicator density in surrounding pages
3. Find competency matrices with tabular structures  
4. Combine multiple competency sections if found
5. Validate with role indicators and section headers

---

## 🎯 **Category 4: Legacy Dotted TOC Format (4 docs)**

### **Script**: `extract_legacy_dotted_toc.py`
### **Strategy**: Dotted TOC Parsing + Page Range Extraction

#### **Reasoning**
These documents have unique dotted TOC format that requires special parsing. Extract page numbers from dotted lines, then navigate to competency sections.

#### **Key Features**
- **Dotted Pattern Parsing**: Regex patterns for `COMPETENC...........45` format
- **Page Range Validation**: Verify extracted pages contain CanMEDS content
- **Legacy Indicators**: Look for "ROTATION", "OBJECTIVES", "TRAINING"
- **Dual Validation**: Both page range and content validation required

#### **Example Documents**
- Neurology Board
- Anesthesia Board
- Diagnostic Radiology Board

#### **Extraction Process**
1. Parse dotted TOC lines with regex patterns
2. Extract page numbers for competency-related entries
3. Determine page range from TOC entries
4. Validate that pages contain CanMEDS content (≥30% of pages)
5. Extract full page range and validate content

---

## 🎯 **Category 5: CanMEDS Without Levels (7 docs)**

### **Script**: `extract_canmeds_without_levels.py`
### **Strategy**: CanMEDS Role Detection + Simplified Validation

#### **Reasoning**
These documents have CanMEDS framework but no progressive competency levels (R1-R4, F1-F2). Focus on finding CanMEDS roles with simpler competency structure.

#### **Key Features**
- **CanMEDS Focus**: Primary detection based on CanMEDS roles density
- **Simplified Validation**: No level requirements, just role presence
- **Section Headers**: "OUTCOMES AND COMPETENCIES", "COMPETENCIES AND OUTCOMES"
- **Validation**: Requires ≥4 of 7 CanMEDS roles

#### **Example Documents**
- Communication and Swallowing Disorders
- Occupational Therapy Diploma
- Family Dental Medicine Diploma

#### **Extraction Process**
1. Find pages with high CanMEDS role density (≥3 roles)
2. Check for competency section headers as confirmation
3. Extract from start of CanMEDS content to learning opportunities
4. Validate with minimum 4 CanMEDS roles present

---

## 🚀 **Running the Extractors**

### **Individual Extraction**
```bash
# Run specific category extractor
python3 extract_advanced_key_enabling.py
python3 extract_standard_canmeds.py
python3 extract_basic_role_based.py
python3 extract_legacy_dotted_toc.py
python3 extract_canmeds_without_levels.py
```

### **All Categories at Once**
```bash
# Run master script to execute all extractors
python3 run_all_extractors.py
```

---

## 📁 **Output Structure**

Each extractor creates:
```
extracted_competencies/
├── 01_Advanced_Key_and_Enabling/
│   ├── document1_competencies.txt
│   ├── document2_competencies.txt
│   └── extraction_summary.json
├── 02_Standard_CanMEDS/
│   ├── document1_competencies.txt
│   └── extraction_summary.json
└── master_extraction_summary.json
```

---

## 🔍 **Validation Criteria by Category**

### **Advanced Key & Enabling**
- ✅ Key Competencies present
- ✅ Enabling Competencies present  
- ✅ CanMEDS roles present
- ✅ Progressive levels (R1-R4, F1-F2)
- **Threshold**: ≥2/4 indicators

### **Standard CanMEDS** 
- ✅ CanMEDS roles (≥4/7 roles)
- ✅ Competency section header
- ✅ Learning objectives
- **Threshold**: ≥4 CanMEDS roles

### **Basic Role-Based**
- ✅ Role indicators (≥2 indicators)
- ✅ Competency section header
- ✅ Matrix elements (optional)
- **Threshold**: ≥2 role indicators + header

### **Legacy Dotted TOC**
- ✅ CanMEDS roles (≥3/7 roles)
- ✅ Competency terms present
- ✅ Legacy format indicators
- **Threshold**: ≥3 CanMEDS roles + competency terms

### **CanMEDS Without Levels**
- ✅ CanMEDS roles (≥4/7 roles)
- ✅ Competency section header
- ✅ No level requirements
- **Threshold**: ≥4 CanMEDS roles

---

## ⚡ **Performance Characteristics**

| Category | Expected Success Rate | Processing Speed | Complexity |
|----------|----------------------|------------------|------------|
| Advanced Key & Enabling | 90-95% | Fast | Low |
| Standard CanMEDS | 85-90% | Medium | Medium |
| Basic Role-Based | 80-85% | Medium | High |
| Legacy Dotted TOC | 75-80% | Slow | High |
| CanMEDS Without Levels | 85-90% | Fast | Low |

---

## 🛠️ **Troubleshooting**

### **Common Issues**
1. **PDF Text Extraction Fails**: Check if PDF is text-based or scanned image
2. **No CanMEDS Roles Found**: Document may use alternative terminology
3. **Section Boundaries Wrong**: TOC parsing may have failed, check manual markers
4. **Validation Failed**: Adjust thresholds for specific document variations

### **Manual Intervention Points**
- Documents with non-standard CanMEDS role names
- PDFs with poor text extraction quality
- Documents with hybrid competency structures
- Unusual TOC formatting in legacy documents

---

## 📈 **Success Metrics**

### **Target Metrics**
- **Overall Extraction Rate**: >85% 
- **Content Quality**: >90% of extracted sections contain valid competency content
- **False Positives**: <5% of extractions contain non-competency content
- **Processing Time**: <2 minutes per document average

### **Quality Indicators**
- ✅ Correct page range identification
- ✅ Complete competency content extraction  
- ✅ Minimal non-competency content inclusion
- ✅ Proper section boundary detection

---

**Generated**: Based on analysis of 125 SCFHS curriculum documents  
**Last Updated**: January 2025  
**Extraction Scripts**: 5 category-specific extractors + 1 master coordinator
