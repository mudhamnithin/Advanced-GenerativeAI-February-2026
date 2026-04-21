from langchain_core.prompts import PromptTemplate

extract_p = PromptTemplate(
    input_variables=["res"],
    template="""
read the resume and give:
skills
tools
experience

resume:
{res}

dont add extra data
"""
)