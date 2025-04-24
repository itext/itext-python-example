from setuptools import setup


setup(
    name="itextpy",
    version="9.1.0",
    packages=[
        "itextpy",
        "iText-stubs",
    ],
    package_data={
        "itextpy": [
            "binaries/**/*.dll",
            "__init__.py",
        ],
        "iText-stubs": [
            '**/*.pyi',
        ],
    },
    install_requires=(
        "pythonnet>=3.0",               # Essential pythonnet dependency
        "netstandard-stubs>=2.0,<2.1",  # Typing stubs for .NET
    ),
    entry_points={},
)
