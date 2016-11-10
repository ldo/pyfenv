#+
# This Python 3 module gives access to the floating-point environment-control
# functions available in <fenv.h> with C99.
#
# This code as it currently stands is certainly GCC-specific, and almost
# certainly x86-specific. How to make it more portable while keeping it in
# pure Python?
#-

import enum
import ctypes as ct

libm = ct.cdll.LoadLibrary("libm.so.6")

class FE :
    # Define bits representing the exception. We use the bit positions
    # of the appropriate bits in the FPU control word.
    INVALID = 0x01
    DENORM = 0x02
    DIVBYZERO = 0x04
    OVERFLOW = 0x08
    UNDERFLOW = 0x10
    INEXACT = 0x20
    ALL_EXCEPT = INEXACT | DIVBYZERO | UNDERFLOW | OVERFLOW | INVALID

    # The ix87 FPU supports all of the four defined rounding modes.  We
    # use again the bit positions in the FPU control word as the values
    # for the appropriate macros.
    TONEAREST = 0
    DOWNWARD = 0x400
    UPWARD = 0x800
    TOWARDZERO = 0xc00

    fexcept_t = ct.c_ushort

#end FE

@enum.unique
class EXCEPT(enum.Enum) :
    "the various possible floating-point exceptions."
    # values are bit numbers
    INVALID = 0
    DENORM = 1
    DIVBYZERO = 2
    OVERFLOW = 3
    UNDERFLOW = 4
    INEXACT = 5

    @classmethod
    def from_mask(celf, mask) :
        "converts a bitmask to a frozenset of EXCEPT.xxx values."
        result = set()
        for e in celf.__members__.values() :
            if 1 << e.value & mask != 0 :
                result.add(e)
            #end if
        #end for
        return \
            frozenset(result)
    #end from_mask

    @classmethod
    def to_mask(celf, flags) :
        "converts a set of EXCEPT.xxx values to a bitmask."
        result = 0
        for e in celf.__members__.values() :
            if e in flags :
                result |= 1 << e.value
            #end if
        #end for
        return \
            result
    #end to_mask

#end EXCEPT
EXCEPT_ALL = frozenset \
  (
    e for e in EXCEPT.__members__.values()
  )

@enum.unique
class ROUND(enum.Enum) :
    TONEAREST = 0
    DOWNWARD = 1
    UPWARD = 2
    TOWARDZERO = 3

    @classmethod
    def get(celf) :
        "returns the current rounding setting as a ROUND.xxx value."
        return \
            celf(libm.fegetround())
    #end get

    def set(self) :
        "sets the current rounding direction to this ROUND.xxx value."
        libm.fesetround(self.value)
    #end set

#end ROUND

# man page says these return nonzero iff error; but what errors could I check for?
libm.feclearexcept.restype = ct.c_int
libm.feclearexcept.argtypes = (ct.c_int,)
libm.fegetexceptflag.restype = ct.c_int
libm.fegetexceptflag.argtypes = (ct.POINTER(FE.fexcept_t), ct.c_int)
libm.feraiseexcept.restype = ct.c_int
libm.feraiseexcept.argtypes = (ct.c_int,)
libm.fesetexceptflag.restype = ct.c_int
libm.fesetexceptflag.argtypes = (ct.POINTER(FE.fexcept_t), ct.c_int)
libm.fetestexcept.restype = ct.c_int
libm.fetestexcept.argtypes = (ct.c_int,)

libm.fegetround.restype = ct.c_int
libm.fegetround.argtypes = ()
libm.fesetround.restype = ct.c_int
libm.fesetround.argtypes = (ct.c_int,)

# TODO: fenv_t functions

libm.feenableexcept.restype =  ct.c_int
libm.feenableexcept.argtypes = (ct.c_int,)
libm.fedisableexcept.restype =  ct.c_int
libm.fedisableexcept.argtypes = (ct.c_int,)
libm.fegetexcept.restype =  ct.c_int
libm.fegetexcept.argtypes = ()

class ExceptFlag :
    "wrapper for implementation-defined representation of exception flags." \
    " Do not instantiate directly; use the getflag method."

    __slots__ = ("_flags",)

    def __init__(self, _flags) :
        self._flags = _flags
    #end __init__

    @classmethod
    def clear(celf, excepts) :
        "clears the exceptions represented by excepts, which is a set of EXCEPT.xxx values."
        libm.feclearexcept(EXCEPT.to_mask(excepts))
    #end clear

    @classmethod
    def getflag(celf, excepts) :
        "returns the state of the exceptions represented by excepts," \
        " which is a set of EXCEPT.xxx values, as a new ExceptFlag object."
        c_result = FE.fexcept_t()
        libm.fegetexceptflag(ct.byref(c_result), EXCEPT.to_mask(excepts))
        return \
            celf(EXCEPT.from_mask(c_result.value))
    #end getflag

    @classmethod
    def raıse(celf, excepts) :
        "raises the exceptions represented by excepts, which is a set of EXCEPT.xxx values."
        libm.feraiseexcept(EXCEPT.to_mask(excepts))
    #end raıse

    def setflag(self, excepts) :
        "sets status for all exceptions represented by excepts, which is a set of" \
        " EXCEPT.xxx values, to those saved in this ExceptFlag instance."
        c_flags = FE.fexcept_t(EXCEPT.to_mask(self._flags))
        libm.fesetexceptflag(ct.byref(c_flags), EXCEPT.to_mask(excepts))
    #end setflag

    @classmethod
    def test(celf, excepts) :
        "returns a set of EXCEPT.xxx values indicating which of the exceptions" \
        " in excepts, which is a set of EXCEPT.xxx values, are currently set."
        return \
            EXCEPT.from_mask(libm.fetestexcept(EXCEPT.to_mask(excepts)))
    #end test

#end ExceptFlag

# TODO: floating-point environment, enable/disable individual exceptions