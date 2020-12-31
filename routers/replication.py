import asyncio
from typing import List

from fastapi import status as http_status

from routers.common import NodeStatus
from routers.requests import async_post, gather_get, secondary2url


class ReplicationStatus:
    def __init__(self, write_concern: int, num_nodes: int):
        self.success_counter = write_concern
        self.total_counter = num_nodes
        self.future = asyncio.Future()
        if write_concern == 0:
            self.success()

    def count(self, success: bool):
        self.total_counter -= 1
        if success:
            self.success_counter -= 1

        if self.success_counter == 0:
            self.success()
        elif self.total_counter == 0 and self.success_counter > 0:
            self.fail()

    def success(self):
        self.future.set_result(True)

    def fail(self):
        self.future.set_exception(RuntimeError(f"Failed to replicate"))


class Replicator:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes


async def replicate(urls: List[str], json: dict, write_concern: int):
    status = ReplicationStatus(write_concern, len(urls))

    def _done_callback(fut: asyncio.Future):
        success = fut.exception() is None and fut.result().status == http_status.HTTP_200_OK
        status.count(success)

    for url in urls:
        task = asyncio.ensure_future(async_post(url, json))
        task.add_done_callback(_done_callback)

    return await status.future


async def check_health(hosts: List[str]):
    urls = [f"{secondary2url(host)}/health" for host in hosts]
    responses = await gather_get(urls)
    statuses = [NodeStatus.unhealthy if response is None else NodeStatus(response["status"]) for response in responses]
    return statuses
