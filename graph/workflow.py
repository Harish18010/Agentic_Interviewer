from langgraph.graph import StateGraph, END
from graph.state import InterviewState
from agents.interviewer import ask_question_node
from agents.grader import grade_answer_node

def route_after_grade(state):
    if state["follow_up_count"] > 0:
        return "wait_for_user"
    else:
        return "ask_next"

def build_graph():
    workflow = StateGraph(InterviewState)

    workflow.add_node("grader", grade_answer_node)
    workflow.add_node("interviewer", ask_question_node)

    workflow.set_entry_point("grader")
    
    workflow.add_conditional_edges(
        "grader",
        route_after_grade,
        {
            "wait_for_user": END,
            "ask_next": "interviewer"
        }
    )
    
    workflow.add_edge("interviewer", END)

    return workflow.compile()