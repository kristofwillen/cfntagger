from setuptools import setup, find_packages
setup(
    name="cfntagger",
    version="0.9.0",
    packages=find_packages(),
    scripts=['cfntagger'],

    # metadata for upload to PyPI
    author="Kristof Willen",
    author_email="kristof.willen@gmail.com",
    description="A Cloudformation tagging tool",
    url="https://github.com/kristofwillen/cfntagger",
    license="GPL",
    keywords="cloudformation tagging",
    install_requires=['ruamel.yaml', 'colorama', 'gitpython'],
    tests_require=["pytest-cov", "cfn-lint", 'pytest'],
)
