"""Trends and Simplification Agent - Identifies and explains key ADAS trends."""

from typing import Dict, Any, Optional
from agents import BaseAgent 
from utils.api_clients.uspto_client import USPTOClien

class TrendsSimplificationAgent(BaseAgent):
    """Identifies trends and translates to plain language with silicon implications
    
    NOW ENHANCED WITH:
    - USPTO patent filing data for innovation velocity
    - Evidence from real patent trends
    """

    def __init__(self, api_client, uspto_client=None):
        super().__init__("TrendsSimplificationAgent", api_client)
        self.uspto_client = uspto_client
        
        if self.uspto_client:
            self.logger.info("✅ USPTO patent data available for trend analysis")
        else:
            self.logger.warning("⚠️ USPTO patent data unavailable - using market data only")

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify 5-7 key trends in ADAS with jargon-free explanations.
        
        NOW ENHANCED WITH PATENT DATA:
        - Innovation velocity from USPTO filings
        - Real patent evidence for trends
        - White space identification
        
        Acceptance Criteria:
        - No unexplained acronyms
        - Each trend tied to a silicon implication
        - Evidence-backed (paper, OEM statement, research note, OR patent data)
        """
        
        self.logger.info("Analyzing ADAS trends...")
        
        # NEW: Get patent trend data if available
        patent_data = await self._get_patent_trends()
        
        system_prompt = """You are a technical translator specializing in automotive semiconductors.

Your task: Identify key trends in US ADAS and translate to clear, jargon-free language.

Requirements:
1. Identify 5-7 major trends
2. Explain each in plain language (no unexplained acronyms)
3. Connect each trend to silicon/semiconductor implications
4. Provide evidence (cite papers, OEM statements, research, OR patent filings)

Trend categories to consider:
- Sensor evolution (camera resolution, radar frequency)
- Processing paradigm shifts (centralized vs distributed)
- AI/ML integration
- Power efficiency demands
- Functional safety requirements
- Cost pressures
- Regulatory changes

INNOVATION VELOCITY INDICATORS (from patent data):
- High patent growth (>50% YoY) = Accelerating trend
- Moderate growth (20-50% YoY) = Steady innovation
- Low growth (<20% YoY) = Maturing technology
- Declining filings = Potential commoditization

