"""
Test USPTO MCP Integration
"""

import sys
sys.path.append('.')

from utils.mcp_clients.uspto_client import USPTOClient, quick_search
import json


def test_basic_search():
    """Test 1: Basic patent search"""
    print("=" * 80)
    print("TEST 1: Basic Patent Search")
    print("=" * 80)
    
    results = quick_search(
        query="ADAS sensor fusion",
        companies=["NVIDIA", "Qualcomm"]
    )
    
    print(f"\n✅ Found {results['total_found']} patents")
    print(f"📄 Returned: {results['returned']} results\n")
    
    if results['patents']:
        print("Sample Patent:")
        patent = results['patents'][0]
        print(f"  Title: {patent['title']}")
        print(f"  Assignee: {patent['assignee']}")
        print(f"  Filing Date: {patent['filing_date']}")
        print(f"  Abstract: {patent['abstract'][:150]}...")
    
    return results


def test_trend_analysis():
    """Test 2: Innovation trend analysis"""
    print("\n" + "=" * 80)
    print("TEST 2: Innovation Trend Analysis")
    print("=" * 80)
    
    client = USPTOClient()
    trends = client.analyze_trends(
        technology="4D radar imaging",
        companies=["NVIDIA", "Qualcomm", "Mobileye", "Tesla"],
        years=[2022, 2023, 2024]
    )
    
    print(f"\n📊 Analysis: {trends['technology']}")
    print(f"📅 Period: {trends['analysis_period']}")
    print(f"📈 Total Filings: {trends['total_filings']}")
    
    if 'yoy_growth_percent' in trends:
        print(f"🚀 YoY Growth: {trends['yoy_growth_percent']}%")
    
    print("\n🏆 By Company:")
    for company, data in trends['by_company'].items():
        print(f"  {company}: {data['total']} patents")
    
    if trends.get('insights'):
        print("\n💡 Insights:")
        for insight in trends['insights']:
            print(f"  {insight}")
    
    return trends


def test_white_space():
    """Test 3: White space identification"""
    print("\n" + "=" * 80)
    print("TEST 3: Patent White Space Analysis")
    print("=" * 80)
    
    client = USPTOClient()
    white_space = client.find_white_space(
        technology_areas=[
            "low power transformer inference automotive",
            "event based camera ADAS",
            "quantum sensor automotive",
            "4D radar imaging"
        ],
        threshold=20
    )
    
    print(f"\n🎯 Opportunities (< {white_space['threshold']} patents):")
    for opp in white_space['opportunities']:
        print(f"  {opp['technology']}: {opp['patent_count']} patents - {opp['status']}")
    
    print(f"\n⚠️  Crowded Areas:")
    for area in white_space['crowded_areas']:
        print(f"  {area['technology']}: {area['patent_count']} patents - {area['status']}")
    
    return white_space


if __name__ == "__main__":
    print("\n🧪 USPTO MCP Integration Tests\n")
    
    try:
        # Run tests
        test_basic_search()
        test_trend_analysis()
        test_white_space()
        
        print("\n" + "=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()