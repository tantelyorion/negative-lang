#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="negative-lang",
    version="1.0.0",
    author="Negative Language Team",
    author_email="team@negative-lang.org",
    description="Negative - A programming language based on negative logic and constraints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/negative-lang/negative",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
        "web": [
            "flask>=2.0.0",
            "flask-cors>=3.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "negative=negative.cli:main",
            "neg=negative.cli:main",  # Short alias
        ],
    },
    package_data={
        "negative": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
)