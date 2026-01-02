"""Pain Point Extraction Agent - Identifies customer pain points."""

from typing import Dict, Any, Optional
from agents import BaseAgent
import json

class PainPointExtractionAgent(BaseAgent):
    """Extracts and categorizes customer pain points.
    
    NOW ENHANCED WITH:
    - GitHub developer feedback (real issues from ADAS projects)
    - Actual bug reports and feature requests
    - Developer pain point frequency analysis
    """
    
    def __init__(self, api_client, github_client=None):
        super().__init__("PainPointExtractionAgent", api_client)
        self.github_client = github_client  # NEW: Add GitHub client
        
        if self.github_client:
            self.logger.info("✅ GitHub developer feedback available")
        else:
            self.logger.warning("⚠️ GitHub data unavailable - using market analysis only")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract customer pain points from ADAS ecosystem.
        
        NOW ENHANCED WITH GITHUB DATA:
        - Real developer pain points from open-source ADAS projects
        - Issue frequency and severity from actual bug reports
        - Community consensus on biggest challenges
        
        Acceptance Criteria:
        - Pain points linked to at least one credible source
        - Clear attribution (OEM vs Tier-1 vs silicon vendor vs developer)
        - GitHub evidence when available (issue count, labels)
        """
        
        self.logger.info("Extracting customer pain points...")
        
        # NEW: Get GitHub developer pain points
        github_data = await self._get_github_pain_points()
        
        system_prompt = """You are a customer insights analyst for automotive semiconductors.

Your task: Identify and categorize pain points in the ADAS semiconductor ecosystem.

Pain point categories:
1. Technical (performance, power, integration)
2. Business (cost, time-to-market, supply chain)
3. Operational (support, tools, documentation)
4. Strategic (future-proofing, scalability, vendor lock-in)

For each pain point, identify:
- Who experiences it (OEMs, Tier-1s, silicon vendors, developers)
- What the pain is
- Why it matters (impact)
- Supporting evidence (source + GitHub issues if available)

GITHUB DEVELOPER FEEDBACK:
When GitHub issue data is available, use it to:
1. Validate market-reported pain points with real developer complaints
2. Quantify severity by issue frequency (>20 issues = High severity)
3. Identify technical details from issue descriptions
4. Add evidence from actual bug reports

