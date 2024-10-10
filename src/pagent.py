import operator
from typing import Annotated, TypedDict
from langchain_core.messages import HumanMessage
from typing import List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langgraph.constants import Send
from langgraph.graph import END, StateGraph, START
from pydantic import BaseModel, Field, model_validator
from langchain_community.document_loaders import PyPDFLoader
from BillAgent import BillAgent
# Model and prompts
# Define model and prompts we will use
subjects_prompt = """Generate a comma separated list of things of exactly {count} examples related to: {topic}."""
joke_prompt = """Generate a poem {subject}"""
best_joke_prompt = """Below are a bunch of poems about {topic}. Select the best one! Return the ID of the best one.

{jokes}"""

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(
    model_name="meta-llama/Llama-3.1-70B-Instruct",
    # model_name="meta-llama/llama-3.1-405b-instruct",
    api_key="test123",
    base_url="http://localhost:8000/v1",
    # temperature = 0
)


class Subjects(BaseModel):
    """ List of examples related to a given Topic"""
    subjects: list[str]=Field(..., description="List of subjects each as string")


class Joke(BaseModel):
    """single Poem Based on the subject"""
    joke: str = Field(..., description="Poem Based on the subject")


class BestJoke(BaseModel):
    """has the ID of the best joke among all the Poems"""
    id: int = Field(description="Index of the best Poem, starting with 0")


model = llm

# Graph components: define the components that will make up the graph


# This will be the overall state of the main graph.
# It will contain a topic (which we expect the user to provide)
# and then will generate a list of subjects, and then a joke for
# each subject
class OverallState(TypedDict):
    count: int
    # Notice here we use the operator.add
    # This is because we want combine all the jokes we generate
    # from individual nodes back into one list - this is essentially
    # the "reduce" part
    bill: str
    runs: Annotated[List, operator.add]


# This will be the state of the node that we will "map" all
# subjects to in order to generate a joke
class BAgentState(TypedDict):
    bill: str

class Agent:
    def __init__(self):
        graph = StateGraph(OverallState)
        graph.add_node("bill_agent", self.bill_agent)
        graph.add_conditional_edges(START, self.start_agent, ["bill_agent"])
        graph.add_edge("bill_agent", END)
        self.app = graph.compile()



    # Here we generate a joke, given a subject
    def bill_agent(self, state: BAgentState):
        agent = BillAgent()
        res = agent.run(state['bill'])
        return {"runs": [res]}



    def start_agent(self, state: OverallState):
        return [Send("bill_agent", {"bill": state["bill"]}) for s in range(state["count"])]



    def init(self, bill = None, count = 2):
        res = self.app.invoke({"bill":bill, "count":count})
        return {"res":res['runs']}


async def get_bill():
    file_path = "20232AB1_97.pdf"
    loader = PyPDFLoader(file_path)
    pages = []
    async for page in loader.alazy_load():
        pages.append(page)
    bill = ''.join([i.page_content for i in pages])
    return bill

if __name__=="__main__":
    agent = Agent()
    res = agent.init(get_bill())
    for i in res['res']:
        print(i)
