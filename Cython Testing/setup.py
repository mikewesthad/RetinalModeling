from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy

#extension_name  = "NearestNeighborPlacement"
extension_name  = "Retina"
filename        = extension_name+".pyx"

ext_modules = [Extension(extension_name, [filename])]

setup(
    name = extension_name,
    cmdclass = {'build_ext':build_ext},
    ext_modules = ext_modules,
    include_dirs = [numpy.get_include()]
)