Output format:
{
  "pain_points": [
    {
      "category": "Technical|Business|Operational|Strategic",
      "title": "<Short description>",
      "description": "<Detailed explanation>",
      "impacted_stakeholders": ["OEM|Tier1|SiliconVendor|Developer"],  // Added Developer
      "severity": "High|Medium|Low",
      "impact": "<Business impact>",
      "current_workarounds": ["<Workaround 1>", "<Workaround 2>"],
      "evidence": {
        "source_type": "academic|financial|industry|oem_statement|github_issues",  // NEW: github_issues
        "source_name": "<Source>",
        "url": "<URL if available>",
        "key_quote": "<Supporting quote or data>",
        "github_issue_count": <number>,  // NEW: Number of related GitHub issues
        "developer_priority": "High|Medium|Low"  // NEW: Based on GitHub reactions/comments
      },
      "related_to": ["<Related pain point>"]
    }
  ],
  "github_insights": {  // NEW section
    "data_available": true|false,
    "repos_analyzed": ["<repo1>", "<repo2>"],
    "total_issues_analyzed": <number>,
    "top_developer_pain_points": [
      {
        "keyword": "<pain point keyword>",
        "occurrences": <number>,
        "severity": "High|Medium|Low"
      }
    ]
  },
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
        
        prompt = self._build_prompt(github_data)
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_pain_point_data(response)
            
            # Add metadata about data sources
            result['data_sources'] = {
                'market_analysis': 'available',
                'github_issues': 'github_api' if github_data else 'unavailable'
            }
            
            validation = self._validate_acceptance_criteria(result)
            
            if not validation['passed']:
                self.logger.warning(f"Validation issues: {validation['reasons']}")
                result['validation_warnings'] = validation['reasons']
            
            total_points = len(result.get('pain_points', []))
            self.logger.info(f"Identified {total_points} pain points")
            
            if github_data:
                github_total = github_data.get('total_issues_analyzed', 0)
                self.logger.info(f"Enhanced with {github_total} GitHub issues")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Pain point extraction failed: {str(e)}")
            raise
    
    async def _get_github_pain_points(self) -> Optional[Dict[str, Any]]:
        """Get developer pain points from GitHub issues"""
        
        if not self.github_client:
            return None
        
        try:
            self.logger.info("Fetching GitHub developer pain points...")
            
            # Analyze pain points from major open-source ADAS projects
            pain_points = self.github_client.analyze_pain_points(
                repos=[
                    "autoware/autoware",           # Open-source ADAS stack
                    "commaai/openpilot",           # Open-source driver assistance
                    "ApolloAuto/apollo"            # Baidu's autonomous driving platform
                ],
                keywords=[
                    "latency",                     # Performance issues
                    "performance",                 # General performance
                    "memory leak",                 # Memory management
                    "sensor fusion",               # Multi-sensor integration
                    "calibration",                 # Sensor calibration
                    "thermal",                     # Thermal issues
                    "power consumption",           # Power efficiency
                    "GPU",                         # GPU-related issues
                    "inference",                   # AI inference problems
                    "synchronization"              # Timing/sync issues
                ],
                time_range="6months"              # Last 6 months of issues
            )
            
            # Count total issues analyzed
            total_issues = sum(
                data.get('occurrences', 0) 
                for data in pain_points.get('pain_points', {}).values()
            )
            
            pain_points['total_issues_analyzed'] = total_issues
            pain_points['repos_analyzed'] = [
                "autoware/autoware",
                "commaai/openpilot", 
                "ApolloAuto/apollo"
            ]
            
            self.logger.info(f"✅ Analyzed {total_issues} GitHub issues across 3 ADAS projects")
            
            return pain_points
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch GitHub data: {str(e)}")
            return None
    
    def _build_prompt(self, github_data: Optional[Dict]) -> str:
        """Build prompt with optional GitHub data"""
        
        base_prompt = """Identify pain points in the US ADAS semiconductor market.

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
        
        if github_data and github_data.get('pain_points'):
            github_section = f"""

DEVELOPER PAIN POINTS (from GitHub Issues - Real ADAS Projects):
Analyzed {github_data.get('total_issues_analyzed', 0)} issues from:
{', '.join(github_data.get('repos_analyzed', []))}

Top Developer Complaints (by frequency):
"""
            # Add top pain points from GitHub
            for keyword, data in sorted(
                github_data.get('pain_points', {}).items(),
                key=lambda x: x[1].get('occurrences', 0),
                reverse=True
            )[:10]:  # Top 10
                occurrences = data.get('occurrences', 0)
                severity = "High" if occurrences > 20 else "Medium" if occurrences > 10 else "Low"
                
                github_section += f"\n- {keyword}: {occurrences} issues (Severity: {severity})"
                
                # Add example issue if available
                examples = data.get('example_issues', [])
                if examples:
                    github_section += f"\n  Example: \"{examples[0].get('title', 'N/A')}\""
            
            github_section += """

Use this GitHub data to:
1. Validate and quantify pain points with real developer feedback
2. Add technical details from actual bug reports
3. Identify pain points that affect real-world implementations
4. Cross-reference market analysis with hands-on developer experience

For pain points with GitHub evidence, include:
- Issue count (shows how widespread the problem is)
- Example issue titles (shows real-world manifestations)
- Severity rating based on frequency
"""
            
            return base_prompt + github_section
        
        else:
            return base_prompt
    
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
            
            # NEW: If GitHub data available, check for GitHub evidence
            if data.get('data_sources', {}).get('github_issues') == 'github_api':
                evidence = point.get('evidence', {})
                if evidence.get('source_type') == 'github_issues' and not evidence.get('github_issue_count'):
                    validation['reasons'].append(f"Pain point {i+1} using GitHub evidence but missing issue count")
        
        return validation