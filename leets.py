import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API URL from environment variable or use default
API_URL = os.getenv('API_URL', 'https://leetapi-882701280393.us-central1.run.app')

def fetch_data(endpoint):
    """Fetch data from API endpoint"""
    try:
        response = requests.get(f"{API_URL}/api/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def create_difficulty_chart(data):
    """Create a pie chart for difficulty distribution"""
    if not data or 'difficulty_distribution' not in data:
        return None
    
    difficulty_data = data['difficulty_distribution']
    fig = px.pie(
        values=list(difficulty_data.values()),
        names=list(difficulty_data.keys()),
        title='Question Difficulty Distribution',
        color_discrete_map={
            'easy': '#00ff00',
            'medium': '#ffa500',
            'hard': '#ff0000'
        }
    )
    return fig

def create_platform_chart(data):
    """Create a pie chart for platform distribution"""
    if not data or 'platform_distribution' not in data:
        return None
    
    platform_data = data['platform_distribution']
    fig = px.pie(
        values=list(platform_data.values()),
        names=list(platform_data.keys()),
        title='Questions by Platform',
        color_discrete_map={
            'leetcode': '#FFA116',  # LeetCode orange
            'gfg': '#2F8D46'  # GFG green
        }
    )
    return fig

def create_acceptance_rate_chart(questions):
    """Create a bar chart for acceptance rates"""
    if not questions:
        return None
    
    df = pd.DataFrame(questions)
    df['acceptance_rate'] = df['acceptance_rate'].str.rstrip('%').astype(float)
    
    fig = px.bar(
        df,
        x='difficulty',
        y='acceptance_rate',
        title='Acceptance Rate by Difficulty',
        color='platform',
        barmode='group',
        color_discrete_map={
            'LeetCode': '#FFA116',
            'GeeksforGeeks': '#2F8D46'
        }
    )
    return fig

def display_question_table(questions):
    """Display questions in a table format"""
    if not questions:
        return
    
    df = pd.DataFrame(questions)
    
    # Create HTML links for each URL
    df['url'] = df.apply(lambda row: f'<a href="{row["url"]}" target="_blank" style="color: #FFA116; text-decoration: none;">Open</a>', axis=1)
    
    # Convert DataFrame to HTML with styling
    html_table = df.to_html(
        escape=False,
        index=False,
        classes='dataframe',
        render_links=True
    )
    
    # Add custom CSS for better table styling
    st.markdown("""
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
        }
        .dataframe th {
            background-color: #f0f2f6;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        .dataframe td {
            padding: 12px;
            border-bottom: 1px solid #e1e4e8;
        }
        .dataframe tr:hover {
            background-color: #f8f9fa;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display the table
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Add a note about opening links
    st.markdown("""
        <div style='background-color: #f0f2f6; padding: 10px; border-radius: 5px; margin-top: 10px;'>
            <p style='margin: 0;'><strong>Note:</strong> Click the "Open" link to view the question in a new tab.</p>
        </div>
    """, unsafe_allow_html=True)

def fetch_company_questions(company):
    """Fetch questions for a specific company from the API"""
    try:
        response = requests.get(f"{API_URL}/api/questions/{company}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching questions: {str(e)}")
        return []

def fetch_company_summary(company):
    """Fetch summary for a specific company from the API"""
    try:
        response = requests.get(f"{API_URL}/api/summary/{company}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching summary: {str(e)}")
        return {}

def main():
    st.set_page_config(
        page_title="Coding Questions Explorer",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Coding Questions Explorer")
    st.markdown("---")
    
    # Fetch available companies
    companies_data = fetch_data("companies")
    if not companies_data or companies_data.get("status") != "success":
        st.error("Failed to fetch companies list")
        return
    
    companies = companies_data["companies"]
    
    # Sidebar for filters
    st.sidebar.title("Filters")
    company = st.sidebar.selectbox(
        "Select Company",
        companies,
        format_func=lambda x: x.title()
    )
    
    difficulty = st.sidebar.selectbox(
        "Select Difficulty",
        ["All", "Easy", "Medium", "Hard"]
    )
    
    # Fetch summary data
    summary_data = fetch_data(f"summary/{company}")
    if summary_data and summary_data.get("status") == "success":
        summary = summary_data["summary"]
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Questions", summary["total_questions"])
        with col2:
            st.metric("Easy Questions", summary["difficulty_distribution"]["easy"])
        with col3:
            st.metric("Medium Questions", summary["difficulty_distribution"]["medium"])
        with col4:
            st.metric("Hard Questions", summary["difficulty_distribution"]["hard"])
        
        # Display charts
        col1, col2 = st.columns(2)
        with col1:
            difficulty_chart = create_difficulty_chart(summary_data)
            if difficulty_chart:
                st.plotly_chart(difficulty_chart, use_container_width=True)
        
        with col2:
            platform_chart = create_platform_chart(summary_data)
            if platform_chart:
                st.plotly_chart(platform_chart, use_container_width=True)
        
        # Fetch and display questions
        endpoint = f"questions/{company}"
        if difficulty != "All":
            endpoint += f"?difficulty={difficulty.lower()}"
        
        questions_data = fetch_data(endpoint)
        if questions_data and questions_data.get("status") == "success":
            questions = questions_data["questions"]
            
            # Display acceptance rate chart
            acceptance_chart = create_acceptance_rate_chart(questions)
            if acceptance_chart:
                st.plotly_chart(acceptance_chart, use_container_width=True)
            
            # Display questions table
            st.markdown("### Questions")
            display_question_table(questions)
        else:
            st.error("Failed to fetch questions data")
    else:
        st.error("Failed to fetch summary data")

if __name__ == "__main__":
    main() 