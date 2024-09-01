from abc import ABC, abstractmethod
from typing import Optional, Dict, Callable

from .types import VERSION_TYPE


class AbstractFunctionRegistry(ABC):

    @abstractmethod
    def save_version(
        self,
        function_name: str,
        version: Optional[VERSION_TYPE] = None,
        metadata: Optional[Dict] = None,
    ) -> Callable:
        raise NotImplementedError(
            f"{self.__class__.__name__}.save_version() is not implemented"
        )

    @abstractmethod
    def get_version(
        self,
        function_name: str,
        version: Optional[VERSION_TYPE] = None,
        custom_search_function: Optional[Callable] = None,
    ) -> Dict:
        """Retrieve a specific version of a function or the latest version if not specified."""
        raise NotImplementedError(
            f"{self.__class__.__name__}.get_version() is not implemented"
        )

    @abstractmethod
    def extend(self) -> None:
        raise NotImplementedError(
            f"{self.__class__.__name__}.extend() is not implemented"
        )
