# Anthropic API Client for Agent Communication 

import os 
from anthropic import Anthropic
import logging
from typing import List, Dict, Any 
from dotenv import load_dotenv

load_dotenv()

class AnthropicClient: 
    # Wrapper for Anthropic API calls 

    def __init__(self): 
        api_key=os.getenv('ANTHROPIC_API_KEY')
        if not api_key: 
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv('ANTHROPIC_MODEL')
        self.logger = logging.getLogger('AnthropicClient')

    async def send_message(
        self, 
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096
    )  -> str: 
        # Try to send a message to Claude and get a response back

        try:
            messages = [{"role":"user", "content" : prompt}]

            response = self.client.messages.create(
                model = self.model,
                max_tokens = max_tokens,
                system = system_prompt if system_prompt else None, 
                messages = messages
            )

            return response.content[0].text
        
        except Exception as e: 
            self.logger.error(f"API call failed: {str(e)}")
            raise

    async def send_with_tools(
        self, 
        prompt: str, 
        tools: List[Dict[str, Any]],
        system_prompt: str = ""
    ) -> Dict[str, Any]:
        # Sending message with tool use capability 

        try:
            response=self.client.messages.create(
                model=self.model,
                max_tokens = 4096,
                system = system_prompt if system_prompt else None, 
                messages=[{"role":"user","content":prompt}],
                tools=tools
            )

            return response

        except Exception as e:
            self.logger.error(f"Tool-enabled API call failed: {str(e)}")
            raise