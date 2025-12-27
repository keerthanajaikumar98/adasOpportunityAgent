"""Scheduled analysis runner for GitHub Actions."""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.api_client import AnthropicClient
from orchestrator.master_agent import MasterOpportunityAgent

# Import all agents
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

def setup_logging():
    """Configure logging for scheduled run."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f'scheduled_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

async def main():
    """Run scheduled analysis."""
    setup_logging()
    logger = logging.getLogger('scheduled_analysis')
    
    logger.info("=" * 70)
    logger.info("SCHEDULED ADAS ANALYSIS - Starting")
    logger.info(f"Time: {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    try:
        # Load environment (API key from GitHub Actions secret)
        load_dotenv()
        
        # Initialize API client
        api_client = AnthropicClient()
        logger.info("✓ API client initialized")
        
        # Initialize all agents
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
        
        # Run full analysis
        master = MasterOpportunityAgent(api_client, agents)
        logger.info("Starting full opportunity mapping analysis...")
        
        results = await master.run_full_analysis()
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("SCHEDULED ANALYSIS COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Execution time: {results['metadata']['execution_time_seconds']:.2f}s")
        logger.info(f"Agents succeeded: {results['metadata']['agents_executed']}")
        logger.info(f"Agents failed: {results['metadata']['agents_failed']}")
        
        logger.info("\n📄 Results saved to outputs/reports/")
        logger.info("Dashboard will auto-update on next Streamlit Cloud refresh")
        
    except Exception as e:
        logger.error(f"Scheduled analysis failed: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())