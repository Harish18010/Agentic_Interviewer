from langchain_core.prompts import PromptTemplate
from langchain_core.messages import AIMessage
from utils.llm_config import get_llm
import time

def generate_followup_node(state):
    questions = state.get("question_bank", [])
    idx = state.get("current_question_index", 0)
    messages = state.get("messages", [])
    follow_up_count = state.get("follow_up_count", 0)
    feedback_log = state.get("feedback_log", [])
    
    sys_metrics = state.get("sys_metrics", {
        "total_tokens": 0, "latencies": [], "start_time": time.time(), "end_time": 0.0
    })

    if not questions or idx >= len(questions):
        return {"follow_up_count": 0}

    current_q = questions[idx]
    last_answer = messages[-1].content
    
    last_feedback = ""
    if feedback_log:
        last_feedback = feedback_log[-1].get("detailed_feedback", "")

    llm = get_llm(temperature=0.6)

    prompt = PromptTemplate(
        template="""
        You are a Technical Interviewer.
        The candidate gave a PARTIALLY CORRECT answer to the question below.
        
        ORIGINAL QUESTION: {question}
        TOPIC: {topic}
        CANDIDATE ANSWER: {answer}
        GRADER FEEDBACK: {feedback}
        
        YOUR TASK:
        Ask a short, targeted follow-up question to help the candidate correct their mistake or add the missing detail.
        - Do NOT give the answer away.
        - Be encouraging but firm.
        - Keep it conversational (1-2 sentences).
        
        OUTPUT: Just the follow-up question text.
        """,
        input_variables=["question", "topic", "answer", "feedback"]
    )

    start_time = time.time()
    chain = prompt | llm
    
    response = chain.invoke({
        "question": current_q["question"],
        "topic": current_q["topic"],
        "answer": last_answer,
        "feedback": last_feedback
    })
    
    token_usage = response.response_metadata.get('usage_metadata', {}).get('total_token_count', 0)
    sys_metrics["total_tokens"] += token_usage
    sys_metrics["latencies"].append(time.time() - start_time)

    return {
        "messages": [AIMessage(content=response.content)],
        "follow_up_count": follow_up_count + 1,
        "sys_metrics": sys_metrics
    }