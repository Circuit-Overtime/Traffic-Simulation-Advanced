from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy
import os
import importlib.util

# Base directory for all paths
BASE_DIR = os.path.join('C:\\Users\\ELIXPO\\Desktop\\Trafic Signal\\Adaptive-Traffic-Signal-Timer\\Code\\YOLO\\darkflow')

# Dynamically load the version.py module
spec = importlib.util.spec_from_file_location(
    "version", 
    os.path.join(BASE_DIR, 'darkflow', 'version.py')  # Path corrected for version.py
)
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)

VERSION = version_module.__version__

# Define extensions based on the operating system
if os.name == 'nt':  # Windows
    ext_modules = [
        Extension(
            "darkflow.cython_utils.nms",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "nms.pyx")],
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "darkflow.cython_utils.cy_yolo2_findboxes",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "cy_yolo2_findboxes.pyx")],
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "darkflow.cython_utils.cy_yolo_findboxes",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "cy_yolo_findboxes.pyx")],
            include_dirs=[numpy.get_include()]
        )
    ]

elif os.name == 'posix':  # Unix-like systems
    ext_modules = [
        Extension(
            "darkflow.cython_utils.nms",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "nms.pyx")],
            libraries=["m"],  # Unix-specific math library
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "darkflow.cython_utils.cy_yolo2_findboxes",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "cy_yolo2_findboxes.pyx")],
            libraries=["m"],
            include_dirs=[numpy.get_include()]
        ),
        Extension(
            "darkflow.cython_utils.cy_yolo_findboxes",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "cy_yolo_findboxes.pyx")],
            libraries=["m"],
            include_dirs=[numpy.get_include()]
        )
    ]

else:  # Fallback for other systems
    ext_modules = [
        Extension(
            "darkflow.cython_utils.nms",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "nms.pyx")],
            libraries=["m"]
        ),
        Extension(
            "darkflow.cython_utils.cy_yolo2_findboxes",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "cy_yolo2_findboxes.pyx")],
            libraries=["m"]
        ),
        Extension(
            "darkflow.cython_utils.cy_yolo_findboxes",
            sources=[os.path.join(BASE_DIR, "darkflow", "cython_utils", "cy_yolo_findboxes.pyx")],
            libraries=["m"]
        )
    ]

# Setup configuration
setup(
    version=VERSION,
    name='darkflow',
    description='Darkflow',
    license='GPLv3',
    url='https://github.com/thtrieu/darkflow',
    packages=find_packages(),
    scripts=[os.path.join(BASE_DIR, 'darkflow', 'flow')],
    ext_modules=cythonize(ext_modules)
)
