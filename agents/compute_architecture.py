"""Compute & Architecture Agent - Analyzes ideal processing requirements."""

from typing import Dict, Any
from agents import BaseAgent
import json

class ComputeArchitectureAgent(BaseAgent):
    """Analyzes ideal compute and architecture requirements for ADAS."""
    
    def __init__(self, api_client):
        super().__init__("ComputeArchitectureAgent", api_client)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Define ideal processing requirements for ADAS workloads.
        
        Focus on:
        - Camera processing requirements
        - Radar processing requirements
        - Sensor fusion compute needs
        - AI/ML inference requirements
        """
        
        self.logger.info("Analyzing compute architecture requirements...")
        
        system_prompt = """You are a semiconductor architect specializing in automotive ADAS systems.

Your task: Define ideal processing requirements for ADAS workloads.

Analyze requirements for:
1. Camera Processing
   - Resolution and frame rates
   - Image processing pipelines
   - Object detection/classification
   - Compute requirements (TOPS)
   - Memory bandwidth needs
   - Power budget

2. Radar Processing
   - Signal processing requirements
   - FFT and beamforming needs
   - Point cloud processing
   - Compute requirements
   - Latency targets

3. Sensor Fusion
   - Multi-sensor data integration
   - Real-time processing needs
   - Compute requirements
   - Memory requirements

4. AI/ML Inference
   - Neural network requirements
   - Precision needs (INT8, FP16, etc.)
   - Model sizes and complexity
   - Inference latency targets
   - Power efficiency

Output format:
{
  "camera_processing": {
    "target_resolution": "<resolution>",
    "frame_rate_fps": <number>,
    "processing_pipeline": ["<step 1>", "<step 2>"],
    "compute_tops": "<range>",
    "memory_bandwidth_gbps": "<range>",
    "power_budget_w": "<range>",
    "key_algorithms": ["<algorithm 1>", "<algorithm 2>"]
  },
  "radar_processing": {
    "frequency_band": "<band>",
    "processing_requirements": ["<requirement 1>", "<requirement 2>"],
    "compute_tops": "<range>",
    "latency_target_ms": "<range>",
    "power_budget_w": "<range>"
  },
  "sensor_fusion": {
    "input_sources": ["<source 1>", "<source 2>"],
    "fusion_approach": "<centralized|distributed>",
    "compute_tops": "<range>",
    "memory_gb": "<range>",
    "real_time_requirements": "<description>",
    "power_budget_w": "<range>"
  },
  "ai_ml_inference": {
    "target_models": ["<model type 1>", "<model type 2>"],
    "precision_requirements": ["<INT8|FP16|FP32>"],
    "typical_model_size": "<range>",
    "inference_latency_ms": "<target>",
    "batch_processing": "<yes|no>",
    "compute_tops": "<range>",
    "power_efficiency_tops_per_watt": "<target>"
  },
  "architecture_recommendations": {
    "preferred_approach": "<description>",
    "key_trade_offs": ["<trade-off 1>", "<trade-off 2>"],
    "critical_bottlenecks": ["<bottleneck 1>", "<bottleneck 2>"]
  },
  "confidence": "High|Medium|Low",
  "confidence_rationale": ""
}
"""
        
        # Get context from previous agents
        trends_data = context.get('trends_simplification_data', {})
        pain_points = context.get('pain_point_extraction_data', {})
        
        prompt = f"""Define ideal processing requirements for US ADAS semiconductors.

Context from previous analysis:
Trends: {json.dumps(trends_data.get('trends', [])[:3], indent=2) if trends_data else 'Not available'}
Pain Points: {json.dumps(pain_points.get('pain_points', [])[:3], indent=2) if pain_points else 'Not available'}

Focus on L2+ and L3 ADAS requirements for:
- Multi-camera systems (4-8 cameras)
- Long-range and short-range radar
- Centralized or domain-based compute
- Real-time AI inference

Provide realistic, achievable requirements based on current technology trends."""
        
        try:
            response = await self.api_client.send_message(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=4096
            )
            
            result = self._parse_architecture_data(response)
            
            self.logger.info("Compute architecture analysis complete")
            return result
            
        except Exception as e:
            self.logger.error(f"Architecture analysis failed: {str(e)}")
            raise
    
    def _parse_architecture_data(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        
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