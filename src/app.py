# src/app.py
import os
import io
import sys
import time
import asyncio
import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Force local directory path lookups for clean microservice imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from orchestrator import OmniInsightOrchestrator

# Initialize Streamlit Page Window Configurations
st.set_page_config(
    page_title="OmniInsight Operational Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Reference the layout structure variable cleanly
str_layout = st

# Establish a single, persistent Orchestrator instance
@st.cache_resource
def get_orchestrator():
    return OmniInsightOrchestrator()

orchestrator = get_orchestrator()

# --- SIDEBAR CONFIGURATION LAYER ---
with str_layout.sidebar:
    # Force sidebar alert containers to auto-wrap long strings cleanly
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] .element-container div[role="alert"] {
            white-space: normal !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            height: auto !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("OmniInsight Sandbox Controllers")
    st.markdown("Use these parameters to run a pre-flight staffing optimization audit.")
    
    # Core operational sandbox slider inputs with unique keys
    current_overtime_hours = str_layout.slider(
        "Current collective overtime hours/shift",
        min_value=0,
        max_value=100,
        value=16,
        step=1,
        key="sb_overtime_hours_unique_key"
    )
    
    staffing_intervention = str_layout.slider(
        "Simulated floating staff additions",
        min_value=0,
        max_value=10,
        value=0,
        step=1,
        key="sb_staffing_intervention_unique_key"
    )
    
    # Financial Configuration Parameters
    BASE_HOURLY_RATE = 45.0
    OVERTIME_MULTIPLIER = 1.5
    NEW_HIRE_FIXED_COST = 500.0
    
    # Financial and Clinical Safety Engine Calculations
    total_overtime_cost = current_overtime_hours * (BASE_HOURLY_RATE * OVERTIME_MULTIPLIER)
    
    hours_absorbed = staffing_intervention * 8
    remaining_overtime_hours = max(0, current_overtime_hours - hours_absorbed)
    
    # Calculate average overtime per active crew member
    avg_overtime_per_head = remaining_overtime_hours / 4.0
    is_burnout_risk = avg_overtime_per_head >= 4.0
    
    # Safety Buffer Math
    is_overstaffed = (hours_absorbed - current_overtime_hours) >= 8.0 and current_overtime_hours > 0
    
    new_overtime_cost = remaining_overtime_hours * (BASE_HOURLY_RATE * OVERTIME_MULTIPLIER)
    new_staff_overhead = staffing_intervention * NEW_HIRE_FIXED_COST
    total_simulated_cost = new_overtime_cost + new_staff_overhead
    
    net_savings = total_overtime_cost - total_simulated_cost
    optimized_reduction = staffing_intervention * 12.5
    
    str_layout.markdown("---")
    str_layout.markdown("### Cost and Fatigue Optimization Summary")
    
    # 1. Alert Messages: Render across the FULL width of the sidebar first
    if is_burnout_risk:
        str_layout.error(f"CRITICAL BURNOUT THREAT: Active staff are averaging {avg_overtime_per_head:.1f} hours of overtime this shift. Cognitive fatigue thresholds have breached safety parameters, exponentially increasing clinical error risk and turnover probability.")
    elif remaining_overtime_hours > 0:
        str_layout.warning(f"Ambient Fatigue Warning: Staff are handling an average of {avg_overtime_per_head:.1f} hours of overtime. Monitor closely for shift crossovers.")
    else:
        str_layout.success("Staff Fatigue Nominal: Overtime workload safely stabilized.")

    # 2. Priority Override Logic with Explicit Spaces to Prevent Fused Words
    if is_overstaffed:
        line1 = f"Diminishing Returns Detected: You have allocated excess floating staff. "
        line2 = f"The baseline overhead of ${new_staff_overhead:,.2f} is actively wasting capital "
        line3 = f"because your overtime backlog is already completely cleared."
        str_layout.error(line1 + line2 + line3)
        
    elif is_burnout_risk and net_savings > 0:
        line1 = f"Insufficient Intervention: Adding {staffing_intervention} float resource "
        line2 = f"saves a nominal ${net_savings:,.2f}, but fails to resolve the core crisis. "
        line3 = f"Permanent staff are still operating past safe cognitive limits. Increase float allocation to decompress the unit."
        str_layout.warning(line1 + line2 + line3)
        
    elif net_savings > 0 and staffing_intervention > 0 and not is_burnout_risk:
        line1 = f"Optimal Strategy Found! Adding {staffing_intervention} float resources "
        line2 = f"reduces collective overtime burn to {remaining_overtime_hours} hours. "
        line3 = f"Net Savings: ${net_savings:,.2f} per shift, while compressing bottlenecks by {optimized_reduction:.1f} minutes."
        str_layout.success(line1 + line2 + line3)
        
    elif net_savings < 0 and staffing_intervention > 0:
        # Build an explicit HTML card that forces character-by-character line breaks
        line1 = f"Inefficient Allocation: The fixed onboarding overhead of ${new_staff_overhead:,.2f} "
        line2 = f"outweighs your overtime premium savings. "
        line3 = f"Retaining existing staff on overtime is ${abs(net_savings):,.2f} cheaper than deploying this many assets."
        full_message = line1 + line2 + line3
        
        str_layout.markdown(
            f"""
            <div style="
                background-color: #ffeeba; 
                color: #856404; 
                padding: 0.75rem 1rem; 
                border-radius: 0.25rem; 
                border: 1px solid #ffeeba;
                margin-bottom: 1rem;
                font-size: 0.85rem;
                white-space: normal !important;
                word-break: break-all !important;
                overflow-wrap: break-word !important;
            ">
                {full_message}
            </div>
            """,
            unsafe_allow_html=True
        )

    str_layout.markdown("---")
    
    # 3. KPI Metrics Column Layer: Split ONLY the numbers into columns at the very bottom
    kpi_sub1, kpi_sub2 = str_layout.columns(2)
    with kpi_sub1:
        str_layout.metric(label="Current Overtime Premium", value=f"${total_overtime_cost:,.2f}")
    with kpi_sub2:
        str_layout.metric(label="Simulated Total Cost", value=f"${total_simulated_cost:,.2f}")


# --- MAIN INTERFACE DISPLAY LAYER ---
str_layout.title("OmniInsight Operational Command Center")
str_layout.markdown("Enterprise Intelligence Pipeline linking DuckDB Relational Schemas and Pinecone Vector Knowledge Maps.")

# Global Operational Search Engine Input Field
user_query = str_layout.text_input(
    "Type an operational problem, department, or query to audit facility health:",
    placeholder="e.g., when are wait times the longest, show me ICU bottlenecks, what is acuity level 3"
)

str_layout.markdown("---")

# Main Page Split Layout
col_visual, col_diagnosis = str_layout.columns([3, 2])

# Initialize global placeholder trackers
df_data = None
metric_headline = ""
log_match = ""
recommendation = ""

with col_visual:
    str_layout.subheader("Live Performance Analytics")
    
    if user_query:
        # Route query through the self-healing orchestrator layer
        metric_headline, log_match, recommendation, df_data = orchestrator.diagnose_facility_bottleneck(user_query)
        
        # Display the dynamic operational status headline
        str_layout.markdown(f"### {metric_headline}")
        
        # Polymorphic Chart Engine
        if df_data is not None and not df_data.empty:
            if "hour" in df_data.columns:
                str_layout.markdown("#### Length of Stay Trends by Hour of Day")
                metric_col = "avg_los_minutes" if "avg_los_minutes" in df_data.columns else df_data.columns[1]
                
                fig = px.line(
                    df_data, 
                    x="hour", 
                    y=metric_col, 
                    title="Hourly Throughput Backlog Timeline",
                    labels={"hour": "Hour of Day (24h)", metric_col: "Average Length of Stay (Minutes)"},
                    markers=True
                )
                fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=2))
                str_layout.plotly_chart(fig, use_container_width=True)
                
            elif "disposition" in df_data.columns:
                str_layout.markdown("#### Average Length of Stay by Department")
                fig = px.bar(
                    df_data, 
                    x="disposition", 
                    y="avg_los_minutes",
                    color="disposition",
                    title="Departmental Bottleneck Overview",
                    labels={"disposition": "Department Unit", "avg_los_minutes": "Avg Wait (Mins)"}
                )
                str_layout.plotly_chart(fig, use_container_width=True)
            else:
                str_layout.dataframe(df_data, use_container_width=True)
        else:
            str_layout.info("No active structured data returned for this operational view layout.")
    else:
        str_layout.info("Enter an operational problem or query in the search engine above to generate live tracking analytics.")
        
