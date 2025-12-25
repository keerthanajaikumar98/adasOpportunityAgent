"""Base Agent functionality for ADAS Opportunity Mapping Agent."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

class BaseAgent(ABC):
    # Base Class for all specialized agents

    def __init__(self, name: str, api_client):
        self.name = name 
        self.api_client = api_client 
        self.logger = logging.getLogger(name)
        self.confidence_level = "Unknown"

        @abstractmethodasync def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # Execute the agent's main task
            pass
        
        def validate_sources(self, sources: List[str]) -> bool:
            # Validate that the sources meet my quality criteria 
            # HAve to add implementation 
            pass

        def calculate_confidence(self, data: Dict[str, Any]) -> str:
            # Calculate confidence level: High, Medium or Low
            #Have to add implementation
            pass