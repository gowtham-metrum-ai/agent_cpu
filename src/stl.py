import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
from pagent import Agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import pdfplumber
class Review(BaseModel):
    """Review Given by the Agent for the Passed Bill"""
    name: str=Field(..., description="Name of the Agent")
    review: str=Field(..., description="Review for the Bill")
    suggestion: str=Field(..., description="Suggestions for improving the Bill")
    score: int=Field(..., description="A Number from 0 to 10 ")

# def js2md():
parser = PydanticOutputParser(pydantic_object=Review)
def get_bill(file):
    # file_path = "20232AB1_97.pdf"
    data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            data.append(text)
    bill = ''.join(data)
    return bill

def main():
    st.title("Parallel Agent")
    uploaded_file = st.file_uploader('Choose your .pdf file', type="pdf")
        
    count = st.slider("Number of Replicas", 0, 5, 2)
    if uploaded_file:
        # bill = get_bill(uploaded_file)
        bill = ""

    
    if st.button("Start Agent") and uploaded_file:
        agent = Agent()
        res = agent.init(bill, count)
        st.write(res['res'])
        for i, runs in enumerate(res['res']):
            st.write(f"### Replica {i+1}")
            for r in runs:
                print(r)


if __name__ == "__main__":
    main()