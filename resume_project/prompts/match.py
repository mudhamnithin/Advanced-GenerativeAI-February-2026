from langchain_core.prompts import PromptTemplate

match_p = PromptTemplate(
    input_variables=["data", "job"],
    template="""
compare resume and job

resume:
{data}

job:
{job}

tell matching and missing skills
dont assume anything
"""
)