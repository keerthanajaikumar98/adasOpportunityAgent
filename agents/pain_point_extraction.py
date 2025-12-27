"""Pain Point Extraction Agent - Identifies customer pain points."""

from typing import Dict, Any
from agents import BaseAgent
import json

class PainPointExtractionAgent(BaseAgent):
    """Extracts and categorizes customer pain points."""
    
    def __init__(self, api_client):
        super().__init__("PainPointExtractionAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract customer pain points from ADAS ecosystem.
        
        Acceptance Criteria:
        - Pain points linked to at least one credible source
        - Clear attribution (OEM vs Tier-1 vs silicon vendor)
        """
        
        self.logger.info("Extracting customer pain points...")
        
        system_prompt = """You are a customer insights analyst for automotive semiconductors.

Your task: Identify and categorize pain points in the ADAS semiconductor ecosystem.

Pain point categories:
1. Technical (performance, power, integration)
2. Business (cost, time-to-market, supply chain)
3. Operational (support, tools, documentation)
4. Strategic (future-proofing, scalability, vendor lock-in)

For each pain point, identify:
- Who experiences it (OEMs, Tier-1s, silicon vendors)
- What the pain is
- Why it matters (impact)
- Supporting evidence (source)

Output format:
{
  "pain_points": [
    {
      "category": "Technical|Business|Operational|Strategic",
      "title": "<Short description>",
      "description": "<Detailed explanation>",
      "impacted_stakeholders": ["OEM|Tier1|SiliconVendor"],
      "severity": "High|Medium|Low",
      "impact": "<Business impact>",
      "current_workarounds": ["<Workaround 1>", "<Workaround 2>"],
      "evidence": {
        "source_type": "academic|financial|industry|oem_statement",
        "source_name": "<Source>",
        "url": "<URL if available>",
        "key_quote": "<Supporting quote or data>"
      },
      "related_to": ["<Related pain point>"]
    }
  ],
  "summary": {
    "total_pain_points": <number>,
    "by_category": {
      "technical": <number>,
      "business": <number>,
      "operational": <number>,
      "strategic": <number>
    },
    "top_3_critical": [
      "<Pain point 1>",
      "<Pain point 2>",
      "<Pain point 3>"
    ]
  },
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        prompt = """Identify pain points in the US ADAS semiconductor market.

Focus areas:
1. Camera processing challenges
2. Radar processing limitations
3. Sensor fusion complexity
4. AI/ML compute requirements
5. Power/thermal constraints
6. Cost pressures
7. Time-to-market demands
8. Integration difficulties

For each pain point:
- Cite evidence (OEM statements, Tier-1 presentations, research papers)
- Attribute to specific stakeholder type
- Explain business impact
- Note any current workarounds

Prioritize pain points that:
- Are widely experienced
- Have significant business impact
- Currently lack good solutions
- Represent opportunity for innovation"""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_pain_point_data(response)
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation issues: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            total_points = len(result.get('pain_points', []))
            self.logger.info(f"Identified {total_points} pain points")
            return result
            
        except Exception as e:
            self.logger.error(f"Pain point extraction failed: {str(e)}")
            raise
    
    def _parse_pain_point_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
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
        """Validate acceptance criteria."""
        
        validation = {'passed': True, 'reasons': []}
        
        pain_points = data.get('pain_points', [])
        
        # Check each pain point has evidence
        for i, point in enumerate(pain_points):
            if not point.get('evidence'):
                validation['passed'] = False
                validation['reasons'].append(f"Pain point {i+1} missing evidence")
            
            # Check stakeholder attribution
            if not point.get('impacted_stakeholders'):
                validation['passed'] = False
                validation['reasons'].append(f"Pain point {i+1} missing stakeholder attribution")
        
        return validation