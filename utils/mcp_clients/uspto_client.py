# utils/api_clients/uspto_client.py (NEW - simpler approach)
"""
Direct USPTO API Client (no MCP server needed)
"""
import httpx
import logging
from typing import List, Dict, Optional
from datetime import datetime

class USPTOClient:
    """Direct USPTO Patent API client"""
    
    def __init__(self):
        self.base_url = "https://developer.uspto.gov/ibd-api/v1"
        self.logger = logging.getLogger('USPTOClient')
        self.timeout = 30.0
    
    def search_patents(self, query: str, rows: int = 10, 
                       companies: Optional[List[str]] = None) -> Dict:
        """
        Search patents directly from USPTO API
        
        Args:
            query: Search query (e.g., "ADAS sensor fusion")
            rows: Number of results to return (max 100)
            companies: Optional list of companies to filter by
        
        Returns:
            Dict with patent results
        """
        try:
            # Build query
            search_query = query
            if companies:
                company_filter = " OR ".join([f'assigneeEntityName:"{c}"' for c in companies])
                search_query = f"{query} AND ({company_filter})"
            
            self.logger.info(f"Searching USPTO: {search_query}")
            
            # Make API call
            response = httpx.get(
                f"{self.base_url}/patent/application",
                params={
                    "searchText": search_query,
                    "rows": rows,
                    "sort": "filingDate desc"
                },
                timeout=self.timeout
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Parse results
            patents = []
            for doc in data.get('docs', []):
                patents.append({
                    'patent_number': doc.get('patentApplicationNumber', 'N/A'),
                    'title': doc.get('inventionTitle', 'N/A'),
                    'assignee': doc.get('assigneeEntityName', 'N/A'),
                    'filing_date': doc.get('filingDate', 'N/A'),
                    'abstract': doc.get('abstractText', ['N/A'])[0] if doc.get('abstractText') else 'N/A',
                    'inventors': doc.get('firstNamedApplicant', 'N/A')
                })
            
            result = {
                'query': query,
                'total_found': data.get('numFound', 0),
                'returned': len(patents),
                'patents': patents
            }
            
            self.logger.info(f"✅ Found {result['total_found']} patents, returned {result['returned']}")
            return result
            
        except Exception as e:
            self.logger.error(f"USPTO search failed: {str(e)}")
            return {
                'query': query,
                'total_found': 0,
                'returned': 0,
                'patents': [],
                'error': str(e)
            }
    
    def analyze_trends(self, technology: str, companies: List[str], 
                       years: List[int]) -> Dict:
        """
        Analyze patent filing trends over time
        
        Args:
            technology: Technology area to analyze
            companies: List of companies to track
            years: List of years to analyze
        
        Returns:
            Trend analysis with YoY growth
        """
        try:
            self.logger.info(f"Analyzing trends for: {technology}")
            
            by_company = {}
            total_filings = 0
            
            for company in companies:
                company_patents = []
                
                for year in years:
                    # Search by company and year
                    query = f'{technology} AND assigneeEntityName:"{company}" AND filingDate:[{year}-01-01 TO {year}-12-31]'
                    
                    response = httpx.get(
                        f"{self.base_url}/patent/application",
                        params={
                            "searchText": query,
                            "rows": 0  # Just get count
                        },
                        timeout=self.timeout
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        count = data.get('numFound', 0)
                        company_patents.append({
                            'year': year,
                            'count': count
                        })
                        total_filings += count
                
                by_company[company] = {
                    'total': sum(p['count'] for p in company_patents),
                    'by_year': company_patents
                }
            
            # Calculate YoY growth
            yoy_growth = None
            if len(years) >= 2:
                earliest_year = years[0]
                latest_year = years[-1]
                
                earliest_total = sum(
                    by_company[c]['by_year'][0]['count'] 
                    for c in companies
                )
                latest_total = sum(
                    by_company[c]['by_year'][-1]['count'] 
                    for c in companies
                )
                
                if earliest_total > 0:
                    yoy_growth = ((latest_total - earliest_total) / earliest_total) * 100
            
            result = {
                'technology': technology,
                'analysis_period': f"{min(years)}-{max(years)}",
                'total_filings': total_filings,
                'by_company': by_company,
                'yoy_growth_percent': round(yoy_growth, 1) if yoy_growth else None,
                'insights': self._generate_insights(by_company, yoy_growth)
            }
            
            self.logger.info(f"✅ Analyzed {total_filings} patents across {len(companies)} companies")
            return result
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {str(e)}")
            return {
                'technology': technology,
                'total_filings': 0,
                'by_company': {},
                'error': str(e)
            }
    
    def find_white_space(self, technology_areas: List[str], 
                        threshold: int = 30) -> Dict:
        """
        Find emerging technologies with low patent competition
        
        Args:
            technology_areas: List of technology areas to check
            threshold: Patent count threshold for "white space"
        
        Returns:
            Opportunities (low patent count) and crowded areas
        """
        try:
            self.logger.info(f"Analyzing {len(technology_areas)} technology areas")
            
            opportunities = []
            crowded_areas = []
            
            for tech in technology_areas:
                # Get patent count for this technology
                response = httpx.get(
                    f"{self.base_url}/patent/application",
                    params={
                        "searchText": tech,
                        "rows": 0
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    patent_count = data.get('numFound', 0)
                    
                    entry = {
                        'technology': tech,
                        'patent_count': patent_count,
                        'status': self._assess_competition(patent_count, threshold)
                    }
                    
                    if patent_count < threshold:
                        opportunities.append(entry)
                    else:
                        crowded_areas.append(entry)
            
            result = {
                'threshold': threshold,
                'opportunities': sorted(opportunities, key=lambda x: x['patent_count']),
                'crowded_areas': sorted(crowded_areas, key=lambda x: x['patent_count'], reverse=True)
            }
            
            self.logger.info(f"✅ Found {len(opportunities)} opportunities, {len(crowded_areas)} crowded areas")
            return result
            
        except Exception as e:
            self.logger.error(f"White space analysis failed: {str(e)}")
            return {
                'threshold': threshold,
                'opportunities': [],
                'crowded_areas': [],
                'error': str(e)
            }
    
    def _generate_insights(self, by_company: Dict, yoy_growth: Optional[float]) -> List[str]:
        """Generate insights from trend data"""
        insights = []
        
        # Top innovator
        if by_company:
            top_company = max(by_company.items(), key=lambda x: x[1]['total'])
            insights.append(f"{top_company[0]} leads with {top_company[1]['total']} patents")
        
        # Growth assessment
        if yoy_growth is not None:
            if yoy_growth > 50:
                insights.append(f"Accelerating innovation ({yoy_growth:.1f}% YoY growth)")
            elif yoy_growth > 20:
                insights.append(f"Steady innovation ({yoy_growth:.1f}% YoY growth)")
            elif yoy_growth > 0:
                insights.append(f"Maturing technology ({yoy_growth:.1f}% YoY growth)")
            else:
                insights.append(f"Declining filings ({yoy_growth:.1f}% YoY change)")
        
        return insights
    
    def _assess_competition(self, patent_count: int, threshold: int) -> str:
        """Assess competition level"""
        if patent_count < threshold * 0.5:
            return "Emerging - Low Competition"
        elif patent_count < threshold:
            return "Growing - Moderate Competition"
        elif patent_count < threshold * 2:
            return "Established - High Competition"
        else:
            return "Mature - Very High Competition"


# Quick search helper
def quick_search(query: str, companies: Optional[List[str]] = None, rows: int = 10) -> Dict:
    """Quick patent search helper"""
    client = USPTOClient()
    return client.search_patents(query, rows, companies)