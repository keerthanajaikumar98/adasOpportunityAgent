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
    page_icon="🚗",
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
    
    print(f"🔍 Looking for results with timestamp: {timestamp}")
    
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
                print(f"✅ Loaded: {filepath.name}")
            except Exception as e:
                print(f"❌ Error loading {filepath.name}: {e}")
        else:
            print(f"⚠️  Not found: {agent_name}")
    
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
            print(f"❌ Error loading summary: {e}")
    
    return {
        'results': results,
        'metadata': metadata,
        'execution_log': execution_log,
        'timestamp': timestamp
    }

def show_attribution(item, field_name="data"):
    """Show whether data is from a source or AI-derived."""
    if isinstance(item, dict):
        if 'source' in item or 'sources' in item or 'evidence' in item:
            st.markdown(f'<span class="source-badge">📚 From Source</span>', unsafe_allow_html=True)
        else:
            st.markdown(f'<span class="ai-badge">🤖 AI Analysis</span>', unsafe_allow_html=True)

def show_confidence(confidence, rationale):
    """Display confidence level with rationale."""
    color_map = {
        'High': '🟢',
        'Medium': '🟡',
        'Low': '🔴',
        'Unknown': '⚪'
    }
    
    emoji = color_map.get(confidence, '⚪')
    st.markdown(f"**Confidence:** {emoji} {confidence}")
    
    if rationale:
        with st.expander("View Confidence Rationale"):
            st.markdown(rationale)

