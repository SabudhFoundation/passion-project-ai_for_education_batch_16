import streamlit as st
import requests
import tempfile
import os

# ----PAGE SETUP
st.set_page_config(page_title="UpskillxAI", layout="wide")

st.markdown("<h1 style='text-align: center;'>UpskillxAI</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>AI Powered Upskilling</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload your CV and JD to match with top jobs and uncover your skill gaps.</p>", unsafe_allow_html=True)

# ---- SIDEBAR (INPUT)
with st.sidebar:
    st.header("Document Upload")
    st.markdown("Provide your details below to get started.")
    
    uploaded_files = st.file_uploader(
        "Upload CV",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        help="Supported formats: PDF, DOCX, TXT."
    )

    with st.expander("Or paste CV text directly"):
        user_text = st.text_area("Paste CV text here...", height=150)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    jd_input = st.text_area("Job Description (Paste Text or URL)", placeholder="e.g., https://linkedin.com/... or paste text")
    
    job_pref = st.text_input("Target Role", placeholder="e.g., Senior Software Engineer")
    
    analyze_btn = st.button("Analyze Profile", type="primary", use_container_width=True)

# ---- MAIN AREA
if analyze_btn:
    if not (uploaded_files or user_text):
        st.warning("Please upload a CV or paste CV text.")
    elif not jd_input:
        st.warning("Please provide a Job Description (URL or text).")
    else:
        resume_input = ""
        if uploaded_files:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, uploaded_files.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_files.getvalue())
            resume_input = temp_path
        else:
            resume_input = user_text
            
        with st.spinner("Analyzing profile, finding skill gaps, matching jobs, and fetching resources... (This may take a minute)"):
            try:
                response = requests.post("http://127.0.0.1:8000/pipeline/run", json={
                    "resume_input": resume_input,
                    "jd_input": jd_input,
                    "target_role": job_pref,
                    "location": ""
                })
                if response.status_code == 200:
                    st.session_state["pipeline_data"] = response.json()
                else:
                    st.error(f"Error from backend: {response.text}")
            except Exception as e:
                st.error(f"Failed to connect to backend API: {e}. Make sure it is running on port 8000.")

if "pipeline_data" in st.session_state:
    data = st.session_state["pipeline_data"]
    
    extracted_skills = data.get("candidate_skills", [])
    required_skills = data.get("required_skills", [])
    skill_gaps = data.get("skill_gaps", [])
    ats_score = data.get("ats_score", 0)
    job_listings = data.get("job_listings", [])
    static_resources = data.get("static_resources", [])
    career_summary = data.get("career_summary", "")
    
    st.markdown("---")
    
    st.subheader("Profile Overview")
    
    # Career Summary
    if career_summary:
        st.info(career_summary)
        
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(label="Target Role", value=job_pref if job_pref else "Not specified")
    with m2:
        st.metric(label="Skills Found", value=str(len(extracted_skills)))
    with m3:
        st.metric(label="ATS Match Score", value=f"{ats_score}%")
    with m4:
        st.metric(label="Job Matches", value=str(len(job_listings)) if job_listings else "0")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---- TABS ----
    # Dropped Resume Builder as discussed
    tab1, tab2, tab3, tab4 = st.tabs([
        ":material/query_stats: Skills Analysis", 
        ":material/work: Job Matches", 
        ":material/school: Learning Paths",
        ":material/forum: Career Assistant"
    ])
    
    with tab1:
        st.markdown("#### Skill Match Breakdown")
        c1, c2 = st.columns(2)
        with c1:
            st.success("**Verified Skills (You possess these)**")
            if extracted_skills:
                for skill in extracted_skills:
                    st.markdown(f"- {skill}")
            else:
                st.write("No technical skills detected.")
        with c2:
            st.warning("**Skill Gaps (Recommended to learn)**")
            if skill_gaps:
                for skill in skill_gaps:
                    st.markdown(f"- {skill}")
            else:
                st.write("No major skill gaps detected!")
                
        with st.expander("View Extracted Raw Text"):
            st.text("RESUME TEXT:\n" + data.get("resume_text", ""))
            st.text("\n\nJD TEXT:\n" + data.get("job_description", ""))
            
    with tab2:
        st.markdown("#### Recommended Opportunities")
        if not job_listings:
            st.info("No jobs found for this role/location right now.")
        else:
            for job in job_listings:
                with st.container(border=True):
                    colA, colB = st.columns([3, 1])
                    with colA:
                        st.markdown(f"### {job.get('Title', 'Unknown Title')}")
                        st.markdown(f"**{job.get('Company', 'Unknown Company')}** | {job.get('Location', 'Unknown Location')}")
                        st.markdown(
                            f"""
                            <style>
                            @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20,400,0,0');
                            </style>
                            <div style='margin-top: 8px; display: flex; gap: 8px; align-items: center;'>
                                <span style='background-color: #E2E8F0; color: #475569; padding: 4px 10px; border-radius: 16px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 4px;'>
                                    <span class="material-symbols-rounded" style="font-size: 16px;">work_history</span> {job.get('Experience', 'Not specified')}
                                </span>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        st.caption(job.get('Description', ''))
                    with colB:
                        st.markdown(f"<h4 style='color: #059669; margin-bottom: 0;'>{job.get('Salary', 'Not Disclosed')}</h4>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        if job.get('Link') and job.get('Link') != 'N/A':
                            st.link_button("Apply Now", job['Link'], type="primary", use_container_width=True)
                        else:
                            st.button("No Link", disabled=True, key=job.get('Title')+job.get('Company'))

    with tab3:
        st.markdown("#### Recommended Learning Paths")
        if not static_resources:
            st.info("No resources found.")
        else:
            cols = st.columns(3)
            for i, res in enumerate(static_resources):
                col = cols[i % 3]
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{res.get('title', 'Course')}**")
                        st.link_button("View Resource", res.get("link", "#"), use_container_width=True)

    with tab4:
        st.markdown("#### Career Assistant")
        st.markdown("Ask questions about your career path, recommended courses, or skill gaps.")
        
        with st.chat_message("user"):
            st.markdown("Is the Google Generative AI course relevant for me?")
            
        with st.chat_message("assistant"):
            st.markdown("It is not highly relevant at this point because you are pursuing a core Data Science role. Focusing on foundational machine learning and advanced statistical modeling would be more beneficial for your current career trajectory.")
            
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        chat_col1, chat_col2 = st.columns([5, 1])
        with chat_col1:
            st.text_input("Message Career Assistant", placeholder="Type your question here...", label_visibility="collapsed")
        with chat_col2:
            st.button("Send", use_container_width=True, type="primary")

elif not analyze_btn and "pipeline_data" not in st.session_state:
    st.info("Please upload your CV and JD in the sidebar, then click 'Analyze Profile'.")
    st.markdown(
        """
        <div style='text-align: center; padding: 100px 20px; border: 2px dashed #CBD5E1; border-radius: 12px; background-color: #F8FAFC; margin-top: 40px;'>
            <h2 style='color: #475569;'>Awaiting Document Upload</h2>
            <p style='color: #64748B; font-size: 18px;'>Upload your resume and Job Description in the sidebar to generate your personalized career dashboard.</p>
        </div>
        """, unsafe_allow_html=True
    )