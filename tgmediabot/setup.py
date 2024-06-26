import os

from setuptools import find_packages, setup

current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "requirements.txt")) as f:
    requirements = f.read().splitlines()

setup(
    name="tgmediabot",
    version="0.1.2",
    author="Garootman",
    author_email="",
    description="Lib to manage the Telegram bot",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ваш_профиль/my_project",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
