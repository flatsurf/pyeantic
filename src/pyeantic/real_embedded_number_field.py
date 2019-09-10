# -*- coding: utf-8 -*-
r"""
Real Embedded Number Fields for SageMath

This wraps e-antic for SageMath providing number fields with less of a focus on
number theory but fast exact ball arithmetic of the kind that is usually
required for classical geometry.
"""
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

from sage.all import QQ, UniqueRepresentation, ZZ, RR, Fields, Field, RBF, AA, \
                     Morphism, Hom, SetsWithPartialMaps, NumberField, NumberFields
from sage.structure.element import FieldElement
from sage.categories.map import Map

from pyeantic import eantic


class RealEmbeddedNumberFieldElement(FieldElement):
    r"""
    An element of a :class:`RealEmbeddedNumberField`, i.e., a wrapper of
    e-antic's ``renf_elem_class`.

    ..NOTES:

    This class wraps a ``renf_elem_class`` (which, at no additional runtime
    cost wraps a ``renf_elem``.) At the moment it's not possible to use a
    ``renf_elem_class`` directly in SageMath. Changing this might lead to a
    slight improvement in performance.

    EXAMPLES::

        sage: from pyeantic import RealEmbeddedNumberField
        sage: K = NumberField(x^2 - 2, 'a', embedding=sqrt(AA(2)))
        sage: K = RealEmbeddedNumberField(K)
        sage: a = K.gen()

    TESTS::

        sage: from pyeantic.real_embedded_number_field import RealEmbeddedNumberFieldElement
        sage: isinstance(a, RealEmbeddedNumberFieldElement)
        True

    """
    renf_elem_class = cppyy.gbl.eantic.renf_elem_class

    def __init__(self, parent, value):
        if isinstance(value, cppyy.gbl.eantic.renf_elem_class):
            self.renf_elem = value
        else:
            value = parent.number_field(value)
            self.renf_elem = parent.renf.zero()

            gen_pow = parent.renf.one()
            for coeff in value.polynomial().coefficients(sparse=False):
                self.renf_elem = self.renf_elem + coeff * gen_pow
                gen_pow = gen_pow * parent.renf.gen()

        FieldElement.__init__(self, parent)

    def _add_(self, other):
        r"""
        Return the sum of this element and ``other``.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.gen() + 1
            (a+1 ~ 2.414214)

        """
        return self.parent()(self.renf_elem + other.renf_elem)

    def _sub_(self, other):
        r"""
        Return the difference of this element and ``other``.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.gen() - 1
            (a-1 ~ 0.414214)

        """
        return self.parent()(self.renf_elem - other.renf_elem)

    def _mul_(self, other):
        r"""
        Return the product of this element and ``other``.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.gen() * K.gen()
            2

        """
        return self.parent()(self.renf_elem * other.renf_elem)

    def _div_(self, other):
        r"""
        Return the quotient of this element by ``other``.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: 1 / K.gen()
            (1/2*a ~ 0.707107)

        """
        return self.parent()(
            self.parent().number_field(self) /
            self.parent().number_field(other))

    def _neg_(self):
        r"""
        Return the negative of this element.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: -K.gen()
            (-a ~ -1.414214)

        """
        return self.parent()(-self.renf_elem)

    def _repr_(self):
        r"""
        Return a printable representation of this element.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.gen()
            (a ~ 1.414214)

        """
        return repr(self.renf_elem)

    def _cmp_(self, other):
        r"""
        Compare this element and ``other``.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.gen() > 0
            True
            sage: K.gen() < 1
            False

        """
        if self.renf_elem < other.renf_elem:
            return -1
        if self.renf_elem == other.renf_elem:
            return 0
        return 1


