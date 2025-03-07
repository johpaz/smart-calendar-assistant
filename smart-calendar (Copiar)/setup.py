from setuptools import setup, find_packages

setup(
    name="smart_calendar",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'langchain',
        'langchain-openai',
        'langgraph',
        'python-dotenv'
    ],
)