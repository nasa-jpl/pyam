#!/usr/bin/python2

"""
This is a wrapper around pysvn classes to log each method call. The
_method_verbose and _function_returning_verbose_class classes are
generic wrappers that log invocations. I'm applying these generic
wrappers to pysvn here.

This whole module can (and maybe should) be made completely generic. But
this works ok for now.

Details:

Generally we use pysvn thusly:

  c = pysvn.Client()
  c.do_stuff()

Here pysvn.Client looks like a class we're instantiating with a
constructor.  This isn't how it's implemented internally, however:
pysvn.Client() is a function that returns an instance of some internal
class. This distinction is important in the way we write the logging
wrappers here:

  pysvn.Client() is wrapped to construct an instance of
  _function_returning_verbose_class. This class takes the place of the
  normal pysvn client class.

  All non-callable attributes of _function_returning_verbose_class are
  mapped directly to attributes of pysvn client. All callable ones are,
  however, replaced by instances of _method_verbose. This class acts
  like the method it wraps, except it logs input and output.
"""

from __future__ import absolute_import
from __future__ import print_function
from .. import yam_log
import pysvn
import sys


class _method_verbose:
    """Wraps a method of a given instance of a class. All calls to this method are
    logged

    """

    def __init__(self, obj, func, funcname):
        self._obj = obj
        self._func = func
        self._funcname = funcname

    def __call__(self, *args, **kwargs):
        yam_log.enter("{}( args={}, kwargs={} )".format(self._funcname, args, kwargs))

        try:
            ret = self._func(*args, **kwargs)
        except Exception as e:
            yam_log.lexit("Exception of type {}: {}\n".format(type(e), e))
            raise

        try:
            yam_log.lexit("returned {}\n".format(ret))
        except:
            yam_log.lexit("returned [unprintable]\n")
        return ret


class _function_returning_verbose_class:
    """wraps a function that returns a class instance. All method invocations from
    this instance are logged

    """

    def __init__(self, T, name_T, *args, **kwargs):
        self._wrapped_obj = T(*args, **kwargs)
        self._name_T = name_T

    def __getattr__(self, name):
        attr = getattr(self._wrapped_obj, name)

        if callable(attr):
            return _method_verbose(self._wrapped_obj, attr, "{}.{}".format(self._name_T, name))
        else:
            return attr

    # when setting any internal attributes, they apply to the wrapper class.
    # Anything else (like callback_get_login) goes into the internal class
    def __setattr__(self, name, value):
        if name[0] == "_":
            self.__dict__[name] = value
        else:
            setattr(self._wrapped_obj, name, value)


# wrap the given pysvn members. This is required because in pysvn attributes
# such as 'Client' are actually functions that construct objects in module
# _pysvn. I explicitly wrap the ones I know about. A more generic approach was
# too much trouble than it's worth; python has trouble here

_known_class_attributes = ("Client",)

# I set the my wrapper attributes
for attr in _known_class_attributes:
    # I need this extra layer with attr=attr in order to bind attr NOW,
    # and generate different functions for different values of attr
    def _make_local_wrapper(attr=attr):
        def _local_wrapper(*args, **kwargs):
            return _function_returning_verbose_class(getattr(pysvn, attr), "pysvn.{}".format(attr), *args, **kwargs)

        return _local_wrapper

    setattr(sys.modules[__name__], attr, _make_local_wrapper(attr))


# And I copy all the other attributes directly, except internal ones (beginning
# with '_'). These act as pass-throughs
for attr in dir(pysvn):
    if attr[0] != "_" and attr not in _known_class_attributes:
        setattr(sys.modules[__name__], attr, getattr(pysvn, attr))
