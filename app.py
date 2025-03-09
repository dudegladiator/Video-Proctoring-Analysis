import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from main import load_activity_log, load_candidates
from util import get_score_color

# Set page configuration
st.set_page_config(
    page_title="Proctoring Analysis Dashboard",
    page_icon="🔍",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
    .candidate-box {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
    }
    .candidate-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    /* Improved styles for the button */
    .stButton > button {
        width: 100%;
        margin-top: -10px;
        border-radius: 0 0 10px 10px;
        background-color: rgba(0, 0, 0, 0.1);
        border: none;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: rgba(0, 0, 0, 0.2);
        color: white;
        border: none;
    }
    /* Improved analysis section styling */
    .analysis-card {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        background-color: #ffffff;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    .analysis-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .analysis-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 15px;
        color: #333;
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 10px;
    }
    .score-display {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
    }
    .analysis-content {
        color: #333;
        line-height: 1.6;
    }
    .factor-list {
        margin-top: 10px;
        padding-left: 20px;
    }
    .factor-item {
        margin-bottom: 8px;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_candidate' not in st.session_state:
    st.session_state.selected_candidate = None
if 'candidates' not in st.session_state:
    st.session_state.candidates = load_candidates() 
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = 'All'

# Navigation functions
def navigate_to_details(candidate_id):
    st.session_state.selected_candidate = candidate_id
    st.session_state.page = 'details'

def navigate_to_main():
    st.session_state.page = 'main'

# Main page with candidate overview
def show_main_page():
    st.title("📊 Proctoring Analysis Dashboard")
    st.write("Monitor student activity during online examinations")
    
    # Filtering options
    col1, col2 = st.columns(2)
    with col1:
        filter_status = st.selectbox(
            "Filter by Risk Level",
            ['All', 'High Risk', 'Medium Risk', 'Low Risk', 'No Risk']
        )
    with col2:
        search_term = st.text_input("Search by Name", "")
    
    # Apply filters
    filtered_candidates = st.session_state.candidates
    if filter_status != 'All':
        filtered_candidates = [c for c in filtered_candidates if c['status'] == filter_status]
    if search_term:
        filtered_candidates = [c for c in filtered_candidates if search_term.lower() in c['name'].lower()]
    
    if len(filtered_candidates) == 0:
        st.warning("No candidates match your filter criteria")
    else:
        # Dashboard metrics
        st.subheader("Risk Overview")
        metric_cols = st.columns(4)
        
        high_risk = len([c for c in st.session_state.candidates if c['status'] == 'High Risk'])
        medium_risk = len([c for c in st.session_state.candidates if c['status'] == 'Medium Risk'])
        low_risk = len([c for c in st.session_state.candidates if c['status'] == 'Low Risk'])
        no_risk = len([c for c in st.session_state.candidates if c['status'] == 'No Risk'])
        
        metric_cols[0].metric("High Risk", high_risk, f"{high_risk/len(st.session_state.candidates)*100:.1f}%")
        metric_cols[1].metric("Medium Risk", medium_risk, f"{medium_risk/len(st.session_state.candidates)*100:.1f}%")
        metric_cols[2].metric("Low Risk", low_risk, f"{low_risk/len(st.session_state.candidates)*100:.1f}%")
        metric_cols[3].metric("No Risk", no_risk, f"{no_risk/len(st.session_state.candidates)*100:.1f}%")
        
        # Display candidates
        st.subheader(f"Candidates ({len(filtered_candidates)})")
        
        if not filtered_candidates:
            st.info("No candidates match your filter criteria.")
        else:
            # Create grid layout with 4 columns
            cols = st.columns(4)
            
            for i, candidate in enumerate(filtered_candidates):
                with cols[i % 4]:
                    # Create clickable candidate box
                    st.markdown(
                        f"""
                        <div class="candidate-box" style="background-color: {candidate['color']};">
                            <h3 style="color: black;">{candidate['name']}</h3>
                            <p style="color: black;">Risk Score: {candidate['overall_score']}/100</p>
                            <p style="color: black;">Status: {candidate['status']}</p>
                            <p style="color: black; font-size: 0.8em;">{candidate['exam_name']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.button(f"View Details", key=f"btn_{candidate['id']}"):
                        navigate_to_details(candidate['id'])

# Detailed candidate analysis page
def show_details_page():
    candidate_id = st.session_state.selected_candidate
    candidate = next((c for c in st.session_state.candidates if c['id'] == candidate_id), None)
    
    if not candidate:
        st.error("Candidate not found")
        return
    
    # Back button
    if st.button("← Back to Dashboard"):
        navigate_to_main()
    
    st.title(f"Analysis: {candidate['name']}")
    st.write(f"Exam: {candidate['exam_name']} | Date: {candidate['exam_date']}")
    
    # Overall Analysis First
    st.subheader("Overall Risk Assessment")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <h2>Risk Score: {candidate['overall_score']}/100</h2>
            <div style="
                background: linear-gradient(90deg, #4CAF50, #FFEB3B, #FFA726, #FF5252);
                height: 30px;
                border-radius: 15px;
                position: relative;
                margin: 20px 0;
            ">
                <div style="
                    position: absolute;
                    left: {candidate['overall_score']}%;
                    top: -20px;
                    transform: translateX(-50%);
                    font-size: 20px;
                ">▼</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(f"**Status:** {candidate['status']}")
    st.markdown(f"**Analysis:** {candidate['overall_analysis']}")
    
    activity_log = load_activity_log(candidate_id)
    
    # Activity log table
    st.subheader("Activity Log")
    df = pd.DataFrame(activity_log)
    st.dataframe(df, height=300, use_container_width=True)
    
    # JSON view
    with st.expander("View Raw Activity Log"):
        st.json(activity_log)
        
    # Activity timeline visualization - with improvements
    st.subheader("Activity Timeline")
    valid_logs = [log for log in activity_log if log['timeStampInVideo'] != "NaN:NaN:NaN"]
    
    if valid_logs:
        # Define suspicion levels for activities
        activity_levels = {
            # High Suspicion (Level 4)
            "Cell phone detected": 4,
            "Browser window swapped": 4,
            "Copy": 4,
            "Cut": 4,
            "Paste": 4,
            "Laptop detected": 4,
            "No face detected": 4,
            "Tab change detected": 4,
            "Window change detected": 4,
            
            # Medium-High Suspicion (Level 3)
            "Display change detected": 3,
            
            # Medium Suspicion (Level 2)
            "Window focus changed": 2,
            "Candidate looking left": 2,
            
            # Low Suspicion (Level 1)
            "Candidate looking right": 1,
            "Candidate looking down": 1,
            "Candidate looking up": 1,
            "Candidate iris looking left": 1,
            "Candidate iris looking right": 1,
        }
        
        # Convert timestamps to minutes
        timeline_data = []
        for log in valid_logs:
            ts = log['timeStampInVideo']
            parts = ts.split(':')
            minutes = int(parts[0]) * 60 + int(parts[1]) + int(parts[2])/60
            activity = log['activityDescription']
            level = activity_levels.get(activity, 1)  # Default to level 1 if not found
            timeline_data.append({
                'minutes': minutes,
                'activity': activity,
                'level': level
            })
        
        # Sort by time
        timeline_data.sort(key=lambda x: x['minutes'])
        
        # Create plot - IMPROVED: removed first/last 5 min markers
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot activities by suspicion level
        for level in range(4, 0, -1):
            level_data = [item for item in timeline_data if item['level'] == level]
            if level_data:
                minutes = [item['minutes'] for item in level_data]
                activities = [item['activity'] for item in level_data]
                
                # Create continuous line for each suspicion level
                if len(minutes) > 1:
                    ax.plot(minutes, [level] * len(minutes), 
                        marker='o',
                        linestyle='-',
                        linewidth=2,
                        label=f"Level {level} Activities",
                        alpha=0.7)
                else:
                    ax.scatter(minutes, [level] * len(minutes),
                            label=f"Level {level} Activities")
        
        # Customize plot
        ax.set_xlabel('Time (minutes)')
        ax.set_ylabel('Suspicion Level')
        ax.set_yticks([1, 2, 3, 4])
        ax.set_yticklabels(['Low', 'Medium', 'Medium-High', 'High'])
        
        # IMPROVED: removed first/last 5 min markers
        
        # Ensure time doesn't go negative
        ax.set_xlim(left=0)  # Start from 0
        
        # Enhance grid and legend
        ax.grid(True, alpha=0.3)
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Add title and adjust layout
        plt.title('Activity Timeline by Suspicion Level')
        plt.tight_layout()
        
        st.pyplot(fig)
        
        st.info("""
        Activity Suspicion Levels:
        - High: Cell phone, browser swaps, copy/paste, multiple devices
        - Medium-High: Display changes
        - Medium: Window focus changes, looking left
        - Low: Normal looking patterns (right, up, down)
        """)
    
    # IMPROVED: Detailed Analysis Section with better design
    st.markdown("---")  # Separator
    st.subheader("Detailed Analysis")
    
    # AI-Based Analysis - improved styling
    st.markdown(
        f"""
        <div class="analysis-card">
            <div class="analysis-header">AI-Based Analysis</div>
            <div class="score-display" style="background-color: {get_score_color(candidate['ai_based_proctoring']['score'])}; color: white;">
                Score: {candidate['ai_based_proctoring']['score']}/100
            </div>
            <div style="
                background: linear-gradient(90deg, #4CAF50, #FFEB3B, #FFA726, #FF5252);
                height: 30px;
                border-radius: 15px;
                position: relative;
                margin: 20px 0;
            ">
                <div style="
                    position: absolute;
                    left: {candidate['ai_based_proctoring']['score']}%;
                    top: -20px;
                    transform: translateX(-50%);
                    font-size: 20px;
                    color: black;
                ">▼</div>
            </div>
            <div class="analysis-content">
                {candidate['ai_based_proctoring']['analysis']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    
    # Algorithm-Based Analysis - improved styling
    st.markdown(
        f"""
        <div class="analysis-card">
            <div class="analysis-header">Algorithm-Based Analysis</div>
            <div class="score-display" style="background-color: {get_score_color(candidate['algorithm_based_proctoring']['score'])}; color: white;">
                Score: {candidate['algorithm_based_proctoring']['score']}/100
            </div>
            <div style="
                background: linear-gradient(90deg, #4CAF50, #FFEB3B, #FFA726, #FF5252);
                height: 30px;
                border-radius: 15px;
                position: relative;
                margin: 20px 0;
            ">
                <div style="
                    position: absolute;
                    left: {candidate['algorithm_based_proctoring']['score']}%;
                    top: -20px;
                    transform: translateX(-50%);
                    font-size: 20px;
                    color: black;
                ">▼</div>
            </div>
            <div class="analysis-content">
                <strong>Key Factors:</strong>
                <ul class="factor-list">
                    <li class="factor-item">{candidate['algorithm_based_proctoring']['factor1']}</li>
                    <li class="factor-item">{candidate['algorithm_based_proctoring']['factor2']}</li>
                    <li class="factor-item">{candidate['algorithm_based_proctoring']['factor3']}</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ML-Based Analysis - improved styling
    st.markdown(
        f"""
        <div class="analysis-card">
            <div class="analysis-header">ML-Based Analysis</div>
            <div class="score-display" style="background-color: {get_score_color(candidate['ml_based_proctoring']['score'])}; color: white;">
                Score: {candidate['ml_based_proctoring']['score']}/100
            </div>
            <div style="
                background: linear-gradient(90deg, #4CAF50, #FFEB3B, #FFA726, #FF5252);
                height: 30px;
                border-radius: 15px;
                position: relative;
                margin: 20px 0;
            ">
                <div style="
                    position: absolute;
                    left: {candidate['ml_based_proctoring']['score']}%;
                    top: -20px;
                    transform: translateX(-50%);
                    font-size: 20px;
                    color: black;
                ">▼</div>
            </div>
            <div class="analysis-content">
                <p>Machine learning model evaluation based on patterns detected in candidate's activity.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Additional graphs for deeper analysis
    st.markdown("---")

    # Create two columns for side-by-side graphs
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Activity Type Distribution")
        
        # Count activities by type
        activity_counts = {}
        for event in activity_log:
            desc = event.get("activityDescription", "")
            count = event.get("count", 1)
            if desc in activity_counts:
                activity_counts[desc] += count
            else:
                activity_counts[desc] = count
        
        # Create pie chart of activity types
        if activity_counts:
            fig1, ax1 = plt.subplots(figsize=(8, 8))
            labels = list(activity_counts.keys())
            sizes = list(activity_counts.values())
            
            # Custom colors based on suspicion level
            colors = []
            for label in labels:
                if label in ["Browser window swapped", "Window change detected"]:
                    colors.append("#FF5252")  # Red for high risk
                elif label in ["Window focus changed"]:
                    colors.append("#FFA726")  # Orange for medium risk
                else:
                    colors.append("#4CAF50")  # Green for low risk
            
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
            ax1.axis('equal')
            
            st.pyplot(fig1)
            st.caption("Distribution of activity types, colored by risk level")

    with col2:
        st.markdown("#### Activity Heatmap by Exam Period")
        
        # Create heatmap of activity intensity across exam time
        valid_logs = [log for log in activity_log if log.get("timeStampInVideo") != "NaN:NaN:NaN"]
        
        if valid_logs:
            # Convert timestamps to minutes for the heatmap
            time_bins = {
                "0-5min": 0,
                "5-15min": 0,
                "15-30min": 0, 
                "30min+": 0
            }
            
            high_risk_bins = time_bins.copy()
            med_risk_bins = time_bins.copy()
            low_risk_bins = time_bins.copy()
            
            for log in valid_logs:
                ts = log.get("timeStampInVideo", "00:00:00")
                parts = ts.split(':')
                minutes = int(parts[0]) * 60 + int(parts[1])
                
                # Determine which bin this activity belongs to
                if minutes < 5:
                    time_period = "0-5min"
                elif minutes < 15:
                    time_period = "5-15min"
                elif minutes < 30:
                    time_period = "15-30min"
                else:
                    time_period = "30min+"
                
                # Determine risk level based on activity type
                activity = log.get("activityDescription", "")
                if activity in ["Browser window swapped", "Window change detected"]:
                    high_risk_bins[time_period] += 1
                elif activity in ["Window focus changed"]:
                    med_risk_bins[time_period] += 1
                else:
                    low_risk_bins[time_period] += 1
            
            # Create heatmap data
            time_periods = list(time_bins.keys())
            risk_levels = ["High Risk", "Medium Risk", "Low Risk"]
            
            data = np.array([
                list(high_risk_bins.values()),
                list(med_risk_bins.values()),
                list(low_risk_bins.values())
            ])
            
            fig2, ax2 = plt.subplots(figsize=(8, 6))
            im = ax2.imshow(data, cmap="YlOrRd")
            
            # Show all ticks and label them
            ax2.set_xticks(np.arange(len(time_periods)))
            ax2.set_yticks(np.arange(len(risk_levels)))
            ax2.set_xticklabels(time_periods)
            ax2.set_yticklabels(risk_levels)
            
            # Rotate the tick labels and align them
            plt.setp(ax2.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            
            # Loop over data dimensions and create text annotations
            for i in range(len(risk_levels)):
                for j in range(len(time_periods)):
                    ax2.text(j, i, data[i, j], ha="center", va="center", color="black")
            
            ax2.set_title("Activity Intensity by Time Period")
            fig2.tight_layout()
            
            # Add colorbar
            cbar = fig2.colorbar(im)
            cbar.set_label("Number of Activities")
            
            st.pyplot(fig2)
            st.caption("Activity frequency by risk level and exam period")


# Route to the correct page
if st.session_state.page == 'main':
    show_main_page()
elif st.session_state.page == 'details':
    show_details_page()
