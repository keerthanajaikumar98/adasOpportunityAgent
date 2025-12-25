""" Market Size Agent - Analyzes ADS Semiconductor Market Sizing."""

from typing import Dict, Any, List
from agents import BaseAgent 
import Logging 

class MarketSizeAgent(BaseAgent):
    # Specializes in market size analysis and forecasting 

    def __init__(self, api_client):
        super().__init__("MarketSizeAgent", api_client)

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market size for US ADAS semiconductors.
        
        Acceptance Criteria:
        - ≥3 independent credible sources
        - Explicit base year, projection year, and CAGR
        - Divergent forecasts surfaced with rationale
        """
        
        self.logger.info("Starting market size analysis...")
        
        system_prompt = """You are a market analysis expert specializing in automotive semiconductors.
        
Your task: Analyze the US ADAS semiconductor market size with rigorous sourcing.

Requirements:
1. Find at least 3 independent credible sources
2. Extract: base year, projection year, CAGR, market size figures
3. Break down by: camera, radar, sensor fusion/compute
4. Surface any divergent forecasts with explanations
5. Calculate confidence based on source agreement

Allowed sources:
- Financial research: JP Morgan, Goldman Sachs, Morgan Stanley
- Academic: IEEE, arXiv, ACM, SAE papers
- Industry: Company financial disclosures, investor presentations

Output format:
{
  "current_market_size_usd_millions": <number>,
  "base_year": <year>,
  "projected_market_size_usd_millions": <number>,
  "projection_year": <year>,
  "cagr_percent": <number>,
  "breakdown": {
    "camera": {"size_usd_millions": <number>, "percentage": <number>},
    "radar": {"size_usd_millions": <number>, "percentage": <number>},
    "sensor_fusion_compute": {"size_usd_millions": <number>, "percentage": <number>}
  },
  "sources": [
    {"name": "", "url": "", "figure": "", "year": ""}
  ],
  "divergent_forecasts": [
    {"source": "", "difference": "", "rationale": ""}
  ],
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        prompt = f"""Analyze the US ADAS semiconductor market size.

Context from previous agents:
{context.get('previous_findings', 'None yet - this is the first analysis')}

Focus areas:
- Camera processing semiconductors
- Radar processing semiconductors  
- Sensor fusion and AI compute chips

Provide comprehensive market sizing with all required fields."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            # Parse and validate response
            result = self._parse_market_data(response)
            
            # Validate acceptance criteria
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation failed: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            self.logger.info("Market size analysis complete")
            return result
            
        except Exception as e:
            self.logger.error(f"Market size analysis failed: {str(e)}")
            raise
    
    def _parse_market_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured market data."""
        import json
        
        try:
            # Extract JSON from response
            # LLM might wrap it in markdown code blocks
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse market data: {str(e)}")
            return {"error": "Parse failed", "raw_response": response}
    
    def _validate_acceptance_criteria(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate against agent's acceptance criteria."""
        
        validation = {
            'passed': True,
            'reasons': []
        }
        
        # Check for ≥3 sources
        sources = data.get('sources', [])
        if len(sources) < 3:
            validation['passed'] = False
            validation['reasons'].append(f"Only {len(sources)} sources (need ≥3)")
        
        # Check for required fields
        required_fields = ['base_year', 'projection_year', 'cagr_percent']
        for field in required_fields:
            if field not in data or data[field] is None:
                validation['passed'] = False
                validation['reasons'].append(f"Missing required field: {field}")
        
        # Check confidence level
        if data.get('confidence') not in ['High', 'Medium', 'Low']:
            validation['passed'] = False
            validation['reasons'].append("Invalid confidence level")
        
        return validation