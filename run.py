import asyncio
from prefect import flow, task
from prefect.concurrency.asyncio import concurrency
from prefect_dask.task_runners import DaskTaskRunner
from new import my_flow, fl


@flow()
async def my_flow2():
    await asyncio.gather(fl() for x in range(5))

if __name__ == "__main__":
    main_flow_state = asyncio.run(my_flow2())
