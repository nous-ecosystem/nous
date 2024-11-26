from setuptools import setup, find_packages

setup(
    name="nous",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "discord.py",
        "python-dotenv",
        "dependency-injector",
        "aiohttp",
        "sqlalchemy",
        "aioredis",
        "aiomysql",
        "alembic",
        "typing-extensions",
    ],
    python_requires=">=3.8",
)
