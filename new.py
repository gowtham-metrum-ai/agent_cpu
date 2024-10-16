from prefect import task, flow
from prefect.task_runners import ThreadPoolTaskRunner
import asyncio
from prefect_dask.task_runners import DaskTaskRunner

def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped




@task
def task_a():
    print("Task A")

@task
def task_b():
    print("Task B")

@task
def task_c():
    print("Task C")
    
@task
def task_d():
    print("Task D")

@flow
def fl():
    a = task_a.submit()
    b = task_b.submit(wait_for=[a])
    # Wait for task_a and task_b to complete
    c = task_c.submit(wait_for=[b])
    # task_d will wait for task_c to complete
    # Note: If waiting for one task it must still be in a list.
    d = task_d(wait_for=[c])

@task
def my_flow():
    fl()
    


if __name__=="__main__":
    my_flow()

