from typing import Dict

from setuptools import find_packages, setup

version: Dict[str, str] = {}
with open("blackjack_gui/version.py", encoding="utf-8") as f:
    exec(f.read(), version)

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="blackjack-gui",
    version=version["__version__"],
    description="A game of Blackjack with graphical user interface.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Simo Tukiainen",
    author_email="tukiains@gmail.com",
    url="https://github.com/tukiains/blackjack-gui",
    license="MIT License",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=["pillow", "wheel"],
    extras_require={
        "dev": ["pre-commit", "pytest", "pytest-flakefinder", "pylint", "mypy", "types-Pillow"],
    },
    scripts=["blackjack"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
)