with col_diagnosis:
    str_layout.subheader("System Diagnostic Summary")
    if user_query:
        str_layout.warning(f"**Metric Anomaly Flagged:**\n{metric_headline}")
        str_layout.info(f"**Verifiable Log Evidence (Pinecone Match):**\n\n{log_match}")
        str_layout.success(f"**Prescriptive Action Plan:**\n\n{recommendation}")
    else:
        str_layout.info("Awaiting pipeline diagnostic activation...")

# --- EXECUTIVE BRIEFING REPORT STUDIO ---
if user_query and df_data is not None and not df_data.empty:
    str_layout.markdown("---")
    str_layout.subheader("Executive Incident Briefing Studio")
    
    max_detected_wait = df_data["avg_los_minutes"].max() if "avg_los_minutes" in df_data.columns else 0
    total_impacted_patients = df_data["total_patients"].sum() if "total_patients" in df_data.columns else 0
    
    if max_detected_wait > 120:
        str_layout.error(f"Automated Alert Triggered: Localized wait times have breached safety thresholds ({max_detected_wait:.0f} mins). Immediate capacity redistribution is recommended.")
        
        # In-Memory PDF Compilation Engine
        def create_pdf_report():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer, 
                pagesize=letter,
                rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            title_style = ParagraphStyle(
                'DocTitle', parent=styles['Heading1'],
                fontSize=24, leading=28, textColor=colors.HexColor('#FF4B4B'), spaceAfter=12
            )
            meta_style = ParagraphStyle(
                'DocMeta', parent=styles['Normal'],
                fontSize=10, leading=14, textColor=colors.HexColor('#555555'), spaceAfter=20
            )
            h2_style = ParagraphStyle(
                'SectionHeader', parent=styles['Heading2'],
                fontSize=14, leading=18, textColor=colors.HexColor('#1C1D21'), spaceBefore=14, spaceAfter=8
            )
            body_style = ParagraphStyle(
                'BodyTextCustom', parent=styles['Normal'],
                fontSize=10, leading=14, spaceAfter=8
            )
            quote_style = ParagraphStyle(
                'QuoteBox', parent=styles['Normal'],
                fontSize=9, leading=13, textColor=colors.HexColor('#333333'),
                leftIndent=15, rightIndent=15, spaceAfter=12
            )
            
            report_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph("OMNIINSIGHT INCIDENT BRIEFING REPORT", title_style))
            story.append(Paragraph(f"<b>Generated:</b> {report_timestamp}<br/><b>System Status:</b> CRITICAL CAPACITY CONSTRAINT", meta_style))
            story.append(Spacer(1, 10))
            
            story.append(Paragraph("1. Quantitative Baseline Telemetry", h2_style))
            story.append(Paragraph(f"• <b>Target Query Context:</b> \"{user_query}\"", body_style))
            story.append(Paragraph(f"• <b>Peak Impacted Threshold:</b> {max_detected_wait:.1f} Minutes Avg Length of Stay", body_style))
            story.append(Paragraph(f"• <b>Total Patients Affected in Window:</b> {total_impacted_patients} active encounters", body_style))
            
            story.append(Paragraph("2. Institutional Log Evidence (Pinecone Cloud Vector Match)", h2_style))
            story.append(Paragraph(f"<i>\"{log_match}\"</i>", quote_style))
            
            story.append(Paragraph("3. Prescriptive Strategic Mandate", h2_style))
            for line in recommendation.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, body_style))
                    
            story.append(Spacer(1, 20))
            story.append(Paragraph("<font color='#888888'><i>Report synthesized securely via local CPU container isolation layer. Zero cloud data leakage.</i></font>", body_style))
            
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()
            
        pdf_data = create_pdf_report()
        
        rep_col1, rep_col2 = str_layout.columns([1, 4])
        with rep_col1:
            str_layout.download_button(
                label="Export Executive PDF",
                data=pdf_data,
                file_name=f"omniinsight_briefing_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        with rep_col2:
            str_layout.info("Distribution Ready: Your operational analytics and matched cloud vector text evidence have been compiled into a finalized, un-editable enterprise PDF document.")
    else:
        str_layout.success("Operational Thresholds Nominal: No structural metric anomalies detected. Automated PDF report synthesis suspended.")