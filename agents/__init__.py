"""Base Agent functionality for ADAS Opportunity Mapping Agent."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAgent(ABC):
    def __init__(self, name: str, api_client):
        self.name = name 
        self.api_client = api_client 
        self.logger = logging.getLogger(name)
        self.confidence_level = "Unknown"

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
        
    def validate_sources(self, sources: List[str]) -> bool:
        """Validate that the sources meet quality criteria"""
        # TODO: Add implementation
        pass

    def calculate_confidence(self, data: Dict[str, Any]) -> str:
        """Calculate confidence level: High, Medium, or Low"""
        # TODO: Add implementation
        pass

