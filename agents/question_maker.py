from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_config import get_llm
import random 

def get_strategy_prompt(role: str, company_type: str, experience_level: str) -> str:
    
    design_topic = "System Design (Scalability focus)"
    if experience_level in ["Intern", "Fresher"]:
        design_topic = "Object Oriented Design (e.g., Chess Game) or Logic Puzzle"
    
    if company_type == "AI / ML Engineer" or ("AI" in role or "Data" in role):
        return f"""
        STRATEGY: AI ENGINEER ({experience_level})
        - Q1 (Theory): Select ONE random core unexpected tricky and random concept from machine learning /deep learning /generative AI.
        - Q2 (Project): Architecture or Loss function specific to their project and improvements which can be made.
        - Q3 (Project): Any important part of project a senior engineer would notice.
        - Q4 (System): {"MLOps/Deployment scenario" if experience_level not in ["Intern", "Fresher"] else " Model Evaluation Metrics not limited to classical ML can ask generative AI also"}.
        - Q5 (Hard): {"Research Trends (Scaling Laws)" if experience_level not in ["Intern", "Fresher"] else "Tricky practical use case of ML/DL/Gen AI Algorithm Implementation logic "}.
        """

    elif company_type == "SDE (FAANG / Product Based)":
        return f"""
        STRATEGY: PRODUCT BASED / FAANG ({experience_level})
        - Q1 (CS Fundamentals): Practical application of OS/DBMS/Networks.
        - Q2 (DSA - Medium): Leetcode Medium Array/String/LinkedList problem.
        - Q3 (DSA - Hard):Leetcode Medium/Hard Graph/DP/Tree problem. Specify constraints.
        - Q4 (Project): Technical challenge deep dive.
        - Q5 (Design): {design_topic}.
        """

    elif company_type == "SDE (Startup / Generalist)":
        return f"""
        STRATEGY: STARTUP / ENGINEERING ({experience_level})
        - Q1 (Practical): Language/Framework specific trade-offs.
        - Q2 (Project): Hardest bug fixed.
        - Q3 (Project): {"Scaling/Performance optimization" if experience_level not in ["Intern", "Fresher"] else "Code structure/Refactoring"}.
        - Q4 (Scenario): Production Debugging.
        - Q5 (Culture): Speed vs. Quality trade-off.
        """
    
    elif company_type == "Product Manager (PM)":
        return """
        STRATEGY: PRODUCT MANAGER
        - Q1 (Technical): SQL Query.
        - Q2 (Guesstimate): Market Sizing.
        - Q3 (Product Sense): Root Cause Analysis.
        - Q4 (Case Study): Metric Improvement.
        - Q5 (Behavioral): Conflict resolution.
        """

    elif company_type == "SDE (Service Based)":
        return """
        STRATEGY: SERVICE BASED
        - Q1 (Basic): OOPs concepts.
        - Q2 (Language): Python/Java specifics.
        - Q3 (Database): SQL Basics.
        - Q4 (Project): Explain project flow.
        - Q5 (Logic): Puzzle/Aptitude.
        """
    
    return ""
    

def generate_questions(resume_data: dict, role: str, company_type: str, experience_level: str):
    llm = get_llm(temperature=0.9) 
    parser = JsonOutputParser()
    
    strategy_instruction = get_strategy_prompt(role, company_type, experience_level)
    seed = random.randint(1, 10000)

    prompt_template = PromptTemplate(
        template="""
        You are a Senior Technical Interviewer.
        
        # SYSTEM CONTEXT
        - Random Seed: {seed}
        
        CANDIDATE PROFILE:
        {resume_data}
        
        EXPERIENCE LEVEL: {experience_level}

        YOUR STRATEGY:
        {strategy_instruction}

        YOUR TASK:
        Generate exactly 5 interview questions following the strategy above.
        
        CRITICAL RULES:
        - ADJUST COMPLEXITY: Ensure questions are appropriate for a '{experience_level}'. 
          (e.g., Don't ask an Intern about distributed sharding).
        - DIVERSITY: Do NOT simply copy the examples. Pick different topics.
        - RELEVANCE: Match the candidate's tech stack.
        - If the strategy asks for DSA, ensure it matches the difficulty (Medium vs Hard).
        - If asking about LeetCode Hard, specify the constraints.
        - If asking for RCA/Guesstimate, ensure it is open-ended.

        OUTPUT SCHEMA (Strict JSON):
        [
            {{
                "id": 1,
                "question": "The actual question text...",
                "topic": "Topic Category",
                "difficulty": "Easy/Medium/Hard"
            }},
            ...
        ]

        {format_instructions}
        """,
        input_variables=["resume_data", "company_type", "strategy_instruction", "experience_level", "seed"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt_template | llm | parser

    try:
        print(f"Generating Questions for {experience_level} level (Seed: {seed})...")
        questions = chain.invoke({
            "resume_data": str(resume_data),
            "company_type": company_type,
            "strategy_instruction": strategy_instruction,
            "experience_level": experience_level,
            "seed": seed
        })
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []