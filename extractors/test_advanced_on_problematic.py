#!/usr/bin/env python3
"""
Test the Advanced AI CanMEDS Extractor on previously problematic documents
"""

import subprocess
import os
import json

# Problematic documents that previously failed or had poor results
problematic_docs = [
    "74. __Psychiatry Board__.pdf",
    "85. __Pediatrics Board__.pdf", 
    "96. __Oral And Maxillofacial Surgery Board__.pdf",
    "15. __Adult Critical Care Board__.pdf",
    "59. __Pediatric Otolaryngology__.pdf"
]

def test_advanced_extractor():
    """Test the advanced extractor on problematic documents"""
    
    base_path = "../Document_Categories/02_Standard_CanMEDS_Format"
    output_dir = "../Extracted_Competencies/03_Advanced_AI_Problematic_Test"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print("Testing Advanced AI Extractor on Previously Problematic Documents")
    print("=" * 70)
    
    results = []
    
    for doc_name in problematic_docs:
        doc_path = os.path.join(base_path, doc_name)
        
        if os.path.exists(doc_path):
            print(f"\nProcessing: {doc_name}")
            
            # Run the advanced extractor
            try:
                result = subprocess.run([
                    'python3', 'advanced_ai_canmeds_extractor.py', 
                    doc_path, output_dir
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    print(f"✓ Successfully processed {doc_name}")
                    results.append({"doc": doc_name, "status": "success"})
                else:
                    print(f"✗ Failed to process {doc_name}")
                    print(f"Error: {result.stderr}")
                    results.append({"doc": doc_name, "status": "failed", "error": result.stderr})
            
            except subprocess.TimeoutExpired:
                print(f"✗ Timeout processing {doc_name}")
                results.append({"doc": doc_name, "status": "timeout"})
            except Exception as e:
                print(f"✗ Exception processing {doc_name}: {str(e)}")
                results.append({"doc": doc_name, "status": "exception", "error": str(e)})
        else:
            print(f"✗ Document not found: {doc_path}")
            results.append({"doc": doc_name, "status": "not_found"})
    
    # Check results
    summary_file = os.path.join(output_dir, "extraction_summary_advanced.json")
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        print(f"\n=== Advanced Extractor Test Results ===")
        print(f"Documents tested: {len(problematic_docs)}")
        print(f"Successful extractions: {summary['successful_extractions']}")
        print(f"Excellent quality: {summary['excellent_extractions']}")
        print(f"Success rate: {summary['extraction_rate']}")
        print(f"Excellence rate: {summary['excellent_rate']}")
        
        # Show individual results
        print(f"\nIndividual Results:")
        for result in summary['results']:
            doc_name = os.path.basename(result['pdf_path'])
            if result['extraction_successful']:
                validation = result.get('validation', 'Unknown quality')
                roles = result.get('detailed_analysis', {}).get('role_count', 0)
                print(f"✓ {doc_name}: {validation} ({roles}/7 roles)")
            else:
                reason = result.get('failure_reason', 'Unknown error')
                print(f"✗ {doc_name}: Failed - {reason}")
    
    return results

if __name__ == "__main__":
    test_advanced_extractor()
