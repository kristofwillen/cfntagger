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
    install_requires=[
        'ruamel.yaml==0.17.21', 
        'colorama>=0.4.4', 
        'gitpython>=3.1.27'
    ],
    tests_require=[
        'pytest-cov>=3.0.0', 
        'cfn-lint>=0.58.1', 
        'pytest>=7.1.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
