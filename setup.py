import setuptools  # type: ignore

setuptools.setup(
    name="padme",
    author="JCSDA",
    description="Plotting tools for Analysis, Diagnostics, Monitoring, and Evaluation",
    url="",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        'Natural Language :: English',
        "Operating System :: OS Independent",
    ],
    setup_requires=["setuptools-git-versioning"],
    setuptools_git_versioning={
        "enabled": True,
    },
    install_requires=[
#        'bespin @ git+ssh://git@github.com/travissluka/bespin',        
        'cartopy',
        'click',
        'matplotlib',
        'netcdf4',
        'numpy>=1.19',
        'pyyaml'
    ],
    package_dir={"": "src"},
    packages = setuptools.find_packages(where='src'),
    package_data={"padme": [
        'py.typed',
        'config/latlon_domains.yaml',
        ]},
    zip_safe=False,
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'padme=padme.bin.padme:cli',
        ]
    }
)
