
from prefect import flow, task
from pagent import Agent
from BillAgent import BillAgent
from typing import List
from prefect.task_runners import ThreadPoolTaskRunner

# @task(name="Upload Bill")
# def upload_bill(bill_content: str) -> str:
#     return bill_content

# @task(name="Process Bill")
# def process_bill(bill: str, count: int) -> dict:
#     agent = Agent()
#     return agent.init(bill, count)

# @task(name="Analyze Results")
# def analyze_results(results: dict) -> List[str]:
#     analyzed_results = []
#     for i, runs in enumerate(results['res']):
#         analyzed_results.append(f"Replica {i+1} Analysis:")
#         for r in runs:
#             analyzed_results.append(r)
#     return analyzed_results

@flow(name="Bill", task_runner=ThreadPoolTaskRunner(max_workers=3))
def bill_workflow(bill: str, count: int):
    # uploaded_bill = ""
    agent =  Agent()
    results = agent.init(bill, count)
    return results

# if __name__ == "__main__":
#     results = bill_analysis_workflow(" ")
#     print(results)

if __name__ == "__main__":
    bill_analysis_workflow.deploy(
        name="my-deployment",
        work_pool_name="my-work-pool",
        image="my-docker-image:dev",
        push=False
    )