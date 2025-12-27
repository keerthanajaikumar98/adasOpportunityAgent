"""Bottleneck Diagnosis Agent - Identifies technical bottlenecks."""

from typing import Dict, Any
from agents import BaseAgent
import json

class BottleneckDiagnosisAgent(BaseAgent):
    """Diagnoses technical bottlenecks in current ADAS solutions."""
    
    def __init__(self, api_client):
        super().__init__("BottleneckDiagnosisAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify technical bottlenecks preventing optimal ADAS performance.
        
        Acceptance Criteria:
        - Each bottleneck has root cause analysis
        - Explanation of why current solutions fail
        """
        
        self.logger.info("Diagnosing technical bottlenecks...")
        
        system_prompt = """You are a systems engineer specializing in automotive semiconductor debugging.

Your task: Identify technical bottlenecks in current ADAS semiconductor solutions.

Bottleneck categories:
1. Compute/Performance
   - Insufficient processing power
   - Inefficient architectures
   - Poor parallelization

2. Power/Thermal
   - Excessive power consumption
   - Thermal throttling
   - Power delivery limitations

3. Memory/Bandwidth
   - Memory capacity constraints
   - Bandwidth bottlenecks
   - Latency issues

4. Integration/System
   - Poor sensor integration
   - Communication bottlenecks
   - Software/hardware mismatch

5. Cost/Economics
   - Prohibitive silicon costs
   - Yield issues
   - Economic scalability

For each bottleneck:
- Name and category
- Root cause (why it exists)
- Impact on system performance
- Why current solutions fail to address it
- Difficulty of solving (technical, economic)
- Potential solution approaches

Output format:
{
  "bottlenecks": [
    {
      "name": "<Bottleneck name>",
      "category": "compute|power|memory|integration|cost",
      "severity": "Critical|High|Medium|Low",
      "description": "<What the bottleneck is>",
      "root_cause": "<Why it exists>",
      "impact": "<Effect on ADAS performance>",
      "affected_workloads": ["<workload 1>", "<workload 2>"],
      "why_current_solutions_fail": "<Explanation>",
      "difficulty_to_solve": {
        "technical": "High|Medium|Low",
        "economic": "High|Medium|Low",
        "time_to_solution": "<estimate>"
      },
      "potential_approaches": ["<approach 1>", "<approach 2>"],
      "evidence": {
        "source": "<Source>",
        "supporting_data": "<Data or quote>"
      }
    }
  ],
  "critical_path_bottlenecks": ["<bottleneck 1>", "<bottleneck 2>"],
  "quick_wins": ["<bottleneck that's easier to solve>"],
  "long_term_challenges": ["<fundamental bottleneck>"],
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        # Get context
        competitive_data = context.get('competitive_landscape_data', {})
        pain_points = context.get('pain_point_extraction_data', {})
        architecture = context.get('compute_architecture_data', {})
        
        prompt = f"""Diagnose technical bottlenecks in US ADAS semiconductor solutions.

Competitive landscape insights:
{json.dumps(competitive_data.get('solutions', [])[:3], indent=2) if competitive_data else 'Not available'}

Known pain points:
{json.dumps(pain_points.get('pain_points', [])[:3], indent=2) if pain_points else 'Not available'}

Ideal requirements:
{json.dumps(architecture, indent=2)[:500] if architecture else 'Not available'}

Focus on:
1. Bottlenecks preventing L2+ to L3 transition
2. Camera/radar processing limitations
3. AI inference efficiency gaps
4. Power/thermal constraints
5. Cost barriers to adoption

Identify root causes and explain why current approaches fall short."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_bottleneck_data(response)
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation issues: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            total_bottlenecks = len(result.get('bottlenecks', []))
            self.logger.info(f"Identified {total_bottlenecks} technical bottlenecks")
            return result
            
        except Exception as e:
            self.logger.error(f"Bottleneck diagnosis failed: {str(e)}")
            raise
    
    def _parse_bottleneck_data(self, response: str) -> Dict[str, Any]:
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
        
        bottlenecks = data.get('bottlenecks', [])
        
        for i, bottleneck in enumerate(bottlenecks):
            # Must have root cause
            if not bottleneck.get('root_cause'):
                validation['passed'] = False
                validation['reasons'].append(f"Bottleneck {i+1} missing root cause")
            
            # Must explain why current solutions fail
            if not bottleneck.get('why_current_solutions_fail'):
                validation['passed'] = False
                validation['reasons'].append(f"Bottleneck {i+1} missing failure explanation")
        
        return validation