from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage
from utils.llm_config import get_llm
import time

def clean_json_text(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def grade_answer_node(state):
    idx = state.get("current_question_index", 0)
    questions = state.get("question_bank", [])
    messages = state.get("messages", [])
    follow_up_count = state.get("follow_up_count", 0)
    
    sys_metrics = state.get("sys_metrics", {
        "total_tokens": 0, "latencies": [], "start_time": time.time(), "end_time": 0.0
    })

    if not questions or idx >= len(questions):
        return {"current_grade_status": "Complete"}

    current_q = questions[idx]
    user_answer = messages[-1].content

    llm = get_llm(temperature=0.0)
    parser = JsonOutputParser()

    prompt = PromptTemplate(
        template="""
        You are a Senior Technical Interviewer and Grader.
        
        # CONTEXT
        QUESTION: {question}
        TOPIC: {topic}
        CANDIDATE ANSWER: {answer}
        
        # YOUR TASK
        1. Identify if the user SKIPPED (e.g., "I don't know", "pass", "skip").
        2. If SKIPPED: Mark status "Skipped" and provide the CORRECT technical answer in 'detailed_feedback'.
        3. If ANSWERED: Grade strictly based on the rules below.
        
        # CRITICAL GRADING RULES:
        1. IF the question is Factual (e.g., "What is ACID?"):
           - Check for specific technical accuracy and keywords matching the criteria.
           
        2. IF the question is Open-Ended (e.g., System Design, Guesstimate, RCA):
           - DO NOT look for a single "correct" answer.
           - IGNORE the final number or specific solution choice.
           - EVALUATE THE APPROACH: Did they break the problem down? Did they handle edge cases? Did they justify their choice?
        
        3. ASSIGN STATUS:
           - "Correct": Logical approach OR factual accuracy.
           - "Partially Correct": Good approach but missed edge cases, or minor factual error.
           - "Incorrect": Completely wrong logic or fact.
           - "Skipped": User explicitly skipped or said they don't know.

        # OUTPUT REQUIREMENTS
        1. "concise_feedback": A short, spoken-style summary (Max 2 sentences) acknowledging the answer.
        2. "detailed_feedback": A deep, technical analysis (Paragraph). IF SKIPPED, explain the correct answer here.
        
        OUTPUT SCHEMA (Strict JSON):
        {{
            "status": "Correct/Partially Correct/Incorrect/Skipped",
            "concise_feedback": "Short spoken feedback...",
            "detailed_feedback": "In-depth technical analysis OR Correct Answer..."
        }}
        
        {format_instructions}
        """,
        input_variables=["question", "topic", "answer"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    start_time = time.time()
    chain_gen = prompt | llm
    
    response_msg = chain_gen.invoke({
        "question": current_q["question"],
        "topic": current_q["topic"],
        "answer": user_answer
    })
    
    usage = response_msg.response_metadata.get('usage_metadata')
    if usage:
        token_usage = usage.get('total_token_count', 0)
    else:
        token_usage = response_msg.response_metadata.get('token_usage', {}).get('total_tokens', 0)
    
    try:
        raw_content = response_msg.content
        cleaned_content = clean_json_text(raw_content)
        grade_result = parser.parse(cleaned_content)
    except Exception:
        grade_result = {
            "status": "Incorrect", 
            "concise_feedback": "I'm having trouble understanding that. Let's move on.", 
            "detailed_feedback": "System Error: Failed to parse grading response. Moving to next question."
        }

    end_time = time.time()
    latency = end_time - start_time
    
    sys_metrics["total_tokens"] += token_usage
    sys_metrics["latencies"].append(latency)

    log_entry = {
        "index": idx + 1,
        "question": current_q["question"],
        "user_answer": user_answer,
        "status": grade_result["status"],
        "detailed_feedback": grade_result["detailed_feedback"]
    }

    status = grade_result["status"]
    
    should_advance = (status != "Partially Correct") or (status == "Partially Correct" and follow_up_count >= 2)
    
    next_idx = idx + 1 if should_advance else idx
    next_follow_up = 0 if should_advance else follow_up_count
    
    flow_status = "Correct" if should_advance else "Partially Correct"
    
    output_messages = []
    if should_advance:
         output_messages = [AIMessage(content=grade_result["concise_feedback"])]

    return {
        "current_grade_status": flow_status,
        "current_question_index": next_idx, 
        "follow_up_count": next_follow_up,
        "feedback_log": [log_entry],
        "sys_metrics": sys_metrics,
        "messages": output_messages
    }