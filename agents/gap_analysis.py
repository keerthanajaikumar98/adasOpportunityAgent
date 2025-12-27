"""Gap Analysis & Opportunity Agent - Identifies market opportunities."""

from typing import Dict, Any
from agents import BaseAgent
import json

class GapAnalysisAgent(BaseAgent):
    """Identifies gaps and surfaces product opportunities."""
    
    def __init__(self, api_client):
        super().__init__("GapAnalysisAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze gaps and identify top opportunities.
        
        Acceptance Criteria:
        - No opportunity without clearly articulated unmet need
        - ROI and timeline ranges (not point estimates)
        """
        
        self.logger.info("Analyzing market gaps and opportunities...")
        
        system_prompt = """You are a product strategy expert specializing in semiconductor opportunities.

Your task: Identify the top 3 ASIC/semiconductor opportunities in US ADAS market.

For each opportunity, analyze:
1. Unmet need (what's missing in the market)
2. Target customer segment
3. Technical gap (what current solutions can't do)
4. Proposed ASIC approach
5. Key differentiators
6. Market size potential
7. Time to execute (realistic range)
8. Estimated development cost vs ROI (ranges, not point estimates)
9. Best-positioned innovators (who could build this)

Requirements:
- Every opportunity must address a clear, validated unmet need
- Use market data and trends from previous analysis
- Provide realistic timelines (e.g., "18-24 months" not "20 months")
- Give cost/ROI as ranges (e.g., "$5-8M development" not "$6.5M")
- Consider technical feasibility, not just market desire

Output format:
{
  "opportunities": [
    {
      "name": "<Opportunity name>",
      "rank": 1,
      "unmet_need": "<Clear problem statement>",
      "target_segment": "<Camera/Radar/Fusion/AI Compute>",
      "technical_gap": "<What current solutions cannot do>",
      "asic_approach": {
        "compute_strategy": "<Specialized vs general purpose>",
        "power_target": "<Power budget>",
        "integration_level": "<Discrete vs integrated>",
        "cost_position": "<Premium vs cost-optimized>"
      },
      "key_differentiators": [
        "<Differentiator 1>",
        "<Differentiator 2>",
        "<Differentiator 3>"
      ],
      "market_size": {
        "addressable_market_usd_millions": <number>,
        "market_share_target_percent": <number>,
        "revenue_potential_range_usd_millions": "<range>"
      },
      "execution": {
        "time_to_market_months_range": "<range>",
        "development_cost_range_usd_millions": "<range>",
        "estimated_roi_range": "<range>",
        "risk_level": "Low|Medium|High"
      },
      "best_positioned_innovators": [
        "<Company/type 1>",
        "<Company/type 2>"
      ],
      "supporting_evidence": [
        {"source": "", "claim": ""}
      ]
    }
  ],
  "confidence": "High|Medium|Low",
  "confidence_rationale": "",
  "assumptions": [
    {"assumption": "", "risk_if_wrong": "", "validation_signal": ""}
  ]
}
"""
        
        # Gather context from previous agents
        market_data = context.get('market_size_data', {})
        trends_data = context.get('trends_simplification_data', {})
        competitive_data = context.get('competitive_landscape_data', {})
        pain_points = context.get('pain_point_extraction_data', {})
        bottlenecks = context.get('bottleneck_diagnosis_data', {})
        
        prompt = f"""Identify top 3 semiconductor opportunities in US ADAS market.

Market Context:
- Market Size: ${market_data.get('current_market_size_usd_millions', 'Unknown')}M
- Growth Rate: {market_data.get('cagr_percent', 'Unknown')}% CAGR
- Key Segments: Camera, Radar, Sensor Fusion/AI Compute

Trends Identified:
{json.dumps(trends_data.get('trends', [])[:5], indent=2) if trends_data else 'No trends data available'}

Pain Points:
{json.dumps(pain_points.get('pain_points', [])[:5], indent=2) if pain_points else 'No pain point data available'}

Technical Bottlenecks:
{json.dumps(bottlenecks.get('bottlenecks', [])[:3], indent=2) if bottlenecks else 'No bottleneck data available'}

Focus on opportunities where:
1. Customer pain is validated
2. Technical gap is clear
3. Market timing is right (not too early, not too late)
4. Differentiation is defensible

Provide realistic, evidence-based analysis."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_gap_data(response)
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation issues: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            self.logger.info(f"Identified {len(result.get('opportunities', []))} opportunities")
            return result
            
        except Exception as e:
            self.logger.error(f"Gap analysis failed: {str(e)}")
            raise
    
    def _parse_gap_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured gap analysis."""
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
        
        opportunities = data.get('opportunities', [])
        
        # Check opportunity count
        if len(opportunities) != 3:
            validation['passed'] = False
            validation['reasons'].append(f"Expected 3 opportunities, got {len(opportunities)}")
        
        # Check each opportunity
        for i, opp in enumerate(opportunities):
            # Must have unmet need
            if not opp.get('unmet_need'):
                validation['passed'] = False
                validation['reasons'].append(f"Opportunity {i+1} missing unmet need")
            
            # Must have ranges (not point estimates)
            execution = opp.get('execution', {})
            if 'range' not in str(execution.get('time_to_market_months_range', '')):
                validation['reasons'].append(f"Opportunity {i+1} should use time ranges")
            
            if 'range' not in str(execution.get('development_cost_range_usd_millions', '')):
                validation['reasons'].append(f"Opportunity {i+1} should use cost ranges")
        
        return validation