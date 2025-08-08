#!/usr/bin/env python3
"""
Test script for the enhanced CanMEDS extractor
Focuses on problematic documents that failed with the original extractor
"""

import os
import sys
from pathlib import Path
from extract_standard_canmeds_enhanced import EnhancedStandardCanMEDSExtractor

def test_problematic_documents():
    """Test the enhanced extractor on known problematic documents"""
    
    # Known problematic documents from our analysis
    test_cases = [
        {
            'file': '24. __Diagnostic Neuroradiology Fellowship__.pdf',
            'expected_issues': 'Original extracted PROGRAM STRUCTURE instead of competencies',
            'expected_improvement': 'Should find actual competency section or reject extraction'
        },
        {
            'file': '81. __Periodontics Board__.pdf', 
            'expected_issues': 'Original extracted REFERENCES section only',
            'expected_improvement': 'Should find competency section or mark as failed extraction'
        },
        {
            'file': '129. __Adult Critical Care Fellowship__.pdf',
            'expected_issues': 'Good baseline - should maintain or improve quality',
            'expected_improvement': 'Should maintain excellent extraction with better validation'
        }
    ]
    
    # Paths
    input_dir = "../Document_Categories/02_Standard_CanMEDS_Format"
    output_dir = "../Extracted_Competencies/02_Standard_CanMEDS_Format_ENHANCED_TEST"
    
    print("🧪 TESTING ENHANCED CanMEDS EXTRACTOR")
    print("=" * 60)
    
    # Create extractor
    extractor = EnhancedStandardCanMEDSExtractor()
    
    # Test each document
    for test_case in test_cases:
        file_path = os.path.join(input_dir, test_case['file'])
        
        if not os.path.exists(file_path):
            print(f"⚠️  Test file not found: {test_case['file']}")
            continue
            
        print(f"\n🔍 Testing: {test_case['file']}")
        print(f"Expected issues: {test_case['expected_issues']}")
        print(f"Expected improvement: {test_case['expected_improvement']}")
        print("-" * 50)
        
        # Run extraction
        result = extractor.extract_competencies(file_path, output_dir)
        
        if result:
            # Analyze results
            analysis = result.get('detailed_analysis', {})
            validation = result.get('validation', '')
            
            print(f"📊 RESULTS:")
            print(f"   Success: {result['extraction_successful']}")
            print(f"   Validation: {validation}")
            print(f"   Template: {result.get('template', 'unknown')}")
            print(f"   Roles found: {analysis.get('role_count', 0)}/7")
            print(f"   Roles: {', '.join(analysis.get('roles_found', []))}")
            print(f"   Content length: {analysis.get('content_length', 0)} chars")
            print(f"   Competency score: {analysis.get('competency_type_score', 0):.1f}")
            print(f"   Contamination score: {analysis.get('contamination_score', 0):.1f}")
            print(f"   Page range size: {analysis.get('page_range_size', 0)} pages")
            
            # Quality assessment
            if result['extraction_successful']:
                if analysis.get('contamination_score', 0) < 10:
                    print("✅ QUALITY: Clean extraction with low contamination")
                elif analysis.get('contamination_score', 0) < 30:
                    print("⚠️  QUALITY: Some contamination detected")
                else:
                    print("❌ QUALITY: High contamination - may contain non-competency content")
                    
                if analysis.get('role_count', 0) >= 5:
                    print("✅ COMPLETENESS: Good CanMEDS role coverage")
                elif analysis.get('role_count', 0) >= 3:
                    print("⚠️  COMPLETENESS: Partial CanMEDS role coverage")
                else:
                    print("❌ COMPLETENESS: Poor CanMEDS role coverage")
            else:
                print("❌ EXTRACTION FAILED")
        else:
            print("❌ EXTRACTION COMPLETELY FAILED")

def compare_with_original():
    """Compare results with original extractor output"""
    
    original_dir = "../Extracted_Competencies/02_Standard_CanMEDS_Format"
    enhanced_dir = "../Extracted_Competencies/02_Standard_CanMEDS_Format_ENHANCED_TEST"
    
    print(f"\n📊 COMPARISON WITH ORIGINAL EXTRACTOR")
    print("=" * 60)
    
    test_files = [
        '24. __Diagnostic Neuroradiology Fellowship___competencies.txt',
        '81. __Periodontics Board___competencies.txt', 
        '129. __Adult Critical Care Fellowship___competencies.txt'
    ]
    
    for filename in test_files:
        original_path = os.path.join(original_dir, filename)
        enhanced_path = os.path.join(enhanced_dir, filename)
        
        print(f"\n📄 Comparing: {filename}")
        print("-" * 40)
        
        # Check original
        if os.path.exists(original_path):
            with open(original_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                original_lines = len([l for l in original_content.split('\n') if l.strip()])
                
            print(f"Original: {len(original_content)} chars, {original_lines} lines")
            
            # Quick quality check
            if 'REFERENCES' in original_content and 'MEDICAL EXPERT' not in original_content:
                print("⚠️  Original appears to contain references, not competencies")
            elif 'PROGRAM STRUCTURE' in original_content and original_content.count('COMPETENC') < 3:
                print("⚠️  Original appears to contain program structure, not competencies") 
            elif original_content.count('MEDICAL EXPERT') > 0:
                print("✅ Original appears to contain competency content")
            else:
                print("❓ Original content type unclear")
        else:
            print("❌ Original file not found")
            
        # Check enhanced  
        if os.path.exists(enhanced_path):
            with open(enhanced_path, 'r', encoding='utf-8') as f:
                enhanced_content = f.read()
                enhanced_lines = len([l for l in enhanced_content.split('\n') if l.strip()])
                
            print(f"Enhanced: {len(enhanced_content)} chars, {enhanced_lines} lines")
            
            # Extract validation info
            validation_line = [l for l in enhanced_content.split('\n') if l.startswith('Validation:')]
            if validation_line:
                print(f"Validation: {validation_line[0].replace('Validation: ', '')}")
            
            # Extract roles found
            roles_line = [l for l in enhanced_content.split('\n') if l.startswith('Roles Found:')]
            if roles_line:
                print(f"Roles: {roles_line[0].replace('Roles Found: ', '')}")
                
        else:
            print("❌ Enhanced file not found")

def main():
    """Run the test suite"""
    
    print("🔬 ENHANCED CANMEDS EXTRACTOR TEST SUITE")
    print("=" * 70)
    print("Testing enhanced extractor on problematic documents")
    print("This will help validate the improvements made\n")
    
    # Run tests
    test_problematic_documents()
    
    # Compare results
    compare_with_original()
    
    print(f"\n🎯 TEST SUMMARY")
    print("=" * 40)
    print("✅ Tests completed")
    print("📁 Enhanced outputs saved to: ../Extracted_Competencies/02_Standard_CanMEDS_Format_ENHANCED_TEST")
    print("📊 Review the comparison results above to validate improvements")
    print("\nKey improvements to look for:")
    print("- Reduced contamination scores (< 30)")
    print("- Higher CanMEDS role counts (≥ 3)")
    print("- More appropriate content extraction")
    print("- Better rejection of non-competency sections")

if __name__ == "__main__":
    main()