Output format:
{
  "trends": [
    {
      "name": "<Descriptive name>",
      "description": "<Plain language explanation>",
      "silicon_implication": "<One-line impact on semiconductor needs>",
      "innovation_velocity": "accelerating|steady|maturing|declining",  // NEW
      "evidence": {
        "type": "paper|oem_statement|research_note|patent_data",  // NEW: patent_data option
        "source": "<Source name>",
        "url": "<URL>",
        "key_quote": "<Relevant quote>",
        "patent_filings": "<Optional: number of recent patents>"  // NEW
      },
      "timeline": "<When this matters: current|1-3 years|3-5 years>"
    }
  ],
  "patent_insights": {  // NEW section
    "data_available": true|false,
    "top_innovators": ["<Company>", ...],
    "emerging_technologies": ["<Tech with rapid patent growth>", ...]
  },
  "acronyms_defined": {
    "<ACRONYM>": "<Definition>"
  },
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        market_context = context.get('market_size_data', {})
        
        # Build enhanced prompt with patent data
        prompt = self._build_prompt(market_context, patent_data)
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            result = self._parse_trends_data(response)
            
            # Add metadata about data sources
            result['data_sources'] = {
                'market_data': 'available',
                'patent_data': 'uspto_api' if patent_data else 'unavailable'
            }
            
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation failed: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            return result
            
        except Exception as e:
            self.logger.error(f"Trends analysis failed: {str(e)}")
            raise
    
    async def _get_patent_trends(self) -> Optional[Dict[str, Any]]:
        """Get patent filing trends from USPTO API"""
        
        if not self.uspto_client:
            return None
        
        try:
            self.logger.info("Fetching USPTO patent trends...")
            
            # Analyze patent trends for key ADAS technologies
            trends = self.uspto_client.analyze_trends(
                technology="ADAS autonomous vehicle semiconductor",
                companies=["NVIDIA", "Qualcomm", "Mobileye", "Tesla", "NXP", "Renesas"],
                years=[2022, 2023, 2024]
            )
            
            # Also check for emerging technologies (white space)
            white_space = self.uspto_client.find_white_space(
                technology_areas=[
                    "low power transformer inference automotive",
                    "4D radar imaging",
                    "event based camera ADAS",
                    "neuromorphic computing automotive",
                    "edge AI acceleration ADAS"
                ],
                threshold=30  # Technologies with <30 patents = emerging
            )
            
            self.logger.info(f"✅ Found {trends.get('total_filings', 0)} ADAS patents (2022-2024)")
            
            return {
                'trends': trends,
                'white_space': white_space
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch patent data: {str(e)}")
            return None
    
    def _build_prompt(self, market_context: Dict, patent_data: Optional[Dict]) -> str:
        """Build enhanced prompt with patent data"""
        
        base_prompt = f"""Identify and explain key trends in US ADAS semiconductors.

MARKET CONTEXT:
- Current market size: ${market_context.get('current_market_size_usd_millions', 'Unknown')}M
- Projected growth: {market_context.get('cagr_percent', 'Unknown')}% CAGR
- Key segments: Camera, Radar, Sensor Fusion/Compute
"""
        
        if patent_data and patent_data.get('trends'):
            trends = patent_data['trends']
            white_space = patent_data.get('white_space', {})
            
            patent_section = f"""

PATENT FILING TRENDS (2022-2024):
Total ADAS patents filed: {trends.get('total_filings', 0)}
YoY Growth: {trends.get('yoy_growth_percent', 'N/A')}%

Innovation Leaders (by patent count):
"""
            # Add top companies
            for company, data in sorted(
                trends.get('by_company', {}).items(),
                key=lambda x: x[1].get('total', 0),
                reverse=True
            )[:5]:
                patent_section += f"- {company}: {data.get('total', 0)} patents\n"
            
            # Add white space opportunities
            if white_space.get('opportunities'):
                patent_section += f"""

EMERGING TECHNOLOGIES (Low Patent Competition):
"""
                for opp in white_space['opportunities'][:3]:
                    patent_section += f"- {opp['technology']}: {opp['patent_count']} patents ({opp['status']})\n"
            
            patent_section += """

Use this patent data to:
1. Validate market trends with innovation velocity
2. Identify emerging opportunities (high market growth + low patent count)
3. Spot mature technologies (high patent count + slowing growth)
"""
            
            return base_prompt + patent_section
        
        else:
            return base_prompt + "\n\nFocus on trends that will drive semiconductor innovation and market opportunities."
    
    def _parse_trends_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured trends data."""
        import json
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Parse failed", "raw_response": response}
    
    def _validate_acceptance_criteria(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against acceptance criteria."""
        
        validation = {'passed': True, 'reasons': []}
        
        trends = data.get('trends', [])
        
        # Check trend count
        if len(trends) < 5 or len(trends) > 7:
            validation['passed'] = False
            validation['reasons'].append(f"Need 5-7 trends, got {len(trends)}")
        
        # Check each trend
        for i, trend in enumerate(trends):
            # Must have silicon implication
            if not trend.get('silicon_implication'):
                validation['passed'] = False
                validation['reasons'].append(f"Trend {i+1} missing silicon implication")
            
            # Must have evidence
            if not trend.get('evidence'):
                validation['passed'] = False
                validation['reasons'].append(f"Trend {i+1} missing evidence")
            
            # NEW: If patent data available, should include innovation velocity
            if data.get('data_sources', {}).get('patent_data') == 'uspto_api':
                if not trend.get('innovation_velocity'):
                    validation['reasons'].append(f"Trend {i+1} missing innovation velocity (patent data available)")
        
        # Check for acronym definitions
        if not data.get('acronyms_defined'):
            validation['reasons'].append("No acronyms defined (may be acceptable if none used)")
        
        return validation