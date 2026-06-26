import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from visualizations import (
    create_status_pie_chart,
    create_group_comparison_chart,
    create_monthly_trend_chart,
    create_publication_type_chart,
    create_acceptance_gauge,
    create_publication_timeline,
    create_summary_metrics
)
from config import (
    APP_NAME, APP_SUBTITLE, APP_ICON,
    PUBLICATION_STATUSES, PUBLICATION_TYPES,
    STATUS_COLORS
)

# Page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title=f"{APP_NAME} - Research Tracker",
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def init_db():
    return Database()

db = init_db()
# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
    .error-message {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #145a8c;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Login function
def login():
    """Handle user login"""
    st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🔬 Lahore Science Foundry</h1>", 
                unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Khwarizmi Science Society</h3>", 
                unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Research Management System</h4>", 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            st.markdown("### 👤 Login to Your Account")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_submitted = st.form_submit_button("🔑 Login")
            with col_btn2:
                st.form_submit_button("🔄 Reset")
            
            if login_submitted:
                if username and password:
                    success, message, user_data = db.verify_user(username, password)
                    if success:
                        st.session_state.user = user_data
                        st.session_state.authenticated = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both username and password")
        
        st.markdown("---")
        st.info("""
        **Default Admin Credentials:**
        - Username: `admin`
        - Password: `Admin@KSS2024`
        
        Please change these after first login!
        """)

# Logout function
def logout():
    """Handle user logout"""
    st.session_state.user = None
    st.session_state.authenticated = False
    st.session_state.current_page = "Dashboard"
    st.rerun()

# Main application
def main_app():
    """Main application after authentication"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"## 👋 Welcome, {st.session_state.user['name']}")
        st.markdown(f"**Group:** {st.session_state.user['group_name']}")
        st.markdown(f"**Role:** {st.session_state.user['role']}")
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📋 Navigation")
        
        pages = {
            "📊 Dashboard": "Dashboard",
            "📝 Add Publication": "Add Publication",
            "📚 View Publications": "View Publications",
            "👥 Group Meetings": "Group Meetings",
            "📈 Analytics": "Analytics",
            "👤 User Management": "User Management",
            "📥 Export Data": "Export Data"
        }
        
        # Remove User Management for non-admin users
        if st.session_state.user['role'] != 'admin':
            del pages["👤 User Management"]
        
        selected_page = st.radio(
            "Select Page",
            list(pages.keys()),
            key="navigation",
            label_visibility="collapsed"
        )
        
        st.session_state.current_page = pages[selected_page]
        
        st.markdown("---")
        
        # Quick stats in sidebar
        if st.button("📊 Refresh Stats", use_container_width=True):
            st.rerun()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Main content area
    if st.session_state.current_page == "Dashboard":
        show_dashboard()
    elif st.session_state.current_page == "Add Publication":
        show_add_publication()
    elif st.session_state.current_page == "View Publications":
        show_view_publications()
    elif st.session_state.current_page == "Group Meetings":
        show_group_meetings()
    elif st.session_state.current_page == "Analytics":
        show_analytics()
    elif st.session_state.current_page == "User Management":
        show_user_management()
    elif st.session_state.current_page == "Export Data":
        show_export_data()

def show_dashboard():
    """Display main dashboard"""
    st.markdown(f"<div class='main-header'>{APP_NAME}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-header'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)
    
    # Get statistics
    group_name = st.session_state.user['group_name']
    if st.session_state.user['role'] == 'admin':
        # Admin sees all data
        stats = db.get_group_stats(group_name)  # Modify to get all groups if needed
    else:
        stats = db.get_group_stats(group_name)
    
    if stats:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        metrics = create_summary_metrics(stats)
        if metrics:
            with col1:
                st.metric(
                    label=metrics[0]['label'],
                    value=metrics[0]['value'],
                    delta=metrics[0]['delta']
                )
            with col2:
                st.metric(
                    label=metrics[1]['label'],
                    value=metrics[1]['value'],
                    delta=metrics[1]['delta']
                )
            with col3:
                st.metric(
                    label=metrics[2]['label'],
                    value=metrics[2]['value'],
                    delta=metrics[2]['delta']
                )
            with col4:
                st.metric(
                    label=metrics[3]['label'],
                    value=metrics[3]['value'],
                    delta=metrics[3]['delta']
                )
        
        st.markdown("---")
        
        # Charts
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("### 📊 Publication Status")
            fig_pie = create_status_pie_chart(stats)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_right:
            st.markdown("### 🎯 Acceptance Rate")
            fig_gauge = create_acceptance_gauge(stats.get('acceptance_rate', 0))
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Monthly trend
        st.markdown("### 📈 Publication Trends")
        if stats.get('monthly_trend'):
            fig_trend = create_monthly_trend_chart(stats['monthly_trend'])
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Publication types
        if stats.get('type_distribution'):
            st.markdown("### 📚 Publication Types")
            fig_types = create_publication_type_chart(stats['type_distribution'])
            st.plotly_chart(fig_types, use_container_width=True)
    else:
        st.warning("No statistics available. Start by adding publications!")

def show_add_publication():
    """Add new publication form"""
    st.markdown("## 📝 Add New Publication")
    
    with st.form("add_publication_form", clear_on_submit=True):
        st.markdown("### Publication Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            paper_title = st.text_input(
                "Paper Title *",
                placeholder="Enter the complete paper title",
                max_chars=500
            )
            authors = st.text_area(
                "Authors *",
                placeholder="Enter authors (comma-separated)\nExample: John Doe, Jane Smith, Robert Johnson",
                height=100
            )
            corresponding_author = st.text_input(
                "Corresponding Author",
                placeholder="Primary contact author"
            )
            journal_name = st.text_input(
                "Journal Name",
                placeholder="Target or submitted journal"
            )
        
        with col2:
            status = st.selectbox(
                "Status *",
                PUBLICATION_STATUSES,
                help="Current status of the publication"
            )
            publication_type = st.selectbox(
                "Publication Type *",
                PUBLICATION_TYPES,
                help="Type of publication"
            )
            submission_id = st.text_input(
                "Submission ID",
                placeholder="Journal submission ID (if available)"
            )
            doi = st.text_input(
                "DOI",
                placeholder="Digital Object Identifier (if assigned)"
            )
            impact_factor = st.number_input(
                "Impact Factor",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                format="%.1f"
            )
        
        st.markdown("### Dates")
        col_date1, col_date2, col_date3 = st.columns(3)
        
        with col_date1:
            date_started = st.date_input(
                "Date Started",
                value=datetime.now(),
                help="When work on this paper began"
            )
        
        with col_date2:
            date_submitted = st.date_input(
                "Date Submitted",
                value=None,
                help="When paper was submitted to journal"
            )
        
        with col_date3:
            date_decision = st.date_input(
                "Date of Decision",
                value=None,
                help="When final decision was received"
            )
        
        st.markdown("### Additional Information")
        notes = st.text_area(
            "Notes",
            placeholder="Any additional notes, reviewer comments, or important details",
            height=100
        )
        
        st.markdown("---")
        
        submitted = st.form_submit_button("💾 Save Publication", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            if not paper_title:
                errors.append("Paper title is required")
            if not authors:
                errors.append("At least one author is required")
            if not publication_type:
                errors.append("Publication type is required")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Prepare data
                publication_data = {
                    'paper_title': paper_title,
                    'authors': authors,
                    'corresponding_author': corresponding_author,
                    'journal_name': journal_name,
                    'submission_id': submission_id,
                    'status': status,
                    'publication_type': publication_type,
                    'group_name': st.session_state.user['group_name'],
                    'submitted_by': st.session_state.user['username'],
                    'date_started': date_started.strftime('%Y-%m-%d') if date_started else None,
                    'date_submitted': date_submitted.strftime('%Y-%m-%d') if date_submitted else None,
                    'date_decision': date_decision.strftime('%Y-%m-%d') if date_decision else None,
                    'doi': doi,
                    'impact_factor': impact_factor,
                    'notes': notes
                }
                
                success, message = db.add_publication(publication_data)
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)

def show_view_publications():
    """View and manage publications"""
    st.markdown("## 📚 View Publications")
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search publications", placeholder="Search by title, author, or journal...")
    
    with col2:
        filter_status = st.multiselect(
            "Filter by Status",
            PUBLICATION_STATUSES,
            default=[]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Most Recent", "Title A-Z", "Status", "Submission Date"]
        )
    
    # Get publications
    group_name = st.session_state.user['group_name']
    publications_df = db.get_all_publications(group_name=group_name)
    
    if not publications_df.empty:
        # Apply filters
        if search_term:
            mask = (
                publications_df['paper_title'].str.contains(search_term, case=False, na=False) |
                publications_df['authors'].str.contains(search_term, case=False, na=False) |
                publications_df['journal_name'].str.contains(search_term, case=False, na=False)
            )
            publications_df = publications_df[mask]
        
        if filter_status:
            publications_df = publications_df[publications_df['status'].isin(filter_status)]
        
        # Apply sorting
        if sort_by == "Title A-Z":
            publications_df = publications_df.sort_values('paper_title')
        elif sort_by == "Status":
            publications_df = publications_df.sort_values('status')
        elif sort_by == "Submission Date":
            publications_df = publications_df.sort_values('date_submitted', ascending=False)
        else:  # Most Recent
            publications_df = publications_df.sort_values('updated_at', ascending=False)
        
        # Display publications
        st.markdown(f"### Found {len(publications_df)} publications")
        
        for idx, row in publications_df.iterrows():
            with st.expander(f"📄 {row['paper_title']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Authors:** {row['authors']}")
                    st.markdown(f"**Journal:** {row['journal_name'] or 'Not specified'}")
                    st.markdown(f"**Submission ID:** {row['submission_id'] or 'N/A'}")
                    st.markdown(f"**Type:** {row['publication_type']}")
                    
                    if row['doi']:
                        st.markdown(f"**DOI:** [{row['doi']}](https://doi.org/{row['doi']})")
                    
                    if row['notes']:
                        st.markdown(f"**Notes:** {row['notes']}")
                
                with col2:
                    # Status badge with color
                    status_color = STATUS_COLORS.get(row['status'], '#BDBDBD')
                    st.markdown(f"""
                        <div style='
                            background-color: {status_color};
                            color: white;
                            padding: 10px;
                            border-radius: 5px;
                            text-align: center;
                            font-weight: bold;
                            margin-bottom: 10px;
                        '>
                            {row['status']}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"**Impact Factor:** {row['impact_factor']}")
                    st.markdown(f"**Created:** {row['created_at'][:10] if row['created_at'] else 'N/A'}")
                    st.markdown(f"**Updated:** {row['updated_at'][:10] if row['updated_at'] else 'N/A'}")
                
                # Edit button (simplified - would need full edit form)
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button(f"✏️ Edit", key=f"edit_{row['id']}"):
                        st.info("Edit functionality will be implemented in the full version")
                with col_delete:
                    if st.session_state.user['role'] == 'admin':
                        if st.button(f"🗑️ Delete", key=f"delete_{row['id']}"):
                            success, message = db.delete_publication(
                                row['id'], 
                                st.session_state.user['username'],
                                st.session_state.user['role']
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
    else:
        st.info("No publications found. Start by adding your first publication!")

def show_group_meetings():
    """Group meetings management"""
    st.markdown("## 👥 Group Meetings")
    
    tab1, tab2 = st.tabs(["📅 Add Meeting", "📋 View Meetings"])
    
    with tab1:
        with st.form("add_meeting_form"):
            st.markdown("### Schedule New Meeting")
            
            col1, col2 = st.columns(2)
            
            with col1:
                meeting_date = st.date_input("Meeting Date *", value=datetime.now())
                meeting_time = st.time_input("Meeting Time", value=datetime.now().time())
                next_meeting_date = st.date_input("Next Meeting Date (if scheduled)")
            
            with col2:
                attendees = st.text_area(
                    "Attendees",
                    placeholder="List of attendees (comma-separated)",
                    height=100
                )
                agenda = st.text_area(
                    "Agenda",
                    placeholder="Meeting agenda items",
                    height=100
                )
            
            discussion_points = st.text_area(
                "Discussion Points",
                placeholder="Key points discussed during the meeting",
                height=150
            )
            
            action_items = st.text_area(
                "Action Items",
                placeholder="Action items and responsible persons",
                height=100
            )
            
            submitted = st.form_submit_button("💾 Save Meeting", use_container_width=True)
            
            if submitted:
                if meeting_date:
                    meeting_data = {
                        'group_name': st.session_state.user['group_name'],
                        'meeting_date': meeting_date.strftime('%Y-%m-%d'),
                        'meeting_time': meeting_time.strftime('%H:%M') if meeting_time else None,
                        'attendees': attendees,
                        'agenda': agenda,
                        'discussion_points': discussion_points,
                        'action_items': action_items,
                        'next_meeting_date': next_meeting_date.strftime('%Y-%m-%d') if next_meeting_date else None,
                        'created_by': st.session_state.user['username']
                    }
                    
                    success, message = db.add_group_meeting(meeting_data)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Meeting date is required")
    
    with tab2:
        st.markdown("### Previous Meetings")
        st.info("Meeting history will be displayed here")

def show_analytics():
    """Advanced analytics dashboard"""
    st.markdown("## 📈 Analytics Dashboard")
    
    group_name = st.session_state.user['group_name']
    stats = db.get_group_stats(group_name)
    
    if stats:
        # Comparison charts if admin
        if st.session_state.user['role'] == 'admin':
            st.markdown("### Group Comparison")
            # You would need to fetch all groups' data here
            all_groups_data = {group_name: stats}  # Simplified
            fig_comparison = create_group_comparison_chart(all_groups_data)
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Publication timeline
        st.markdown("### Publication Timeline")
        publications_df = db.get_all_publications(group_name=group_name)
        if not publications_df.empty:
            fig_timeline = create_publication_timeline(publications_df)
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Additional analytics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Status Breakdown")
            for status in PUBLICATION_STATUSES:
                count = stats['status_counts'].get(status, 0)
                if count > 0:
                    st.progress(count / stats['total'] if stats['total'] > 0 else 0, 
                              text=f"{status}: {count}")
        
        with col2:
            st.markdown("### Quick Summary")
            st.info(f"""
            📊 **Total Publications:** {stats['total']}
            📝 **In Progress:** {stats['in_progress']}
            ✅ **Accepted:** {stats['accepted']}
            ❌ **Rejected:** {stats['rejected']}
            📈 **Acceptance Rate:** {stats['acceptance_rate']}%
            """)
    else:
        st.warning("No data available for analytics")

def show_user_management():
    """User management for admin"""
    if st.session_state.user['role'] != 'admin':
        st.error("Access denied. Admin privileges required.")
        return
    
    st.markdown("## 👤 User Management")
    
    tab1, tab2 = st.tabs(["➕ Add User", "👥 View Users"])
    
    with tab1:
        with st.form("add_user_form"):
            st.markdown("### Create New User")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username *")
                new_password = st.text_input("Password *", type="password")
                new_name = st.text_input("Full Name *")
                new_email = st.text_input("Email")
            
            with col2:
                new_group = st.text_input("Research Group *")
                new_role = st.selectbox("Role", ["group_head", "researcher", "viewer"])
            
            submitted = st.form_submit_button("➕ Create User", use_container_width=True)
            
            if submitted:
                if new_username and new_password and new_name and new_group:
                    success, message = db.add_user(
                        username=new_username,
                        password=new_password,
                        name=new_name,
                        email=new_email,
                        group_name=new_group,
                        role=new_role
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill all required fields (*)")
    
    with tab2:
        st.markdown("### Existing Users")
        users_df = db.get_users_by_group()
        if not users_df.empty:
            st.dataframe(
                users_df[['username', 'name', 'group_name', 'role', 'is_active', 'created_at']],
                use_container_width=True
            )
        else:
            st.info("No users found")

def show_export_data():
    """Export functionality"""
    st.markdown("## 📥 Export Data")
    
    group_name = st.session_state.user['group_name']
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "Excel"]
        )
    
    with col2:
        date_range = st.date_input(
            "Date Range (Optional)",
            value=()
        )
    
    if st.button("📥 Generate Export", use_container_width=True):
        with st.spinner("Generating export..."):
            data, filename = db.export_data(
                group_name=group_name,
                format=export_format.lower()
            )
            
            if data:
                if export_format.lower() == 'csv':
                    st.download_button(
                        label="📥 Download CSV",
                        data=data,
                        file_name=filename,
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.download_button(
                        label="📥 Download Excel",
                        data=data,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                st.success("Export generated successfully!")
            else:
                st.error("No data to export")

# Main execution
def main():
    """Main application entry point"""
    if not st.session_state.authenticated:
        login()
    else:
        main_app()

if __name__ == "__main__":
    main()