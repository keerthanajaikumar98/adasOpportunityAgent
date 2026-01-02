"""Streamlit Dashboard for ADAS Opportunity Mapping Agent Results."""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="ADAS Opportunity Mapper",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
    }
    .source-badge {
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 0 4px;
    }
    .api-badge {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 0 4px;
    }
    .ai-badge {
        background-color: #f3e5f5;
        color: #7b1fa2;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin: 0 4px;
    }
    .assumption-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .evidence-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
    }
    .section-divider {
        border-top: 2px solid #e0e0e0;
        margin: 2rem 0;
    }
    .python-viz-footer {
        background-color: #f5f5f5;
        border-top: 1px solid #e0e0e0;
        padding: 8px 12px;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #666;
        font-style: italic;
    }
    .api-status-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_latest_results():
    """Load the most recent analysis results from individual agent files."""
    reports_dir = Path("outputs/reports")
    
    if not reports_dir.exists():
        return {}
    
    # Find the latest execution summary to get timestamp
    summaries = sorted(reports_dir.glob("execution_summary_*.json"))
    
    if not summaries:
        # Fallback: find timestamp from any result file
        all_results = sorted(reports_dir.glob("*_result_*.json"))
        if not all_results:
            return {}
        
        # Extract timestamp from filename: agent_result_YYYYMMDD_HHMMSS.json
        filename_parts = all_results[-1].stem.split('_')
        timestamp = f"{filename_parts[-2]}_{filename_parts[-1]}"
    else:
        with open(summaries[-1], 'r') as f:
            summary_data = json.load(f)
        
        # Extract timestamp from summary filename
        filename_parts = summaries[-1].stem.split('_')
        timestamp = f"{filename_parts[-2]}_{filename_parts[-1]}"
    
    print(f"Looking for results with timestamp: {timestamp}")
    
    # Load individual agent results
    agent_names = [
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
    
    results = {}
    for agent_name in agent_names:
        # Try with _result_ pattern
        filepath = reports_dir / f"{agent_name}_result_{timestamp}.json"
        
        # Fallback: try without _result_
        if not filepath.exists():
            filepath = reports_dir / f"{agent_name}_{timestamp}.json"
        
        # Fallback: find any file with this agent name
        if not filepath.exists():
            matching_files = sorted(reports_dir.glob(f"{agent_name}*.json"))
            if matching_files:
                filepath = matching_files[-1]
        
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    results[agent_name] = json.load(f)
                print(f"Loaded: {filepath.name}")
            except Exception as e:
                print(f"Error loading {filepath.name}: {e}")
        else:
            print(f"Not found: {agent_name}")
    
    # Load execution summary if available
    metadata = {}
    execution_log = []
    
    if summaries:
        try:
            with open(summaries[-1], 'r') as f:
                summary = json.load(f)
                metadata = summary.get('metadata', {})
                execution_log = summary.get('execution_log', [])
        except Exception as e:
            print(f"Error loading summary: {e}")
    
    return {
        'results': results,
        'metadata': metadata,
        'execution_log': execution_log,
        'timestamp': timestamp
    }

def show_api_data_sources(data_sources):
    """Show which APIs were used to enhance the data"""
    if not data_sources:
        return
    
    api_badges = []
    
    if data_sources.get('patent_data') == 'uspto_api':
        api_badges.append('<span class="api-badge">USPTO Patent API</span>')
    
    if data_sources.get('github_issues') == 'github_api':
        api_badges.append('<span class="api-badge">GitHub API</span>')
    
    if data_sources.get('academic_papers') == 'semantic_scholar_api':
        api_badges.append('<span class="api-badge">Semantic Scholar API</span>')
    
    if api_badges:
        st.markdown(' '.join(api_badges), unsafe_allow_html=True)

def show_python_viz_attribution():
    """Show that visualization was created with Python/Plotly"""
    st.markdown(
        '<div class="python-viz-footer">Visualization generated with Python (Plotly)</div>',
        unsafe_allow_html=True
    )

def show_attribution(item, field_name="data"):
    """Show whether data is from a source or AI-derived."""
    if isinstance(item, dict):
        if 'source' in item or 'sources' in item or 'evidence' in item:
            st.markdown(f'<span class="source-badge">From Research Sources</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="ai-badge">AI Analysis (Claude Sonnet 4.5)</span>', unsafe_allow_html=True)

def show_confidence(confidence, rationale):
    """Display confidence level with rationale."""
    color_map = {
        'High': 'green',
        'Medium': 'orange',
        'Low': 'red',
        'Unknown': 'gray'
    }
    
    color = color_map.get(confidence, 'gray')
    st.markdown(f"**Confidence Level:** :{color}[{confidence}]")
    
    if rationale:
        with st.expander("View Confidence Rationale"):
            st.markdown(rationale)

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<div class="main-header">ADAS Semiconductor Opportunity Analysis Dashboard</div>', unsafe_allow_html=True)
    st.markdown("*Automated market intelligence powered by AI and real-time API data*")
    
    # Load data
    try:
        data = load_latest_results()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.info("Please run the analysis first: `python main.py`")
        return
    
    if not data or not data.get('results'):
        st.warning("No analysis results found. Please run: `python main.py`")
        st.code("python main.py", language="bash")
        return
    
    results = data.get('results', {})
    metadata = data.get('metadata', {})
    execution_log = data.get('execution_log', [])
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    
    # Show API status
    st.sidebar.markdown("### API Data Sources")
    apis_available = metadata.get('apis_available', {})
    
    if apis_available.get('uspto'):
        st.sidebar.success("USPTO Patent API - Active")
    else:
        st.sidebar.warning("USPTO Patent API - Unavailable")
    
    if apis_available.get('github'):
        st.sidebar.success("GitHub API - Active")
    else:
        st.sidebar.warning("GitHub API - Unavailable")
    
    if apis_available.get('semantic_scholar'):
        st.sidebar.success("Semantic Scholar API - Active")
    else:
        st.sidebar.info("Semantic Scholar API - Not configured")
    
    # Show analysis info
    st.sidebar.markdown("### Analysis Metadata")
    if metadata:
        st.sidebar.metric("Agents Executed", f"{metadata.get('agents_executed', 0)}/10")
        success_rate = ((metadata.get('agents_executed', 0) - metadata.get('agents_failed', 0)) / max(metadata.get('agents_executed', 1), 1) * 100)
        st.sidebar.metric("Success Rate", f"{success_rate:.0f}%")
        
        if 'start_time' in metadata:
            run_date = datetime.fromisoformat(metadata['start_time']).strftime("%Y-%m-%d %H:%M")
            st.sidebar.text(f"Last Run: {run_date}")
        
        # Show API usage
        api_stats = metadata.get('api_usage_stats', {})
        if any(api_stats.values()):
            st.sidebar.markdown("### API Calls This Run")
            if api_stats.get('uspto_calls', 0) > 0:
                st.sidebar.text(f"USPTO: {api_stats['uspto_calls']}")
            if api_stats.get('github_calls', 0) > 0:
                st.sidebar.text(f"GitHub: {api_stats['github_calls']}")
            if api_stats.get('semantic_scholar_calls', 0) > 0:
                st.sidebar.text(f"Semantic Scholar: {api_stats['semantic_scholar_calls']}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Select View")
    
    # Navigation options
    pages = {
        "Executive Summary": "executive",
        "Source Discovery": "source_discovery",
        "Market Size": "market_size",
        "Trends Analysis": "trends_simplification",
        "Competitive Landscape": "competitive_landscape",
        "Pain Points": "pain_point_extraction",
        "Compute Architecture": "compute_architecture",
        "Bottleneck Diagnosis": "bottleneck_diagnosis",
        "Gap Analysis": "gap_analysis",
        "Positioning & Messaging": "positioning_messaging",
        "Assumptions Tracker": "assumptions"
    }
    
    selected_page = st.sidebar.radio("", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Debug info (collapsible)
    with st.sidebar.expander("Debug Info"):
        st.write(f"Timestamp: {data.get('timestamp', 'Unknown')}")
        st.write(f"Loaded agents: {len(results)}")
        st.write(f"Agent keys: {list(results.keys())}")
    
    # ==================================
    # PAGE: EXECUTIVE SUMMARY
    # ==================================
    if page_key == "executive":
        st.header("Executive Summary")
        
        # Show API enhancement status
        apis_available = metadata.get('apis_available', {})
        if any(apis_available.values()):
            st.markdown('<div class="api-status-box">', unsafe_allow_html=True)
            st.markdown("**Data Enhanced With:**")
            if apis_available.get('uspto'):
                st.markdown("- USPTO Patent Database (innovation trends, filing velocity)")
            if apis_available.get('github'):
                st.markdown("- GitHub Developer Feedback (real pain points from ADAS projects)")
            if apis_available.get('semantic_scholar'):
                st.markdown("- Semantic Scholar (academic research validation)")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick metrics
        col1, col2, col3, col4 = st.columns(4)
        
        market_data = results.get('market_size', {})
        gap_data = results.get('gap_analysis', {})
        
        with col1:
            st.metric("Current Market", 
                     f"${market_data.get('current_market_size_usd_millions', 0):,}M",
                     f"{market_data.get('base_year', 'N/A')}")
        
        with col2:
            st.metric("2030 Projection",
                     f"${market_data.get('projected_market_size_usd_millions', 0):,}M",
                     f"+{market_data.get('cagr_percent', 0)}%")
        
        with col3:
            opportunities = gap_data.get('opportunities', [])
            st.metric("Opportunities", len(opportunities))
        
        with col4:
            trends_data = results.get('trends_simplification', {})
            trends = trends_data.get('trends', [])
            st.metric("Key Trends", len(trends))
        
        # Top insights
        st.markdown("### Key Insights")
        
        if opportunities:
            top_opp = opportunities[0]
            market_size = top_opp.get('market_size', {})
            
            st.markdown(f"""
            <div class="evidence-box">
            <strong>Top Opportunity:</strong> {top_opp.get('name', 'Unknown')}<br>
            <strong>Market Size:</strong> ${market_size.get('addressable_market_usd_millions', 0)}M<br>
            <strong>Revenue Potential:</strong> {market_size.get('revenue_potential_range_usd_millions', 'N/A')}<br>
            <strong>Risk Level:</strong> {top_opp.get('execution', {}).get('risk_level', 'Unknown')}
            </div>
            """, unsafe_allow_html=True)
        
        # Agent execution status
        st.markdown("### Analysis Execution Timeline")
        
        if execution_log:
            timeline_df = pd.DataFrame([
                {
                    'Agent': log['agent'].replace('_', ' ').title(),
                    'Status': 'Success' if log['success'] else 'Failed',
                    'Confidence': log.get('confidence', 'Unknown'),
                    'Time': datetime.fromisoformat(log['timestamp']).strftime("%H:%M:%S"),
                    'APIs Used': ', '.join([
                        k.replace('_data', '').upper() 
                        for k, v in log.get('data_sources', {}).items() 
                        if 'api' in str(v)
                    ]) or 'None'
                }
                for log in execution_log
            ])
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
    
    # ==================================
    # PAGE: MARKET SIZE
    # ==================================
    elif page_key == "market_size":
        st.header("Market Size Analysis")
        
        if 'market_size' not in results:
            st.warning("Market Size data not available")
            return
        
        market_data = results['market_size']
        
        # Attribution
        st.markdown('<span class="source-badge">Based on Financial Research Sources</span>', unsafe_allow_html=True)
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Market",
                     f"${market_data.get('current_market_size_usd_millions', 0):,}M",
                     f"Base: {market_data.get('base_year', 'N/A')}")
        
        with col2:
            st.metric("2030 Projection",
                     f"${market_data.get('projected_market_size_usd_millions', 0):,}M",
                     f"Year: {market_data.get('projection_year', 'N/A')}")
        
        with col3:
            st.metric("CAGR", f"{market_data.get('cagr_percent', 0)}%")
        
        # Market growth chart
        st.markdown("### Market Growth Projection")
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Current (2023)', 'Projected (2030)'],
            y=[market_data.get('current_market_size_usd_millions', 0),
               market_data.get('projected_market_size_usd_millions', 0)],
            marker_color=['#1f77b4', '#2ecc71'],
            text=[f"${market_data.get('current_market_size_usd_millions', 0)}M",
                  f"${market_data.get('projected_market_size_usd_millions', 0)}M"],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=f"US ADAS Semiconductor Market ({market_data.get('cagr_percent', 0)}% CAGR)",
            yaxis_title="Market Size (USD Millions)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        show_python_viz_attribution()
        
        # Segment breakdown
        st.markdown("### Market Breakdown by Segment")
        
        breakdown = market_data.get('breakdown', {})
        if breakdown:
            segment_df = pd.DataFrame([
                {
                    'Segment': 'Camera',
                    'Size ($M)': breakdown['camera']['size_usd_millions'],
                    'Percentage': f"{breakdown['camera']['percentage']}%"
                },
                {
                    'Segment': 'Radar',
                    'Size ($M)': breakdown['radar']['size_usd_millions'],
                    'Percentage': f"{breakdown['radar']['percentage']}%"
                },
                {
                    'Segment': 'Sensor Fusion/Compute',
                    'Size ($M)': breakdown['sensor_fusion_compute']['size_usd_millions'],
                    'Percentage': f"{breakdown['sensor_fusion_compute']['percentage']}%"
                }
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.dataframe(segment_df, use_container_width=True, hide_index=True)
            
            with col2:
                fig = go.Figure(data=[go.Pie(
                    labels=['Camera', 'Radar', 'Sensor Fusion/Compute'],
                    values=[
                        breakdown['camera']['size_usd_millions'],
                        breakdown['radar']['size_usd_millions'],
                        breakdown['sensor_fusion_compute']['size_usd_millions']
                    ],
                    hole=0.3
                )])
                fig.update_layout(title="Market Breakdown (2023)", height=400)
                st.plotly_chart(fig, use_container_width=True)
                show_python_viz_attribution()
        
        # Data sources
        st.markdown("### Primary Data Sources")
        st.markdown('<span class="source-badge">Research Sources</span>', unsafe_allow_html=True)
        
        for source in market_data.get('sources', []):
            with st.expander(f"**{source.get('name', 'Unknown')}** ({source.get('year', 'N/A')})"):
                st.markdown(f"**Finding:** {source.get('figure', 'N/A')}")
                if source.get('url'):
                    st.markdown(f"**URL:** {source.get('url', 'N/A')}")
        
        # Confidence
        st.markdown("---")
        show_confidence(market_data.get('confidence', 'Unknown'),
                       market_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: TRENDS
    # ==================================
    elif page_key == "trends_simplification":
        st.header("Technology Trends Analysis")
        
        if 'trends_simplification' not in results:
            st.warning("Trends data not available")
            return
        
        trends_data = results['trends_simplification']
        trends = trends_data.get('trends', [])
        
        # Show data sources
        data_sources = trends_data.get('data_sources', {})
        st.markdown('<span class="ai-badge">AI Analysis (Claude Sonnet 4.5)</span>', unsafe_allow_html=True)
        show_api_data_sources(data_sources)
        
        # Patent insights if available
        patent_insights = trends_data.get('patent_insights', {})
        if patent_insights.get('data_available'):
            st.markdown(f"""
            <div class="api-status-box">
            <strong>Enhanced with USPTO Patent Data:</strong><br>
            - Patent Filing Analysis: {', '.join(patent_insights.get('top_innovators', [])[:3])} leading innovation<br>
            - Emerging Technologies Identified: {len(patent_insights.get('emerging_technologies', []))} areas with rapid patent growth
            </div>
            """, unsafe_allow_html=True)
        
        st.metric("Trends Identified", len(trends))
        
        # Timeline filter
        timelines = sorted(set(t.get('timeline', 'Unknown') for t in trends))
        selected_timeline = st.selectbox("Filter by Timeline", ['All'] + timelines)
        
        filtered_trends = trends if selected_timeline == 'All' else [
            t for t in trends if t.get('timeline') == selected_timeline
        ]
        
        # Display trends
        for i, trend in enumerate(filtered_trends, 1):
            st.markdown(f"### {i}. {trend.get('name', 'Unknown')}")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {trend.get('description', 'N/A')}")
                st.markdown(f"**Silicon Implication:** {trend.get('silicon_implication', 'N/A')}")
                
                # Show innovation velocity if available (from USPTO data)
                if trend.get('innovation_velocity'):
                    velocity_colors = {
                        'accelerating': 'green',
                        'steady': 'blue',
                        'maturing': 'orange',
                        'declining': 'red'
                    }
                    velocity = trend['innovation_velocity']
                    color = velocity_colors.get(velocity, 'gray')
                    st.markdown(f"**Innovation Velocity:** :{color}[{velocity.title()}]")
            
            with col2:
                st.metric("Timeline", trend.get('timeline', 'Unknown'))
            
            # Evidence
            evidence = trend.get('evidence', {})
            if evidence:
                evidence_type = evidence.get('type', 'Unknown')
                badge_type = "api-badge" if evidence_type == "patent_data" else "source-badge"
                
                st.markdown(f"""
                <div class="evidence-box">
                <span class="{badge_type}">{evidence_type.replace('_', ' ').title()}</span><br><br>
                <strong>Source:</strong> {evidence.get('source', 'Unknown')}<br>
                <strong>Evidence:</strong> {evidence.get('key_quote', 'N/A')}
                """, unsafe_allow_html=True)
                
                # Add patent filing data if available
                if evidence.get('patent_filings'):
                    st.markdown(f"<br><strong>Patent Activity:</strong> {evidence['patent_filings']}", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Acronyms
        st.markdown("### Acronyms & Definitions")
        acronyms = trends_data.get('acronyms_defined', {})
        
        if acronyms:
            acro_df = pd.DataFrame([
                {'Acronym': k, 'Definition': v}
                for k, v in acronyms.items()
            ])
            st.dataframe(acro_df, use_container_width=True, hide_index=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(trends_data.get('confidence', 'Unknown'),
                       trends_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: PAIN POINTS
    # ==================================
    elif page_key == "pain_point_extraction":
        st.header("Market Pain Points Analysis")
        
        if 'pain_point_extraction' not in results:
            st.warning("Pain Points data not available")
            return
        
        pain_data = results['pain_point_extraction']
        pain_points = pain_data.get('pain_points', [])
        summary = pain_data.get('summary', {})
        
        # Show data sources
        data_sources = pain_data.get('data_sources', {})
        st.markdown('<span class="source-badge">From Industry Reports & Stakeholder Statements</span>', unsafe_allow_html=True)
        show_api_data_sources(data_sources)
        
        # GitHub insights if available
        github_insights = pain_data.get('github_insights', {})
        if github_insights.get('data_available'):
            st.markdown(f"""
            <div class="api-status-box">
            <strong>Enhanced with GitHub Developer Feedback:</strong><br>
            - Analyzed {github_insights.get('total_issues_analyzed', 0)} real issues from: {', '.join(github_insights.get('repos_analyzed', []))}<br>
            - Top developer complaints validated with actual bug reports and feature requests
            </div>
            """, unsafe_allow_html=True)
        
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        
        by_category = summary.get('by_category', {})
        
        with col1:
            st.metric("Total Pain Points", summary.get('total_pain_points', 0))
        
        with col2:
            st.metric("Technical", by_category.get('technical', 0))
        
        with col3:
            st.metric("Business", by_category.get('business', 0))
        
        with col4:
            st.metric("Operational", by_category.get('operational', 0))
        
        # Top 3 critical
        st.markdown("### Top 3 Critical Pain Points")
        for point in summary.get('top_3_critical', []):
            st.markdown(f"- **{point}**")
        
        # Filters
        st.markdown("### All Pain Points")
        
        col1, col2 = st.columns(2)
        
        with col1:
            categories = sorted(set(p['category'] for p in pain_points))
            category_filter = st.selectbox("Filter by Category", ['All'] + categories)
        
        with col2:
            severities = ['All', 'High', 'Medium', 'Low']
            severity_filter = st.selectbox("Filter by Severity", severities)
        
        filtered_points = pain_points
        if category_filter != 'All':
            filtered_points = [p for p in filtered_points if p['category'] == category_filter]
        if severity_filter != 'All':
            filtered_points = [p for p in filtered_points if p['severity'] == severity_filter]
        
        # Display pain points
        for pain in filtered_points:
            severity = pain.get('severity', 'Unknown')
            severity_indicator = {'High': ':red[●]', 'Medium': ':orange[●]', 'Low': ':green[●]'}
            indicator = severity_indicator.get(severity, ':gray[●]')
            
            with st.expander(f"{indicator} **{pain.get('title', 'Unknown')}**"):
                st.markdown(f"**Category:** {pain.get('category', 'N/A')}")
                st.markdown(f"**Severity:** {severity}")
                
                st.markdown(f"**Description:** {pain.get('description', 'N/A')}")
                st.markdown(f"**Impact:** {pain.get('impact', 'N/A')}")
                
                st.markdown("**Impacted Stakeholders:**")
                for stakeholder in pain.get('impacted_stakeholders', []):
                    st.markdown(f"- {stakeholder}")
                
                # Evidence
                evidence = pain.get('evidence', {})
                if evidence:
                    evidence_type = evidence.get('source_type', 'Unknown')
                    badge_type = "api-badge" if evidence_type == "github_issues" else "source-badge"
                    
                    st.markdown(f"""
                    <div class="evidence-box">
                    <span class="{badge_type}">{evidence_type.replace('_', ' ').title()}</span><br><br>
                    <strong>Source:</strong> {evidence.get('source_name', 'Unknown')}<br>
                    <strong>Evidence:</strong> {evidence.get('key_quote', 'N/A')}
                    """, unsafe_allow_html=True)
                    
                    # Add GitHub-specific data if available
                    if evidence.get('github_issue_count'):
                        st.markdown(f"<br><strong>Related GitHub Issues:</strong> {evidence['github_issue_count']}", unsafe_allow_html=True)
                        st.markdown(f"<strong>Developer Priority:</strong> {evidence.get('developer_priority', 'Unknown')}", unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        
        # GitHub pain points summary if available
        if github_insights.get('top_developer_pain_points'):
            st.markdown("### Developer Pain Point Frequency (from GitHub)")
            
            github_df = pd.DataFrame(github_insights['top_developer_pain_points'])
            
            fig = px.bar(github_df, x='keyword', y='occurrences',
                        color='severity',
                        title='Most Frequent Developer Complaints',
                        labels={'keyword': 'Pain Point', 'occurrences': 'Number of Issues'})
            st.plotly_chart(fig, use_container_width=True)
            show_python_viz_attribution()
        
        # Confidence
        st.markdown("---")
        show_confidence(pain_data.get('confidence', 'Unknown'),
                       pain_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: COMPETITIVE LANDSCAPE
    # ==================================
    elif page_key == "competitive_landscape":
        st.header("Competitive Landscape")
        
        if 'competitive_landscape' not in results:
            st.warning("Competitive Landscape data not available")
            return
        
        comp_data = results['competitive_landscape']
        solutions = comp_data.get('solutions', [])
        
        st.markdown('<span class="source-badge">From Vendor Specifications</span>', unsafe_allow_html=True)
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Solutions Analyzed", len(solutions))
        
        with col2:
            st.metric("Market Coverage", f"{comp_data.get('market_coverage_percent', 0)}%")
        
        with col3:
            categories = set(sol.get('category', 'Unknown') for sol in solutions)
            st.metric("Categories", len(categories))
        
        # Competitive positioning chart
        st.markdown("### Performance vs Power Efficiency")
        
        chart_data = []
        for sol in solutions:
            specs = sol.get('specifications', {})
            tops = specs.get('compute_tops', 'Unknown')
            power = specs.get('power_consumption_w', 'Unknown')
            
            if tops != 'Unknown' and power != 'Unknown':
                try:
                    chart_data.append({
                        'Company': sol['company'],
                        'Product': sol['product'],
                        'TOPS': float(tops),
                        'Power (W)': float(power),
                        'Category': sol['category'],
                        'Position': sol['market_position']
                    })
                except:
                    pass
        
        if chart_data:
            df = pd.DataFrame(chart_data)
            fig = px.scatter(df, x='Power (W)', y='TOPS',
                           size='TOPS', color='Category',
                           hover_data=['Company', 'Product', 'Position'],
                           title='AI Compute Performance vs Power Consumption')
            st.plotly_chart(fig, use_container_width=True)
            show_python_viz_attribution()
        
        # Solutions table
        st.markdown("### All Solutions")
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            category_filter = st.multiselect(
                "Filter by Category",
                options=sorted(categories),
                default=list(categories)
            )
        
        with col2:
            positions = sorted(set(sol.get('market_position', 'Unknown') for sol in solutions))
            position_filter = st.multiselect(
                "Filter by Position",
                options=positions,
                default=positions
            )
        
        filtered_solutions = [
            sol for sol in solutions
            if sol.get('category') in category_filter
            and sol.get('market_position') in position_filter
        ]
        
        table_data = []
        for sol in filtered_solutions:
            specs = sol.get('specifications', {})
            table_data.append({
                'Company': sol['company'],
                'Product': sol['product'],
                'Category': sol['category'],
                'TOPS': specs.get('compute_tops', 'Unknown'),
                'Power (W)': specs.get('power_consumption_w', 'Unknown'),
                'Process (nm)': specs.get('process_node_nm', 'Unknown'),
                'Position': sol['market_position']
            })
        
        if table_data:
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(comp_data.get('confidence', 'Unknown'),
                       comp_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: GAP ANALYSIS
    # ==================================
    elif page_key == "gap_analysis":
        st.header("Gap Analysis & Market Opportunities")
        
        if 'gap_analysis' not in results:
            st.warning("Gap Analysis data not available")
            return
        
        gap_data = results['gap_analysis']
        opportunities = gap_data.get('opportunities', [])
        
        st.markdown('<span class="ai-badge">AI-Synthesized from All Previous Agents (Claude Sonnet 4.5)</span>', unsafe_allow_html=True)
        
        st.metric("Opportunities Identified", len(opportunities))
        
        # Opportunity comparison
        st.markdown("### Opportunity Comparison Matrix")
        
        comp_data = []
        for opp in opportunities:
            market = opp.get('market_size', {})
            execution = opp.get('execution', {})
            
            comp_data.append({
                'Rank': opp['rank'],
                'Opportunity': opp['name'][:50] + '...' if len(opp['name']) > 50 else opp['name'],
                'Market ($M)': market.get('addressable_market_usd_millions', 0),
                'Revenue ($M)': market.get('revenue_potential_range_usd_millions', 'N/A'),
                'Time (mo)': execution.get('time_to_market_months_range', 'N/A'),
                'ROI': execution.get('estimated_roi_range', 'N/A'),
                'Risk': execution.get('risk_level', 'Unknown')
            })
        
        st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)
        
        # Detailed opportunities
        st.markdown("### Detailed Opportunity Analysis")
        
        for opp in opportunities:
            st.markdown(f"## #{opp['rank']}: {opp['name']}")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            market = opp.get('market_size', {})
            execution = opp.get('execution', {})
            
            with col1:
                st.metric("Market Size", f"${market.get('addressable_market_usd_millions', 0)}M")
            
            with col2:
                st.metric("Revenue Potential", market.get('revenue_potential_range_usd_millions', 'N/A'))
            
            with col3:
                st.metric("Time to Market", execution.get('time_to_market_months_range', 'N/A'))
            
            with col4:
                risk = execution.get('risk_level', 'Unknown')
                risk_colors = {'High': 'red', 'Medium': 'orange', 'Low': 'green'}
                color = risk_colors.get(risk, 'gray')
                st.metric("Risk", f":{color}[{risk}]")
            
            # Details
            st.markdown(f"**Target Segment:** {opp.get('target_segment', 'N/A')}")
            st.markdown(f"**Unmet Need:** {opp.get('unmet_need', 'N/A')}")
            st.markdown(f"**Technical Gap:** {opp.get('technical_gap', 'N/A')}")
            
            # Differentiators
            st.markdown("**Key Differentiators:**")
            for diff in opp.get('key_differentiators', []):
                st.markdown(f"- {diff}")
            
            # Evidence
            st.markdown("**Supporting Evidence:**")
            for evidence in opp.get('supporting_evidence', []):
                st.markdown(f"""
                <div class="evidence-box">
                <strong>{evidence.get('source', 'Unknown')}</strong><br>
                {evidence.get('claim', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(gap_data.get('confidence', 'Unknown'),
                       gap_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: POSITIONING & MESSAGING
    # ==================================
    elif page_key == "positioning_messaging":
        st.header("Positioning & Messaging Strategy")
        
        if 'positioning_messaging' not in results:
            st.warning("Positioning & Messaging data not available")
            return
        
        pos_data = results['positioning_messaging']
        opportunities = pos_data.get('opportunities', [])
        
        st.markdown('<span class="ai-badge">AI-Generated Go-to-Market Strategy (Claude Sonnet 4.5)</span>', unsafe_allow_html=True)
        
        st.metric("Opportunities Positioned", len(opportunities))
        
        for opp in opportunities:
            st.markdown(f"## {opp.get('opportunity_name', 'Unknown')}")
            
            # Elevator pitch
            st.markdown("### Elevator Pitch")
            st.info(opp.get('elevator_pitch', 'N/A'))
            
            # Taglines
            st.markdown("### Tagline Options")
            for tagline in opp.get('tagline_options', []):
                st.markdown(f"- *\"{tagline}\"*")
            
            # USP
            st.markdown("### Unique Selling Proposition")
            usp = opp.get('usp', {})
            
            st.markdown(f"> {usp.get('core_differentiation', 'N/A')}")
            
            with st.expander("View Proof Points"):
                for proof in usp.get('proof_points', []):
                    st.markdown(f"- {proof}")
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(pos_data.get('confidence', 'Unknown'),
                       pos_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: ASSUMPTIONS TRACKER
    # ==================================
    elif page_key == "assumptions":
        st.header("Assumptions Tracker")
        
        st.markdown("""
        This page tracks all assumptions made during the analysis. Understanding these assumptions 
        is critical for validating the conclusions.
        """)
        
        # Collect all assumptions from all agents
        all_assumptions = []
        
        # From Gap Analysis
        if 'gap_analysis' in results:
            gap_assumptions = results['gap_analysis'].get('assumptions', [])
            for assumption in gap_assumptions:
                all_assumptions.append({
                    'Agent': 'Gap Analysis',
                    'Assumption': assumption.get('assumption', 'N/A'),
                    'Risk if Wrong': assumption.get('risk_if_wrong', 'N/A'),
                    'Validation Signal': assumption.get('validation_signal', 'N/A'),
                    'Type': 'Explicit'
                })
        
        # Display assumptions
        if all_assumptions:
            st.metric("Total Assumptions Tracked", len(all_assumptions))
            
            # Display as cards
            for i, assumption in enumerate(all_assumptions, 1):
                st.markdown(f"""
                <div class="assumption-box">
                <strong>#{i} - {assumption['Agent']}</strong> ({assumption['Type']})<br><br>
                <strong>Assumption:</strong> {assumption['Assumption']}<br>
                <strong>Risk if Wrong:</strong> {assumption['Risk if Wrong']}<br>
                <strong>Validation Signal:</strong> {assumption['Validation Signal']}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No explicit assumptions tracked. Run gap_analysis agent to populate.")
        
        # AI assumptions (meta)
        st.markdown("### AI Model & Data Assumptions")
        
        st.markdown("""
        <div class="assumption-box">
        <strong>AI Analysis Framework:</strong><br>
        - Language Model: Claude Sonnet 4.5 (Anthropic)<br>
        - Analysis based on patterns in provided data, not domain expertise<br>
        - Confidence ratings reflect data quality and convergence, not certainty<br>
        - All numeric estimates should be validated with industry experts<br><br>
        <strong>Data Enhancement:</strong><br>
        - API integrations (USPTO, GitHub) provide real-time validation<br>
        - Visualizations generated programmatically using Python (Plotly)<br>
        - Analysis replicable and version-controlled
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()