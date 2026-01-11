from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages
import operator

class InterviewContext(TypedDict):
    company_type: str
    difficulty: str

class SystemMetrics(TypedDict):
    total_tokens: int
    latencies: List[float]
    start_time: float
    end_time: float

class InterviewState(TypedDict):
    resume_text: str 
    candidate_profile: Dict[str, Any]
    interview_context: InterviewContext
    sys_metrics: SystemMetrics
    question_bank: List[Dict[str, Any]] 
    current_question_index: int 
    messages: Annotated[List[dict], add_messages] 
    feedback_report: str
    feedback_log: Annotated[List[Dict], operator.add]
    follow_up_count: int
    experience_level: str
    current_grade_status: str