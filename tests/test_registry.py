import unittest
from typing import Callable

from function_registry import FunctionRegistry
from function_registry.exceptions import (
    DistinctVersionTypeError,
    MissingVersionError,
    VersionNotFoundError,
    VersionAlreadyExistsError,
)
from function_registry.types import FR_VERSION_DICT_TYPE


class TestFunctionRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = FunctionRegistry(strict_version_strategy=True)
        self.loose_registry = FunctionRegistry(strict_version_strategy=False)

    def test_save_and_get_function(self):
        """
        Test the save and retrieval of a versioned function in the registry.

        This test defines a function `add` that adds two numbers and saves it
        in the registry with a specific version. It then retrieves the function
        from the registry and checks if the retrieved function matches the
        original function by comparing their outputs for the same inputs.

        Asserts:
            - The output of the original `add` function with inputs (1, 2)
                matches the output of the retrieved versioned function with
                the same inputs.
            - The output of the retrieved versioned function with inputs (1, 2)
                is equal to 3.
        """

        @self.registry.save_version("add", version=1)
        def add(a, b):
            return a + b

        versioned_function = self.registry.get_version("add", version=1)
        self.assertEqual(add(1, 2), versioned_function["function"](1, 2))
        self.assertEqual(versioned_function["function"](1, 2), 3)

    def test_save_version_without_version_strict(self):
        """
        Test case for saving a version without specifying a version in strict mode.

        This test ensures that the `save_version` decorator raises a `MissingVersionError`
        when attempting to save a function version without providing a version string
        in strict mode.

        Raises:
            MissingVersionError: If the version string is not provided.
        """
        with self.assertRaises(MissingVersionError):

            @self.registry.save_version("multiply")
            def multiply(a, b):
                return a * b

    def test_save_duplicate_version(self):
        """
        Test case for saving a duplicate version of a function in the registry.

        This test ensures that attempting to save a function with a version that
        already exists in the registry raises a VersionAlreadyExistsError.

        Steps:
        1. Save the first version of the function "divide" with version 1.
        2. Attempt to save a second version of the function "divide" with the same version 1.
        3. Verify that a VersionAlreadyExistsError is raised.

        Raises:
            VersionAlreadyExistsError: If a function with the same name and version already exists in the registry.
        """

        @self.registry.save_version("divide", version=1)
        def divide_v1(a, b):
            return a / b

        with self.assertRaises(VersionAlreadyExistsError):

            @self.registry.save_version("divide", version=1)
            def divide_v2(a, b):
                return a // b

    def test_get_latest_version(self):
        """
        Test case for retrieving the latest version of a function from the registry.

        This test defines two versions of a function named 'subtract' and saves them
        in the registry with versions 1 and 2, respectively. It then retrieves the
        latest version of the 'subtract' function from the registry and asserts that
        the function behaves as expected.

        The expected behavior is that the latest version (version 2) of the 'subtract'
        function should return 1 when called with arguments 5 and 3.
        """

        @self.registry.save_version("subtract", version=1)
        def subtract_v1(a, b):
            return a - b

        @self.registry.save_version("subtract", version=2)
        def subtract_v2(a, b):
            return a - b - 1

        latest_version = self.registry.get_version("subtract")
        self.assertEqual(latest_version["function"](5, 3), 1)

    def test_metadata_storage(self):
        """
        Test the storage and retrieval of function metadata in the registry.

        This test verifies that a function can be saved with specific metadata
        and that the metadata can be correctly retrieved when accessing the
        function version from the registry.

        The test performs the following steps:
        1. Defines a function `metadata_func` and saves it in the registry with
            version 1 and metadata containing the author "John Doe".
        2. Retrieves the versioned function from the registry.
        3. Asserts that the retrieved metadata contains the correct author and version.

        Asserts:
            - The author in the metadata of the retrieved function is "John Doe".
            - The version in the metadata of the retrieved function is 1.
        """

        @self.registry.save_version(
            "metadata_func", version=1, metadata={"author": "John Doe"}
        )
        def metadata_func():
            return "Test"

        versioned_func = self.registry.get_version("metadata_func", 1)
        self.assertEqual(versioned_func["metadata"]["author"], "John Doe")
        self.assertEqual(versioned_func["metadata"]["version"], 1)

    def test_custom_search_function(self):
        """
        Test the custom search function for retrieving the latest version of a registered function.

        This test registers two versions of a function named 'search_func' with versions '1.0.0' and '1.1.0'.
        It then defines a custom search function that selects the latest version based on the version keys.
        Finally, it asserts that the latest version of 'search_func' is correctly identified and returns the expected result.

        Steps:
        1. Register 'search_func' version '1.0.0' returning "v1".
        2. Register 'search_func' version '1.1.0' returning "v2".
        3. Define a custom search function that selects the maximum version key.
        4. Retrieve the latest version of 'search_func' using the custom search function.
        5. Assert that the latest version's function returns "v2".

        Asserts:
        - The latest version's function should return "v2".
        """

        @self.registry.save_version("search_func", version="1.0.0")
        def search_func():
            return "v1"

        @self.registry.save_version("search_func", version="1.1.0")
        def search_func():
            return "v2"

        def custom_search(versions: FR_VERSION_DICT_TYPE) -> str:
            return max(versions.keys(), key=lambda v: v)

        latest_version = self.registry.get_version(
            "search_func", custom_search_function=custom_search
        )
        self.assertEqual(latest_version["function"](), "v2")

    def test_multi_decorator_integration(self):
        """
        Test the integration of multiple decorators on a function.

        This test defines a `log_decorator` that logs the function call and
        applies it to `log_func` along with the `save_version` decorator from
        the registry. It then retrieves the versioned function from the registry
        and verifies that the function works correctly and logs the call.

        Steps:
        1. Define a `log_decorator` that logs the function call.
        2. Apply `log_decorator` and `save_version` decorators to `log_func`.
        3. Retrieve the versioned function from the registry.
        4. Call the versioned function and capture logs.
        5. Assert that the function returns the correct result.
        """

        def log_decorator(func: Callable):
            def wrapper(*args, **kwargs):
                import logging

                logging.basicConfig(level=logging.INFO)
                logging.info(f"Calling {func.__name__}")
                return func(*args, **kwargs)

            return wrapper

        @self.registry.save_version("log_func", version=1)
        @log_decorator
        def log_func(x, y):
            return x + y

        versioned_func = self.registry.get_version("log_func", 1)
        with self.assertLogs() as cm:
            result = versioned_func["function"](3, 4)
        self.assertEqual(result, 7)

    def test_get_all_versions(self):
        """
        Test the retrieval of all versions of a function from the registry.

        This test defines two versions of a function named 'multi_version_func'
        and saves them in the registry with versions 1 and 2 respectively.
        It then retrieves all versions of 'multi_version_func' from the registry
        and asserts that there are exactly two versions available and that
        both version 1 and version 2 are present in the retrieved versions.
        """

        @self.registry.save_version("multi_version_func", version=1)
        def multi_version_func():
            return "v1"

        @self.registry.save_version("multi_version_func", version=2)
        def multi_version_func():
            return "v2"

        all_versions = self.registry.get_all_versions("multi_version_func")
        self.assertEqual(len(all_versions), 2)
        self.assertIn(1, all_versions)
        self.assertIn(2, all_versions)

    def test_get_function_not_found(self):
        """
        Test case for the `get_version` method when the requested function is not found.

        This test ensures that a `ValueError` is raised when attempting to retrieve
        a version of a function that does not exist in the registry.

        Raises:
            ValueError: If the function name provided does not exist in the registry.
        """
        with self.assertRaises(ValueError):
            self.registry.get_version("non_existent_func", version=1)

    def test_get_version_not_found(self):
        """
        Test case for retrieving a version of a function that does not exist.

        This test defines a function `not_found_func` with version 1 and attempts to
        retrieve version 2 of the same function from the registry. It expects a
        `VersionNotFoundError` to be raised, indicating that the requested version
        does not exist in the registry.
        """

        @self.registry.save_version("not_found_func", version=1)
        def not_found_func():
            return "v1"

        with self.assertRaises(VersionNotFoundError):
            self.registry.get_version("not_found_func", version=2)

    def test_invalid_version_type_error(self):
        """
        Test case for ensuring that saving a function version with a different type
        raises a DistinctVersionTypeError.
        This test defines a function `mixed_version_func` and attempts to save it
        with two different version types: an integer and a string. The first save
        uses an integer version, while the second save uses a string version. The
        test expects a DistinctVersionTypeError to be raised when the second save
        is attempted.
        Raises:
            DistinctVersionTypeError: If the version type of the function being saved
            does not match the type of the previously saved version.
        """

        @self.registry.save_version("mixed_version_func", version=1)
        def mixed_version_func():
            return "v1"

        with self.assertRaises(DistinctVersionTypeError):

            @self.registry.save_version("mixed_version_func", version="1.1.0")
            def mixed_version_func():
                return "v2"

    def test_save_version_without_version_loose(self):
        """
        Test the save_version method of the loose_registry to ensure that functions
        can be saved with and without specifying a version, and that the correct
        version is retrieved when requested.

        This test performs the following steps:
        1. Save a function "loose_func" with version 1.
        2. Save another version of "loose_func" without specifying a version.
        3. Save a third version of "loose_func" with version 3.
        4. Save a fourth version of "loose_func" without specifying a version.
        5. Retrieve the latest version of "loose_func" and assert that it matches
            the expected output of the last saved function.

        The test ensures that the latest version of the function is correctly
        retrieved when no specific version is requested.
        """

        @self.loose_registry.save_version("loose_func", version=1)
        def loose_func():
            return "loose"

        @self.loose_registry.save_version("loose_func")
        def loose_func():
            return "loose2"

        @self.loose_registry.save_version("loose_func", version=3)
        def loose_func():
            return "loose3"

        @self.loose_registry.save_version("loose_func")
        def loose_func():
            return "loose4"

        versioned_func = self.loose_registry.get_version("loose_func")
        self.assertEqual(versioned_func["function"](), "loose4")
        self.assertEqual(versioned_func["metadata"]["version"], 4)
