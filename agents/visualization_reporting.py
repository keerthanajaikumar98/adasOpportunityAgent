"""Visualization & Reporting Agent - Generates visual outputs."""

from typing import Dict, Any, List
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import json

class VisualizationReportingAgent:
    """Generates visual reports and documents."""
    
    def __init__(self, output_dir: str = './outputs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create subdirectories
        (self.output_dir / 'reports').mkdir(exist_ok=True)
        (self.output_dir / 'visualizations').mkdir(exist_ok=True)
        (self.output_dir / 'archives').mkdir(exist_ok=True)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate all visual outputs."""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        outputs = {}
        
        # 1. Market Size Visualization
        if 'market_size_data' in context:
            market_viz_path = self._create_market_size_viz(
                context['market_size_data'],
                timestamp
            )
            outputs['market_size_viz'] = market_viz_path
        
        # 2. Trends Document
        if 'trends_simplification_data' in context:
            trends_doc_path = self._create_trends_document(
                context['trends_simplification_data'],
                timestamp
            )
            outputs['trends_document'] = trends_doc_path
        
        # 3. Competitive Landscape
        if 'competitive_landscape_data' in context:
            comp_viz_path = self._create_competitive_landscape(
                context['competitive_landscape_data'],
                timestamp
            )
            outputs['competitive_landscape'] = comp_viz_path
        
        # 4. Gap Analysis Report
        if 'gap_analysis_data' in context:
            gap_report_path = self._create_gap_analysis_report(
                context['gap_analysis_data'],
                timestamp
            )
            outputs['gap_analysis_report'] = gap_report_path
        
        # 5. Executive Summary
        exec_summary_path = self._create_executive_summary(
            context,
            timestamp
        )
        outputs['executive_summary'] = exec_summary_path
        
        return {
            'outputs': outputs,
            'timestamp': timestamp
        }
    
    def _create_market_size_viz(self, data: Dict, timestamp: str) -> str:
        """Create market size visualization."""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Market size over time
        years = [data.get('base_year', 2024), data.get('projection_year', 2030)]
        sizes = [
            data.get('current_market_size_usd_millions', 0),
            data.get('projected_market_size_usd_millions', 0)
        ]
        
        ax1.plot(years, sizes, marker='o', linewidth=2, markersize=10)
        ax1.set_title('US ADAS Semiconductor Market Size', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Market Size (USD Millions)')
        ax1.grid(True, alpha=0.3)
        
        # Add CAGR annotation
        cagr = data.get('cagr_percent', 0)
        ax1.text(
            0.5, 0.95,
            f'CAGR: {cagr:.1f}%',
            transform=ax1.transAxes,
            ha='center',
            va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        
        # Market breakdown by segment
        breakdown = data.get('breakdown', {})
        if breakdown:
            segments = []
            percentages = []
            
            for segment, values in breakdown.items():
                segments.append(segment.replace('_', ' ').title())
                percentages.append(values.get('percentage', 0))
            
            colors = sns.color_palette('Set2', len(segments))
            ax2.pie(percentages, labels=segments, autopct='%1.1f%%', colors=colors)
            ax2.set_title('Market Breakdown by Segment', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        filename = f'market_size_{timestamp}.png'
        filepath = self.output_dir / 'visualizations' / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _create_trends_document(self, data: Dict, timestamp: str) -> str:
        """Create trends document (simplified version)."""
        
        filename = f'trends_analysis_{timestamp}.json'
        filepath = self.output_dir / 'reports' / filename
        
        # Create a formatted trends report
        report = {
            'title': 'Key ADAS Semiconductor Trends',
            'generated_at': datetime.now().isoformat(),
            'trends': data.get('trends', []),
            'acronyms': data.get('acronyms_defined', {}),
            'confidence': data.get('confidence', 'Unknown')
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(filepath)
    
    def _create_competitive_landscape(self, data: Dict, timestamp: str) -> str:
        """Create competitive landscape visualization."""
        
        # This would create a table or chart of competitors
        # Simplified version here
        filename = f'competitive_landscape_{timestamp}.json'
        filepath = self.output_dir / 'reports' / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(filepath)
    
    def _create_gap_analysis_report(self, data: Dict, timestamp: str) -> str:
        """Create gap analysis report."""
        
        filename = f'gap_analysis_{timestamp}.json'
        filepath = self.output_dir / 'reports' / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return str(filepath)
    
    def _create_executive_summary(self, context: Dict, timestamp: str) -> str:
        """Create executive summary combining all findings."""
        
        summary = {
            'title': 'ADAS Opportunity Mapping - Executive Summary',
            'generated_at': datetime.now().isoformat(),
            'market_overview': context.get('market_size_data', {}),
            'key_trends': context.get('trends_simplification_data', {}).get('trends', [])[:3],
            'top_opportunities': context.get('gap_analysis_data', {}).get('opportunities', [])[:3],
            'execution_metadata': context.get('metadata', {})
        }
        
        filename = f'executive_summary_{timestamp}.json'
        filepath = self.output_dir / 'reports' / filename
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return str(filepath)