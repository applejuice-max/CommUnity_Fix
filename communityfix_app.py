import streamlit as st
import pandas as pd
import datetime
import json
from pathlib import Path
import base64
import io
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="CommUnityFix - Barangay Union",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79, #2e7d32);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .emergency-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .success-card {
        background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .report-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .status-received { border-left-color: #ffc107; }
    .status-progress { border-left-color: #17a2b8; }
    .status-resolved { border-left-color: #28a745; }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1f4e79, #2e7d32);
    }
    .stButton > button {
        background: linear-gradient(90deg, #007bff, #0056b3);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #0056b3, #004085);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data storage
if 'reports' not in st.session_state:
    st.session_state.reports = []
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False
if 'admin_password' not in st.session_state:
    st.session_state.admin_password = "admin123"  # Default password

# Data persistence functions
def save_data_to_file():
    """Save reports data to JSON file"""
    try:
        data = {
            'reports': st.session_state.reports,
            'last_updated': datetime.datetime.now().isoformat()
        }
        with open('reports_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving data: {e}")

def load_data_from_file():
    """Load reports data from JSON file"""
    try:
        if Path('reports_data.json').exists():
            with open('reports_data.json', 'r') as f:
                data = json.load(f)
                st.session_state.reports = data.get('reports', [])
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Load data on startup
load_data_from_file()

# Sample emergency contacts
EMERGENCY_CONTACTS = {
    "Barangay Hall": "123-4567",
    "Police Station": "911",
    "Fire Department": "911",
    "Hospital Emergency": "911",
    "Rescue Services": "123-4567"
}

# Sample tips for minor problems
TIPS = [
    "For minor garbage issues: Separate biodegradable from non-biodegradable waste",
    "Small potholes: Mark the area with visible objects to alert others while waiting for repair",
    "Streetlight issues: Note the exact location and pole number if available",
    "Drainage problems: Clear visible debris if safe to do so",
    "Graffiti: Document with photos for proper reporting"
]

def save_report(name, contact, issue_type, location, description, photo=None):
    """Save a new report to session state"""
    report_id = len(st.session_state.reports) + 1
    
    # Handle photo upload
    photo_data = None
    if photo is not None:
        try:
            # Convert uploaded file to base64 for storage
            photo_data = base64.b64encode(photo.read()).decode()
        except Exception as e:
            st.warning(f"Could not process photo: {e}")
    
    new_report = {
        'id': report_id,
        'name': name,
        'contact': contact,
        'issue_type': issue_type,
        'location': location,
        'description': description,
        'status': 'Received',
        'assigned_to': 'Not assigned',
        'date_reported': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'comments': [],
        'photo': photo_data,
        'priority': 'Medium'  # Default priority
    }
    st.session_state.reports.append(new_report)
    
    # Save to file
    save_data_to_file()
    
    return report_id

def add_comment(report_id, comment_text, author="Admin"):
    """Add a comment to a report"""
    for report in st.session_state.reports:
        if report['id'] == report_id:
            comment = {
                'author': author,
                'text': comment_text,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            report['comments'].append(comment)
            break

def create_progress_charts():
    """Create various charts for progress tracking"""
    if not st.session_state.reports:
        return None, None, None, None
    
    # Convert reports to DataFrame for easier analysis
    df = pd.DataFrame(st.session_state.reports)
    df['date_reported'] = pd.to_datetime(df['date_reported'])
    
    # 1. Status Distribution Pie Chart
    status_counts = df['status'].value_counts()
    status_colors = {'Received': '#ffc107', 'In Progress': '#17a2b8', 'Resolved': '#28a745'}
    
    fig_pie = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Report Status Distribution",
        color_discrete_map=status_colors
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # 2. Issue Type Bar Chart
    issue_counts = df['issue_type'].value_counts()
    fig_bar = px.bar(
        x=issue_counts.index,
        y=issue_counts.values,
        title="Reports by Issue Type",
        labels={'x': 'Issue Type', 'y': 'Number of Reports'},
        color=issue_counts.values,
        color_continuous_scale='Blues'
    )
    fig_bar.update_layout(showlegend=False)
    
    # 3. Timeline Chart
    df_daily = df.groupby(df['date_reported'].dt.date).size().reset_index(name='count')
    fig_timeline = px.line(
        df_daily,
        x='date_reported',
        y='count',
        title="Reports Over Time",
        labels={'date_reported': 'Date', 'count': 'Number of Reports'}
    )
    fig_timeline.update_traces(line=dict(width=3))
    
    # 4. Resolution Time Analysis
    resolved_reports = df[df['status'] == 'Resolved'].copy()
    if not resolved_reports.empty:
        # Calculate days to resolution (simplified - using current date as resolution date)
        resolved_reports['days_to_resolution'] = (datetime.datetime.now() - resolved_reports['date_reported']).dt.days
        avg_resolution_time = resolved_reports['days_to_resolution'].mean()
        
        fig_resolution = px.histogram(
            resolved_reports,
            x='days_to_resolution',
            title=f"Resolution Time Distribution (Avg: {avg_resolution_time:.1f} days)",
            labels={'days_to_resolution': 'Days to Resolution', 'count': 'Number of Reports'},
            nbins=10
        )
    else:
        fig_resolution = None
    
    return fig_pie, fig_bar, fig_timeline, fig_resolution

def organize_reports_by_status():
    """Organize reports by status for better admin management"""
    if not st.session_state.reports:
        return {}
    
    organized = {
        'Received': [],
        'In Progress': [],
        'Resolved': []
    }
    
    for report in st.session_state.reports:
        status = report['status']
        if status in organized:
            organized[status].append(report)
    
    return organized

def organize_reports_by_priority():
    """Organize reports by priority level"""
    if not st.session_state.reports:
        return {}
    
    organized = {
        'Emergency': [],
        'High': [],
        'Medium': [],
        'Low': []
    }
    
    for report in st.session_state.reports:
        priority = report.get('priority', 'Medium')
        if priority in organized:
            organized[priority].append(report)
    
    return organized

def organize_reports_by_date():
    """Organize reports by date (Today, This Week, This Month, Older)"""
    if not st.session_state.reports:
        return {}
    
    now = datetime.datetime.now()
    today = now.date()
    week_ago = today - datetime.timedelta(days=7)
    month_ago = today - datetime.timedelta(days=30)
    
    organized = {
        'Today': [],
        'This Week': [],
        'This Month': [],
        'Older': []
    }
    
    for report in st.session_state.reports:
        report_date = datetime.datetime.strptime(report['date_reported'], "%Y-%m-%d %H:%M").date()
        
        if report_date == today:
            organized['Today'].append(report)
        elif report_date >= week_ago:
            organized['This Week'].append(report)
        elif report_date >= month_ago:
            organized['This Month'].append(report)
        else:
            organized['Older'].append(report)
    
    return organized

def organize_reports_by_issue_type():
    """Organize reports by issue type"""
    if not st.session_state.reports:
        return {}
    
    organized = {}
    for report in st.session_state.reports:
        issue_type = report['issue_type']
        if issue_type not in organized:
            organized[issue_type] = []
        organized[issue_type].append(report)
    
    return organized

def display_organized_reports(organized_reports, title, show_actions=True, context=""):
    """Display organized reports in a clean format"""
    st.subheader(title)
    
    if not organized_reports:
        st.info("No reports in this category.")
        return
    
    for category, reports in organized_reports.items():
        if reports:  # Only show categories that have reports
            with st.expander(f"{category} ({len(reports)} reports)", expanded=False):
                for report in reports:
                    # Create a card-like display for each report
                    status_color = {
                        'Received': '🟡',
                        'In Progress': '🔵', 
                        'Resolved': '🟢'
                    }.get(report['status'], '⚪')
                    
                    priority_emoji = {
                        'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 'Emergency': '🔴'
                    }.get(report.get('priority', 'Medium'), '⚪')
                    
                    col1, col2, col3 = st.columns([4, 2, 1])
                    
                    with col1:
                        st.write(f"**{status_color} Report #{report['id']}** - {report['issue_type']}")
                        st.write(f"📍 {report['location']}")
                        st.write(f"👤 {report['name']} - {report['date_reported']}")
                        st.write(f"📝 {report['description'][:100]}{'...' if len(report['description']) > 100 else ''}")
                    
                    with col2:
                        st.write(f"**Status:** {report['status']}")
                        st.write(f"**Priority:** {priority_emoji} {report.get('priority', 'Medium')}")
                        st.write(f"**Assigned:** {report['assigned_to']}")
                    
                    with col3:
                        if show_actions:
                            # Make keys unique by adding context
                            unique_key_base = f"{context}_{category}_{report['id']}"
                            if st.button(f"Quick Update", key=f"quick_{unique_key_base}"):
                                st.session_state[f"quick_update_{unique_key_base}"] = True
                            
                            if st.button(f"View Full", key=f"full_{unique_key_base}"):
                                st.session_state[f"view_full_{unique_key_base}"] = True
                    
                    # Quick update form
                    unique_key_base = f"{context}_{category}_{report['id']}"
                    if st.session_state.get(f"quick_update_{unique_key_base}", False):
                        with st.form(f"quick_form_{unique_key_base}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                new_status = st.selectbox("Status", 
                                    ["Received", "In Progress", "Resolved"],
                                    index=["Received", "In Progress", "Resolved"].index(report['status']),
                                    key=f"status_{unique_key_base}")
                            with col2:
                                new_priority = st.selectbox("Priority",
                                    ["Low", "Medium", "High", "Emergency"],
                                    index=["Low", "Medium", "High", "Emergency"].index(report.get('priority', 'Medium')),
                                    key=f"priority_{unique_key_base}")
                            
                            assigned_to = st.text_input("Assign To", value=report['assigned_to'], key=f"assign_{unique_key_base}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("Update"):
                                    report['status'] = new_status
                                    report['priority'] = new_priority
                                    report['assigned_to'] = assigned_to
                                    save_data_to_file()
                                    st.session_state[f"quick_update_{unique_key_base}"] = False
                                    st.success("Report updated!")
                                    st.rerun()
                            with col2:
                                if st.form_submit_button("Cancel"):
                                    st.session_state[f"quick_update_{unique_key_base}"] = False
                                    st.rerun()
                    
                    # Full view
                    if st.session_state.get(f"view_full_{unique_key_base}", False):
                        with st.expander(f"Full Report #{report['id']} Details", expanded=True):
                            st.write(f"**Reporter:** {report['name']}")
                            st.write(f"**Contact:** {report['contact']}")
                            st.write(f"**Issue Type:** {report['issue_type']}")
                            st.write(f"**Location:** {report['location']}")
                            st.write(f"**Description:** {report['description']}")
                            st.write(f"**Date Reported:** {report['date_reported']}")
                            st.write(f"**Status:** {report['status']}")
                            st.write(f"**Priority:** {report.get('priority', 'Medium')}")
                            st.write(f"**Assigned To:** {report['assigned_to']}")
                            
                            # Show photo if available
                            if report.get('photo'):
                                try:
                                    photo_data = base64.b64decode(report['photo'])
                                    st.image(photo_data, caption="Report Photo", use_column_width=True)
                                except:
                                    st.warning("Could not display photo")
                            
                            # Show comments
                            if report.get('comments'):
                                st.write("**Comments & Updates:**")
                                for comment in reversed(report['comments']):
                                    st.write(f"💬 **{comment['author']}** ({comment['timestamp']}): {comment['text']}")
                            
                            if st.button(f"Close Full View", key=f"close_full_{unique_key_base}"):
                                st.session_state[f"view_full_{unique_key_base}"] = False
                                st.rerun()
                    
                    st.divider()

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🏘️ CommUnityFix</h1>
        <h3>Barangay Union - Community Issue Reporting System</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🏘️ CommUnityFix")
    st.sidebar.markdown("**Barangay Union**")
    st.sidebar.markdown("---")
    
    if not st.session_state.admin_logged_in:
        page = st.sidebar.radio("Navigation", ["Report Issue", "Emergency Contacts", "Progress Dashboard", "Admin Login"])
    else:
        page = st.sidebar.radio("Navigation", ["Report Issue", "Emergency Contacts", "Progress Dashboard", "Admin Dashboard", "Logout"])
    
    # Report Issue Page
    if page == "Report Issue":
        show_report_page()
    
    # Emergency Contacts Page
    elif page == "Emergency Contacts":
        show_contacts_page()
    
    # Progress Dashboard Page
    elif page == "Progress Dashboard":
        show_progress_dashboard()
    
    # Admin Login Page
    elif page == "Admin Login":
        show_admin_login()
    
    # Admin Dashboard
    elif page == "Admin Dashboard":
        if st.session_state.admin_logged_in:
            show_admin_dashboard()
        else:
            st.warning("Please log in first")
            show_admin_login()
    
    # Logout
    elif page == "Logout":
        st.session_state.admin_logged_in = False
        st.success("Logged out successfully!")
        st.rerun()

def show_report_page():
    st.title("📝 Report a Community Issue")
    st.markdown("Use this form to report problems in our community. Your reports help make Barangay Union better!")
    
    # Add some helpful information
    with st.expander("ℹ️ Before Reporting"):
        st.write("""
        - **Take a photo** if possible to help us understand the issue better
        - **Be specific** about the location (street names, landmarks, house numbers)
        - **Describe the severity** and any safety concerns
        - **Include your contact** so we can follow up if needed
        """)
    
    with st.form("report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Your Name *", placeholder="Enter your full name")
            contact = st.text_input("Contact Number *", placeholder="09XXXXXXXXX", help="Include area code if applicable")
            issue_type = st.selectbox(
                "Issue Type *",
                ["Pothole", "Garbage Accumulation", "Broken Streetlight", 
                 "Clogged Drainage", "Graffiti", "Damaged Road", "Water Leak", 
                 "Noise Complaint", "Safety Hazard", "Other"]
            )
            priority = st.selectbox(
                "Priority Level",
                ["Low", "Medium", "High", "Emergency"],
                help="Emergency: Immediate danger to life/property"
            )
        
        with col2:
            location = st.text_input("Location *", placeholder="Ex: Near Barangay Hall, Main Street")
            description = st.text_area("Description *", placeholder="Please describe the issue in detail...", height=100)
            photo = st.file_uploader("Upload Photo (Optional)", type=['png', 'jpg', 'jpeg'], help="Maximum file size: 5MB")
            
            # Show photo preview if uploaded
            if photo is not None:
                try:
                    image = Image.open(photo)
                    st.image(image, caption="Photo Preview", use_column_width=True)
                except Exception as e:
                    st.warning(f"Could not preview image: {e}")
        
        st.markdown("**Required fields*")
        submitted = st.form_submit_button("🚀 Submit Report", use_container_width=True)
        
        if submitted:
            # Enhanced validation
            errors = []
            if not name or len(name.strip()) < 2:
                errors.append("Please enter a valid name (at least 2 characters)")
            if not contact or len(contact.strip()) < 10:
                errors.append("Please enter a valid contact number (at least 10 digits)")
            if not location or len(location.strip()) < 5:
                errors.append("Please provide a more specific location")
            if not description or len(description.strip()) < 10:
                errors.append("Please provide a more detailed description (at least 10 characters)")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                report_id = save_report(name, contact, issue_type, location, description, photo)
                st.markdown(f"""
                <div class="success-card">
                    <h3>✅ Report Submitted Successfully!</h3>
                    <p><strong>Report ID:</strong> #{report_id}</p>
                    <p>Thank you for helping improve our community!</p>
                </div>
                """, unsafe_allow_html=True)
                st.info("📞 You can check the status of your report by contacting Barangay Hall or logging in as admin.")

def show_contacts_page():
    st.title("📞 Emergency Contacts & Tips")
    
    st.header("🚨 Emergency Contacts")
    col1, col2 = st.columns(2)
    
    with col1:
        for service, number in list(EMERGENCY_CONTACTS.items())[:3]:
            st.markdown(f"""
            <div class="emergency-card">
                <h4>{service}</h4>
                <h2>{number}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for service, number in list(EMERGENCY_CONTACTS.items())[3:]:
            st.markdown(f"""
            <div class="emergency-card">
                <h4>{service}</h4>
                <h2>{number}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.header("🛠️ Tips for Minor Problems")
    
    for i, tip in enumerate(TIPS, 1):
        st.markdown(f"""
        <div class="report-card">
            <strong>{i}.</strong> {tip}
        </div>
        """, unsafe_allow_html=True)
    
    st.header("🚨 Emergency Procedures")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("🏥 Medical Emergency", expanded=False):
            st.write("""
            **Immediate Actions:**
            1. Call emergency services immediately (911)
            2. Provide clear location details
            3. Do not move injured person unless necessary
            4. Have someone wait to guide emergency responders
            5. Apply first aid if trained
            """)
        
        with st.expander("🔥 Fire Emergency", expanded=False):
            st.write("""
            **Immediate Actions:**
            1. Alert everyone in the area
            2. Call fire department (911)
            3. Use fire extinguisher if safe
            4. Evacuate immediately if fire spreads
            5. Meet at designated assembly point
            """)
    
    with col2:
        with st.expander("🌪️ Natural Disasters", expanded=False):
            st.write("""
            **General Guidelines:**
            1. Stay informed through official channels
            2. Follow evacuation orders immediately
            3. Have emergency kit ready
            4. Stay away from windows and doors
            5. Check on neighbors if safe
            """)
        
        with st.expander("🚨 Security Issues", expanded=False):
            st.write("""
            **Safety Measures:**
            1. Call police immediately (911)
            2. Do not confront suspicious persons
            3. Lock doors and windows
            4. Stay in safe location
            5. Report to barangay officials
            """)
    
    # Quick action buttons
    st.header("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📞 Call Emergency (911)", use_container_width=True):
            st.info("Dial 911 for immediate emergency assistance")
    
    with col2:
        if st.button("🏛️ Contact Barangay Hall", use_container_width=True):
            st.info("Barangay Hall: 123-4567")
    
    with col3:
        if st.button("📝 Report Issue", use_container_width=True):
            st.info("Use the 'Report Issue' page to submit non-emergency problems")

def show_progress_dashboard():
    st.title("📊 Progress Dashboard")
    st.markdown("Track the progress of community reports and get insights into issue resolution")
    
    if not st.session_state.reports:
        st.info("No reports available yet. Submit some reports to see progress tracking!")
        return
    
    # Key Metrics Section
    st.header("📈 Key Metrics")
    
    total_reports = len(st.session_state.reports)
    received = len([r for r in st.session_state.reports if r['status'] == 'Received'])
    in_progress = len([r for r in st.session_state.reports if r['status'] == 'In Progress'])
    resolved = len([r for r in st.session_state.reports if r['status'] == 'Resolved'])
    
    # Calculate additional metrics
    resolution_rate = (resolved / total_reports * 100) if total_reports > 0 else 0
    avg_resolution_time = 0
    if resolved > 0:
        resolved_reports = [r for r in st.session_state.reports if r['status'] == 'Resolved']
        total_days = sum([(datetime.datetime.now() - datetime.datetime.strptime(r['date_reported'], "%Y-%m-%d %H:%M")).days for r in resolved_reports])
        avg_resolution_time = total_days / resolved if resolved > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Reports", total_reports, delta=None)
    with col2:
        st.metric("Resolution Rate", f"{resolution_rate:.1f}%", delta=f"{resolved} resolved")
    with col3:
        st.metric("Avg Resolution Time", f"{avg_resolution_time:.1f} days", delta="from submission")
    with col4:
        st.metric("In Progress", in_progress, delta=f"{in_progress/total_reports*100:.1f}%" if total_reports > 0 else "0%")
    with col5:
        st.metric("Pending", received, delta=f"{received/total_reports*100:.1f}%" if total_reports > 0 else "0%")
    
    # Charts Section
    st.header("📊 Visual Analytics")
    
    # Create charts
    fig_pie, fig_bar, fig_timeline, fig_resolution = create_progress_charts()
    
    if fig_pie and fig_bar and fig_timeline:
        # First row - Status and Issue Type
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Second row - Timeline
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Third row - Resolution Time (if available)
        if fig_resolution:
            st.plotly_chart(fig_resolution, use_container_width=True)
    
    # Recent Activity Section
    st.header("🕒 Recent Activity")
    
    # Get recent reports (last 10)
    recent_reports = sorted(st.session_state.reports, key=lambda x: x['date_reported'], reverse=True)[:10]
    
    for report in recent_reports:
        status_color = {
            'Received': '🟡',
            'In Progress': '🔵', 
            'Resolved': '🟢'
        }.get(report['status'], '⚪')
        
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"**{status_color} Report #{report['id']}** - {report['issue_type']}")
                st.write(f"📍 {report['location']}")
                st.write(f"👤 {report['name']} - {report['date_reported']}")
            
            with col2:
                st.write(f"**Status:** {report['status']}")
                st.write(f"**Assigned:** {report['assigned_to']}")
                if report.get('priority'):
                    priority_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 'Emergency': '🔴'}
                    st.write(f"**Priority:** {priority_emoji.get(report['priority'], '⚪')} {report['priority']}")
            
            with col3:
                progress_key = f"progress_view_{report['id']}"
                if st.button(f"View Details", key=progress_key):
                    st.session_state[f"show_report_{progress_key}"] = True
            
            # Show report details if requested
            if st.session_state.get(f"show_report_{progress_key}", False):
                with st.expander(f"Report #{report['id']} Details", expanded=True):
                    st.write(f"**Description:** {report['description']}")
                    st.write(f"**Contact:** {report['contact']}")
                    
                    # Show photo if available
                    if report.get('photo'):
                        try:
                            photo_data = base64.b64decode(report['photo'])
                            st.image(photo_data, caption="Report Photo", use_column_width=True)
                        except:
                            st.warning("Could not display photo")
                    
                    # Show comments
                    if report.get('comments'):
                        st.write("**Comments & Updates:**")
                        for comment in reversed(report['comments']):
                            st.write(f"💬 **{comment['author']}** ({comment['timestamp']}): {comment['text']}")
                    
                    if st.button(f"Close Details", key=f"close_{progress_key}"):
                        st.session_state[f"show_report_{progress_key}"] = False
                        st.rerun()
            
            st.divider()
    
    # Issue Type Analysis
    st.header("🔍 Issue Analysis")
    
    # Create issue type breakdown
    issue_analysis = {}
    for report in st.session_state.reports:
        issue_type = report['issue_type']
        if issue_type not in issue_analysis:
            issue_analysis[issue_type] = {'total': 0, 'resolved': 0, 'in_progress': 0, 'received': 0}
        
        issue_analysis[issue_type]['total'] += 1
        issue_analysis[issue_type][report['status'].lower().replace(' ', '_')] += 1
    
    # Display issue analysis
    for issue_type, stats in issue_analysis.items():
        resolution_rate = (stats['resolved'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(f"{issue_type}", stats['total'])
        with col2:
            st.metric("Resolved", stats['resolved'], f"{resolution_rate:.1f}%")
        with col3:
            st.metric("In Progress", stats['in_progress'])
        with col4:
            st.metric("Pending", stats['received'])
        
        # Progress bar
        progress = resolution_rate / 100
        st.progress(progress)
        st.write(f"Resolution Progress: {resolution_rate:.1f}%")
        st.divider()
    
    # Performance Insights
    st.header("💡 Performance Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Quick Stats")
        st.write(f"• **Most Common Issue:** {max(issue_analysis.keys(), key=lambda x: issue_analysis[x]['total']) if issue_analysis else 'N/A'}")
        st.write(f"• **Best Resolved Issue:** {max(issue_analysis.keys(), key=lambda x: issue_analysis[x]['resolved']/issue_analysis[x]['total'] if issue_analysis[x]['total'] > 0 else 0) if issue_analysis else 'N/A'}")
        st.write(f"• **Total Reports This Month:** {len([r for r in st.session_state.reports if datetime.datetime.strptime(r['date_reported'], '%Y-%m-%d %H:%M').month == datetime.datetime.now().month])}")
    
    with col2:
        st.subheader("🎯 Recommendations")
        if resolution_rate < 50:
            st.warning("⚠️ Resolution rate is below 50%. Consider increasing resources for faster resolution.")
        elif resolution_rate < 80:
            st.info("💡 Good progress! Aim for 80%+ resolution rate.")
        else:
            st.success("🎉 Excellent resolution rate! Keep up the great work!")
        
        if avg_resolution_time > 7:
            st.warning("⚠️ Average resolution time is over a week. Consider streamlining processes.")
        elif avg_resolution_time > 3:
            st.info("💡 Resolution time is acceptable but could be improved.")
        else:
            st.success("🎉 Great response time! Issues are being resolved quickly.")

def show_admin_login():
    st.title("🔐 Admin Login")
    
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        
        if login_btn:
            if password == st.session_state.admin_password:
                st.session_state.admin_logged_in = True
                st.success("Login successful! Redirecting to dashboard...")
                st.rerun()
            else:
                st.error("Incorrect password!")

def show_admin_dashboard():
    st.title("📊 Admin Dashboard")
    st.markdown("Welcome to the Admin Control Panel - Manage and organize all community reports efficiently")
    
    # Statistics
    total_reports = len(st.session_state.reports)
    received = len([r for r in st.session_state.reports if r['status'] == 'Received'])
    in_progress = len([r for r in st.session_state.reports if r['status'] == 'In Progress'])
    resolved = len([r for r in st.session_state.reports if r['status'] == 'Resolved'])
    
    # Calculate resolution rate
    resolution_rate = (resolved / total_reports * 100) if total_reports > 0 else 0
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Reports</h3>
            <h1>{total_reports}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Received</h3>
            <h1>{received}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>In Progress</h3>
            <h1>{in_progress}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Resolved</h3>
            <h1>{resolved}</h1>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Resolution Rate</h3>
            <h1>{resolution_rate:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Organization Options
    st.header("🗂️ Organize Reports")
    
    # Tabs for different organization methods
    tab1, tab2, tab3, tab4 = st.tabs(["📊 By Status", "⚡ By Priority", "📅 By Date", "🏷️ By Issue Type"])
    
    with tab1:
        organized_by_status = organize_reports_by_status()
        display_organized_reports(organized_by_status, "Reports Organized by Status", context="status")
    
    with tab2:
        organized_by_priority = organize_reports_by_priority()
        display_organized_reports(organized_by_priority, "Reports Organized by Priority", context="priority")
    
    with tab3:
        organized_by_date = organize_reports_by_date()
        display_organized_reports(organized_by_date, "Reports Organized by Date", context="date")
    
    with tab4:
        organized_by_type = organize_reports_by_issue_type()
        display_organized_reports(organized_by_type, "Reports Organized by Issue Type", context="type")
    
    # Quick Actions Section
    st.header("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            load_data_from_file()
            st.success("Data refreshed!")
            st.rerun()
    
    with col2:
        if st.button("💾 Backup Now", use_container_width=True):
            save_data_to_file()
            st.success("Data backed up successfully!")
    
    with col3:
        if st.button("📊 View Analytics", use_container_width=True):
            st.info("Switch to Progress Dashboard for detailed analytics")
    
    with col4:
        if st.button("📥 Export All", use_container_width=True):
            if st.session_state.reports:
                df_export = pd.DataFrame(st.session_state.reports)
                csv = df_export.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"all_reports_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No reports to export")
    
    # Advanced Search and Filter
    st.header("🔍 Advanced Search & Filter")
    
    with st.expander("Advanced Search Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            search_name = st.text_input("Search by Reporter Name")
            search_location = st.text_input("Search by Location")
            search_issue = st.selectbox("Filter by Issue Type", ["All"] + list(set([r['issue_type'] for r in st.session_state.reports])))
        
        with col2:
            search_status = st.selectbox("Filter by Status", ["All", "Received", "In Progress", "Resolved"])
            search_priority = st.selectbox("Filter by Priority", ["All", "Low", "Medium", "High", "Emergency"])
            date_range = st.date_input("Filter by Date Range", value=[datetime.datetime.now().date() - datetime.timedelta(days=30), datetime.datetime.now().date()])
        
        if st.button("Apply Filters"):
            filtered_reports = st.session_state.reports.copy()
            
            if search_name:
                filtered_reports = [r for r in filtered_reports if search_name.lower() in r['name'].lower()]
            if search_location:
                filtered_reports = [r for r in filtered_reports if search_location.lower() in r['location'].lower()]
            if search_issue != "All":
                filtered_reports = [r for r in filtered_reports if r['issue_type'] == search_issue]
            if search_status != "All":
                filtered_reports = [r for r in filtered_reports if r['status'] == search_status]
            if search_priority != "All":
                filtered_reports = [r for r in filtered_reports if r.get('priority', 'Medium') == search_priority]
            
            # Date filtering
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_reports = [r for r in filtered_reports if 
                                  start_date <= datetime.datetime.strptime(r['date_reported'], "%Y-%m-%d %H:%M").date() <= end_date]
            
            st.session_state['filtered_reports'] = filtered_reports
            st.success(f"Found {len(filtered_reports)} reports matching your criteria")
    
    # Display filtered results if available
    if 'filtered_reports' in st.session_state and st.session_state['filtered_reports']:
        st.subheader(f"🔍 Search Results ({len(st.session_state['filtered_reports'])} reports)")
        
        for report in st.session_state['filtered_reports']:
            status_color = {'Received': '🟡', 'In Progress': '🔵', 'Resolved': '🟢'}.get(report['status'], '⚪')
            priority_emoji = {'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 'Emergency': '🔴'}.get(report.get('priority', 'Medium'), '⚪')
            
            with st.container():
                col1, col2, col3 = st.columns([4, 2, 1])
                
                with col1:
                    st.write(f"**{status_color} Report #{report['id']}** - {report['issue_type']}")
                    st.write(f"📍 {report['location']} | 👤 {report['name']} | 📅 {report['date_reported']}")
                
                with col2:
                    st.write(f"**Status:** {report['status']} | **Priority:** {priority_emoji} {report.get('priority', 'Medium')}")
                    st.write(f"**Assigned:** {report['assigned_to']}")
                
                with col3:
                    search_key = f"search_manage_{report['id']}"
                    if st.button(f"Manage", key=search_key):
                        st.session_state[f"manage_report_{search_key}"] = True
                
                # Quick management form
                if st.session_state.get(f"manage_report_{search_key}", False):
                    with st.form(f"manage_form_{search_key}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            new_status = st.selectbox("Status", ["Received", "In Progress", "Resolved"], 
                                                    index=["Received", "In Progress", "Resolved"].index(report['status']),
                                                    key=f"m_status_{search_key}")
                            new_priority = st.selectbox("Priority", ["Low", "Medium", "High", "Emergency"],
                                                      index=["Low", "Medium", "High", "Emergency"].index(report.get('priority', 'Medium')),
                                                      key=f"m_priority_{search_key}")
                        with col2:
                            assigned_to = st.text_input("Assign To", value=report['assigned_to'], key=f"m_assign_{search_key}")
                            comment = st.text_area("Add Comment", key=f"m_comment_{search_key}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Report"):
                                report['status'] = new_status
                                report['priority'] = new_priority
                                report['assigned_to'] = assigned_to
                                if comment:
                                    add_comment(report['id'], comment)
                                save_data_to_file()
                                st.session_state[f"manage_report_{search_key}"] = False
                                st.success("Report updated!")
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Cancel"):
                                st.session_state[f"manage_report_{search_key}"] = False
                                st.rerun()
                
                st.divider()
    
    # Reports table with status management
    st.header("📋 All Reports (Legacy View)")
    
    if st.session_state.reports:
        # Search and filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Search reports", placeholder="Search by location, issue type, or name")
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Received", "In Progress", "Resolved"])
        
        with col3:
            issue_filter = st.selectbox("Filter by Issue Type", ["All"] + list(set([r['issue_type'] for r in st.session_state.reports])))
        
        # Filter reports based on search and filters
        filtered_reports = st.session_state.reports.copy()
        
        if search_term:
            filtered_reports = [r for r in filtered_reports if 
                              search_term.lower() in r['location'].lower() or 
                              search_term.lower() in r['issue_type'].lower() or 
                              search_term.lower() in r['name'].lower()]
        
        if status_filter != "All":
            filtered_reports = [r for r in filtered_reports if r['status'] == status_filter]
        
        if issue_filter != "All":
            filtered_reports = [r for r in filtered_reports if r['issue_type'] == issue_filter]
        
        # Create DataFrame for display
        df_data = []
        for report in filtered_reports:
            df_data.append({
                'ID': report['id'],
                'Name': report['name'],
                'Issue Type': report['issue_type'],
                'Location': report['location'],
                'Status': report['status'],
                'Date Reported': report['date_reported'],
                'Assigned To': report['assigned_to'],
                'Priority': report.get('priority', 'Medium')
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Show filtered count
            st.info(f"Showing {len(filtered_reports)} of {len(st.session_state.reports)} reports")
        else:
            st.warning("No reports match your search criteria.")
        
        # Report management
        st.header("🛠️ Manage Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Update Report Status")
            report_id = st.selectbox("Select Report", 
                                   [f"#{r['id']} - {r['issue_type']} - {r['location']}" 
                                    for r in st.session_state.reports])
            
            selected_report = None
            selected_id = None
            
            if report_id:
                selected_id = int(report_id.split('#')[1].split(' - ')[0])
                selected_report = next((r for r in st.session_state.reports if r['id'] == selected_id), None)
                
                if selected_report:
                    # Display report details
                    st.markdown(f"""
                    <div class="report-card">
                        <h4>Report #{selected_report['id']}</h4>
                        <p><strong>Reporter:</strong> {selected_report['name']}</p>
                        <p><strong>Contact:</strong> {selected_report['contact']}</p>
                        <p><strong>Issue:</strong> {selected_report['issue_type']}</p>
                        <p><strong>Location:</strong> {selected_report['location']}</p>
                        <p><strong>Description:</strong> {selected_report['description']}</p>
                        <p><strong>Date:</strong> {selected_report['date_reported']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show photo if available
                    if selected_report.get('photo'):
                        try:
                            photo_data = base64.b64decode(selected_report['photo'])
                            st.image(photo_data, caption="Report Photo", use_column_width=True)
                        except:
                            st.warning("Could not display photo")
                    
                    new_status = st.selectbox("Update Status", 
                                            ["Received", "In Progress", "Resolved"],
                                            index=["Received", "In Progress", "Resolved"].index(selected_report['status']))
                    assigned_to = st.text_input("Assign To", value=selected_report['assigned_to'])
                    priority = st.selectbox("Priority", 
                                          ["Low", "Medium", "High", "Emergency"],
                                          index=["Low", "Medium", "High", "Emergency"].index(selected_report.get('priority', 'Medium')))
                    
                    if st.button("Update Report", use_container_width=True):
                        selected_report['status'] = new_status
                        selected_report['assigned_to'] = assigned_to
                        selected_report['priority'] = priority
                        save_data_to_file()  # Save changes
                        st.success("Report updated successfully!")
                        st.rerun()
        
        with col2:
            st.subheader("Add Comment")
            if selected_report:
                comment = st.text_area("Add comment/update", placeholder="Enter your comment or status update...")
                if st.button("Add Comment", use_container_width=True):
                    if comment:
                        add_comment(selected_id, comment)
                        save_data_to_file()  # Save changes
                        st.success("Comment added!")
                        st.rerun()
                    else:
                        st.warning("Please enter a comment")
        
        # Display comments for selected report
        if selected_report and selected_report['comments']:
            st.subheader("💬 Comments & Updates")
            for comment in reversed(selected_report['comments']):
                with st.container():
                    st.markdown(f"""
                    <div class="report-card">
                        <strong>{comment['author']}</strong> - <em>{comment['timestamp']}</em><br>
                        {comment['text']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Export functionality
        st.header("📊 Export & Backup")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Reports to CSV", use_container_width=True):
                if st.session_state.reports:
                    df_export = pd.DataFrame(st.session_state.reports)
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"reports_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No reports to export")
        
        with col2:
            if st.button("💾 Backup Data", use_container_width=True):
                save_data_to_file()
                st.success("Data backed up successfully!")
    
    else:
        st.info("No reports submitted yet.")

if __name__ == "__main__":
    main()