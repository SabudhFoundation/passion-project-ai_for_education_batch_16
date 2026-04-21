import streamlit as st
import re

# ----PAGE SETUP
st.set_page_config(page_title="UpskillxAI", layout="wide")



st.title("UpskillxAI")
st.markdown("### AI Powered Upskilling")
st.markdown("Upload your CV to match with top jobs and uncover your skill gaps.")

# ---- SIDEBAR (INPUT)
with st.sidebar:
    st.header("Document Upload")
    st.markdown("Provide your details below to get started.")
    
    uploaded_files = st.file_uploader(
        "Upload CV(s)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT. You can upload multiple files."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    job_pref = st.text_input("Target Role", placeholder="e.g., Senior Software Engineer")
    
    with st.expander("Or paste CV text directly"):
        user_text = st.text_area("Paste text here...", height=150)

# ---- MAIN AREA
if uploaded_files or user_text:
    
    # 1. Processing Logic (Mocked)
    all_text = ""
    if uploaded_files:
        for i, file in enumerate(uploaded_files):
            # Fake processing
            text = f"[Text extracted from {file.name}]"
            all_text += text + "\n\n"
    if user_text:
        all_text += user_text

    # Mock Data
    text_lower = all_text.lower()
    extracted_skills = ["Python", "Pandas", "SQL", "Data Analysis", "Git", "Docker"]
    experience = "3+ years"
    required_skills = ["Python", "Machine Learning", "Communication", "Problem Solving", "Cloud Computing"]
    
    # 2. Main Dashboard Layout
    st.markdown("---")
    
    # Overview Metrics
    st.subheader("Profile Overview")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Detected Experience", value=experience)
    with m2:
        st.metric(label="Skills Found", value=str(len(extracted_skills)))
    with m3:
        st.metric(label="Skill Match", value="75%")
    with m4:
        st.metric(label="Job Matches", value="12")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---- TABS ----
    tab1, tab2, tab3 = st.tabs(["Skills Analysis", "Job Matches", "Learning Paths"])
    
    # TAB 1: Analysis
    with tab1:
        st.markdown("#### Skill Match Breakdown")
        st.markdown("We've analyzed your profile against industry standards for your target role.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.success("**Verified Skills (You possess these)**")
            for skill in extracted_skills:
                st.markdown(f"- {skill}")
        with c2:
            st.warning("**Skill Gaps (Recommended to learn)**")
            for skill in required_skills:
                if skill not in extracted_skills:
                    st.markdown(f"- {skill}")
                
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("View Extracted Raw Text"):
            st.text(all_text)
            
    # TAB 2: Jobs
    with tab2:
        st.markdown("#### Recommended Opportunities")
        st.markdown("Hand-picked roles based on your verified skills and experience level.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        hardcoded_jobs_json = [
            {
                "position": "Senior Software Engineer", 
                "company": "Microsoft", 
                "location": "Redmond, WA (Hybrid)", 
                "jobUrl": "https://careers.microsoft.com/software-engineer", 
                "salary": "$150,000 - $190,000"
            },
            {
                "position": "Data Scientist", 
                "company": "Google", 
                "location": "Mountain View, CA (On-site)", 
                "jobUrl": "https://careers.google.com/data-scientist", 
                "salary": "$160,000 - $210,000"
            },
            {
                "position": "Machine Learning Engineer", 
                "company": "OpenAI", 
                "location": "San Francisco, CA (Remote)", 
                "jobUrl": "https://openai.com/careers/ml-engineer", 
                "salary": "$200,000 - $280,000"
            }
        ]
        
        for job in hardcoded_jobs_json:
            with st.container(border=True):
                colA, colB = st.columns([3, 1])
                with colA:
                    st.markdown(f"### {job['position']}")
                    st.markdown(f"**{job['company']}** | {job['location']}")
                with colB:
                    st.markdown(f"<h4 style='color: #059669; margin-bottom: 0;'>{job.get('salary', '')}</h4>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.link_button("Apply Now", job['jobUrl'], type="primary", use_container_width=True)

    # TAB 3: Resources
    with tab3:
        st.markdown("#### Recommended Learning Paths")
        st.markdown("Bridge your skill gaps with these highly-rated resources.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            with st.container(border=True):
                st.markdown("#### Python Crash Course")
                st.markdown("A hands-on, project-based introduction to programming. Highly recommended for strengthening fundamentals.")
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("View Book", "https://nostarch.com/pythoncrashcourse2e", use_container_width=True)
        with col_res2:
            with st.container(border=True):
                st.markdown("#### Machine Learning")
                st.markdown("By Andrew Ng. The industry standard introductory course for modern AI and deep learning.")
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("View Course", "https://www.coursera.org/learn/machine-learning", use_container_width=True)
        with col_res3:
            with st.container(border=True):
                st.markdown("#### LeetCode Premium")
                st.markdown("The best platform to help you enhance your algorithms and data structures skills.")
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("Start Practicing", "https://leetcode.com/", use_container_width=True)

else:
    # Empty State when no file is uploaded
    st.info("Please upload your CV or paste text in the sidebar to view your analysis and job matches.")
    
    st.markdown(
        """
        <div style='text-align: center; padding: 100px 20px; border: 2px dashed #CBD5E1; border-radius: 12px; background-color: #F8FAFC; margin-top: 40px;'>
            <h2 style='color: #475569;'>Awaiting Document Upload</h2>
            <p style='color: #64748B; font-size: 18px;'>Upload your resume in the sidebar to generate your personalized career dashboard.</p>
        </div>
        """, unsafe_allow_html=True
    )