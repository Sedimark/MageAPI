from setuptools import setup


setup(
    name="dqp",
    version="0.1",
    packages=["dqp"],
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
        "pythresh",
        "recordlinkage",
        "requests",
        "combo",
        "pycaret",
        "pyod",
        "tqdm",
        "torch",
        "torchvision",
    ],
)
