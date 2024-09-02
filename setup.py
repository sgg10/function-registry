import os
from setuptools import find_packages, setup


def read(filename: str):
    return open(
        os.path.join(os.path.dirname(__file__), filename), encoding="utf-8"
    ).read()


setup(
    name="function_registry",
    version="1.0.0",
    description="Tool to consolidate python functions with multiple versions into a single access point, search by a specific version or custom search with metadata.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
    url="https://github.com/sgg10/function-registry/",
    author="sgg10",
    license="MIT",
    author_email="sgg10.develop@gmail.com",
    project_urls={
        "Bug Reports": "https://github.com/sgg10/function-registry/issues",
        "Source": "https://github.com/sgg10/function-registry/",
        "Repository": "https://github.com/sgg10/function-registry/",
    },
)
