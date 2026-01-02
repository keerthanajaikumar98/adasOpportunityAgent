"""Master orchestration agent for ADAS Opportunity Mapping."""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class MasterOpportunityAgent:
    """Orchestrates the execution of all opportunity mapping agents.
    
    NOW ENHANCED WITH:
    - MCP client integration (USPTO, GitHub, Semantic Scholar)
    - API usage tracking and reporting
    - Fallback handling when APIs unavailable
    """
    
    def __init__(self, api_client, agents: Dict[str, Any], mcp_clients: Optional[Dict[str, Any]] = None):
        """
        Initialize the master agent.
        
        Args:
            api_client: Anthropic API client
            agents: Dictionary of agent instances
            mcp_clients: Optional dictionary of MCP clients (uspto, github, semantic_scholar)
        """
        self.api_client = api_client
        self.agents = agents
        self.mcp_clients = mcp_clients or {}
        
        # Log MCP client availability
        self._log_mcp_status()
        
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
    
    def _log_mcp_status(self):
        """Log which MCP clients are available"""
        logger.info("=" * 80)
        logger.info("MCP CLIENT STATUS")
        logger.info("=" * 80)
        
        if self.mcp_clients.get('uspto'):
            logger.info("✅ USPTO Patent API - Active")
        else:
            logger.warning("⚠️  USPTO Patent API - Unavailable (using market data only)")
        
        if self.mcp_clients.get('github'):
            logger.info("✅ GitHub API - Active")
        else:
            logger.warning("⚠️  GitHub API - Unavailable (using market analysis only)")
        
        if self.mcp_clients.get('semantic_scholar'):
            logger.info("✅ Semantic Scholar API - Active")
        else:
            logger.warning("⚠️  Semantic Scholar API - Unavailable (using web search only)")
        
        logger.info("=" * 80 + "\n")
    
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
        logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        start_time = datetime.now()
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        
        context = {
            'start_time': start_time,
            'timestamp': timestamp,
            'mcp_clients': self.mcp_clients  # Pass MCP clients to context
        }
        
        results = {}
        execution_log = []
        agents_executed = 0
        agents_failed = 0
        api_usage_stats = {
            'uspto_calls': 0,
            'github_calls': 0,
            'semantic_scholar_calls': 0
        }
        
        for agent_name in self.execution_order:
            if agent_name not in self.agents:
                logger.warning(f"Agent '{agent_name}' not found in initialized agents")
                continue
            
            logger.info("=" * 80)
            logger.info(f"EXECUTING: {agent_name}")
            logger.info("=" * 80)
            
            try:
                agent = self.agents[agent_name]
                
                # Execute agent with current context
                agent_result = await agent.execute(context)
                
                # Track API usage if available
                data_sources = agent_result.get('data_sources', {})
                if data_sources.get('patent_data') == 'uspto_api':
                    api_usage_stats['uspto_calls'] += 1
                    logger.info("  📊 Used USPTO Patent API")
                
                if data_sources.get('github_issues') == 'github_api':
                    api_usage_stats['github_calls'] += 1
                    logger.info("  📊 Used GitHub API")
                
                if data_sources.get('academic_papers') == 'semantic_scholar_api':
                    api_usage_stats['semantic_scholar_calls'] += 1
                    logger.info("  📊 Used Semantic Scholar API")
                
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
                    'confidence': agent_result.get('confidence', 'Unknown'),
                    'data_sources': data_sources
                })
                
                agents_executed += 1
                logger.info(f"✅ {agent_name} completed successfully")
                logger.info(f"   Confidence: {agent_result.get('confidence', 'Unknown')}\n")
                
            except Exception as e:
                logger.error(f"❌ {agent_name} failed: {str(e)}", exc_info=True)
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
        
        # Compile metadata with API usage
        metadata = {
            'execution_time_seconds': execution_time,
            'execution_time_formatted': f"{int(execution_time // 60)}m {int(execution_time % 60)}s",
            'start_time': start_time,
            'end_time': end_time,
            'agents_executed': agents_executed,
            'agents_failed': agents_failed,
            'apis_available': {
                'uspto': self.mcp_clients.get('uspto') is not None,
                'github': self.mcp_clients.get('github') is not None,
                'semantic_scholar': self.mcp_clients.get('semantic_scholar') is not None
            },
            'api_usage_stats': api_usage_stats
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
        
        logger.info("\n" + "=" * 80)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"⏱️  Execution Time: {metadata['execution_time_formatted']}")
        logger.info(f"✅ Agents Executed: {agents_executed}")
        logger.info(f"❌ Agents Failed: {agents_failed}")
        logger.info(f"\n📊 API Usage:")
        logger.info(f"   USPTO calls: {api_usage_stats['uspto_calls']}")
        logger.info(f"   GitHub calls: {api_usage_stats['github_calls']}")
        logger.info(f"   Semantic Scholar calls: {api_usage_stats['semantic_scholar_calls']}")
        logger.info(f"\n📄 Summary saved to: {summary_file}")
        logger.info("=" * 80 + "\n")
        
        # Return full analysis for backward compatibility
        full_analysis = {
            'metadata': metadata,
            'results': results,
            'execution_log': execution_log
        }
        
        return full_analysis