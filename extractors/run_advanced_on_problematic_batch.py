#!/usr/bin/env python3
"""
Test the Advanced AI CanMEDS Extractor on all previously problematic documents in one batch
"""

import sys
import os

# Add current directory to path for imports
sys.path.append('.')

from advanced_ai_canmeds_extractor import AdvancedCanMEDSExtractor
import json

# Problematic documents that previously failed or had poor results
problematic_docs = [
    "74. __Psychiatry Board__.pdf",
    "85. __Pediatrics Board__.pdf", 
    "96. __Oral And Maxillofacial Surgery Board__.pdf",
    "15. __Adult Critical Care Board__.pdf",
    "59. __Pediatric Otolaryngology__.pdf"
]

def test_all_problematic():
    """Test all problematic documents in one batch"""
    
    base_path = "../Document_Categories/02_Standard_CanMEDS_Format"
    output_dir = "../Extracted_Competencies/03_Advanced_AI_Problematic_Batch"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("Testing Advanced AI Extractor on Problematic Documents (Batch Mode)")
    print("=" * 70)
    
    extractor = AdvancedCanMEDSExtractor()
    results = []
    
    for doc_name in problematic_docs:
        doc_path = os.path.join(base_path, doc_name)
        
        if os.path.exists(doc_path):
            print(f"\nProcessing: {doc_name}")
            
            try:
                result = extractor.extract_from_pdf(doc_path, output_dir)
                results.append(result)
                
                if result['extraction_successful']:
                    validation = result.get('validation', 'Unknown quality')
                    roles = result.get('detailed_analysis', {}).get('role_count', 0)
                    print(f"✓ {doc_name}: {validation} ({roles}/7 roles)")
                else:
                    reason = result.get('failure_reason', 'Unknown error')
                    print(f"✗ {doc_name}: Failed - {reason}")
            
            except Exception as e:
                print(f"✗ Exception processing {doc_name}: {str(e)}")
                # Create failure report
                results.append({
                    'pdf_path': doc_path,
                    'extraction_successful': False,
                    'failure_reason': str(e),
                    'validation': f'Exception: {str(e)}',
                    'detailed_analysis': {},
                    'content_length': 0
                })
        else:
            print(f"✗ Document not found: {doc_path}")
    
    # Generate summary report
    successful = [r for r in results if r['extraction_successful']]
    excellent = [r for r in successful if 'Excellent' in r.get('validation', '')]
    
    summary = {
        'category': 'Advanced AI-Powered CanMEDS Format (problematic documents test)',
        'total_documents': len(results),
        'successful_extractions': len(successful),
        'excellent_extractions': len(excellent),
        'extraction_rate': f"{len(successful)/len(results)*100:.1f}%" if results else "0%",
        'excellent_rate': f"{len(excellent)/len(results)*100:.1f}%" if results else "0%",
        'results': results
    }
    
    summary_file = os.path.join(output_dir, 'extraction_summary_problematic.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n=== Final Results Summary ===")
    print(f"Documents tested: {len(results)}")
    print(f"Successful extractions: {len(successful)} ({len(successful)/len(results)*100:.1f}%)" if results else "No results")
    print(f"Excellent quality: {len(excellent)} ({len(excellent)/len(results)*100:.1f}%)" if results else "No excellent results")
    print(f"Summary saved: {summary_file}")
    
    return results

if __name__ == "__main__":
    test_all_problematic()
