#!/usr/bin/env python3
"""
Quick Test Script for Quality Optimization
==========================================

Tests the optimized quality scoring to verify improvements work correctly.
"""

import os
import json

def analyze_extraction_results(results_dir, filename):
    """Analyze extraction results to understand quality distribution"""
    
    json_path = os.path.join(results_dir, filename)
    if not os.path.exists(json_path):
        print(f"Results file not found: {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n=== Analysis of {filename} ===")
    print(f"Total documents: {data['total_documents']}")
    print(f"Successful extractions: {data['successful_extractions']}")
    print(f"Extraction rate: {data['extraction_rate']}")
    print(f"Excellent quality: {data['excellent_extractions']}")
    print(f"Supreme quality: {data['supreme_extractions']}")
    
    # Analyze score distribution
    scores = []
    validations = []
    
    for result in data['results']:
        if result.get('extraction_successful', False):
            if 'quality_score' in result:
                scores.append(result['quality_score'])
            validations.append(result.get('validation', 'Unknown'))
    
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        print(f"\n=== Score Distribution ===")
        print(f"Average score: {avg_score:.1f}")
        print(f"Score range: {min_score:.1f} - {max_score:.1f}")
        
        # Count by quality level
        quality_counts = {}
        for validation in validations:
            if 'Supreme' in validation:
                quality_counts['Supreme'] = quality_counts.get('Supreme', 0) + 1
            elif 'Excellent' in validation:
                quality_counts['Excellent'] = quality_counts.get('Excellent', 0) + 1
            elif 'Good' in validation:
                quality_counts['Good'] = quality_counts.get('Good', 0) + 1
            elif 'Acceptable' in validation:
                quality_counts['Acceptable'] = quality_counts.get('Acceptable', 0) + 1
            else:
                quality_counts['Other'] = quality_counts.get('Other', 0) + 1
        
        print(f"\n=== Quality Level Breakdown ===")
        for level, count in quality_counts.items():
            percentage = (count / len(validations)) * 100
            print(f"{level}: {count} ({percentage:.1f}%)")

def main():
    """Main function"""
    base_dir = "../Extracted_Competencies"
    
    # Compare original vs optimized results
    print("=" * 60)
    print("QUALITY OPTIMIZATION ANALYSIS")
    print("=" * 60)
    
    # Original results
    original_dir = os.path.join(base_dir, "07_Final_Perfected_Advanced_Key_Enabling_FULL")
    analyze_extraction_results(original_dir, "extraction_summary_advanced_key_enabling.json")
    
    # Optimized results 
    optimized_dir = os.path.join(base_dir, "08_Optimized_Advanced_Key_Enabling_TEST")
    analyze_extraction_results(optimized_dir, "extraction_summary_advanced_key_enabling.json")
    
    # Final Working Optimized results
    final_optimized_dir = os.path.join(base_dir, "10_Final_Working_Optimized_TEST")
    analyze_extraction_results(final_optimized_dir, "extraction_summary_final_working_optimized.json")
    
    print(f"\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("1. If optimized version has lower success rate but similar score distribution,")
    print("   the thresholds may be too strict and need further adjustment.")
    print("2. If both versions have similar low excellent/supreme rates, the scoring")
    print("   algorithm itself may need enhancement.")
    print("3. Consider hybrid approach: maintain high success rate with better quality classification.")
    print("=" * 60)

if __name__ == "__main__":
    main()
