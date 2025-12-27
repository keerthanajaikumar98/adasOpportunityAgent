👋 Hey there, hope you’re doing great!

I wanted to create a tool to automate a role I really enjoyed at Analog Devices, where I was on the Emerging Business Applications team and worked with an amazing mentor who taught me how to read markets and spot opportunities.

I’ve always kept an eye on the autonomous vehicles industry and have found it fascinating. My capstone project for my Electronics and Communication Engineering degree was an autonomous car, which I later enhanced by adding an accident detection system. That experience made me want a better way to stay plugged into how the industry was evolving.
I especially wanted to keep a pulse on ADAS systems, because that’s where innovation feels rapid and thriving right now. I didn’t want to rely on scattered articles or outdated reports to understand what was changing.
So I created this multi-agent project (with the help of Claude Code) that automatically updates the information every week on Monday at 8 AM. As Andrej Karpathy said, “People who aren’t keeping up even over the last 30 days already have a deprecated worldview.” At the current pace of development, that idea applies far beyond AI and across every fast-moving industry.
I do plan on expanding this over time, but for now this tool is intentionally focused on what a Product Marketing Manager would want to look at when tracking the ADAS space.

**What It Is:**
An autonomous AI system that analyzes the U.S. ADAS semiconductor market and delivers actionable intelligence:

**Market Sizing:** Current market size → Projected growth with CAGR and segment breakdown
**Competitive Mapping:** Comprehensive analysis of leading solutions (NVIDIA, Qualcomm, Mobileye, Tesla, NXP, Renesas, etc.)
**Customer Pain Points:** Identified problems from OEM/Tier-1 reports and industry stakeholders
**Technical Bottlenecks:** Critical barriers blocking next-generation ADAS deployment
**Strategic Opportunities:** Top-ranked ASIC opportunities with market sizing and revenue potential
**Go-to-Market Strategy:** Complete positioning, messaging, elevator pitches, and taglines

Runs automatically every Monday at 8 AM, keeping you current without lifting a finger.

**Architecture: The Multi-Agent Solution**

10 specialized agents work sequentially, each building on previous findings:
┌─────────────────────────────────────────────────────────────┐
│                   Source Discovery                          │
│                   (Finds data sources)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    Market Size                              │
│              (Uses sources to size market)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Trends & Simplification                        │
│        (Uses market data to identify trends)                │
└────────────────┬───────────────────┬────────────────────────┘
                 │                   │
                 ↓                   ↓
┌────────────────────────┐  ┌───────────────────────────────┐
│  Competitive Landscape │  │   Pain Point Extraction       │
│  (Uses market + trends)│  │   (Uses trends context)       │
└────────────┬───────────┘  └──────────┬────────────────────┘
             │                         │
             │        ┌────────────────┘
             │        │
             ↓        ↓
┌─────────────────────────────────────────────────────────────┐
│              Compute Architecture                           │
│    (Uses trends + pain points to define requirements)       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              Bottleneck Diagnosis                           │
│  (Uses competitive + pain points + architecture to find     │
│   gaps between ideal and current solutions)                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                 Gap Analysis                                │
│  (Uses ALL previous agents to identify opportunities)       │
│  Dependencies: market, trends, competitive, pain points,    │
│                bottlenecks                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│            Positioning & Messaging                          │
│    (Uses gap analysis opportunities to create GTM)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│          Visualization & Reporting                          │
│     (Uses ALL agents' data to create final outputs)         │
└─────────────────────────────────────────────────────────────┘

Dependencies Matter:

- Can't identify gaps without knowing the competition
- Can't size opportunities without understanding the market
- Can't create positioning without knowing customer pain points

This is why it's a multi-agent system rather than just one AI call—agents collaborate and build on each other's insights.

**Live Dashboard**
View the live analysis here:
https://adasopportunityagent-ahxgbz4cdj4wk9vg7vwdgb.streamlit.app
Updates automatically every Monday at 8 AM with fresh market intelligence.

Dashboard Features:

- Executive Summary - Key metrics and insights at a glance
- Agent-by-Agent Results - Deep dive into each agent's findings
- Source Attribution - See what's from research (📚) vs AI analysis (🤖)
- Assumptions Tracker - Validate the AI's conclusions
- Interactive Charts - Market growth, competitive positioning, opportunity comparison

Quick Start (Run It Yourself)
# 1. Clone & setup
git clone https://github.com/keerthana-mikkili/asic-opportunity-mapper.git
cd asic-opportunity-mapper
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Add your Anthropic API key
cp .env.template .env
nano .env  # Add your key from console.anthropic.com

# 3. Run analysis
python main.py  # Takes 3-6 minutes, costs ~$0.50-$2.00

# 4. View local dashboard
streamlit run dashboard.py

**Future Expansion**
I'm planning to expand this multi-agent approach to:
- L4/L5 Full Autonomy - Robotaxi market opportunities
- V2X Communication - Vehicle-to-everything semiconductor needs
- In-Cabin Monitoring - Driver/passenger sensing systems
- EV Battery Management - Power electronics and BMS chips


The multi-agent architecture is industry-agnostic—just swap the prompts and sources, and it adapts to any fast-moving market.

Built With

- Python 3.11 - Core language
- Claude Sonnet 4.5 - AI reasoning (Anthropic API)
- Streamlit - Dashboard framework
- Plotly - Interactive charts
- GitHub Actions - Weekly automation


License
MIT License - Use freely for your own market research!

📞 Connect
Keerthana Jaikumar
Product Manager | Market Intelligence 

Built with ❤️ and Claude AI • Keeping pace with the fastest-moving industries on Earth
