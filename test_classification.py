#!/usr/bin/env python
"""
Test script for conference classification feature.
Demonstrates the full workflow of classifying conferences during submission.
"""

import sys
import json
from services.scholar_service import classify_conference

def test_classification():
    """Test the classification functionality with various conference types"""
    
    test_cases = [
        {
            'name': 'NeurIPS 2024',
            'papers': [
                {'title': 'Deep Learning and Neural Networks'},
                {'title': 'Machine Learning Models'},
                {'title': 'AI-Powered Predictions'},
            ],
            'expected_primary': 'Machine Learning'
        },
        {
            'name': 'CHI 2024',
            'papers': [
                {'title': 'User Interface Design'},
                {'title': 'Human-Computer Interaction Studies'},
                {'title': 'User Experience Research'},
            ],
            'expected_primary': 'Human-Computer Interaction'
        },
        {
            'name': 'ICSE 2024',
            'papers': [
                {'title': 'Software Development Practices'},
                {'title': 'Testing and Quality Assurance'},
                {'title': 'Code Architecture'},
            ],
            'expected_primary': 'Software Engineering'
        },
        {
            'name': 'CVPR 2024',
            'papers': [
                {'title': 'Computer Vision and Image Recognition'},
                {'title': 'Object Detection Methods'},
                {'title': 'Visual Scene Understanding'},
            ],
            'expected_primary': 'Computer Vision'
        },
        {
            'name': 'ACL 2024',
            'papers': [
                {'title': 'Natural Language Processing'},
                {'title': 'Language Translation Models'},
                {'title': 'Text Analysis'},
            ],
            'expected_primary': 'Natural Language Processing'
        },
    ]
    
    print("=" * 70)
    print("CONFERENCE CLASSIFICATION TEST SUITE")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        conference_name = test_case['name']
        papers = test_case['papers']
        expected = test_case['expected_primary']
        
        print(f"Testing: {conference_name}")
        print(f"  Expected Primary: {expected}")
        
        result = classify_conference(conference_name, papers)
        
        if result is None:
            print(f"  ✗ FAILED: Classification returned None")
            failed += 1
        else:
            primary = result['primary']
            confidence = result['confidence']
            secondary = result['secondary']
            
            print(f"  Primary: {primary} (confidence: {confidence:.2%})")
            print(f"  Secondary: {', '.join(secondary) if secondary else 'None'}")
            
            if primary == expected:
                print(f"  ✓ PASSED")
                passed += 1
            else:
                print(f"  ✗ FAILED: Expected {expected}, got {primary}")
                failed += 1
        
        print()
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)}")
    print("=" * 70)
    
    # Show classification format
    print()
    print("CLASSIFICATION FORMAT (used in pending submissions):")
    print(json.dumps({
        'primary': 'Machine Learning',
        'secondary': ['Computer Vision', 'Natural Language Processing'],
        'confidence': 0.85,
        'reasoning': 'Classified based on keyword analysis of conference name and paper titles. Primary field matches: 7 occurrences'
    }, indent=2))
    
    return failed == 0

if __name__ == '__main__':
    success = test_classification()
    sys.exit(0 if success else 1)
