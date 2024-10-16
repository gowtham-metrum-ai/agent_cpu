
from prefect import flow, task
from pagent import Agent
from BillAgent import BillAgent
from typing import List
from prefect_dask.task_runners import DaskTaskRunner
from prefect.futures import wait

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

@task
def run(bill:str):
    agent =  BillAgent()
    return agent.run(bill)

@flow(task_runner=DaskTaskRunner)
def elevator(bill: str, count: int):
    res = []
    for _ in range(count):
        res.append(run.submit(bill))
        # floors.append(my_flow.submit())
    wait(res)

if __name__ == "__main__":
    elevator(bill = " ", count = 2)



# @flow(name="Bill")
# def bill_workflow(bill: str):
#     # uploaded_bill = ""
#     agent =  BillAgent()
#     results = agent.run(bill)
#     return results

# if __name__ == "__main__":
#     results = bill_analysis_workflow(" ")
#     print(results)

# if __name__ == "__main__":
#     bill_workflow.deploy(
#         name="my-deployment",
#         work_pool_name="my-work-pool",
#         image="my-docker-image:dev",
#         push=False
#     )