"""Trends and Simplification Agent - Identifies and explains key ADAS trends."""

from typing import Dict, Any
from agents import BaseAgent 

class TrendsSimplification Agent(BaseAgent):
    # Identifies trends and translates to plain language with silicon implications

    def __init__(self, api_client):
        super().__init__("TrendsSimplificationAgent", api_client)

    async def execute(self, context, Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify 5-7 key trends in ADAS with jargon-free explanations.
        
        Acceptance Criteria:
        - No unexplained acronyms
        - Each trend tied to a silicon implication
        - Evidence-backed (paper, OEM statement, or research note)
        """
        
        self.logger.info("Analyzing ADAS trends...")
        
        system_prompt = """You are a technical translator specializing in automotive semiconductors.

Your task: Identify key trends in US ADAS and translate to clear, jargon-free language.

Requirements:
1. Identify 5-7 major trends
2. Explain each in plain language (no unexplained acronyms)
3. Connect each trend to silicon/semiconductor implications
4. Provide evidence (cite papers, OEM statements, or research)

Trend categories to consider:
- Sensor evolution (camera resolution, radar frequency)
- Processing paradigm shifts (centralized vs distributed)
- AI/ML integration
- Power efficiency demands
- Functional safety requirements
- Cost pressures
- Regulatory changes

Output format:
{
  "trends": [
    {
      "name": "<Descriptive name>",
      "description": "<Plain language explanation>",
      "silicon_implication": "<One-line impact on semiconductor needs>",
      "evidence": {
        "type": "paper|oem_statement|research_note",
        "source": "<Source name>",
        "url": "<URL>",
        "key_quote": "<Relevant quote>"
      },
      "timeline": "<When this matters: current|1-3 years|3-5 years>"
    }
  ],
  "acronyms_defined": {
    "<ACRONYM>": "<Definition>"
  },
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        market_context = context.get('market_size_data', {})
        
        prompt = f"""Identify and explain key trends in US ADAS semiconductors.

Market context from previous analysis:
- Current market size: ${market_context.get('current_market_size_usd_millions', 'Unknown')}M
- Projected growth: {market_context.get('cagr_percent', 'Unknown')}% CAGR
- Key segments: Camera, Radar, Sensor Fusion/Compute

Focus on trends that will drive semiconductor innovation and market opportunities."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            result = self._parse_trends_data(response)
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation failed: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            return result
            
        except Exception as e:
            self.logger.error(f"Trends analysis failed: {str(e)}")
            raise
    
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
        
        # Check for acronym definitions
        if not data.get('acronyms_defined'):
            validation['reasons'].append("No acronyms defined (may be acceptable if none used)")
        
        return validation
