# coding:utf8
import os
import numpy
from setuptools import find_packages, setup, Extension

# Package meta-data.
NAME = "python stock lib"
DESCRIPTION = "A Quantitative-research Platform"
REQUIRES_PYTHON = ">=3.5.0"

VERSION = '1.0.0'

# Detect Cython
try:
    import Cython

    ver = Cython.__version__
    _CYTHON_INSTALLED = ver >= "0.28"
except ImportError:
    _CYTHON_INSTALLED = False

if not _CYTHON_INSTALLED:
    print("Required Cython version >= 0.28 is not detected!")
    print('Please run "pip install --upgrade cython" first.')
    exit(-1)

# Numpy include
NUMPY_INCLUDE = numpy.get_include()

here = os.path.abspath(os.path.dirname(__file__))


def get_relative_path_to_cython_file(cython_file_path):
    setup_py_dir = os.path.dirname(os.path.abspath(__file__))
    cython_file_dir = os.path.dirname(cython_file_path)
    relative_path = os.path.relpath(cython_file_dir, setup_py_dir)
    return os.path.join(relative_path, os.path.basename(cython_file_path))

# 使用这个函数来获取相对路径
relative_rolling_path = get_relative_path_to_cython_file(os.path.join(here, "modules/dataHandler/_libs/rolling.pyx"))
relative_expanding_path = get_relative_path_to_cython_file(os.path.join(here, "modules/dataHandler/_libs/expanding.pyx"))
print(relative_rolling_path, "===relative_rolling_path==")
# Cython Extensions
extensions = [
    Extension(
        "stockApp.modules.dataHandler._libs.rolling",
        [relative_rolling_path],
        language="c++",
        include_dirs=[NUMPY_INCLUDE],
    ),
    Extension(
        "stockApp.modules.dataHandler._libs.expanding",
        [relative_expanding_path],
        language="c++",
        include_dirs=[NUMPY_INCLUDE],
    ),
]


# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    license="MIT Licence",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=("tests",)),
    # if your package is a single module, use this instead of 'packages':
    # py_modules=['qlib'],
    # 你的包可以作为一个工具使用
    # entry_points={
    #     # 'console_scripts': ['mycli=mymodule:cli'],
    #     "console_scripts": [
    #         "qrun=qlib.workflow.cli:run",
    #     ],
    # },
    ext_modules=extensions,
    # extras_require={
    #     "dev": [
    #         "coverage",
    #         "pytest>=3",
    #         "pre-commit",
    #         # CI dependencies
    #         "wheel",
    #         "setuptools",
    #         "black",
    #         # Version 3.0 of pylint had problems with the build process, so we limited the version of pylint.
    #         "pylint<=2.17.6",
    #         # Using the latest versions(0.981 and 0.982) of mypy,
    #         # the error "multiprocessing.Value()" is detected in the file "qlib/rl/utils/data_queue.py",
    #         # If this is fixed in a subsequent version of mypy, then we will revert to the latest version of mypy.
    #         # References: https://github.com/python/typeshed/issues/8799
    #         "mypy<0.981",
    #         "flake8",
    #         "nbqa",
    #         "jupyter",
    #         "nbconvert",
    #         # The 5.0.0 version of importlib-metadata removed the deprecated endpoint,
    #         # which prevented flake8 from working properly, so we restricted the version of importlib-metadata.
    #         # To help ensure the dependencies of flake8 https://github.com/python/importlib_metadata/issues/406
    #         "importlib-metadata<5.0.0",
    #         "cmake",
    #         "lxml",
    #         "beautifulsoup4",
    #         # In version 0.4.11 of tianshou, the code:
    #         # logits, hidden = self.actor(batch.obs, state=state, info=batch.info)
    #         # was changed in PR787,
    #         # which causes pytest errors(AttributeError: 'dict' object has no attribute 'info') in CI,
    #         # so we restricted the version of tianshou.
    #         # References:
    #         # https://github.com/thu-ml/tianshou/releases
    #         "tianshou<=0.4.10",
    #         "gym>=0.24",  # If you do not put gym at the end, gym will degrade causing pytest results to fail.
    #     ],
    #     "rl": [
    #         "tianshou<=0.4.10",
    #         "torch",
    #     ],
    # },
    # 接受MANIFEST.in匹配的所有数据文件和目录，启用后加入MANIFEST.in文件
    # include_package_data=False,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    # zip_safe置为False是为了防止使用python setup.py install编译时生成的 zipped egg文件无法在pxd文件中通过cimport方式运行的情况出现
    zip_safe=False
)

# 执行 python setup.py build_ext --inplace --build-lib=/path/to/build/lib