def main():
    """Main dashboard function."""
    
    # Header
    st.markdown('<div class="main-header">🚗 ADAS Opportunity Mapping Dashboard</div>', unsafe_allow_html=True)
    
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
    st.sidebar.title("📊 Navigation")
    
    # Show analysis info
    st.sidebar.markdown("### 📋 Analysis Info")
    if metadata:
        st.sidebar.metric("Agents Executed", f"{metadata.get('agents_executed', 0)}/10")
        st.sidebar.metric("Success Rate", 
                         f"{((metadata.get('agents_executed', 0) - metadata.get('agents_failed', 0)) / max(metadata.get('agents_executed', 1), 1) * 100):.0f}%")
        
        if 'start_time' in metadata:
            run_date = datetime.fromisoformat(metadata['start_time']).strftime("%Y-%m-%d %H:%M")
            st.sidebar.text(f"Last Run: {run_date}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Select Agent View")
    
    # Navigation options
    pages = {
        "📊 Executive Summary": "executive",
        "📍 Source Discovery": "source_discovery",
        "📏 Market Size": "market_size",
        "📈 Trends Analysis": "trends_simplification",
        "🏆 Competitive Landscape": "competitive_landscape",
        "😣 Pain Points": "pain_point_extraction",
        "💻 Compute Architecture": "compute_architecture",
        "🚧 Bottleneck Diagnosis": "bottleneck_diagnosis",
        "💡 Gap Analysis": "gap_analysis",
        "📣 Positioning & Messaging": "positioning_messaging",
        "⚠️ Assumptions Tracker": "assumptions"
    }
    
    selected_page = st.sidebar.radio("", list(pages.keys()))
    page_key = pages[selected_page]
    
    # Debug info (collapsible)
    with st.sidebar.expander("🐛 Debug Info"):
        st.write(f"Timestamp: {data.get('timestamp', 'Unknown')}")
        st.write(f"Loaded agents: {len(results)}")
        st.write(f"Agent keys: {list(results.keys())}")
    
    # ==================================
    # PAGE: EXECUTIVE SUMMARY
    # ==================================
    if page_key == "executive":
        st.header("📊 Executive Summary")
        
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
        st.markdown("### 🎯 Key Insights")
        
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
        st.markdown("### ⚙️ Analysis Execution")
        
        if execution_log:
            timeline_df = pd.DataFrame([
                {
                    'Agent': log['agent'].replace('_', ' ').title(),
                    'Status': '✅ Success' if log['success'] else '❌ Failed',
                    'Confidence': log.get('confidence', 'Unknown'),
                    'Time': datetime.fromisoformat(log['timestamp']).strftime("%H:%M:%S")
                }
                for log in execution_log
            ])
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
    
    # ==================================
    # PAGE: SOURCE DISCOVERY
    # ==================================
    elif page_key == "source_discovery":
        st.header("📍 Source Discovery")
        
        if 'source_discovery' not in results:
            st.warning("Source Discovery data not available")
            return
        
        source_data = results['source_discovery']
        
        st.markdown('<span class="ai-badge">🤖 AI-Generated Source List</span>', unsafe_allow_html=True)
        st.markdown("*The agent identified credible sources for ADAS semiconductor research*")
        
        # Summary metrics
        summary = source_data.get('source_summary', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Sources", summary.get('total_sources', 0))
        
        with col2:
            st.metric("Public Access", summary.get('public_access', 0))
        
        with col3:
            st.metric("Subscription Required", summary.get('subscription_required', 0))
        
        # Sources by category
        st.markdown("### 📚 Sources by Category")
        
        by_category = summary.get('by_category', {})
        if by_category:
            cat_df = pd.DataFrame([
                {'Category': k.title(), 'Count': v}
                for k, v in by_category.items()
            ])
            
            fig = px.bar(cat_df, x='Category', y='Count',
                        title='Source Distribution',
                        color='Category')
            st.plotly_chart(fig, use_container_width=True)
        
        # Source list
        st.markdown("### 📖 Detailed Sources")
        
        sources = source_data.get('sources', [])
        
        # Filter by category
        categories = sorted(set(s.get('category', 'Unknown') for s in sources))
        selected_category = st.selectbox("Filter by Category", ['All'] + categories)
        
        filtered_sources = sources if selected_category == 'All' else [
            s for s in sources if s.get('category') == selected_category
        ]
        
        for source in filtered_sources:
            with st.expander(f"**{source.get('name', 'Unknown')}** ({source.get('category', 'Unknown').title()})"):
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Type:** {source.get('information_type', 'N/A')}")
                    st.markdown(f"**URL Pattern:** `{source.get('url_pattern', 'N/A')}`")
                    
                    st.markdown("**Relevant Topics:**")
                    for topic in source.get('relevant_topics', []):
                        st.markdown(f"- {topic}")
                
                with col2:
                    credibility = source.get('credibility', 'Unknown')
                    cred_color = {'High': '🟢', 'Medium': '🟡', 'Low': '🔴'}
                    st.markdown(f"**Credibility:** {cred_color.get(credibility, '⚪')} {credibility}")
                    st.markdown(f"**Access:** {source.get('access', 'Unknown')}")
                    st.markdown(f"**Update Freq:** {source.get('update_frequency', 'Unknown')}")
                
                if source.get('notes'):
                    st.info(f"💡 {source['notes']}")
        
        # Search strategy
        st.markdown("### 🔍 Recommended Search Strategy")
        st.markdown('<span class="ai-badge">🤖 AI Recommendation</span>', unsafe_allow_html=True)
        st.info(source_data.get('recommended_search_strategy', 'N/A'))
        
        # Confidence
        st.markdown("---")
        show_confidence(source_data.get('confidence', 'Unknown'),
                       source_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: MARKET SIZE
    # ==================================
    elif page_key == "market_size":
        st.header("📏 Market Size Analysis")
        
        if 'market_size' not in results:
            st.warning("Market Size data not available")
            return
        
        market_data = results['market_size']
        
        # Attribution
        st.markdown('<span class="source-badge">📚 Based on Financial Research Sources</span>', unsafe_allow_html=True)
        
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
        st.markdown("### 📊 Market Growth")
        
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
        
        # Segment breakdown
        st.markdown("### 📐 Market Breakdown")
        
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
        
        # Data sources
        st.markdown("### 📚 Data Sources")
        st.markdown('<span class="source-badge">📚 Primary Research Sources</span>', unsafe_allow_html=True)
        
        for source in market_data.get('sources', []):
            with st.expander(f"**{source.get('name', 'Unknown')}** ({source.get('year', 'N/A')})"):
                st.markdown(f"**Finding:** {source.get('figure', 'N/A')}")
                if source.get('url'):
                    st.markdown(f"**URL:** {source.get('url', 'N/A')}")
        
        # Divergent forecasts
        if market_data.get('divergent_forecasts'):
            st.markdown("### 🔀 Divergent Forecasts")
            st.markdown('<span class="ai-badge">🤖 AI Analysis of Differences</span>', unsafe_allow_html=True)
            
            for forecast in market_data['divergent_forecasts']:
                st.markdown(f"""
                <div class="assumption-box">
                <strong>{forecast.get('source', 'Unknown')}</strong><br>
                Difference: {forecast.get('difference', 'N/A')}<br>
                Rationale: {forecast.get('rationale', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(market_data.get('confidence', 'Unknown'),
                       market_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: TRENDS
    # ==================================
    elif page_key == "trends_simplification":
        st.header("📈 Market Trends Analysis")
        
        if 'trends_simplification' not in results:
            st.warning("Trends data not available")
            return
        
        trends_data = results['trends_simplification']
        trends = trends_data.get('trends', [])
        
        st.markdown('<span class="ai-badge">🤖 AI-Simplified Trends</span>', unsafe_allow_html=True)
        st.markdown("*Complex industry trends translated into actionable insights*")
        
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
            
            with col2:
                st.metric("Timeline", trend.get('timeline', 'Unknown'))
            
            # Evidence
            evidence = trend.get('evidence', {})
            if evidence:
                st.markdown(f"""
                <div class="evidence-box">
                <strong>📚 Evidence ({evidence.get('type', 'Unknown')})</strong><br>
                <strong>Source:</strong> {evidence.get('source', 'Unknown')}<br>
                <strong>Quote:</strong> "{evidence.get('key_quote', 'N/A')}"
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Acronyms
        st.markdown("### 📖 Acronyms & Definitions")
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
    # PAGE: COMPETITIVE LANDSCAPE
    # ==================================
    elif page_key == "competitive_landscape":
        st.header("🏆 Competitive Landscape")
        
        if 'competitive_landscape' not in results:
            st.warning("Competitive Landscape data not available")
            st.info("This might be named differently. Check debug info in sidebar.")
            return
        
        comp_data = results['competitive_landscape']
        solutions = comp_data.get('solutions', [])
        
        st.markdown('<span class="source-badge">📚 From Vendor Specifications</span>', unsafe_allow_html=True)
        
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
        st.markdown("### 📊 Performance vs Power")
        
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
                           title='AI Performance vs Power Consumption')
            st.plotly_chart(fig, use_container_width=True)
        
        # Solutions table
        st.markdown("### 📋 All Solutions")
        
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
        
        # Detailed view
        st.markdown("### 🔍 Detailed Analysis")
        
        companies = sorted(set(sol['company'] for sol in solutions))
        selected_company = st.selectbox("Select Company", companies)
        
        company_solutions = [sol for sol in solutions if sol['company'] == selected_company]
        
        for sol in company_solutions:
            st.markdown(f"#### {sol['product']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Strengths:**")
                for strength in sol.get('strengths', []):
                    st.markdown(f"✅ {strength}")
                
                st.markdown("**Customers:**")
                for customer in sol.get('known_customers', []):
                    st.markdown(f"- {customer}")
            
            with col2:
                st.markdown("**Weaknesses:**")
                for weakness in sol.get('weaknesses', []):
                    st.markdown(f"⚠️ {weakness}")
                
                st.markdown("**Key Features:**")
                for feature in sol.get('key_features', []):
                    st.markdown(f"- {feature}")
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Source attribution
        st.markdown("---")
        st.markdown(f"**Source:** {comp_data.get('source', 'Vendor specifications and public announcements')}")
        
        # Confidence
        show_confidence(comp_data.get('confidence', 'Unknown'),
                       comp_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: PAIN POINTS
    # ==================================
    elif page_key == "pain_point_extraction":
        st.header("😣 Market Pain Points")
        
        if 'pain_point_extraction' not in results:
            st.warning("Pain Points data not available")
            return
        
        pain_data = results['pain_point_extraction']
        pain_points = pain_data.get('pain_points', [])
        summary = pain_data.get('summary', {})
        
        st.markdown('<span class="source-badge">📚 From Industry Reports & Stakeholder Statements</span>', unsafe_allow_html=True)
        
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
        st.markdown("### 🔥 Top 3 Critical Pain Points")
        for point in summary.get('top_3_critical', []):
            st.markdown(f"- 🔴 {point}")
        
        # Filters
        st.markdown("### 📋 All Pain Points")
        
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
            severity_emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
            emoji = severity_emoji.get(pain.get('severity', 'Unknown'), '⚪')
            
            with st.expander(f"{emoji} **{pain.get('title', 'Unknown')}**"):
                st.markdown(f"**Category:** {pain.get('category', 'N/A')}")
                st.markdown(f"**Severity:** {pain.get('severity', 'Unknown')}")
                
                st.markdown(f"**Description:** {pain.get('description', 'N/A')}")
                st.markdown(f"**Impact:** {pain.get('impact', 'N/A')}")
                
                st.markdown("**Impacted Stakeholders:**")
                for stakeholder in pain.get('impacted_stakeholders', []):
                    st.markdown(f"- {stakeholder}")
                
                # Evidence
                evidence = pain.get('evidence', {})
                if evidence:
                    st.markdown(f"""
                    <div class="evidence-box">
                    <strong>📚 Evidence</strong><br>
                    <strong>Source:</strong> {evidence.get('source_name', 'Unknown')} ({evidence.get('source_type', 'Unknown')})<br>
                    <strong>Quote:</strong> "{evidence.get('key_quote', 'N/A')}"
                    </div>
                    """, unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(pain_data.get('confidence', 'Unknown'),
                       pain_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: COMPUTE ARCHITECTURE
    # ==================================
    elif page_key == "compute_architecture":
        st.header("💻 Compute Architecture Requirements")
        
        if 'compute_architecture' not in results:
            st.warning("Compute Architecture data not available")
            return
        
        arch_data = results['compute_architecture']
        
        st.markdown('<span class="ai-badge">🤖 AI-Derived from Trends & Pain Points</span>', unsafe_allow_html=True)
        
        # Camera processing
        st.markdown("### 📷 Camera Processing Requirements")
        camera = arch_data.get('camera_processing', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Resolution", camera.get('target_resolution', 'N/A'))
        
        with col2:
            st.metric("Frame Rate", f"{camera.get('frame_rate_fps', 0)} fps")
        
        with col3:
            st.metric("Compute", camera.get('compute_tops', 'N/A'))
        
        with col4:
            st.metric("Power Budget", camera.get('power_budget_w', 'N/A'))
        
        with st.expander("View Processing Pipeline"):
            for step in camera.get('processing_pipeline', []):
                st.markdown(f"- {step}")
        
        # Radar processing
        st.markdown("### 📡 Radar Processing Requirements")
        radar = arch_data.get('radar_processing', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Frequency Band", radar.get('frequency_band', 'N/A'))
        
        with col2:
            st.metric("Compute", radar.get('compute_tops', 'N/A'))
        
        with col3:
            st.metric("Latency Target", radar.get('latency_target_ms', 'N/A'))
        
        # Sensor fusion
        st.markdown("### 🔀 Sensor Fusion Requirements")
        fusion = arch_data.get('sensor_fusion', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Compute", fusion.get('compute_tops', 'N/A'))
        
        with col2:
            st.metric("Memory", fusion.get('memory_gb', 'N/A'))
        
        with col3:
            st.metric("Power Budget", fusion.get('power_budget_w', 'N/A'))
        
        # AI/ML inference
        st.markdown("### 🤖 AI/ML Inference Requirements")
        ai_ml = arch_data.get('ai_ml_inference', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total TOPS", ai_ml.get('compute_tops', 'N/A'))
        
        with col2:
            st.metric("Latency", ai_ml.get('inference_latency_ms', 'N/A'))
        
        with col3:
            st.metric("Efficiency", ai_ml.get('power_efficiency_tops_per_watt', 'N/A'))
        
        # Recommendations
        st.markdown("### 💡 Architecture Recommendations")
        recs = arch_data.get('architecture_recommendations', {})
        
        st.info(recs.get('preferred_approach', 'N/A'))
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Key Trade-offs:**")
            for tradeoff in recs.get('key_trade_offs', []):
                st.markdown(f"- {tradeoff}")
        
        with col2:
            st.markdown("**Critical Bottlenecks:**")
            for bottleneck in recs.get('critical_bottlenecks', []):
                st.markdown(f"- ⚠️ {bottleneck}")
        
        # Confidence
        st.markdown("---")
        show_confidence(arch_data.get('confidence', 'Unknown'),
                       arch_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: BOTTLENECK DIAGNOSIS
    # ==================================
    elif page_key == "bottleneck_diagnosis":
        st.header("🚧 Technical Bottleneck Diagnosis")
        
        if 'bottleneck_diagnosis' not in results:
            st.warning("Bottleneck Diagnosis data not available")
            return
        
        bottle_data = results['bottleneck_diagnosis']
        bottlenecks = bottle_data.get('bottlenecks', [])
        
        st.markdown('<span class="ai-badge">🤖 AI Analysis from Competitive Gaps & Pain Points</span>', unsafe_allow_html=True)
        
        st.metric("Bottlenecks Identified", len(bottlenecks))
        
        # Critical path
        st.markdown("### 🚨 Critical Path Bottlenecks")
        for bottle_name in bottle_data.get('critical_path_bottlenecks', []):
            st.markdown(f"- 🔴 {bottle_name}")
        
        # All bottlenecks
        st.markdown("### 🔧 All Bottlenecks")
        
        for bottle in bottlenecks:
            severity_emoji = {
                'Critical': '🔴',
                'High': '🟠',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(bottle.get('severity', 'Unknown'), '⚪')
            
            with st.expander(f"{severity_emoji} **{bottle.get('name', 'Unknown')}** ({bottle.get('category', 'Unknown')})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Description:** {bottle.get('description', 'N/A')}")
                    st.markdown(f"**Root Cause:** {bottle.get('root_cause', 'N/A')}")
                    st.markdown(f"**Impact:** {bottle.get('impact', 'N/A')}")
                    st.markdown(f"**Why Current Solutions Fail:** {bottle.get('why_current_solutions_fail', 'N/A')}")
                
                with col2:
                    st.markdown(f"**Severity:** {bottle.get('severity', 'Unknown')}")
                    
                    difficulty = bottle.get('difficulty_to_solve', {})
                    st.markdown(f"**Technical Difficulty:** {difficulty.get('technical', 'Unknown')}")
                    st.markdown(f"**Economic Difficulty:** {difficulty.get('economic', 'Unknown')}")
                    st.markdown(f"**Time to Solution:** {difficulty.get('time_to_solution', 'Unknown')}")
                
                st.markdown("**Potential Approaches:**")
                for approach in bottle.get('potential_approaches', []):
                    st.markdown(f"- {approach}")
                
                # Evidence
                evidence = bottle.get('evidence', {})
                if evidence:
                    st.markdown(f"""
                    <div class="evidence-box">
                    <strong>📚 Supporting Evidence</strong><br>
                    <strong>Source:</strong> {evidence.get('source', 'Unknown')}<br>
                    <strong>Data:</strong> {evidence.get('supporting_data', 'N/A')}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(bottle_data.get('confidence', 'Unknown'),
                       bottle_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: GAP ANALYSIS
    # ==================================
    elif page_key == "gap_analysis":
        st.header("💡 Gap Analysis & Opportunities")
        
        if 'gap_analysis' not in results:
            st.warning("Gap Analysis data not available")
            return
        
        gap_data = results['gap_analysis']
        opportunities = gap_data.get('opportunities', [])
        
        st.markdown('<span class="ai-badge">🤖 AI-Synthesized from All Previous Agents</span>', unsafe_allow_html=True)
        
        st.metric("Opportunities Identified", len(opportunities))
        
        # Opportunity comparison
        st.markdown("### 📊 Opportunity Comparison")
        
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
        st.markdown("### 🎯 Detailed Opportunities")
        
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
                risk_emoji = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                st.metric("Risk", f"{risk_emoji.get(risk, '⚪')} {risk}")
            
            # Details
            st.markdown(f"**Target Segment:** {opp.get('target_segment', 'N/A')}")
            st.markdown(f"**Unmet Need:** {opp.get('unmet_need', 'N/A')}")
            st.markdown(f"**Technical Gap:** {opp.get('technical_gap', 'N/A')}")
            
            # Differentiators
            st.markdown("**Key Differentiators:**")
            for diff in opp.get('key_differentiators', []):
                st.markdown(f"- ✨ {diff}")
            
            # ASIC Approach
            asic = opp.get('asic_approach', {})
            if asic:
                with st.expander("View ASIC Approach"):
                    st.markdown(f"**Compute Strategy:** {asic.get('compute_strategy', 'N/A')}")
                    st.markdown(f"**Power Target:** {asic.get('power_target', 'N/A')}")
                    st.markdown(f"**Integration Level:** {asic.get('integration_level', 'N/A')}")
                    st.markdown(f"**Cost Position:** {asic.get('cost_position', 'N/A')}")
            
            # Evidence
            st.markdown("**Supporting Evidence:**")
            for evidence in opp.get('supporting_evidence', []):
                st.markdown(f"""
                <div class="evidence-box">
                <strong>📚 {evidence.get('source', 'Unknown')}</strong><br>
                {evidence.get('claim', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            
            # Best positioned innovators
            st.markdown("**Best Positioned Innovators:**")
            for innovator in opp.get('best_positioned_innovators', []):
                st.markdown(f"- {innovator}")
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(gap_data.get('confidence', 'Unknown'),
                       gap_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: POSITIONING & MESSAGING
    # ==================================
    elif page_key == "positioning_messaging":
        st.header("📣 Positioning & Messaging")
        
        if 'positioning_messaging' not in results:
            st.warning("Positioning & Messaging data not available")
            return
        
        pos_data = results['positioning_messaging']
        opportunities = pos_data.get('opportunities', [])
        
        st.markdown('<span class="ai-badge">🤖 AI-Generated Go-to-Market Strategy</span>', unsafe_allow_html=True)
        
        st.metric("Opportunities Positioned", len(opportunities))
        
        for opp in opportunities:
            st.markdown(f"## {opp.get('opportunity_name', 'Unknown')}")
            
            # Elevator pitch
            st.markdown("### 🎤 Elevator Pitch")
            st.info(opp.get('elevator_pitch', 'N/A'))
            
            # Taglines
            st.markdown("### 💬 Tagline Options")
            for tagline in opp.get('tagline_options', []):
                st.markdown(f"- *\"{tagline}\"*")
            
            # Problem statement
            st.markdown("### 😣 Problem Statement")
            problem = opp.get('problem_statement', {})
            
            st.markdown(f"**Customer Pain:** {problem.get('customer_pain', 'N/A')}")
            st.markdown(f"**Market Context:** {problem.get('market_context', 'N/A')}")
            st.markdown(f"**Urgency:** {problem.get('urgency', 'N/A')}")
            
            # USP
            st.markdown("### ✨ Unique Selling Proposition")
            usp = opp.get('usp', {})
            
            st.markdown(f"> {usp.get('core_differentiation', 'N/A')}")
            
            with st.expander("View Proof Points"):
                for proof in usp.get('proof_points', []):
                    st.markdown(f"- {proof}")
            
            # Messaging pillars
            st.markdown("### 📋 Messaging Pillars")
            
            for pillar in opp.get('messaging_pillars', []):
                with st.expander(f"**{pillar.get('pillar', 'Unknown')}** (Target: {pillar.get('target_audience', 'Unknown')})"):
                    for point in pillar.get('supporting_points', []):
                        st.markdown(f"- {point}")
            
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Confidence
        st.markdown("---")
        show_confidence(pos_data.get('confidence', 'Unknown'),
                       pos_data.get('confidence_rationale', ''))
    
    # ==================================
    # PAGE: ASSUMPTIONS TRACKER
    # ==================================
    elif page_key == "assumptions":
        st.header("⚠️ Assumptions Tracker")
        
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
        
        # From Market Size (divergent forecasts are implicit assumptions)
        if 'market_size' in results:
            for forecast in results['market_size'].get('divergent_forecasts', []):
                all_assumptions.append({
                    'Agent': 'Market Size',
                    'Assumption': f"Choosing {forecast.get('source', 'Unknown')} forecast",
                    'Risk if Wrong': f"Market sizing off by {forecast.get('difference', 'unknown')}",
                    'Validation Signal': forecast.get('rationale', 'N/A'),
                    'Type': 'Implicit (Forecast Selection)'
                })
        
        # From Bottleneck Diagnosis (severity assumptions)
        if 'bottleneck_diagnosis' in results:
            for bottle in results['bottleneck_diagnosis'].get('bottlenecks', [])[:3]:
                all_assumptions.append({
                    'Agent': 'Bottleneck Diagnosis',
                    'Assumption': f"{bottle.get('name', 'Unknown')} is {bottle.get('severity', 'Unknown')} severity",
                    'Risk if Wrong': f"Over/under-investment in solving this bottleneck",
                    'Validation Signal': bottle.get('why_current_solutions_fail', 'N/A'),
                    'Type': 'Implicit (Severity Rating)'
                })
        
        # From Competitive Landscape (market coverage assumption)
        if 'competitive_landscape' in results:
            coverage = results['competitive_landscape'].get('market_coverage_percent', 0)
            all_assumptions.append({
                'Agent': 'Competitive Landscape',
                'Assumption': f"{coverage}% market coverage is sufficient for analysis",
                'Risk if Wrong': f"Missing {100-coverage}% of market could hide key competitors or gaps",
                'Validation Signal': f"Analyzed {results['competitive_landscape'].get('total_solutions_analyzed', 0)} solutions across major vendors",
                'Type': 'Explicit (Coverage)'
            })
        
        # Display assumptions
        if all_assumptions:
            st.metric("Total Assumptions Tracked", len(all_assumptions))
            
            # Filter by type
            types = sorted(set(a['Type'] for a in all_assumptions))
            selected_type = st.selectbox("Filter by Type", ['All'] + types)
            
            filtered_assumptions = all_assumptions if selected_type == 'All' else [
                a for a in all_assumptions if a['Type'] == selected_type
            ]
            
            # Display as cards
            for i, assumption in enumerate(filtered_assumptions, 1):
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
        st.markdown("### 🤖 AI Analysis Assumptions")
        
        st.markdown("""
        <div class="assumption-box">
        <strong>AI Model Assumptions:</strong><br>
        - Claude Sonnet 4.5 was used for all analysis<br>
        - AI decisions are based on patterns in provided data, not domain expertise<br>
        - Confidence ratings reflect data quality and convergence, not certainty<br>
        - All numeric estimates should be validated with domain experts
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()