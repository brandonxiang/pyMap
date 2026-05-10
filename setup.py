from setuptools import setup


setup(
    name="pymap-tile",
    version="0.1.0",
    description="Download raster map tiles and stitch them into PNG mosaics.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Brandon Xiang",
    url="https://github.com/brandonxiang/pyMap",
    py_modules=["pyMap"],
    install_requires=[
        "requests>=2.10.0",
        "Pillow>=3.2.0",
        "tqdm>=4.7.1",
    ],
    entry_points={
        "console_scripts": [
            "pymap=pyMap:main",
            "pyMap=pyMap:main",
        ],
    },
    python_requires=">=3.5",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Utilities",
    ],
)
