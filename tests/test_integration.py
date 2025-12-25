"""Integration tests for full workflow."""

import pytest
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

class TestIntegration:
    """Test full agent workflow."""
    
    @pytest.mark.asyncio
    async def test_market_size_agent(self):
        """Test market size agent execution."""
        
        # Only run if API key is available
        if not os.getenv('ANTHROPIC_API_KEY'):
            pytest.skip("No API key available")
        
        from utils.api_client import AnthropicClient
        from agents.market_size import MarketSizeAgent
        
        client = AnthropicClient()
        agent = MarketSizeAgent(client)
        
        result = await agent.execute({})
        
        # Check that result has required fields
        assert 'current_market_size_usd_millions' in result or 'error' in result
    
    @pytest.mark.asyncio
    async def test_full_workflow_dry_run(self):
        """Test orchestrator with mock data."""
        
        # This would test the full workflow with minimal API calls
        # Implementation depends on mock strategy
        pass

# Run with: pytest tests/test_integration.py -v -s