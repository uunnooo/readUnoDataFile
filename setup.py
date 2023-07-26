import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="readDataFile",
    version="0.0.9",
    author="Uno",
    author_email="uno0522@gmail.com",
    description="uno test data file read",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/uunnooo/readUnoDataFile",
    project_urls={
         "Bug Tracker" : "https://github.com/uunnooo/readUnoDataFile",
    },
    classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent"
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)