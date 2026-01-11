import streamlit as st
import time
import os
from utils.pdf_loader import get_pdf_text
from agents.resume_analyst import analyze_resume
from agents.question_maker import generate_questions
from agents.interviewer import ask_question_node
from graph.workflow import build_graph
from langchain_core.messages import HumanMessage, AIMessage
from utils.voice import text_to_speech
from utils.report_generator import generate_pdf_report
from utils.database import init_db, save_interview, fetch_history, get_interview_data, generate_user_id

init_db()

st.set_page_config(page_title="AI Interviewer", layout="wide")

if "messages" not in st.session_state: st.session_state.messages = []
if "interview_active" not in st.session_state: st.session_state.interview_active = False
if "current_question_index" not in st.session_state: st.session_state.current_question_index = 0
if "question_bank" not in st.session_state: st.session_state.question_bank = []
if "feedback_log" not in st.session_state: st.session_state.feedback_log = []
if "sys_metrics" not in st.session_state: 
    st.session_state.sys_metrics = {"total_tokens": 0, "latencies": [], "start_time": time.time(), "end_time": 0.0}
if "user_id" not in st.session_state: st.session_state.user_id = generate_user_id()

st.title("AI Technical Interviewer")
st.markdown("---")

with st.sidebar:
    st.header(f"Candidate ID: {st.session_state.user_id}")
    st.caption("Save this ID to resume or load history.")
    st.divider()
    
    st.subheader("1. Setup Profile")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    
    experience_level = st.selectbox(
        "Experience Level", 
        ["Intern", "Fresher", "Junior (1-3y)", "Mid-Level (3-5y)", "Senior (5y+)"],
        index=1
    )
    
    st.subheader("2. Target Role")
    company_type = st.selectbox(
        "Target Company",
        ["SDE (FAANG / Product Based)", "SDE (Startup / Generalist)", "AI / ML Engineer", "Product Manager (PM)", "SDE (Service Based)"]
    )
    
    start_btn = st.button("Start Interview", use_container_width=True, type="primary")

    if st.session_state.interview_active:
        st.divider()
        st.subheader("Live Metrics")
        col1, col2 = st.columns(2)
        col1.metric("Tokens", st.session_state.sys_metrics["total_tokens"])
        if st.session_state.sys_metrics["latencies"]:
            avg_lat = sum(st.session_state.sys_metrics["latencies"]) / len(st.session_state.sys_metrics["latencies"])
            col2.metric("Avg Latency", f"{avg_lat:.2f}s")

    st.divider()
    with st.expander("Interview History"):
        lookup_id = st.text_input("Load User ID:", value=st.session_state.user_id)
        if lookup_id:
            history = fetch_history(lookup_id)
            if history:
                for run in history:
                    run_id, run_role, run_time = run
                    if st.button(f"{run_time[:10]} - {run_role}", key=f"hist_{run_id}"):
                        log_data = get_interview_data(run_id)
                        if log_data:
                            pdf_file = generate_pdf_report("Candidate", run_role, log_data)
                            with open(pdf_file, "rb") as f:
                                st.download_button("Download PDF", f, f"Report_{run_id}.pdf")
            else:
                st.info("No history found.")

