"""Implementation of :class:`ModularInteger` class. """

import operator

from sympy.polys.polyutils import PicklableWithSlots
from sympy.polys.polyerrors import CoercionFailed


class ModularInteger(PicklableWithSlots):
    """A class representing a modular integer. """

    mod, dom, sym = None, None, None

    __slots__ = ['val']

    def __init__(self, val):
        if isinstance(val, self.__class__):
            self.val = val.val % self.mod
        else:
            self.val = self.dom.convert(val) % self.mod

    def __hash__(self):
        return hash((self.val, self.mod))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.val)

    def __str__(self):
        return "%s mod %s" % (self.val, self.mod)

    def __int__(self):
        return int(self.to_int())

    def to_int(self):
        if self.sym:
            if self.val <= self.mod // 2:
                return self.val
            else:
                return self.val - self.mod
        else:
            return self.val

    def __pos__(self):
        return self

    def __neg__(self):
        return self.__class__(-self.val)

    @classmethod
    def _get_val(cls, other):
        if isinstance(other, cls):
            return other.val
        else:
            try:
                return cls.dom.convert(other)
            except CoercionFailed:
                return None

    def __add__(self, other):
        val = self._get_val(other)

        if val is not None:
            return self.__class__(self.val + val)
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        val = self._get_val(other)

        if val is not None:
            return self.__class__(self.val - val)
        else:
            return NotImplemented

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        val = self._get_val(other)

        if val is not None:
            return self.__class__(self.val * val)
        else:
            return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        val = self._get_val(other)

        if val is not None:
            return self.__class__(self.val * self._invert(val))
        else:
            return NotImplemented

    def __rdiv__(self, other):
        return self.invert().__mul__(other)

    __truediv__ = __div__
    __rtruediv__ = __rdiv__

    def __mod__(self, other):
        val = self._get_val(other)

        if val is not None:
            return self.__class__(self.val % val)
        else:
            return NotImplemented

    def __rmod__(self, other):
        val = self._get_val(other)

        if val is not None:
            return self.__class__(val % self.val)
        else:
            return NotImplemented

    def __pow__(self, exp):
        if not exp:
            return self.__class__(self.dom.one)

        if exp < 0:
            val, exp = self.invert(), -exp
        else:
            val = self.val

        return self.__class__(val**exp)

    def _compare(self, other, op):
        val = self._get_val(other)

        if val is not None:
            return op(self.val, val % self.mod)
        else:
            return NotImplemented

    def __eq__(self, other):
        return self._compare(other, operator.eq)

    def __ne__(self, other):
        return self._compare(other, operator.ne)

    def __lt__(self, other):
        return self._compare(other, operator.lt)

    def __le__(self, other):
        return self._compare(other, operator.le)

    def __gt__(self, other):
        return self._compare(other, operator.gt)

    def __ge__(self, other):
        return self._compare(other, operator.ge)

    def __nonzero__(self):
        return bool(self.val)

    @classmethod
    def _invert(cls, value):
        return cls.dom.invert(value, cls.mod)

    def invert(self):
        return self.__class__(self._invert(self.val))

_modular_integer_cache = {}


def ModularIntegerFactory(_mod, _dom=None, _sym=True):
    """Create custom class for specific integer modulus."""
    if _dom is None:
        from sympy.polys.domains import ZZ as _dom
    elif not _dom.is_ZZ:
        raise TypeError("expected an integer ring, got %s" % _dom)

    try:
        _mod = _dom.convert(_mod)
    except CoercionFailed:
        ok = False
    else:
        ok = True

    if not ok or _mod < 1:
        raise ValueError("modulus must be a positive integer, got %s" % _mod)

    key = _mod, _dom, _sym

    try:
        cls = _modular_integer_cache[key]
    except KeyError:
        class cls(ModularInteger):
            mod, dom, sym = _mod, _dom, _sym

        if _sym:
            cls.__name__ = "SymmetricModularIntegerMod%s" % _mod
        else:
            cls.__name__ = "ModularIntegerMod%s" % _mod

        _modular_integer_cache[key] = cls

    return cls
