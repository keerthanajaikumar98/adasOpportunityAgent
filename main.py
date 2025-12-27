"""Main entry point for ADAS Opportunity Mapping Agent."""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import argparse
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.api_client import AnthropicClient
from utils.archive_manager import ArchiveManager
from orchestrator.master_agent import MasterOpportunityAgent

# Import all 10 agents
from agents.source_discovery import SourceDiscoveryAgent
from agents.market_size import MarketSizeAgent
from agents.trends_simplification import TrendsSimplificationAgent
from agents.competitive_landscape import CompetitiveLandscapeAgent
from agents.pain_point_extraction import PainPointExtractionAgent
from agents.compute_architecture import ComputeArchitectureAgent
from agents.bottleneck_diagnosis import BottleneckDiagnosisAgent
from agents.gap_analysis import GapAnalysisAgent
from agents.positioning_messaging import PositioningMessagingAgent
from agents.visualization_reporting import VisualizationReportingAgent

def setup_logging(log_level: str = 'INFO'):
    """Configure logging."""
    
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'aoma_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def save_result(agent_name: str, result: dict):
    """Save agent result to JSON file in outputs/reports/ folder."""
    
    output_dir = Path("outputs/reports")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"{agent_name}_result_{timestamp}.json"
    
    # Custom JSON encoder to handle datetime objects
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()  # Convert datetime to ISO format string
            return super().default(obj)
    
    with open(output_file, "w") as f:
        json.dump(result, f, indent=4, cls=DateTimeEncoder)
    
    logging.getLogger('main').info(f"✅ Result saved to {output_file}")

async def main():
    """Main execution function."""
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='ADAS Opportunity Mapping Agent')
    parser.add_argument('--agent', help='Run specific agent only')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    parser.add_argument('--no-archive', action='store_true', help='Skip archiving previous run')
    parser.add_argument('--keep-archives', type=int, default=10, help='Number of archives to keep (default: 10)')
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger('main')
    
    logger.info("=" * 70)
    logger.info("ADAS Opportunity Mapping Agent - Starting")
    logger.info("=" * 70)
    
    # Generate run timestamp (used for archiving)
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Archive previous run BEFORE starting new analysis
        if not args.no_archive and not args.agent:  # Only archive for full runs
            logger.info("\n📦 Archiving previous run...")
            archive_mgr = ArchiveManager()
            archived_folder = archive_mgr.archive_previous_run(run_timestamp)
            
            if archived_folder:
                logger.info(f"✅ Previous files archived to: {archived_folder}")
                
                # Clean old archives
                archive_mgr.clean_old_archives(keep_last_n=args.keep_archives)
            else:
                logger.info("ℹ️  No previous files to archive")
        
        # Initialize API client
        api_client = AnthropicClient()
        logger.info("✓ API client initialized")
        
        # Initialize all 10 agents
        agents = {
            'source_discovery': SourceDiscoveryAgent(api_client),
            'market_size': MarketSizeAgent(api_client),
            'trends_simplification': TrendsSimplificationAgent(api_client),
            'competitive_landscape': CompetitiveLandscapeAgent(api_client),
            'pain_point_extraction': PainPointExtractionAgent(api_client),
            'compute_architecture': ComputeArchitectureAgent(api_client),
            'bottleneck_diagnosis': BottleneckDiagnosisAgent(api_client),
            'gap_analysis': GapAnalysisAgent(api_client),
            'positioning_messaging': PositioningMessagingAgent(api_client),
            'visualization_reporting': VisualizationReportingAgent(),
        }
        logger.info(f"✓ Initialized {len(agents)} agents")
        
        # If specific agent requested, run only that
        if args.agent:
            if args.agent not in agents:
                logger.error(f"Agent '{args.agent}' not found")
                logger.info(f"Available agents: {', '.join(agents.keys())}")
                return
            
            logger.info(f"Running single agent: {args.agent}")
            agent = agents[args.agent]
            result = await agent.execute({})
            
            logger.info("Agent execution complete")
            logger.info(f"Result preview: {str(result)[:200]}...")
            
            # Save the result
            await save_result(args.agent, result)
            return
        
        # Otherwise run full orchestrated analysis
        master = MasterOpportunityAgent(api_client, agents)
        
        logger.info("\nStarting full opportunity mapping analysis...")
        results = await master.run_full_analysis()
        
        # Individual agent results are already saved by master_agent
        # No need to save full_analysis anymore
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("ANALYSIS COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Execution time: {results['metadata']['execution_time_seconds']:.2f}s")
        logger.info(f"Agents succeeded: {results['metadata']['agents_executed']}")
        logger.info(f"Agents failed: {results['metadata']['agents_failed']}")
        logger.info(f"Run timestamp: {run_timestamp}")
        
        # Print individual result files
        logger.info("\n📄 Individual Agent Results:")
        for agent_name in master.execution_order:
            if agent_name in results['results']:
                logger.info(f"  - {agent_name}_result_{run_timestamp}.json")
        
        # Show archive information
        logger.info("\n📚 Archive Management:")
        archive_mgr = ArchiveManager()
        archives = archive_mgr.list_archives()
        logger.info(f"  Total archived runs: {len(archives)}")
        logger.info(f"  Latest outputs in: outputs/reports/")
        if archives:
            logger.info(f"  Oldest archive: {archives[0]}")
            logger.info(f"  Newest archive: {archives[-1]}")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())