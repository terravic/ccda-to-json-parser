from setuptools import find_packages, setup

setup(
    name="ccda-to-json-parser",
    version="1.0.0",
    description="Production-grade HL7 C-CDA XML to JSON parser and AI Skill",
    author="Clinical Data Engineering",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0.0", "defusedxml>=0.7.1"],
    },
    entry_points={
        "console_scripts": [
            "ccda-parser=ccda_parser.cli:main",
        ],
    },
)
