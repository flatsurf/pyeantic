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

template <typename S, typename T>
auto make_renf_elem_class(const S& s, const T& t) {
    return renf_elem_class(s, t);
}

}  // namespace eantic
""")

from cppyy.gbl import eantic

eantic.renf = eantic.renf_class.make

# NOTE: cppyy is confused by template resolution, see
# https://github.com/flatsurf/pyeantic/issues/10
def py_make_renf_elem_class(*args):
    if len(args) == 1:
        return eantic.renf_elem_class(args[0])
    elif len(args) == 2:
        K, v = args
        if isinstance(v, (tuple, list)):
            v = cppyy.gbl.std.vector[int](v)
        return eantic.make_renf_elem_class[cppyy.gbl.std.shared_ptr[eantic.renf_class], type(v)](K, v)

eantic.renf_elem = py_make_renf_elem_class
