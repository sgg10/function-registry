from typing import Union, Iterable


class VersionNotFoundError(Exception):
    def __init__(self, function_name: str, version: Union[str, int]):
        super().__init__(f"Version {version} function {function_name} not found.")
        self.function_name = function_name
        self.version = version


class DistinctVersionTypeError(Exception):
    def __init__(self, function_name: str, types: Iterable[str]):
        super().__init__(
            f"Function {function_name} has distinct versions with different types: {types}. Check versions and make sure they have the same type."
        )
        self.function_name = function_name


class MissingVersionError(Exception):
    def __init__(self, function_name: str, custom_message: str = None):
        super().__init__(
            f"Function {function_name} is missing a version. Please provide a version."
            if not custom_message
            else custom_message
        )
        self.function_name = function_name


class MissingSemanticVersionError(Exception):
    def __init__(self, function_name: str):
        super().__init__(
            f"Function {function_name} is missing a semantic version. Please provide a version."
        )
        self.function_name = function_name


class VersionAlreadyExistsError(Exception):
    def __init__(self, function_name: str, version: Union[str, int]):
        super().__init__(
            f"Version {version} for function {function_name} already exists."
        )
        self.function_name = function_name
        self.version = version
