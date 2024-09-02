# Function Registry

Function Registry is a Python library designed to help consolidate functions and their respective versions into a centralized catalog. Whether you’re working on a single project or need a distributable library, Function Registry provides:

* A ready-to-use `FunctionRegistry` class.
* An abstract base class (`AbstractFunctionRegistry`) for custom implementations.

## Installation

### Requirements
* Python 3.8 or higher
* pip, pipenv, or poetry

### Install with pip
```bash
pip install function_registry
```

### Install from source
```bash
git clone https://github.com/sgg10/function-registry.git
cd function-registry
pip install -e .
```

## Quick Start

### Basic Example

Here’s how to get started with the FunctionRegistry class:

```python
from function_registry import FunctionRegistry

# Create a new function catalog
registry = FunctionRegistry()

# Save a function versions
@registry.save_version("add", version=1)
def add(a, b):
    return a + b

@registry.save_version("add", version=2)
def add(*nums):
    return sum(nums)

# Retrieve the saved function versions

print(registry.get_version("add", version=1)["function"](2, 3))  # 5
print(registry.get_version("add", version=2)["function"](2, 3, 4))  # 9
```

## Features and Examples

### 1. Using sequential or semantic versioning

You can use sequential or semantic versioning for any function, but you must keep the same type of versioning for the same function, otherwise you will get an exception.

Example: you cannot have `@registry.save_version(“add”, version=1)` and then `@registry.save_version(“add”, version=“1.1.0”)`.


```python
@registry.save_version("add", version=1)
def add(a, b):
    return a + b

@registry.save_version("add", version=2)
def add(*nums):
    return sum(nums)

@registry.save_version("div", version="1.0.0")
def div(a, b):
    return a / b

@registry.save_version("div", version="1.0.1")
def div(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Cannot divide by zero"


print(registry.get_version("add", version=1)["function"](2, 3))  # 5
print(registry.get_version("add", version=2)["function"](2, 3, 4))  # 9
print(registry.get_version("div", version="1.0.0")["function"](10, 2))  # 5.0
print(registry.get_version("div", version="1.0.1")["function"](10, 0))  # "Cannot divide by zero"

```

### 2. Using Metadata

Attach custom metadata to functions for advanced search capabilities.

```python
from function_registry import FunctionRegistry

# Create a new function catalog
registry = FunctionRegistry()

@registry.save_version("metadata_func", version=1, metadata={"author": "John Doe"})
def metadata_func():
    return "Metadata Example"

versioned_func = registry.get_version("metadata_func", version=1)
print(versioned_func["metadata"]["author"])  # Output: John Doe
```

### 3. Custom version search

You can create a custom search function to filter versions based on custom criteria.

For example, you can search for the latest version of a function that was created by a specific author.

```python
from function_registry import FunctionRegistry
from function_registry.types import FR_VERSION_DICT_TYPE

AUTHOR = "John Doe"

# Create a new function catalog
registry = FunctionRegistry()

@registry.save_version("add", version=1, metadata={"author": "John Doe"})
def add(a, b):
    return a + b

@registry.save_version("add", version=2, metadata={"author": "Jane Doe"})
def add(*nums):
    return sum(nums)

@registry.save_version("add", version=3, metadata={"author": "John Doe"})
def add(*nums):
    print(f"Adding {len(nums)} numbers")
    return sum(nums)

def custom_search(versions: FR_VERSION_DICT_TYPE):
    filtered_versions = {k: v for k, v in versions.items() if v["metadata"]["author"] == AUTHOR}

    return max(filtered_versions.keys(), key=lambda v: v)

latest_version = registry.get_version("add", custom_search_function=custom_search)
print(latest_version["metadata"]["author"])  # Output: John Doe
print(latest_version["metadata"]["version"])  # Output: 3
print(latest_version["function"](2, 3, 4))  # Output: 9
```

### 4. Custom Function Registry Implementation

Leverage the AbstractFunctionRegistry base class to build your own registry.

```python
from function_registry import AbstractFunctionRegistry

class CustomRegistry(AbstractFunctionRegistry):
    def __init__(self):
        self._functions = {}

    def save_version(self, function_name, version=None, metadata=None):
        # Custom implementation here
        pass

    def get_version(self, function_name, version=None, custom_search_function=None):
        # Custom implementation here
        pass

    def extend(self):
        # Custom implementation here
        pass

# Example usage
custom_registry = CustomRegistry()
```

### 5. Extend Function Registry with other Registries

You can extend the FunctionRegistry class with other registries to combine their functions.

```python
from function_registry import FunctionRegistry

catalog_1 = FunctionRegistry()
catalog_2 = FunctionRegistry()

# Save functions to catalog_1
@catalog_1.save_version("add", version=1)
def add(a, b):
    return a + b

# Save functions to catalog_2
@catalog_2.save_version("sub", version=1)
def sub(a, b):
    return a - b

# Extend catalog_1 with catalog_2
catalog_1.extend(catalog_2)

print(catalog_1.get_version("add", version=1)["function"](2, 3))  # 5
print(catalog_1.get_version("sub", version=1)["function"](5, 3))  # 2
```

### 6. Flexible Function Duplication Strategies

Extend registries with strategies like

* KEEP_EXISTING: Keep the existing function version and ignore the new one.
* OVERWRITE: Overwrite the existing function version with the new one.
* RAISE: Raise an exception if a function version already exists.
* MERGE_WITH_EXISTING_PRIORITY: Merge the existing and new function versions, giving priority to the existing version if one version of the function already exists.
* MERGE_WITH_NEW_PRIORITY: Merge the existing and new function versions, giving priority to the new version if one version of the function already exists.


```python
from function_registry import FunctionRegistry
from function_registry.enums import EXTEND_DUPLICATED_STRATEGIES

catalog_1 = FunctionRegistry()
catalog_2 = FunctionRegistry()


# Save functions to catalog_1
@catalog_1.save_version("add", version=1)
def add(a, b):
    return a + b


# Save functions to catalog_2
@catalog_2.save_version("add", version=1)
def add(a, b):
    return a + b + 100


# Extend catalog_1 with catalog_2
catalog_1.extend(catalog_2, EXTEND_DUPLICATED_STRATEGIES.OVERWRITE)

# Call the function from catalog_1
print(catalog_1.get_version("add", version=1)["function"](1, 2))  # Output: 103
```

## Testing

To run the unit tests, execute the following command from the project root directory:

```bash
python -m unittest discover tests
```

The test cases ensure the library's robustness by covering:

* Function version registration.
* Metadata handling.
* Custom search functions.
* Error handling (e.g., duplicate versions, missing versions).

## Contributing

All contributions to improve Function Registry are welcome! To contribute, follow these steps:

1. Fork the repository.
```bash
git clone https://github.com/sgg10/function-registry.git
cd function-registry
```

2. Create a new branch for your changes:
```bash
git checkout -b feature/new-feature
```

3. Make changes and test them locally.
4. Submit a pull request: Open a pull request describing your changes.


For bug reports or feature requests, please visit the [issues page](https://github.com/sgg10/function-registry/issues).

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.