"""Positioning & Messaging Agent - Creates go-to-market positioning."""

from typing import Dict, Any
from agents import BaseAgent
import json

class PositioningMessagingAgent(BaseAgent):
    """Creates positioning and messaging for identified opportunities."""
    
    def __init__(self, api_client):
        super().__init__("PositioningMessagingAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create positioning and messaging for top opportunities.
        
        Focus on:
        - Problem statement
        - Unique selling proposition (USP)
        - Competitive positioning
        - Value proposition for OEMs
        - Technical differentiation
        - Messaging pillars
        """
        
        self.logger.info("Creating positioning and messaging...")
        
        system_prompt = """You are a product marketing strategist for semiconductor companies.

Your task: Create compelling positioning and messaging for ADAS semiconductor opportunities.

For each opportunity, develop:

1. Problem Statement
   - Customer pain being solved
   - Market context
   - Urgency/timing

2. Solution Positioning
   - What the solution is
   - How it's different
   - Why now

3. Unique Selling Proposition (USP)
   - Core differentiation
   - Defensible advantages
   - Proof points

4. Competitive Positioning
   - Versus incumbent solutions
   - Versus alternative approaches
   - Competitive moats

5. Value Proposition
   - For OEMs (cost, performance, time-to-market)
   - For Tier-1s (integration, support, flexibility)
   - For end-users (safety, features, experience)

6. Technical Differentiation
   - Architecture advantages
   - Performance benefits
   - Integration benefits

7. Messaging Pillars
   - 3-5 key messages
   - Supporting proof points
   - Tailored by audience

Output format:
{
  "opportunities": [
    {
      "opportunity_name": "<From gap analysis>",
      "problem_statement": {
        "customer_pain": "<What problem we solve>",
        "market_context": "<Why it matters now>",
        "urgency": "<Why act now>"
      },
      "solution_positioning": {
        "what_it_is": "<One-sentence description>",
        "how_its_different": "<Key differentiation>",
        "why_now": "<Market timing>"
      },
      "usp": {
        "core_differentiation": "<Main USP>",
        "defensible_advantages": ["<advantage 1>", "<advantage 2>"],
        "proof_points": ["<proof 1>", "<proof 2>"]
      },
      "competitive_positioning": {
        "versus_incumbents": "<How we compare>",
        "versus_alternatives": "<Why we're better>",
        "competitive_moats": ["<moat 1>", "<moat 2>"]
      },
      "value_proposition": {
        "for_oems": ["<value 1>", "<value 2>"],
        "for_tier1s": ["<value 1>", "<value 2>"],
        "for_end_users": ["<value 1>", "<value 2>"]
      },
      "technical_differentiation": {
        "architecture": "<Arch advantage>",
        "performance": "<Performance benefit>",
        "integration": "<Integration benefit>"
      },
      "messaging_pillars": [
        {
          "pillar": "<Key message>",
          "supporting_points": ["<point 1>", "<point 2>"],
          "target_audience": "<OEM|Tier1|Technical|Executive>"
        }
      ],
      "elevator_pitch": "<30-second pitch>",
      "tagline_options": ["<option 1>", "<option 2>", "<option 3>"]
    }
  ],
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        # Get opportunities from gap analysis
        gap_data = context.get('gap_analysis_data', {})
        opportunities = gap_data.get('opportunities', [])
        
        if not opportunities:
            self.logger.warning("No opportunities found in gap analysis")
            return {
                "opportunities": [],
                "confidence": "Low",
                "confidence_rationale": "No opportunities to position"
            }
        
        prompt = f"""Create positioning and messaging for these ADAS semiconductor opportunities:

{json.dumps(opportunities, indent=2)}

Requirements:
1. Focus on top 3 opportunities
2. Create differentiated positioning for each
3. Tailor messaging to different audiences (OEM, Tier-1, technical)
4. Ensure positioning is defensible and evidence-based
5. Make messaging crisp and memorable

Develop compelling go-to-market positioning."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_positioning_data(response)
            
            positioned_opps = len(result.get('opportunities', []))
            self.logger.info(f"Created positioning for {positioned_opps} opportunities")
            return result
            
        except Exception as e:
            self.logger.error(f"Positioning/messaging failed: {str(e)}")
            raise
    
    def _parse_positioning_data(self, response: str) -> Dict[str, Any]:
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