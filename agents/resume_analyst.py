import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_config import get_llm

def analyze_resume(resume_text: str):
    llm = get_llm(temperature=0.0)
    parser = JsonOutputParser()

  
    prompt_template = PromptTemplate(
        template="""
        You are an expert Technical Recruiter with 15 years of experience.
        You are analyzing a candidate's resume for a mock interview system.
        
        RESUME TEXT:
        {resume_text}
        
        YOUR TASK:
        Extract structured data in strict JSON format.
        
        Pay special attention to the "projects" section. 
        For each project, extract:
        - "name": Project Title
        - "description": A 1-sentence summary of what it does.
        - "tech_stack": List of tools/languages used in that specific project.
        
        OUTPUT SCHEMA:
        {{
            "name": "Candidate Name",
            "role": "Inferred Role",
            "skills": ["Skill1", "Skill2"...],
            "projects": [
                {{
                    "name": "Project Name",
                    "description": "Brief summary...",
                    "tech_stack": ["Tool1", "Tool2"]
                }}
            ],
            "experience_level": "Intern/Fresher/Junior/Mid-Level/Senior"
        }}
        CRITICAL INSTRUCTION FOR EXPERIENCE_LEVEL:
        - "Intern": Current student or only internship experience.
        - "Fresher": Graduated, 0-1 years experience.
        - "Junior": 1-3 years professional experience.
        - "Mid-Level": 3-5 years.
        - "Senior": 5+ years.
        
        {format_instructions}
        """,
        input_variables=["resume_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )

    chain = prompt_template | llm | parser

    try:
        print("Wait for some time, resume is being processed")
        result = chain.invoke({"resume_text": resume_text})
        return result
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return None