class RealEmbeddedNumberField(UniqueRepresentation, Field):
    r"""
    See ``RealEmbeddedNumberField`` in ``__init__.py`` for details.
    """
    @staticmethod
    def __classcall__(cls, embed, category=None):
        r"""
        Normalize parameters so embedded real number fields are unique::

            sage: from pyeantic import eantic, RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: L = NumberField(x**2 - 2, 'a')
            sage: L = RealEmbeddedNumberField(L.embeddings(AA)[1])
            sage: M = eantic.renf_class.make("a^2 - 2", "a", "1.4 +/- .1")
            sage: M = RealEmbeddedNumberField(M)
            Traceback (most recent call last):
            ...
            NotImplementedError: cannot build a RealEmbeddedNumberField from a renf_class yet
            sage: K is L
            True
            sage: K is M # not tested yet
            True

        """
        if embed in NumberFields():
            if not RR.has_coerce_map_from(embed):
                raise ValueError("number field must be endowed with an embedding into the reals")
            if not embed.is_absolute():
                raise NotImplementedError("number field must be absolute")
            # We recreate our NumberField from the embedding since number
            # fields with the same embedding might differ by other parameters
            # and therefore do not serve immediately as unique keys.
            embed = embed.coerce_embedding()
        if isinstance(embed, Map):
            K = embed.domain()
            if K not in NumberFields():
                raise ValueError("domain must be a number field")
            if not AA.has_coerce_map_from(embed.codomain()):
                raise ValueError("codomain must coerce into RR")
            if not K.is_absolute():
                raise NotImplementedError("number field must be absolute")
            # We explicitly construct an embedding from the given embedding to
            # make sure that we get a useable key.
            embed = NumberField(K.polynomial(), K.variable_name(), embedding=AA(embed(K.gen())))
        elif isinstance(embed, eantic.renf_class):
            raise NotImplementedError("cannot build a RealEmbeddedNumberField from a renf_class yet")
        else:
            raise TypeError("cannot build RealEmbeddedNumberField from %s" % (type(embed)))

        category = category or Fields()
        return super(RealEmbeddedNumberField, cls).__classcall__(cls, embed, category)

    def __init__(self, embedded, category=None):
        self.number_field = embedded
        var = self.number_field.variable_name()
        self.renf = eantic.renf(
            repr(self.number_field.polynomial().change_variable_name(var)),
            var,
            str(RBF(self.number_field.gen())))

        Field.__init__(self, QQ, category=category)

        self.register_coercion(self.number_field)
        self.number_field.register_conversion(ConversionNumberFieldRenf(self))

    def _repr_(self):
        r"""
        Return a printable representation of this number field.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: RealEmbeddedNumberField(K)
            Number Field in a with defining polynomial x^2 - 2 with a = 1.414213562373095?

        """
        return repr(self.number_field)

    def characteristic(self):
        r"""
        Return zero, the  characteristic of this number field.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: RealEmbeddedNumberField(K).characteristic()
            0

        """
        return ZZ(0)

    def an_element(self):
        r"""
        Return a typical element in this number field.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.an_element()
            (a ~ 1.414214)

        """
        return self(self.number_field.an_element())

    def gen(self):
        r"""
        Return the generator of this number field, i.e., a root of its defining
        polynomial.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: K.gen()
            (a ~ 1.414214)

        """
        return self(self.number_field.gen())

    Element = RealEmbeddedNumberFieldElement


class ConversionNumberFieldRenf(Morphism):
    r"""
    A conversion from :class:`RealEmbeddedNumberField` to a SageMath
    ``NumberField``.

    This could be a coercion map since the two number fields are identical.
    However, having coercions in both directions between parents can lead to
    surprising behaviour (the parents of some results depend on implementation
    details of the coercion framework.) It's better to avoid such problems and
    make the less frequently used coercion a conversion.

    EXAMPLES::

        sage: from pyeantic import RealEmbeddedNumberField
        sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
        sage: KK = RealEmbeddedNumberField(K)
        sage: coercion = K.coerce_map_from(KK)

    TESTS::

        sage: from pyeantic.real_embedded_number_field import ConversionNumberFieldRenf
        sage: isinstance(coercion, ConversionNumberFieldRenf)
        True

    """
    def __init__(self, domain):
        Morphism.__init__(self, Hom(domain, domain.number_field, SetsWithPartialMaps()))

    def _call_(self, x):
        r"""
        Convert ``x`` to the codomain.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: KK = RealEmbeddedNumberField(K)
            sage: a = KK.an_element()
            sage: K(a)
            a

        """
        # Note that Cython would certainly provide a faster path to turn an
        # mpz_class/mpz_t into a SageMath Integer. We should probably change
        # this if it is a bottleneck.
        def zz(mpz):
            import cppyy
            return ZZ(cppyy.gbl.boost.lexical_cast[cppyy.gbl.std.string](mpz))

        rational_coefficients = [zz(c) / zz(x.renf_elem.den()) for c in x.renf_elem.num_vector()]
        while len(rational_coefficients) < self.domain().number_field.degree():
            rational_coefficients.append(QQ.zero())
        return self.codomain()(rational_coefficients)
