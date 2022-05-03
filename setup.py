from setuptools import find_packages, setup
from os import path

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='whiskey-flask',
    version='0.6.1',
    author="Nick Wynja",
    author_email="nick@nickwynja.com",
    description="Whiskey makes writing happen.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nickwynja/whiskey",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "click",
        "configparser",
        "feedgen",
        "flask_flatpages",
        "frozen-flask",
        "Flask-Babel",
        "Jinja2",
        "livereload",
        "Markdown",
        "MarkupSafe",
        "panflute",
        "Pygments",
        "pytz",
        "python-dotenv",
        "pypandoc",
        "weasyprint",
    ],
)
