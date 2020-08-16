r"""
Make e-antic accessible from Python through cppyy

EXAMPLES::

>>> from pyeantic import eantic
>>> K = eantic.renf("x^2 - 2", "x", "[1.4 +/- 1]")
>>> x = eantic.renf_elem(K, "x"); x
(x ~ 1.4142136)
>>> x + 2
(x+2 ~ 3.4142136)

"""
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

def pretty_print(proxy, name):
    proxy.__repr__ = proxy.__str__

cppyy.py.add_pythonization(pretty_print, "eantic")

def enable_arithmetic(proxy, name):
    if name in ["renf_elem_class"]:
        for (op, infix) in [('add', '+'), ('sub', '-'), ('mul', '*'), ('truediv', '/')]:
            python_op = "__%s__" % (op,)
            python_rop = "__r%s__" % (op,)

            implementation = getattr(cppyy.gbl.eantic.cppyy, op)
            def binary(lhs, rhs, implementation=implementation):
                lhs, rhs = for_eantic(lhs), for_eantic(rhs)
                return implementation[type(lhs), type(rhs)](lhs, rhs)
            def rbinary(rhs, lhs, implementation=implementation):
                lhs, rhs = for_eantic(lhs), for_eantic(rhs)
                return implementation[type(lhs), type(rhs)](lhs, rhs)

            setattr(proxy, python_op, binary)
            setattr(proxy, python_rop, rbinary)

        setattr(proxy, "__neg__", lambda self: cppyy.gbl.eantic.cppyy.neg(self))
        setattr(proxy, "__pow__", lambda self, n: cppyy.gbl.eantic.pow(self, n))

cppyy.py.add_pythonization(enable_arithmetic, "eantic")

for path in os.environ.get('PYEANTIC_INCLUDE','').split(':'):
    if path: cppyy.add_include_path(path)

cppyy.cppdef("""
#include <e-antic/renfxx.h>

// See https://bitbucket.org/wlav/cppyy/issues/95/lookup-of-friend-operator
namespace eantic {
std::ostream &operator<<(std::ostream &, const renf_class &);
std::ostream &operator<<(std::ostream &, const renf_elem_class &);
}  // namespace eantic

namespace eantic {
namespace cppyy {
// cppyy does not see the operators provided by boost::operators so we provide
// something to make them explicit here:
template <typename S, typename T>
auto add(const S& lhs, const T& rhs) { return lhs + rhs; }
template <typename S, typename T>
auto sub(const S& lhs, const T& rhs) { return lhs - rhs; }
template <typename S, typename T>
auto mul(const S& lhs, const T& rhs) { return lhs * rhs; }
template <typename S, typename T>
auto truediv(const S& lhs, const T& rhs) { return lhs / rhs; }
template <typename T>
auto neg(const T& value) { return -value; }

template <typename T>
auto make_renf_elem_class(const T& t) {
    return renf_elem_class(t);
}

template <typename T>
auto make_renf_elem_class_with_parent(const std::shared_ptr<renf_class> K, const T& t) {
    return renf_elem_class(K, t);
}

mpq_class rational(const renf_elem_class& x) {
    return static_cast<mpq_class>(x);
}

}  // namespace cppyy
}  // namespace eantic
""")

from cppyy.gbl import eantic

eantic.renf = eantic.renf_class.make

# cppyy is confused by template resolution, see
# https://bitbucket.org/wlav/cppyy/issues/119/templatized-constructor-is-ignored
# and https://github.com/flatsurf/pyeantic/issues/10
def make_renf_elem_class(*args):
    if len(args) == 1:
        v = args[0]
        if isinstance(v, eantic.renf_class):
            return eantic.renf_elem_class(v)
        else:
            v = for_eantic(v)
            return eantic.cppyy.make_renf_elem_class(v)
    elif len(args) == 2:
        K, v = args
        v = for_eantic(v)
        return eantic.cppyy.make_renf_elem_class_with_parent[type(v)](K, v)

def for_eantic(x):
    r"""
    Attempt to convert ``x`` from something that SageMath understand to
    something that the constructor of renf_elem_class understands.

    Typically, this is the conversion of a SageMath Integer to a mpz_class and
    such.

    If no such conversion exists, leave the argument unchanged.
    """
    if isinstance(x, (int, eantic.renf_elem_class, cppyy.gbl.mpz_class, cppyy.gbl.mpq_class)):
        return x
    if isinstance(x, (tuple, list)):
        x = [for_eantic(v) for v in x]
        if not all([isinstance(v, (int, cppyy.gbl.mpz_class, cppyy.gbl.mpq_class)) for v in x]):
            raise TypeError("Coefficients must be convertible to mpq")
        x = [cppyy.gbl.mpq_class(v) for v in x]
        x = cppyy.gbl.std.vector[cppyy.gbl.mpq_class](x)
    if hasattr(x, '__mpq__'):
        x = x.__mpq__()
    if hasattr(x, '__mpz__'):
        x = x.__mpz__()

    try:
        from gmpy2 import mpz, mpq
    except ModuleNotFoundError:
        return x

    if isinstance(x, mpz):
        # we need std.string, or cppyy resolves to the wrong constructor:
        # https://bitbucket.org/wlav/cppyy/issues/127/string-argument-resolves-incorrectly
        x = cppyy.gbl.mpz_class(cppyy.gbl.std.string(str(x)))
    if isinstance(x, mpq):
        # we need std.string, or cppyy resolves to the wrong constructor:
        # https://bitbucket.org/wlav/cppyy/issues/127/string-argument-resolves-incorrectly
        x = cppyy.gbl.mpq_class(cppyy.gbl.std.string(str(x)))
    return x

eantic.renf_elem = make_renf_elem_class
