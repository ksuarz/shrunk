""" shrunk - Rutgers University URL Shortener """

from setuptools import setup

# Text from the README
try:
    with open("README.rst") as fd:
        readme_text = fd.read()
except:
    readme_text = ""

setup(
    name = "shrunk",
    version = "0.2.0",
    packages = ["shrunk"],
    requires = ["pymongo", "wtforms", "flask"],
    package_dir = {"shrunk": "shrunk"},
    package_data = {"shrunk": ["static/css/*", "static/img/*", "static/js/*",
                               "templates/*"]},
    author = "Rutgers Open System Solutions",
    author_email = "oss@oss.rutgers.edu",
    description = "Rutgers University URL Shortener",
    long_description = readme_text,
    keywords = "shrunk rutgers url shortener",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Utilities"
    ],
    url = "https://github.com/oss/shrunk"
)
