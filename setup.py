from setuptools import setup, find_packages

setup(
    name="aegis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click",
        "langchain",
        "langchain-google-genai",
        "langgraph",
        "pydantic",
        "faiss-cpu",
        "gitpython",
        "networkx",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "aegis=cli.main:cli",
        ],
    },
)
