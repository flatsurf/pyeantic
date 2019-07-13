# -*- coding: utf-8 -*-
######################################################################
#  This file is part of pyeantic.
#
#        Copyright (C) 2019 Vincent Delecroix
#        Copyright (C) 2019 Julian Rüth
#
#  pyeantic is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  pyeantic is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with pyeantic. If not, see <https://www.gnu.org/licenses/>.
#####################################################################

import cppyy

# Importing cysignals after cppyy gives us proper stack traces on segfaults
# whereas cppyy otherwise only reports "segmentation violation" (which is
# probably what cling provides.)
import os
if os.environ.get('PYEANTIC_CYSIGNALS', True):
    try:
        import cysignals
    except ModuleNotFoundError:
        pass

def make_iterable(proxy, name):
    if hasattr(proxy, 'begin') and hasattr(proxy, 'end'):
        if not hasattr(proxy, '__iter__'):
            def iter(self):
                i = self.begin()
                while i != self.end():
                    yield i.__deref__()
                    i.__preinc__()

            proxy.__iter__ = iter

cppyy.py.add_pythonization(make_iterable, "eantic")

def pretty_print(proxy, name):
    proxy.__repr__ = proxy.__str__

cppyy.py.add_pythonization(pretty_print, "eantic")

def enable_arithmetic(proxy, name):
    if name in ["renf_elem_class"]:
        for (n, op) in [('add', ord('+')), ('sub', ord('-')), ('mul', ord('*')), ('div', ord('/'))]:
            def cppname(x):
                # some types such as int do not have a __cppname__; there might
                # be a better way to get their cppname but this seems to work
                # fine for the types we're using at least.
                return type(x).__cppname__ if hasattr(type(x), '__cppname__') else type(x).__name__
            def binary(lhs, rhs, op = op):
                lhs = sage_to_gmp(lhs)
                rhs = sage_to_gmp(rhs)
                return cppyy.gbl.eantic.boost_binary[cppname(lhs), cppname(rhs), op](lhs, rhs)
            def inplace(lhs, *args, **kwargs): raise NotImplementedError("inplace operators are not supported yet")
            setattr(proxy, "__%s__"%n, binary)
            setattr(proxy, "__r%s__"%n, binary)
            setattr(proxy, "__i%s__"%n, inplace)
        setattr(proxy, "__neg__", lambda self: cppyy.gbl.eantic.minus(self))
        setattr(proxy, "__pow__", lambda self, n: cppyy.gbl.eantic.pow(self, n))

cppyy.py.add_pythonization(enable_arithmetic, "eantic")

for path in os.environ.get('PYINTERVALXT_INCLUDE','').split(':'):
    if path: cppyy.add_include_path(path)

from .config import libdir

cppyy.cppdef("\n".join([r"""
#pragma cling add_library_path("%s")
"""%path for path in libdir]) + """
#pragma cling load("libeantic")
#pragma cling load("libeanticxx")
""")

cppyy.cppdef("""
#include <e-antic/renfxx.h>

// See https://bitbucket.org/wlav/cppyy/issues/95/lookup-of-friend-operator
namespace eantic {
std::ostream &operator<<(std::ostream &, const renf_class &);
std::ostream &operator<<(std::ostream &, const renf_elem_class &);
}  // namespace eantic

namespace eantic {
// cppyy does not see the operators that come out of boost/operators.hpp.
// Why exactly is not clear to me at the moment. Since they are defined as
// non-template friends inside the template classes such as addable<>, we can
// not explicitly declare them like we did with the operator<< below.
template <typename S, typename T, char op>
auto boost_binary(const S &lhs, const T &rhs) {
  if constexpr (op == '+')
    return lhs + rhs;
  else if constexpr (op == '-')
    return lhs - rhs;
  else if constexpr (op == '*')
    return lhs * rhs;
  else if constexpr (op == '/')
    return lhs / rhs;
  else {
    static_assert(false_v<op>, "operator not implemented");
  }
}
template <typename T>
T minus(const T &lhs) {
  return -lhs;
}

template <typename T>
auto make_renf_elem_class(const T& t) {
    return renf_elem_class(t);
}

template <typename T>
auto make_renf_elem_class_with_parent(const std::shared_ptr<renf_class> K, const T& t) {
    return renf_elem_class(K, t);
}

}  // namespace eantic
""")

from cppyy.gbl import eantic

eantic.renf = eantic.renf_class.make

# cppyy is confused by template resolution, see
# https://bitbucket.org/wlav/cppyy/issues/119/templatized-constructor-is-ignored
# and https://github.com/flatsurf/pyeantic/issues/10
def py_make_renf_elem_class(*args):
    if len(args) == 1:
        v = args[0]
        if isinstance(v, eantic.renf_class):
            return eantic.renf_elem_class(v)
        else:
            v = sage_to_gmp(v)
            return eantic.make_renf_elem_class(v)
    elif len(args) == 2:
        K, v = args
        v = sage_to_gmp(v)
        return eantic.make_renf_elem_class_with_parent[type(v)](K, v)

def sage_to_gmp(x):
    r"""
    Attempt to convert ``x`` from something that SageMath understand to
    something that the constructor of renf_elem_class understands.

    Typically, this is the conversion of a SageMath Integer to a mpz_class and
    such.

    If no such conversion exists, leave the argument unchanged.
    """
    try:
        from gmpy2 import mpz, mpq
    except ModuleNotFoundError:
        return x

    if isinstance(x, (tuple, list)):
        x = [sage_to_gmp(v) for v in x]
        if not all([isinstance(v, (int, cppyy.gbl.mpz_class, cppyy.gbl.mpq_class)) for v in x]):
            raise TypeError("Coefficients must be convertible to mpq")
        x = [cppyy.gbl.mpq_class(v) for v in x]
        x = cppyy.gbl.std.vector[cppyy.gbl.mpq_class](x)
    if hasattr(x, '__mpq__'):
        x = x.__mpq__()
    if hasattr(x, '__mpz__'):
        x = x.__mpz__()
    if isinstance(x, mpz):
        # we need std.string, or cppyy resolves to the wrong constructor:
        # https://bitbucket.org/wlav/cppyy/issues/127/string-argument-resolves-incorrectly
        x = cppyy.gbl.mpz_class(cppyy.gbl.std.string(str(x)))
    if isinstance(x, mpq):
        # we need std.string, or cppyy resolves to the wrong constructor:
        # https://bitbucket.org/wlav/cppyy/issues/127/string-argument-resolves-incorrectly
        x = cppyy.gbl.mpq_class(cppyy.gbl.std.string(str(x)))
    return x

eantic.renf_elem = py_make_renf_elem_class
