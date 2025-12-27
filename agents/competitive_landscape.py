"""Competitive Landscape Agent - Maps current ADAS semiconductor solutions."""

from typing import Dict, Any
from agents import BaseAgent
import json
# import os  <-- REMOVED: not needed in agent anymore

class CompetitiveLandscapeAgent(BaseAgent):
    """Analyzes current competitive landscape of ADAS semiconductors."""
    
    def __init__(self, api_client):
        super().__init__("CompetitiveLandscapeAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map competitive landscape with ≥80% coverage of top suppliers.
        
        Acceptance Criteria:
        - ≥80% coverage of top US-relevant suppliers
        - All undisclosed specs explicitly marked as "Unknown"
        """
        
        self.logger.info("Analyzing competitive landscape...")
        
        system_prompt = """You are a competitive intelligence analyst for automotive semiconductors.

Your task: Map the current competitive landscape of ADAS semiconductor solutions.

Focus on major suppliers and their products for:
- Camera processing chips
- Radar processing chips
- Sensor fusion / AI compute platforms

For each solution, document:
- Company name
- Product name/family
- Process node (nm) - mark "Unknown" if not disclosed
- Compute capability (TOPS) - mark "Unknown" if not disclosed
- Power consumption (W) - mark "Unknown" if not disclosed
- Target ADAS level (L1, L2, L2+, L3, etc.)
- Key features/differentiators
- Known OEM customers
- Approximate market position

CRITICAL: Mark all unknown specifications as "Unknown" - do NOT infer, estimate, or guess.

Major players to consider:
- NVIDIA (DRIVE platform)
- Qualcomm (Snapdragon Ride)
- Mobileye/Intel
- NXP
- Texas Instruments
- Renesas
- Tesla (in-house)
- AMD/Xilinx

Output format:
{
  "solutions": [
    {
      "company": "<Company name>",
      "product": "<Product name/family>",
      "category": "Camera|Radar|Fusion|AI Compute",
      "specifications": {
        "process_node_nm": "<number or 'Unknown'>",
        "compute_tops": "<number or 'Unknown'>",
        "power_consumption_w": "<number or 'Unknown'>",
        "memory_bandwidth": "<spec or 'Unknown'>"
      },
      "target_adas_level": "<L1/L2/L2+/L3/etc>",
      "key_features": ["<feature 1>", "<feature 2>"],
      "known_customers": ["<OEM 1>", "<OEM 2>"],
      "market_position": "<Leader|Challenger|Niche>",
      "strengths": ["<strength 1>", "<strength 2>"],
      "weaknesses": ["<weakness 1>", "<weakness 2>"],
      "source": "<Where this info came from>"
    }
  ],
  "market_coverage_percent": <percentage of major players covered>,
  "total_solutions_analyzed": <number>,
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        prompt = """Analyze the competitive landscape of ADAS semiconductors in the US market.

Requirements:
1. Cover at least 80% of major suppliers
2. Include camera, radar, and sensor fusion/AI compute
3. Mark unknown specs as "Unknown" - no guessing
4. Focus on solutions relevant to US ADAS market
5. Include both established players and emerging competitors

Provide comprehensive competitive intelligence."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_competitive_data(response)
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation issues: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            self.logger.info(f"Analyzed {len(result.get('solutions', []))} competitive solutions")
            return result
            
        except Exception as e:
            self.logger.error(f"Competitive analysis failed: {str(e)}")
            raise
    
    def _parse_competitive_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured competitive data."""
        # import json  <-- REMOVED: already imported at top
        
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
        
        # Check market coverage
        coverage = data.get('market_coverage_percent', 0)
        if coverage < 80:
            validation['passed'] = False
            validation['reasons'].append(f"Market coverage {coverage}% < 80% requirement")
        
        # Check for "Unknown" marking (not estimates)
        solutions = data.get('solutions', [])
        for i, solution in enumerate(solutions):
            specs = solution.get('specifications', {})
            # At least some specs should be Unknown (shows honesty)
            # If ALL specs are numbers, that's suspicious
            unknown_count = sum(1 for v in specs.values() if v == "Unknown")
            if unknown_count == 0 and len(specs) > 3:
                validation['reasons'].append(
                    f"Solution {i+1} ({solution.get('product')}): "
                    f"All specs disclosed - verify authenticity"
                )
        
        return validation

# ====== CHANGES HIGHLIGHTED ======
# 1. Removed all top-level code trying to write results to file:
#    - output_dir, output_file, json.dump(result, ...)
#    - This was causing NameError because `agent_name` and `result` were undefined at import.
# 2. Removed redundant `import os` and inner `import json` in _parse_competitive_data.
# 3. Now the agent **only returns results** via `execute()`.
# 4. File saving is handled in `main.py` (as discussed in previous steps).

