from setuptools import setup

setup(
    name="Sveve",
    url="https://github.com/alexalligator/sveve",
    author="Alex Simpson",
    author_email="alex.simpson@funbit.no",
    version="0.1.0",
    packages=["sveve"],
    license="MIT License",
    description="A (limited) Python wrapper for Sveve's SMS sending API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["requests>=2,<3"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
