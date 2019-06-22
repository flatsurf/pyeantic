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

try:
    import sage.all
except ImportError:
    raise ImportError("sage_interface depends on SageMath")

import numbers

from .cppyy_eantic import eantic

from sage.rings.polynomial.polynomial_element import Polynomial as sage_Polynomial
from sage.rings.number_field.number_field_element import NumberFieldElement as sage_NumberFieldElement

def sage_nf_to_eantic(K):
    r"""
    Convert a Sage number field to eantic

    >>> from sage.all import NumberField, QQ, AA, Rational, polygen
    >>> from pyeantic.sage_conversion import sage_nf_to_eantic
    >>> x = polygen(QQ)
    >>> K = NumberField(x**3 - 3, 'a', embedding=AA(3)**Rational((1,3)))
    >>> L = sage_nf_to_eantic(K)
    >>> L
    NumberField(a^3 - 3, [1.442249570307408382321638310780 +/- 5.49e-31])
    >>> L.gen()
    (a ~ 1.442250)
    """
    x = K.variable_name()
    p = str(K.polynomial()._repr(x))
    emb = str(sage.rings.real_arb.RBF(K.coerce_embedding()(K.gen())))
    return eantic.renf(p, x, emb)

def sage_nf_elem_to_eantic(K, elem):
    r"""
    Convert a Sage number field element to eantic

    Parameters:
    K (eantic number field): the number field to which the conversion is
                             performed
    elem (Sage number field element): the element to convert

    >>> from sage.all import NumberField, QQ, AA, Integer, Rational, polygen
    >>> from pyeantic.sage_conversion import sage_nf_to_eantic
    >>> x = polygen(QQ)
    >>> K = NumberField(x**3 - 3, 'a', embedding=AA(3)**Rational((1,3)))
    >>> L = sage_nf_to_eantic(K)
    >>> sage_nf_elem_to_eantic(L, Integer(1))
    1
    >>> sage_nf_elem_to_eantic(L, Rational((2,3)))
    (2/3 ~ 0.666667)
    >>> sage_nf_elem_to_eantic(L, 'a')
    (a ~ 1.442250)
    >>> sage_nf_elem_to_eantic(L, K.gen())
    (a ~ 1.442250)
    """
    if isinstance(elem, numbers.Integral):
        data = int(elem)
    elif isinstance(elem, str):
        data = elem
    elif isinstance(elem, sage_NumberFieldElement):
        data = elem.polynomial()._repr(K.gen_name())
    else:
        data = str(elem)

    return eantic.renf_elem(K, data)
