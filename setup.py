"""
Setup script for Enterprise Network Scanner.

This script provides installation and distribution configuration
for the network scanning application.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding='utf-8') if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="network-scanner",
    version="1.0.0",
    author="Security Team",
    author_email="security@example.com",
    description="Professional network security assessment tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/enterprise/network-scanner",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.5.1",
        ],
        "docs": [
            "sphinx>=7.1.2",
            "sphinx-rtd-theme>=1.3.0",
        ],
        "security": [
            "cryptography>=41.0.4",
            "requests>=2.31.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "network-scanner=network_scanner.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "network_scanner": [
            "config/*.yaml",
            "reports/templates/*.html",
        ],
    },
    zip_safe=False,
    keywords="network security scanning nmap assessment enterprise",
    project_urls={
        "Bug Reports": "https://github.com/enterprise/network-scanner/issues",
        "Source": "https://github.com/enterprise/network-scanner",
        "Documentation": "https://network-scanner.readthedocs.io/",
    },
)
