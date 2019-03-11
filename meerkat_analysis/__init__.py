try:
    import pylab
    import os

    dir_path = os.path.dirname(os.path.realpath(__file__))

    pylab.style.use(dir_path + "/style/meerkat.mplstyle")
except ImportError:
    pass
