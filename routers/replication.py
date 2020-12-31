import asyncio
import threading
import time
from queue import PriorityQueue
from typing import List, Any
import requests

from fastapi import status as http_status

from routers.common import NodeStatus, SecondaryAppendDataModel
from routers.utils import gather_get, secondary2url


class ReplicationCounter:
    def __init__(self, write_concern: int, num_nodes: int):
        self.success_counter = write_concern
        self.total_counter = num_nodes
        self._lock = threading.Lock()
        self.future = asyncio.Future()
        if write_concern == 0:
            self.success()

    def count(self, success: bool):
        with self._lock:
            self.total_counter -= 1
            if success:
                self.success_counter -= 1

            if self.success_counter == 0:
                self.success()

    def success(self):
        self.future.set_result(True)


class ReplicationTaskDescriptor:
    def __init__(self, counter: ReplicationCounter, message: Any, message_id: int):
        self.counter = counter
        self.message = message
        self.message_id = message_id

    def json(self):
        return SecondaryAppendDataModel(message=self.message, message_id=self.message_id).json()


class Replicator:
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.messages = []
        self.message_id = 0

        self.queues, self.threads = self._create_background_replicators(nodes)

    def replicate(self, message: Any, write_concert: int):
        self.messages.append(message)

        priority = self.message_id
        counter = ReplicationCounter(write_concert - 1, len(self.nodes))
        descriptor = ReplicationTaskDescriptor(counter, message, self.message_id)
        for node, queue in self.queues.items():
            queue.put_nowait((priority, descriptor))

        self.message_id += 1
        return counter.future

    def _create_background_replicators(self, nodes: List[str]):
        queues, threads = {}, {}
        for node in nodes:
            queue = PriorityQueue()
            t = threading.Thread(target=self._background_replication, args=(node, queue))
            t.start()
            queues[node] = queue
            threads[node] = t
        return queues, threads

    @staticmethod
    def _background_replication(node: str, queue: PriorityQueue):
        url = f"{secondary2url(node)}/append"
        while True:
            priority, descriptor = queue.get(block=True, timeout=None)
            response = requests.post(url, data=descriptor.json())

            if response.status_code == http_status.HTTP_200_OK:
                descriptor.counter.count(True)
            else:
                queue.put((priority, descriptor))
                time.sleep(5)


async def check_health(hosts: List[str]):
    urls = [f"{secondary2url(host)}/health" for host in hosts]
    responses = await gather_get(urls)
    statuses = [NodeStatus.unhealthy if response is None else NodeStatus(response["status"]) for response in responses]
    return statuses
