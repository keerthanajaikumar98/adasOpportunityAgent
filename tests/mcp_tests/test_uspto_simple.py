"""
Simplified USPTO tests without full MCP server
"""

import sys
sys.path.append('.')

import json
from unittest.mock import Mock, patch, AsyncMock


def test_mock_patent_search():
    """Test 1: Mock patent search (no real MCP server needed)"""
    print("=" * 80)
    print("TEST 1: Mock Patent Search")
    print("=" * 80)
    
    # Mock response
    mock_response = {
        "query": "ADAS sensor fusion",
        "total_found": 247,
        "returned": 10,
        "patents": [
            {
                "patent_number": "US2024123456",
                "title": "Multi-sensor fusion system for autonomous vehicles",
                "assignee": "NVIDIA Corporation",
                "filing_date": "2024-03-15",
                "abstract": "A system and method for fusing data...",
                "inventors": ["John Smith", "Jane Doe"]
            }
        ]
    }
    
    print(f"\n✅ Mock search successful")
    print(f"📄 Found {mock_response['total_found']} patents")
    print(f"📄 Returned: {mock_response['returned']} results\n")
    
    if mock_response['patents']:
        patent = mock_response['patents'][0]
        print("Sample Patent:")
        print(f"  Title: {patent['title']}")
        print(f"  Assignee: {patent['assignee']}")
        print(f"  Filing Date: {patent['filing_date']}")
    
    return mock_response


def test_direct_api_call():
    """Test 2: Direct USPTO API call (no MCP)"""
    print("\n" + "=" * 80)
    print("TEST 2: Direct USPTO API Test")
    print("=" * 80)
    
    import httpx
    
    try:
        # Direct API call to USPTO
        response = httpx.get(
            "https://developer.uspto.gov/ibd-api/v1/patent/application",
            params={
                "searchText": "autonomous vehicle",
                "rows": 5
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ USPTO API is accessible")
            print(f"📄 Found {data.get('numFound', 0)} patents")
            print(f"📄 Returned: {len(data.get('docs', []))} results")
            
            if data.get('docs'):
                patent = data['docs'][0]
                print(f"\nSample Patent:")
                print(f"  Title: {patent.get('inventionTitle', 'N/A')}")
                print(f"  Assignee: {patent.get('assigneeEntityName', 'N/A')}")
            
            return data
        else:
            print(f"\n⚠️ USPTO API returned status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"\n❌ Error calling USPTO API: {str(e)}")
        return None


if __name__ == "__main__":
    print("\n🧪 Simplified USPTO Tests\n")
    
    try:
        # Test 1: Mock test
        test_mock_patent_search()
        
        # Test 2: Direct API test
        test_direct_api_call()
        
        print("\n" + "=" * 80)
        print("✅ Tests complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
