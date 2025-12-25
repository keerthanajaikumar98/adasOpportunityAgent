"""Master Opportunity Agent - Orchestrates all specialized agents."""

import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio

class MasterOpportunityAgent:
    """Orchestrates execution of all specialized agents."""
    
    def __init__(self, api_client, agents: Dict[str, Any]):
        self.api_client = api_client
        self.agents = agents
        self.logger = logging.getLogger('MasterAgent')
        self.execution_log = []
    
    async def run_full_analysis(self) -> Dict[str, Any]:
        """Execute complete opportunity mapping workflow."""
        
        self.logger.info("=" * 60)
        self.logger.info("Starting ADAS Opportunity Mapping Analysis")
        self.logger.info("=" * 60)
        
        start_time = datetime.now()
        context = {'start_time': start_time}
        results = {}
        
        # Execute agents in sequence
        execution_order = [
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
        
        for agent_name in execution_order:
            try:
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"Executing: {agent_name}")
                self.logger.info(f"{'='*60}")
                
                agent = self.agents.get(agent_name)
                if not agent:
                    self.logger.warning(f"Agent {agent_name} not found, skipping...")
                    continue
                
                # Execute agent with current context
                agent_result = await agent.execute(context)
                
                # Store result
                results[agent_name] = agent_result
                
                # Update context for next agent
                context[f'{agent_name}_data'] = agent_result
                
                # Log execution
                self.execution_log.append({
                    'agent': agent_name,
                    'timestamp': datetime.now(),
                    'success': True,
                    'confidence': agent_result.get('confidence', 'Unknown')
                })
                
                self.logger.info(f"✓ {agent_name} completed successfully")
                
            except Exception as e:
                self.logger.error(f"✗ {agent_name} failed: {str(e)}")
                self.execution_log.append({
                    'agent': agent_name,
                    'timestamp': datetime.now(),
                    'success': False,
                    'error': str(e)
                })
                # Continue with next agent even if one fails
                continue
        
        # Calculate total execution time
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Compile final report
        final_report = {
            'metadata': {
                'execution_time_seconds': execution_time,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'agents_executed': len([log for log in self.execution_log if log['success']]),
                'agents_failed': len([log for log in self.execution_log if not log['success']])
            },
            'results': results,
            'execution_log': self.execution_log
        }
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Analysis Complete!")
        self.logger.info(f"Total time: {execution_time:.2f} seconds")
        self.logger.info(f"Success rate: {final_report['metadata']['agents_executed']}/{len(execution_order)}")
        self.logger.info(f"{'='*60}\n")
        
        return final_report