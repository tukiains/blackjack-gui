
from setuptools import setup, find_packages

version = {}
with open("blackjack_gui/version.py") as f:
    exec(f.read(), version)

with open('README.md') as f:
    readme = f.read()

setup(
    name='blackjack-gui',
    version=version['__version__'],
    description='A game of Blackjack with graphical user interface.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Simo Tukiainen',
    author_email='tukiains@gmail.com',
    url='https://github.com/tukiains/blackjack-gui',
    license='MIT License',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=['pillow', 'wheel'],
    scripts=['blackjack'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],
)
