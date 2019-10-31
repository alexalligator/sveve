from distutils.core import setup

setup(
    name="Sveve",
    version="0.1.0",
    packages=["sveve"],
    license="MIT License",
    long_description=open("README.txt").read(),
    install_requires=["requests>=2,<3"],
)
