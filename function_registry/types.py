from typing import Union, TypedDict, Dict, Callable

VERSION_TYPE = Union[str, int]


class FunctionVersion(TypedDict):
    function: Callable
    metadata: Dict


FR_VERSION_DICT_TYPE = Dict[VERSION_TYPE, FunctionVersion]

FR_DICT_TYPE = Dict[str, FR_VERSION_DICT_TYPE]
