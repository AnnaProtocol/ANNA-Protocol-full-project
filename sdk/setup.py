"""
Setup script para ANNA Protocol SDK
"""

from setuptools import setup, find_packages
import os

# Ler README para descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Ler requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="anna-protocol-sdk",
    version="1.0.0",
    author="ANNA Protocol Team",
    author_email="dev@annaprotocol.io",
    description="SDK oficial em Python para o ANNA Protocol - Identidade e Reputação para Agentes de IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anna-protocol/sdk-python",
    project_urls={
        "Bug Tracker": "https://github.com/anna-protocol/sdk-python/issues",
        "Documentation": "https://docs.annaprotocol.io",
        "Source Code": "https://github.com/anna-protocol/sdk-python",
        "Discord": "https://discord.gg/anna-protocol",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
            "flake8>=6.1.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "anna-cli=anna_sdk.cli:main",
        ],
    },
    keywords=[
        "blockchain",
        "ethereum",
        "polygon",
        "artificial-intelligence",
        "ai",
        "identity",
        "reputation",
        "attestation",
        "decentralized",
        "web3",
        "smart-contracts"
    ],
    include_package_data=True,
    zip_safe=False,
)