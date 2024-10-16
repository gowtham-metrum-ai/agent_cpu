import operator
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage
from typing import List
from prefect import flow, task
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langgraph.constants import Send
from langgraph.graph import END, StateGraph, START
from pydantic import BaseModel, Field, model_validator
from langchain_openai import ChatOpenAI
# from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    # model_name="meta-llama/llama-3.2-3b-instruct:free",
    model_name="meta-llama/llama-3.1-70b-instruct",
    api_key="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",
    base_url="https://openrouter.ai/api/v1",
    temperature = 0
)
from langchain_community.document_loaders import PyPDFLoader





lac_prompt= """You are the Legal and Compliance Agent, 
Analyze the constitutionality of this legislative bill. Identify any sections that might conflict with the constitution or existing legal precedents. 
Ensure the bill respects fundamental rights and freedoms. 
Cross-check for potential contradictions with current laws and regulations, and point out any sections that could lead to legal disputes or challenges. 
Lastly, review the bill for procedural compliance with legislative requirements such as format, language, and legislative terms.
Give a Review a Suggestion and a Score(out of 10) for the Bill based on your observation.
------------------------------------------------
BILL
{bill}
"""
eabi_prompt = """You are the  Economic and Budgetary Impact Agent, 
Evaluate the financial implications of this legislative bill. 
Conduct a cost-benefit analysis, outlining the short- and long-term financial costs of implementing the bill. 
Identify any budgetary impacts, such as required funding or reallocation of resources, and assess the viability of any funding mechanisms proposed in the bill. 
Analyze how this bill may affect the overall economy, including its potential impact on businesses, industries, employment, and tax revenue. 
Finally, determine whether the fiscal obligations created by the bill are sustainable in the long term.
Give a Review a Suggestion and a Score(out of 10) for the Bill based on your observation.
------------------------------------------------
BILL
{bill}"""

saei_prompt = """You are the Social and Environmental Impact Agent,
Assess the social and environmental impact of this legislative bill. 
Examine how the bill will affect different demographic groups, with particular attention to marginalized or vulnerable populations. 
Determine whether the bill promotes social equity or poses any risks of disproportionate harm to certain groups. 
Next, evaluate the environmental consequences, including impacts on natural resources, pollution levels, climate, and sustainability. 
Ensure compliance with environmental regulations. 
Finally, gather or summarize public opinion and stakeholder feedback related to this bill, if available.
Give a Review a Suggestion and a Score(out of 10) for the Bill based on your observation.
------------------------------------------------
BILL
{bill}"""

iafa_prompt = """You are the Implementation and Feasibility Agent, 
Analyze the feasibility and practicality of implementing this legislative bill. 
Assess whether the necessary resources (financial, human, and technological) are available to enforce the provisions of the bill. 
Identify any potential administrative challenges and ensure that relevant government agencies or bodies are capable of handling the bill’s requirements. 
Review the enforceability of the bill, looking for any provisions that may be difficult to enforce or monitor. 
Finally, check the bill’s timeline for implementation to ensure it is realistic, and flag any risks that could hinder its successful rollout.
Give a Review a Suggestion and a Score(out of 10) for the Bill based on your observation.
------------------------------------------------
BILL
{bill}
"""



class Review(BaseModel):
    """Review Given by the Agent for the Passed Bill"""
    name: str=Field(..., description="Name of the Agent")
    review: str=Field(..., description="Review for the Bill")
    suggestion: str=Field(..., description="Suggestions for improving the Bill")
    score: int=Field(..., description="A Number from 0 to 10 ")




model = llm
class OverallState(TypedDict):
    bill: str
    reviews: Annotated[List, operator.add]
    completed: bool



class EABIAgent():
    def __init__(self):
        graph = StateGraph(OverallState)
        # graph.add_node("Legal and Compliance Agent", self.LAC)
        graph.add_node("Economic and Budgetary Impact Agent", self.EABI)
        # graph.add_node("Social and Environmental Impact Agent", self.SAEI)
        # graph.add_node("Implementation and Feasibility Agent", self.IAFA)
        # graph.add_edge(START, "Legal and Compliance Agent")
        graph.add_edge(START, "Economic and Budgetary Impact Agent")
        # graph.add_edge("Economic and Budgetary Impact Agent", "Social and Environmental Impact Agent")
        # graph.add_edge(START, "Implementation and Feasibility Agent")
        # graph.add_edge("Legal and Compliance Agent", END)
        # graph.add_edge("Economic and Budgetary Impact Agent", END)
        graph.add_edge("Economic and Budgetary Impact Agent", END)
        # graph.add_edge("Implementation and Feasibility Agent", END)
        self.agent = graph.compile()


    # Here we generate a joke, given a subject
    @task(name = "Legal and Compliance Agent")
    def LAC(self, state: OverallState):
        parser = PydanticOutputParser(pydantic_object=Review)
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user query. return the output only inside a JSON Format\n{format_instructions}\n Only return the JSON",
            ),
            ("human", lac_prompt),
        ]).partial(format_instructions=parser.get_format_instructions())
        chain = prompt | model #| parser
        response = chain.invoke(state['bill'])
        return {"reviews": [response.content]}

    @task(name = "Economic and Budgetary Impact Agent")
    def EABI(self, state: OverallState):
        parser = PydanticOutputParser(pydantic_object=Review)
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user query. return the output only inside a JSON Format\n{format_instructions} Only return the JSON",
            ),
            ("human", eabi_prompt),
        ]).partial(format_instructions=parser.get_format_instructions())
        chain = prompt | model #| parser
        response = chain.invoke(state['bill'])
        return {"reviews": [response.content]}

    @task(name = "Social and Environmental Impact Agent")
    def SAEI(self, state: OverallState):
        parser = PydanticOutputParser(pydantic_object=Review)
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user query. return the output only inside a JSON Format\n{format_instructions} Only return the JSON",
            ),
            ("human", saei_prompt),
        ]).partial(format_instructions=parser.get_format_instructions())
        chain = prompt | model #| parser
        response = chain.invoke(state['bill'])
        return {"reviews": [response.content]}

    @task(name = "Implementation and Feasibility Agent")
    def IAFA(self, state: OverallState):
        parser = PydanticOutputParser(pydantic_object=Review)
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer the user query. return the output only inside a JSON Format\n{format_instructions}",
            ),
            ("human", iafa_prompt),
        ]).partial(format_instructions=parser.get_format_instructions())
        chain = prompt | model #| parser
        response = chain.invoke(state['bill'])
        return {"reviews": [response.content]}
    
    def run(self, bill = None):
        res = self.agent.invoke({"bill":bill})
        return res['reviews']

async def get_bill():
    file_path = "20232AB1_97.pdf"
    loader = PyPDFLoader(file_path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page)
    bill = ''.join([i.page_content for i in pages])
    return bill

if __name__=="__main__":
    agent = BillAgent()
    res = agent.run(get_bill())
    for i in res:
        print(i)




