from setuptools import setup, find_packages

setup(
    name="podcast_pal",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "pymongo>=3.12.0",
        "python-dateutil>=2.8.2"
    ],
    entry_points={
        'console_scripts': [
            'podcast-pal=podcast_pal.main:main',
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for tracking and analyzing Overcast podcast listening history",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/podcast-pal",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
) 