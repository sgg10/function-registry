from functools import wraps
from typing import Optional, Dict, Callable, Set

from .base import AbstractFunctionRegistry
from .enums import EXTEND_DUPLICATED_STRATEGIES
from .types import VERSION_TYPE, FR_DICT_TYPE
from .exceptions import (
    DistinctVersionTypeError,
    VersionNotFoundError,
    MissingSemanticVersionError,
    MissingVersionError,
    VersionAlreadyExistsError,
)


class FunctionRegistry(AbstractFunctionRegistry):

    def __init__(self, strict_version_strategy: bool = True) -> None:
        """
        Initializes the FunctionRegistry.

        Args:
            strict_version_strategy (bool): If True, enforces a strict versioning strategy for functions. Defaults to True.

        Attributes:
            _functions (FR_DICT_TYPE): A dictionary to store registered functions.
            strict_version_strategy (bool): Indicates whether a strict versioning strategy is enforced.
        """
        self._functions: FR_DICT_TYPE = {}
        self.strict_version_strategy: bool = strict_version_strategy

    def _get_function_version_type(self, function_name: str) -> Set[str]:
        """
        Retrieve the set of version types for a given function.

        Args:
            function_name (str): The name of the function for which to retrieve version types.

        Returns:
            Set[str]: A set containing the types of the versions associated with the specified function.
        """
        return set(
            type(version).__name__ for version in self._functions[function_name].keys()
        )

    def _assign_default_version(self, function_name: str) -> VERSION_TYPE:
        """
        Assigns the default version for a given function based on its version type.

        Args:
            function_name (str): The name of the function for which the default version is to be assigned.

        Returns:
            VERSION_TYPE: The default version assigned to the function.

        Raises:
            MissingSemanticVersionError: If the version type is a string, indicating a semantic version is missing.
            MissingVersionError: If the version type is neither an integer nor a string, indicating the first version must be provided.
        """
        _type = next(iter(self._get_function_version_type(function_name)), None)
        if _type == "int":
            return max(self._functions[function_name].keys()) + 1
        elif _type == "str":
            raise MissingSemanticVersionError(function_name)
        else:
            raise MissingVersionError(
                function_name,
                f"First version for function '{function_name}' must be provided.",
            )

    def save_version(
        self,
        function_name: str,
        version: Optional[VERSION_TYPE] = None,
        metadata: Optional[Dict] = None,
    ) -> Callable:
        """
        A decorator to save a versioned function with optional metadata.

        Args:
            function_name (str): The name of the function to be saved.
            version (Optional[VERSION_TYPE], optional): The version of the function. Defaults to None.
            metadata (Optional[Dict], optional): Additional metadata to be associated with the function. Defaults to None.

        Raises:
            MissingVersionError: If no version is provided and strict version strategy is enabled.
            VersionAlreadyExistsError: If the specified version already exists for the function.
            DistinctVersionTypeError: If there are multiple distinct version types for the function.

        Returns:
            Callable: The decorated function.
        """

        def decorator(func: Callable) -> Callable:
            nonlocal version
            if not version and self.strict_version_strategy:
                raise MissingVersionError(function_name)

            if function_name not in self._functions:
                self._functions[function_name] = {}

            if version in self._functions[function_name]:
                raise VersionAlreadyExistsError(function_name, version)

            version_types = (
                self._get_function_version_type(function_name)
                | {type(version).__name__}
            ) - {"NoneType"}

            if len(version_types) > 1:
                raise DistinctVersionTypeError(function_name, version_types)

            if version is None:
                version = self._assign_default_version(function_name)

            self._functions[function_name][version] = {
                "function": func,
                "metadata": {**(metadata or {}), "version": version},
            }

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_all_versions(self, function_name: str):
        """
        Retrieve all versions of a specified function.

        Args:
            function_name (str): The name of the function to retrieve versions for.

        Returns:
            list: A list of all versions of the specified function.

        Raises:
            ValueError: If no function is found with the given name.
        """
        if function_name not in self._functions:
            raise ValueError(f"No function found with name '{function_name}'")
        return self._functions[function_name]

    def get_version(
        self,
        function_name: str,
        version: Optional[VERSION_TYPE] = None,
        custom_search_function: Optional[Callable] = None,
    ) -> Dict:
        """
        Retrieve the specified version of a function from the registry.

        Args:
            function_name (str): The name of the function to retrieve.
            version (Optional[VERSION_TYPE]): The version of the function to retrieve. If not provided, the latest version is used.
            custom_search_function (Optional[Callable]): A custom function to determine the version if `version` is not provided.

        Returns:
            Dict: The function details for the specified version.

        Raises:
            ValueError: If the function name is not found in the registry.
            MissingSemanticVersionError: If the version type is a string and no version is provided.
            VersionNotFoundError: If the specified version is not found for the function.
        """

        if function_name not in self._functions:
            raise ValueError(f"No function found with name '{function_name}'")

        version_type = self._get_function_version_type(function_name).pop()

        if version is None:

            if custom_search_function:
                version = custom_search_function(self._functions[function_name])
            elif version_type == "int":
                version = max(self._functions[function_name].keys())
            elif version_type == "str":
                raise MissingSemanticVersionError(function_name)

        if version not in self._functions[function_name]:
            raise VersionNotFoundError(function_name, version)

        return self._functions[function_name][version]

    def extend(
        self,
        registry: "FunctionRegistry",
        duplication_strategy: int = EXTEND_DUPLICATED_STRATEGIES.RAISE,
    ) -> None:
        """
        Extends the current function registry with another registry's functions based on the specified duplication strategy.
        To see strategies, check the `enums.EXTEND_DUPLICATED_STRATEGIES` enum.

        Args:
        - registry (FunctionRegistry): The function registry to extend from.
        - duplication_strategy (int): Strategy to handle duplicated functions.
            Possible values are defined in EXTEND_DUPLICATED_STRATEGIES:
                - RAISE: Raise an error if there are duplicated functions.
                - KEEP_EXISTING: Keep the existing functions and ignore the new ones.
                - OVERWRITE: Overwrite the existing functions with the new ones.
                - MERGE_WITH_EXISTING_PRIORITY: Merge the functions, giving priority to the existing ones.
                - MERGE_WITH_NEW_PRIORITY: Merge the functions, giving priority to the new ones.
        Raises:
        - ValueError: If an invalid duplication strategy is provided or if there are
            duplicated functions with different version types.
        """

        if (
            duplication_strategy
            not in EXTEND_DUPLICATED_STRATEGIES.__members__.values()
        ):
            raise ValueError(
                f"Invalid duplication strategy. Possible values are {EXTEND_DUPLICATED_STRATEGIES}"
            )

        existing_functions = set(self._functions.keys())
        new_functions = set(registry._functions.keys())

        duplicated_functions = existing_functions & new_functions

        if (
            duplication_strategy == EXTEND_DUPLICATED_STRATEGIES.RAISE
            and duplicated_functions
        ):
            raise ValueError(
                f"Function(s) {duplicated_functions} already exist in the registry"
            )

        def _validate_version_types():
            for fn in duplicated_functions:
                if self._get_function_version_type(
                    fn
                ) != registry._get_function_version_type(fn):
                    raise ValueError(
                        f"Function '{fn}' has different version types in both registries"
                    )

        def _merge_duplicates(existing_priority: bool) -> Dict:
            _validate_version_types()
            merged = {}
            for fn in duplicated_functions:
                merged[fn] = (
                    (registry._functions[fn] | self._functions[fn])
                    if existing_priority
                    else (self._functions[fn] | registry._functions[fn])
                )
            return merged

        if duplication_strategy == EXTEND_DUPLICATED_STRATEGIES.KEEP_EXISTING:
            self._functions = registry._functions | self._functions
        elif duplication_strategy == EXTEND_DUPLICATED_STRATEGIES.OVERWRITE:
            self._functions |= registry._functions
        else:
            existing_priority = (
                duplication_strategy
                == EXTEND_DUPLICATED_STRATEGIES.MERGE_WITH_EXISTING_PRIORITY
            )
            merged = _merge_duplicates(existing_priority)
            self._functions |= registry._functions | merged
