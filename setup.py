from setuptools import find_packages, setup


setup(
    name="snowbytes",
    version=open("version.md", encoding="utf-8").read().split(" ")[2],
    include_package_data=True,
    description="Snowbytes: Snowflake infrastructure as code",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/getbigbytes/snowbytes",
    author="TJ Murphy",
    packages=find_packages(include=["snowbytes", "snowbytes.*"]),
    python_requires=">=3.9",
    project_urls={
        "Homepage": "https://github.com/getbigbytes/snowbytes",
    },
    entry_points={
        "console_scripts": [
            "snowbytes=snowbytes.cli:snowbytes_cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: SQL",
        "Topic :: Database",
    ],
    install_requires=[
        "click==8.1.7",
        "inflection==0.5.1",
        "pyparsing==3.0.9",
        "pyyaml",
        "snowflake-connector-python==3.12.3",
        "snowflake-snowpark-python==1.24.0",
        "pyOpenSSL>=22.1.0",
        "jinja2",
        "pathspec",
    ],
    extras_require={
        "dev": [
            "black",
            "build",
            "codespell==2.2.6",
            "mypy",
            "pytest-cov",
            "pytest-profiling!=1.8.0",
            "pytest-xdist",
            "pytest>=6.0",
            "python-dotenv",
            "ruff",
            "tabulate",
            "twine!=5.1.0",
            "types-pytz",
            "types-pyyaml",
        ]
    },
)
