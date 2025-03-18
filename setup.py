from setuptools import setup, find_packages

setup(
    name="itext_python",
    version="9.1.0",
    packages=find_packages(),
    package_data={
        "itext_python": ["dlls/*.dll"]
    },
    install_requires=[
        "pythonnet>=3.0"  # Essential pythonnet dependency
    ],
    entry_points={},
)

