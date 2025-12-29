from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import AIMessage
from utils.llm_config import get_llm
import time

def grade_answer_node(state):
    idx = state.get("current_question_index", 0)
    questions = state.get("question_bank", [])
    messages = state.get("messages", [])
    follow_up_count = state.get("follow_up_count", 0)
    feedback_log = state.get("feedback_log", [])
    
    sys_metrics = state.get("sys_metrics", {
        "total_tokens": 0,
        "latencies": [],
        "start_time": time.time(),
        "end_time": 0.0
    })

    if not questions or idx >= len(questions):
        return {"current_question_index": idx + 1}

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
        4. Decide if a FOLLOW-UP is needed (Max depth 3).

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

        # FOLLOW-UP RULES:
        - Trigger a follow-up IF:
          a) The answer is "Partially Correct" (missing key details).
          b) The Topic is "DSA" or "System Design" and the user missed Time Complexity/Scalability.
          c) The Topic involves a "Project" or "Experience" and the answer lacks technical depth, trade-offs, or specific implementation details.
        - DO NOT follow up if the answer is completely Wrong, completely Correct, or Skipped.

        # OUTPUT REQUIREMENTS
        1. "concise_feedback": A short, spoken-style summary (Max 2 sentences) for the audio voice.
        2. "detailed_feedback": A deep, technical analysis (Paragraph). IF SKIPPED, explain the correct answer here.
        
        OUTPUT SCHEMA (Strict JSON):
        {{
            "status": "Correct/Partially Correct/Incorrect/Skipped",
            "concise_feedback": "Short spoken feedback...",
            "detailed_feedback": "In-depth technical analysis OR Correct Answer...",
            "needs_follow_up": true/false,
            "follow_up_question": "The actual follow-up question text (if needed)"
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
    
    token_usage = response_msg.response_metadata.get('usage_metadata', {}).get('total_token_count', 0)
    
    try:
        grade_result = parser.invoke(response_msg)
    except:
        grade_result = {"status": "Error", "concise_feedback": "Error parsing.", "detailed_feedback": "Error", "needs_follow_up": False}

    end_time = time.time()
    latency = end_time - start_time
    
    sys_metrics["total_tokens"] += token_usage
    sys_metrics["latencies"].append(latency)

    try:
        # Check follow-up logic (Max 3 depth, not skipped)
        if grade_result.get("needs_follow_up") and follow_up_count < 3 and grade_result["status"] != "Skipped":
            
            # Log the interaction so it appears in the report
            partial_log = {
                "index": idx + 1,
                "question": current_q["question"] if follow_up_count == 0 else "Follow-up Question",
                "user_answer": user_answer,
                "status": "Follow-up Interaction",
                "detailed_feedback": grade_result["concise_feedback"]
            }
            
            return {
                "messages": [
                    AIMessage(content=grade_result['concise_feedback']),
                    AIMessage(content=grade_result['follow_up_question'])
                ],
                "follow_up_count": follow_up_count + 1,
                "sys_metrics": sys_metrics,
                "feedback_log": [partial_log] 
            }
        
        final_log = {
            "index": idx + 1,
            "question": current_q["question"] if follow_up_count == 0 else "Final Follow-up Answer",
            "user_answer": user_answer,
            "status": grade_result["status"],
            "detailed_feedback": grade_result["detailed_feedback"]
        }
        
        return {
            "messages": [AIMessage(content=grade_result['concise_feedback'])],
            "current_question_index": idx + 1,
            "follow_up_count": 0, 
            "feedback_log": [final_log],
            "sys_metrics": sys_metrics
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {"current_question_index": idx + 1}