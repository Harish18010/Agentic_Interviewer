from langchain_core.prompts import ChatPromptTemplate
from utils.llm_config import get_llm
import time

def ask_question_node(state):
    idx = state.get("current_question_index", 0)
    questions = state.get("question_bank", [])
    sys_metrics = state.get("sys_metrics", {
        "total_tokens": 0,
        "latencies": [],
        "start_time": time.time(),
        "end_time": 0.0
    })
    
    if idx >= len(questions):
        return {
            "messages": [{"role": "assistant", "content": "Thank you! That concludes our interview. I have gathered enough data to provide feedback."}],
            "current_question_index": idx 
        }
    
    current_q = questions[idx]
    
    llm = get_llm(temperature=0.7)
    
    prompt = ChatPromptTemplate.from_template(
        """
        You are a professional Technical Interviewer.
        Your goal is to ask the next technical question clearly and professionally.
        
        CONTEXT:
        - Question Number: {index} of {total}
        - Topic: {topic}
        
        RAW QUESTION:
        {raw_question}
        
        YOUR TASK:
        Rephrase the "RAW QUESTION" slightly to sound natural and spoken.
        - If it's the first question, welcome the candidate briefly.
        - DO NOT change the technical core of the question.
        - Keep it concise.
        """
    )
    
    chain = prompt | llm
    start_time = time.time()
    
    response = chain.invoke({
        "index": idx + 1,
        "total": len(questions),
        "topic": current_q["topic"],
        "raw_question": current_q["question"]
    })
    end_time = time.time()
    latency = end_time - start_time
    token_usage = response.response_metadata.get('usage_metadata', {}).get('total_token_count', 0)
    sys_metrics["total_tokens"] += token_usage
    sys_metrics["latencies"].append(latency)
    
    return {"messages": [response],
            "sys_metrics":sys_metrics
            }