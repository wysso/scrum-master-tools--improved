"""
Setup configuration for ScrumMaster package
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="scrummaster",
    version="2.11.1",
    author="ScrumMaster Team",
    author_email="team@scrummaster.dev",
    description="Tools for analyzing Jira projects for ScrumMasters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scrummaster/scrummaster-tools",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Bug Tracking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "smt=scrummaster.cli:main",
            "sm-completion=scrummaster.tools.sprint_completion:main",
            "sm-worklog=scrummaster.tools.worklog_summary:main",
            "sm-anomalies=scrummaster.tools.anomaly_detector:main",
            "sm-planning=scrummaster.tools.planning:main",
        ],
    },
    include_package_data=True,
    package_data={
        "scrummaster": ["config/*.py"],
    },
)