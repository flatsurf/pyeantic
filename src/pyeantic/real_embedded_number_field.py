# -*- coding: utf-8 -*-
r"""
Real Embedded Number Fields for SageMath

This wraps e-antic for SageMath providing number fields with less of a focus
on number theory but fast exact ball arithmetic of the kind that is usually
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

from sage.all import QQ, UniqueRepresentation, ZZ, RR, Fields, Field, RBF, AA, Morphism, Hom, SetsWithPartialMaps, NumberField, NumberFields, RealBallField
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

        sage: TestSuite(a).run()

    """
    renf_elem_class = cppyy.gbl.eantic.renf_elem_class

    def __init__(self, parent, value):
        r"""
        TESTS::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x^2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: a = K.gen()

            sage: from pyeantic.real_embedded_number_field import RealEmbeddedNumberFieldElement
            sage: isinstance(a, RealEmbeddedNumberFieldElement)
            True

        """
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
            (a+1 ~ 2.4142136)

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
            (a-1 ~ 0.41421356)

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
            (1/2*a ~ 0.70710678)

        """
        return self.parent()(self.renf_elem / other.renf_elem)

    def _neg_(self):
        r"""
        Return the negative of this element.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: -K.gen()
            (-a ~ -1.4142136)

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
            (a ~ 1.4142136)

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

    def __getstate__(self):
        r"""
        Return picklable data defining this element.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: loads(dumps(K.gen())) == K.gen()
            True

        """
        return (self.parent(), self.parent().number_field(self))

    def __setstate__(self, state):
        r"""
        Restore this element from the unpickled state.

        EXAMPLES::

            sage: from pyeantic import RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)
            sage: loads(dumps(K.one())) == K.one()
            True

        """
        self._set_parent(state[0])
        self.renf_elem = self.parent()(state[1]).renf_elem


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
            sage: K is L
            True
            sage: K is M
            True

        """
        if isinstance(embed, eantic.renf_class):
            # Since it is quite annoying to convert an fmpz polynomial, we parse
            # the printed representation of the renf_class. This is of course
            # not very robust…
            import re
            match = re.match("^NumberField\\(([^,]+), (\\[[^\\]]+\\])\\)$", repr(embed))
            assert match, "renf_class printed in an unexpected way"
            minpoly = match.group(1)
            root_str = match.group(2)
            match = re.match("^\\d*\\*?([^\\^ *]+)[\\^ ]", minpoly)
            assert match, "renf_class printed leading coefficient in an unexpected way"
            minpoly = QQ[match.group(1)](minpoly)
            roots = []
            AA_roots = minpoly.roots(AA, multiplicities=False)
            for prec in [53, 64, 128, 256]:
                R = RealBallField(prec)
                root = R(root_str)
                roots = [aa for aa in AA_roots if R(aa).overlaps(root)]
                if len(roots) == 1:
                    break
            if len(roots) != 1:
                raise RuntimeError("cannot distinguish roots with limited ball field precision")
            embed = NumberField(minpoly, minpoly.variable_name(), embedding=roots[0])
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
            embed = NumberField(K.polynomial().change_variable_name('x'), 'a', embedding=AA(embed(K.gen())))
        else:
            raise TypeError("cannot build RealEmbeddedNumberField from %s" % (type(embed)))

        category = category or Fields()
        return super(RealEmbeddedNumberField, cls).__classcall__(cls, embed, category)

    def __init__(self, embedded, category=None):
        r"""
        TESTS::

            sage: from pyeantic import eantic, RealEmbeddedNumberField
            sage: K = NumberField(x**2 - 2, 'a', embedding=sqrt(AA(2)))
            sage: K = RealEmbeddedNumberField(K)

            sage: from pyeantic.real_embedded_number_field import RealEmbeddedNumberField
            sage: isinstance(K, RealEmbeddedNumberField)
            True

            sage: TestSuite(K).run()

        """
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
            (a ~ 1.4142136)

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
            (a ~ 1.4142136)

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
        sage: coercion = K.convert_map_from(KK)

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
        rational_coefficients = [ZZ(c.get_str()) / ZZ(x.renf_elem.den().get_str()) for c in x.renf_elem.num_vector()]
        while len(rational_coefficients) < self.domain().number_field.degree():
            rational_coefficients.append(QQ.zero())
        return self.codomain()(rational_coefficients)
