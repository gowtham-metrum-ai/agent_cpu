from prefect import flow, task
from prefect.futures import wait
from prefect_dask.task_runners import DaskTaskRunner
import time
from new import my_flow, fl


@task
def stop_at_floor(floor):
    print(f"elevator moving to floor {floor}")
    time.sleep(floor)
    print(f"elevator stops on floor {floor}")


@flow(task_runner=DaskTaskRunner)
def elevator():
    floors = []
    for floor in range(10):
        floors.append(my_flow.submit())
    wait(floors)

if __name__ == "__main__":
    elevator()
