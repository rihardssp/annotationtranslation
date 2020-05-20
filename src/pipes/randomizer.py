import typing
from random import random, Random

from src.container.base import IContainer
from src.pipes.base import PipeBase


class RandomizerPipe(PipeBase):

    def __init__(self, n: int):
        self.n = n

    def _process_amr(self, container_list: typing.List[IContainer]) -> typing.List[IContainer]:
        if self.n > len(container_list):
            raise Exception(f"can't select {self.n} random values from list with {len(container_list)} values")

        rand = Random()

        new_list: typing.List[IContainer] = []
        for i in range(self.n):
            new_list.append(container_list.pop(rand.randrange(0, len(container_list))))

        return new_list

