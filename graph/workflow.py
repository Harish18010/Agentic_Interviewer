from langgraph.graph import StateGraph, END
from graph.state import InterviewState
from agents.interviewer import ask_question_node
from agents.grader import grade_answer_node
from agents.followup import generate_followup_node

def route_after_grade(state):
    status = state.get("current_grade_status", "Correct")
    follow_up_count = state.get("follow_up_count", 0)

    if status == "Partially Correct" and follow_up_count < 2:
        return "generate_followup"
    else:
        return "interviewer"

def build_graph():
    workflow = StateGraph(InterviewState)

    workflow.add_node("grader", grade_answer_node)
    workflow.add_node("generate_followup", generate_followup_node)
    workflow.add_node("interviewer", ask_question_node)

    workflow.set_entry_point("grader")
    
    workflow.add_conditional_edges(
        "grader",
        route_after_grade,
        {
            "generate_followup": "generate_followup",
            "interviewer": "interviewer"
        }
    )

    workflow.add_edge("generate_followup", END)
    workflow.add_edge("interviewer", END)

    return workflow.compile()