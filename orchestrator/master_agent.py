"""Master orchestration agent for ADAS Opportunity Mapping."""

import logging
from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class MasterOpportunityAgent:
    """Orchestrates the execution of all opportunity mapping agents."""
    
    def __init__(self, api_client, agents: Dict[str, Any]):
        """
        Initialize the master agent.
        
        Args:
            api_client: Anthropic API client
            agents: Dictionary of agent instances
        """
        self.api_client = api_client
        self.agents = agents
        
        # Define execution order with dependencies
        self.execution_order = [
            'source_discovery',
            'market_size',
            'trends_simplification',
            'competitive_landscape',
            'pain_point_extraction',
            'compute_architecture',
            'bottleneck_diagnosis',
            'gap_analysis',
            'positioning_messaging',
            'visualization_reporting'
        ]
    
    def _save_agent_result(self, agent_name: str, result: dict, timestamp: str):
        """Save individual agent result to separate file."""
        output_dir = Path("outputs/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{agent_name}_result_{timestamp}.json"
        
        # Custom JSON encoder for datetime
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, cls=DateTimeEncoder)
        
        logger.info(f"✅ Saved {agent_name} result to {output_file}")
    
    async def run_full_analysis(self) -> Dict[str, Any]:
        """
        Execute all agents in the correct order.
        
        Returns:
            Dict containing all agent results and metadata
        """
        logger.info("Starting full opportunity mapping analysis...")
        
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        
        context = {
            'start_time': start_time,
            'timestamp': timestamp
        }
        
        results = {}
        execution_log = []
        agents_executed = 0
        agents_failed = 0
        
        for agent_name in self.execution_order:
            if agent_name not in self.agents:
                logger.warning(f"Agent '{agent_name}' not found in initialized agents")
                continue
            
            logger.info(f"Executing agent: {agent_name}")
            
            try:
                agent = self.agents[agent_name]
                
                # Execute agent with current context
                agent_result = await agent.execute(context)
                
                # Store result in context for next agents
                context[f'{agent_name}_data'] = agent_result
                results[agent_name] = agent_result
                
                # Save individual agent result immediately
                self._save_agent_result(agent_name, agent_result, timestamp)
                
                # Log execution
                execution_log.append({
                    'agent': agent_name,
                    'timestamp': datetime.now(),
                    'success': True,
                    'confidence': agent_result.get('confidence', 'Unknown')
                })
                
                agents_executed += 1
                logger.info(f"✓ {agent_name} completed successfully")
                
            except Exception as e:
                logger.error(f"✗ {agent_name} failed: {str(e)}", exc_info=True)
                execution_log.append({
                    'agent': agent_name,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': str(e)
                })
                agents_failed += 1
                
                # Continue with next agent even if one fails
                context[f'{agent_name}_data'] = {}
                results[agent_name] = {'error': str(e)}
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Compile metadata
        metadata = {
            'execution_time_seconds': execution_time,
            'start_time': start_time,
            'end_time': end_time,
            'agents_executed': agents_executed,
            'agents_failed': agents_failed
        }
        
        # Save summary file with metadata only
        summary = {
            'metadata': metadata,
            'execution_log': execution_log,
            'results_files': {
                agent_name: f"{agent_name}_result_{timestamp}.json"
                for agent_name in self.execution_order
                if agent_name in results
            }
        }
        
        summary_file = Path("outputs/reports") / f"execution_summary_{timestamp}.json"
        
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, cls=DateTimeEncoder)
        
        logger.info(f"✅ Execution summary saved to {summary_file}")
        
        # Return full analysis for backward compatibility
        full_analysis = {
            'metadata': metadata,
            'results': results,
            'execution_log': execution_log
        }
        
        return full_analysis