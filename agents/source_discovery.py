"""Source Discovery Agent - Finds and validates credible data sources."""

from typing import Dict, Any, List
from agents import BaseAgent
import json

class SourceDiscoveryAgent(BaseAgent):
    """Discovers and validates credible sources for ADAS analysis."""
    
    def __init__(self, api_client):
        super().__init__("SourceDiscoveryAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover credible sources for ADAS semiconductor analysis.
        
        Acceptance Criteria:
        - Sources categorized by type (academic, financial, industry)
        - Each source validated for credibility
        - Sources mapped to relevant topics
        """
        
        self.logger.info("Discovering credible sources...")
        
        system_prompt = """You are a research librarian specializing in automotive semiconductors.

Your task: Identify the most credible and relevant sources for ADAS semiconductor market analysis.

Source categories:
1. Academic (IEEE, arXiv, ACM, SAE papers)
2. Financial Research (JP Morgan, Goldman Sachs, Morgan Stanley reports)
3. Industry (OEM press releases, Tier-1 reports, semiconductor vendor whitepapers)
4. Standards Bodies (SAE, ISO standards)

For each source, identify:
- Source name and URL pattern
- Type of information it provides
- Credibility level (High/Medium)
- Typical update frequency
- Access requirements (public/subscription)
- Relevance to specific topics

Focus on sources that cover:
- ADAS market sizing and forecasts
- Camera/radar/sensor fusion technology
- Semiconductor architectures
- OEM adoption trends
- Safety standards and regulations

Output format:
{
  "sources": [
    {
      "name": "<Source name>",
      "category": "academic|financial|industry|standards",
      "url_pattern": "<Base URL or search pattern>",
      "credibility": "High|Medium",
      "information_type": "<What it covers>",
      "update_frequency": "<How often updated>",
      "access": "public|subscription|mixed",
      "relevant_topics": ["<topic 1>", "<topic 2>"],
      "example_searches": ["<search query 1>", "<search query 2>"],
      "notes": "<Any important notes about using this source>"
    }
  ],
  "source_summary": {
    "total_sources": <number>,
    "by_category": {
      "academic": <number>,
      "financial": <number>,
      "industry": <number>,
      "standards": <number>
    },
    "public_access": <number>,
    "subscription_required": <number>
  },
  "recommended_search_strategy": "<How to use these sources effectively>",
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        prompt = """Identify credible sources for US ADAS semiconductor market analysis.

Requirements:
1. Cover all source categories (academic, financial, industry, standards)
2. Focus on sources with highest credibility
3. Include both free and subscription sources
4. Provide specific URL patterns or search strategies
5. Map sources to relevant analysis topics

Topics to cover:
- Market sizing and growth forecasts
- Camera processing technology
- Radar processing technology
- Sensor fusion and AI compute
- Competitive landscape
- Technical specifications
- OEM adoption and deployment

Provide actionable source discovery recommendations."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_source_data(response)
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation issues: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            total_sources = len(result.get('sources', []))
            self.logger.info(f"Discovered {total_sources} credible sources")
            return result
            
        except Exception as e:
            self.logger.error(f"Source discovery failed: {str(e)}")
            raise
    
    def _parse_source_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        
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
        """Validate acceptance criteria."""
        
        validation = {'passed': True, 'reasons': []}
        
        sources = data.get('sources', [])
        
        # Check categorization
        categories = set()
        for source in sources:
            cat = source.get('category')
            if cat:
                categories.add(cat)
        
        expected_categories = {'academic', 'financial', 'industry'}
        if not expected_categories.issubset(categories):
            missing = expected_categories - categories
            validation['reasons'].append(f"Missing source categories: {missing}")
        
        # Check credibility ratings
        for i, source in enumerate(sources):
            if 'credibility' not in source:
                validation['passed'] = False
                validation['reasons'].append(f"Source {i+1} missing credibility rating")
        
        return validation