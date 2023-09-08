from setuptools import setup, find_packages

def get_version():
    with open('./cfntagger/version.py', 'r', encoding='utf-8') as f:
        data = f.readlines()
        return data[0].split('"')[1]

setup(
    name="cfntagger",
    version=get_version(),
    packages=find_packages(),
    scripts=['cfntagger/cfntagger'],

    # metadata for upload to PyPI
    author="Kristof Willen",
    author_email="kristof.willen@gmail.com",
    description="A Cloudformation tagging tool",
    url="https://github.com/kristofwillen/cfntagger",
    license="GPL",
    keywords="cloudformation tagging",
    install_requires=[
        'ruamel.yaml>=0.17.24',
        'colorama>=0.4.4',
        'gitpython>=3.1.34'
    ],
    tests_require=[
        'pytest-cov>=3.0.0',
        'cfn-lint>=0.77.0',
        'pytest>=7.3.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)
