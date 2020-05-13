import time
import typing
from abc import ABC, abstractmethod

from src.container.base import IContainer


class PipeBase(ABC):
    """This defines a pipes interface"""

    def __init__(self, debug_mode):
        self.debug_mode = debug_mode
        self.last_run_time = 0

    def process(self, container_list: typing.List[IContainer]) -> typing.List[IContainer]:
        before_calc = time.perf_counter()
        result = self._process_amr(container_list)
        after_calc = time.perf_counter()
        self.last_run_time = after_calc - before_calc

        return result

    @abstractmethod
    def _process_amr(self, container_list: typing.List[IContainer]) -> typing.List[IContainer]:
        pass