if start_btn and uploaded_file:
    with st.status("Initializing Interview ", expanded=True) as status:
        st.write("Parsing Resume...")
        resume_text = get_pdf_text(uploaded_file)
        
        st.write("Analyzing Profile...")
        profile = analyze_resume(resume_text)
        st.session_state.profile = profile
        
      
        role = profile.get("role", company_type)
        questions = generate_questions(profile, role, company_type, experience_level)
        st.session_state.question_bank = questions
        
        st.session_state.sys_metrics = {"total_tokens": 0, "latencies": [], "start_time": time.time(), "end_time": 0.0}
        st.session_state.feedback_log = []
        st.session_state.messages = []
        st.session_state.follow_up_count = 0
        st.session_state.current_question_index = 0

        initial_state = {
            "resume_text": resume_text,
            "candidate_profile": profile,
            "company_type": company_type,
            "experience_level": experience_level,
            "question_bank": questions,
            "current_question_index": 0,
            "messages": [],
            "feedback_log": [],
            "sys_metrics": st.session_state.sys_metrics,
            "follow_up_count": 0,
            "current_grade_status": "Pending"
        }
        
        st.write("Interviewer is ready...")
        first_q_response = ask_question_node(initial_state)
        
        if "sys_metrics" in first_q_response:
            st.session_state.sys_metrics = first_q_response["sys_metrics"]
            
        st.session_state.messages = [first_q_response["messages"][0]]
        st.session_state.interview_active = True
        
        audio_file = "temp_audio.mp3"
        saved_path = text_to_speech(first_q_response["messages"][0].content, filename=audio_file)
        
        status.update(label="Interview Started!", state="complete", expanded=False)
        time.sleep(1)
        
        if saved_path:
            with open(saved_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3", autoplay=True)
        
        st.rerun()

if st.session_state.interview_active:
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            if "###_HIDDEN_FEEDBACK_###" in msg.content:
                st.info("(Audio Feedback Played)") 
            else:
                st.markdown(msg.content)

    if user_input := st.chat_input("Type your answer here..."):
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        app = build_graph()
        
        with st.status("AI Agents at work...", expanded=True) as status:
            st.write("Interviewer is evaluating your response...")
            
            current_inputs = {
                "messages": [HumanMessage(content=user_input)], 
                "current_question_index": st.session_state.current_question_index,
                "question_bank": st.session_state.question_bank,
                "feedback_log": st.session_state.feedback_log,
                "follow_up_count": st.session_state.get("follow_up_count", 0),
                "sys_metrics": st.session_state.sys_metrics,
                "experience_level": experience_level,
                "current_grade_status": "Pending"
            }
            
            result = app.invoke(current_inputs)
            
            st.write("Interviewer is formulating next response...")
            
            st.session_state.current_question_index = result["current_question_index"]
            st.session_state.follow_up_count = result.get("follow_up_count", 0)
            if "sys_metrics" in result: st.session_state.sys_metrics = result["sys_metrics"]
            if "feedback_log" in result: st.session_state.feedback_log = result["feedback_log"]
            
            all_msgs = result["messages"]
            new_msgs = [m for m in all_msgs if isinstance(m, AIMessage)]
            
            status.update(label="Response Ready", state="complete", expanded=False)
            
            if new_msgs:
                combined_text = " ... ".join([m.content for m in new_msgs])
                audio_file = "temp_audio.mp3"
                saved_path = text_to_speech(combined_text, filename=audio_file)
                if saved_path: 
                    with open(saved_path, "rb") as f:
                        st.audio(f.read(), format="audio/mp3", autoplay=True)

            for i, msg in enumerate(new_msgs):
                with st.chat_message("assistant"):
                    if i == 0 and st.session_state.sys_metrics["latencies"]:
                        last_latency = st.session_state.sys_metrics["latencies"][-1]
                        st.caption(f"Latency: {last_latency:.2f}s | Total Tokens: {st.session_state.sys_metrics['total_tokens']}")

                    if len(new_msgs) > 1 and i == 0:
                        st.info("Playing Feedback...")
                        st.session_state.messages.append(AIMessage(content=f"###_HIDDEN_FEEDBACK_### {msg.content}"))
                    else:
                        st.markdown(msg.content)
                        st.session_state.messages.append(msg)

            if st.session_state.current_question_index >= len(st.session_state.question_bank):
                st.success("Interview Complete! Generating Report...")
                st.session_state.interview_active = False
                
                save_interview(st.session_state.user_id, company_type, st.session_state.feedback_log)
                
                if os.path.exists("temp_audio.mp3"):
                    os.remove("temp_audio.mp3")
                
                pdf_file = generate_pdf_report(st.session_state.profile.get("name", "Candidate"), company_type, st.session_state.feedback_log)
                with open(pdf_file, "rb") as f:
                    st.download_button("Download Detailed Report", f, "Interview_Report.pdf", type="primary")

else:
    if not uploaded_file:
        st.info("Welcome! Please upload your resume on the left sidebar to begin.")