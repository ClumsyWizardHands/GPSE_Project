#!/usr/bin/env python3
"""
Test case to verify temporal awareness fix in GPSE
"""

from run_gpse_enhanced_memory import TemporalEventParser

def test_temporal_parser():
    """Test the temporal event parser with known examples"""
    parser = TemporalEventParser()
    
    # Test cases
    test_cases = [
        {
            "title": "Israel strikes Iran nuclear facility in overnight raid",
            "content": "Israeli forces attacked Iranian nuclear installations following intelligence reports...",
            "expected": "PAST"
        },
        {
            "title": "US preparing new sanctions against Russia",
            "content": "The Biden administration will announce new measures next week...",
            "expected": "FUTURE"
        },
        {
            "title": "Fighting continues in eastern Ukraine",
            "content": "Russian forces are currently advancing on multiple fronts...",
            "expected": "PRESENT/ONGOING"
        },
        {
            "title": "China responds after US naval exercise",
            "content": "Beijing issued strong statements following the completion of joint drills...",
            "expected": "PAST"
        },
        {
            "title": "NATO plans to increase troop presence",
            "content": "Alliance leaders will meet to discuss potential deployment...",
            "expected": "FUTURE"
        }
    ]
    
    print("Testing Temporal Event Parser")
    print("=" * 50)
    
    for i, test in enumerate(test_cases, 1):
        result = parser.classify_event_temporality(test["title"], test["content"])
        status = "✓" if result == test["expected"] else "✗"
        
        print(f"\nTest {i}: {status}")
        print(f"Title: {test['title']}")
        print(f"Expected: {test['expected']}")
        print(f"Got: {result}")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == "__main__":
    test_temporal_parser()
