import streamlit as st
import re

# ----PAGE SETUP
st.set_page_config(page_title="UpskillxAI", layout="wide")



st.markdown("<h1 style='text-align: center;'>UpskillxAI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>AI Powered Upskilling</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload your CV to match with top jobs and uncover your skill gaps.</p>", unsafe_allow_html=True)

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        ":material/query_stats: Skills Analysis", 
        ":material/work: Job Matches", 
        ":material/school: Learning Paths",
        ":material/description: Resume Builder",
        ":material/forum: Career Assistant"
    ])
    
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
                "location": "Redmond, WA",
                "workplace": "Hybrid",
                "role": "Full-time",
                "jobUrl": "https://careers.microsoft.com/software-engineer", 
                "salary": "$150,000 - $190,000"
            },
            {
                "position": "Data Scientist", 
                "company": "Google", 
                "location": "Mountain View, CA", 
                "workplace": "Office",
                "role": "Full-time",
                "jobUrl": "https://careers.google.com/data-scientist", 
                "salary": "$160,000 - $210,000"
            },
            {
                "position": "Machine Learning Engineer", 
                "company": "OpenAI", 
                "location": "San Francisco, CA", 
                "workplace": "Remote",
                "role": "Contract",
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
                    st.markdown(
                        f"""
                        <style>
                        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20,400,0,0');
                        </style>
                        <div style='margin-top: 8px; display: flex; gap: 8px; align-items: center;'>
                            <span style='background-color: #E2E8F0; color: #475569; padding: 4px 10px; border-radius: 16px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 4px;'>
                                <span class="material-symbols-rounded" style="font-size: 16px;">apartment</span> {job.get('workplace', 'Office')}
                            </span>
                            <span style='background-color: #E2E8F0; color: #475569; padding: 4px 10px; border-radius: 16px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 4px;'>
                                <span class="material-symbols-rounded" style="font-size: 16px;">schedule</span> {job.get('role', 'Full-time')}
                            </span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
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

    # TAB 4: Resume Builder
    with tab4:
        st.markdown("#### Resume Builder")
        st.markdown("Generate a tailored resume based on your extracted skills and target roles.")
        st.info("This feature is currently under development. Stay tuned!")

    # TAB 5: Career Assistant
    with tab5:
        st.markdown("#### Career Assistant")
        st.markdown("Ask questions about your career path, recommended courses, or skill gaps.")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Hardcoded chat history
        with st.chat_message("user"):
            st.markdown("Is the Google Generative AI course relevant for me?")
            
        with st.chat_message("assistant"):
            st.markdown("It is not highly relevant at this point because you are pursuing a core Data Science role. Focusing on foundational machine learning and advanced statistical modeling would be more beneficial for your current career trajectory.")
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Fake chat input
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            st.text_input("Message Career Assistant", placeholder="Type your question here...", label_visibility="collapsed")
        with chat_col2:
            st.button("Send", use_container_width=True, type="primary")

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