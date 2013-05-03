"""
Implementation of NSCoding for OC_PythonObject and friends

NOTE: this only works with a keyed archiver, not with a plain archiver. It
should be easy enough to change this later on if needed.

A minor problem with NSCoding support is that NSCoding restores
graphs recusively while Pickle does so depth-first (more of less).
This can cause problems when the object state contains the
object itself, which is why we need a 'setValue' callback for the
load_* functions below.
"""
from __future__ import unicode_literals
import sys
import objc
from types import *

try:
    import copyreg
except ImportError:
    # Python 2.x
    import copy_reg as copyreg
import copy

from pickle import PicklingError, UnpicklingError, whichmodule


if sys.version_info[0] == 3: # pragma: no cover (py3k)
    unicode = str
    long = int
    intern = sys.intern


OC_PythonObject = objc.lookUpClass("OC_PythonObject")

NSArray = objc.lookUpClass("NSArray")
NSDictionary = objc.lookUpClass("NSDictionary")
NSString = objc.lookUpClass("NSString")

kOP_REDUCE=0
kOP_INST=1
kOP_GLOBAL=2
kOP_NONE=3
kOP_BOOL=4
kOP_INT=5
kOP_LONG=6
kOP_FLOAT=7
kOP_UNICODE=8
kOP_STRING=9
kOP_TUPLE=10
kOP_LIST=11
kOP_DICT=12
kOP_GLOBAL_EXT=13
kOP_FLOAT_STR=14

kKIND = NSString.stringWithString_("kind")
kFUNC = NSString.stringWithString_("func")
kARGS = NSString.stringWithString_("args")
kLIST = NSString.stringWithString_("list")
kDICT = NSString.stringWithString_("dict")
kSTATE = NSString.stringWithString_("state")
kCLASS = NSString.stringWithString_("class")
kVALUE = NSString.stringWithString_("value")
kNAME = NSString.stringWithString_("name")
kMODULE = NSString.stringWithString_("module")
kCODE = NSString.stringWithString_("code")

class _EmptyClass:
    pass

encode_dispatch = {}

# Code below tries to mirror the implementation in pickle.py, with
# adaptations because we're not saving to a byte stream but to another
# serializer.

def save_reduce(coder, func, args,
        state=None, listitems=None, dictitems=None, obj=None):

    if not isinstance(args, tuple):
        raise PicklingError("args from reduce() should be a tuple")

    if not callable(func):
        raise PicklingError("func from reduce should be callable")

    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_REDUCE, kKIND)
        coder.encodeObject_forKey_(func, kFUNC)
        coder.encodeObject_forKey_(args, kARGS)
        if listitems is None:
            coder.encodeObject_forKey_(None, kLIST)
        else:
            coder.encodeObject_forKey_(list(listitems), kLIST)

        if dictitems is None:
            coder.encodeObject_forKey_(None, kDICT)
        else:
            coder.encodeObject_forKey_(dict(dictitems), kDICT)
        coder.encodeObject_forKey_(state, kSTATE)

    else:
        coder.__pyobjc__encodeInt_(kOP_REDUCE)
        coder.encodeObject_(func)
        coder.encodeObject_(args)
        if listitems is None:
            coder.encodeObject_(None)
        else:
            coder.encodeObject_(list(listitems))

        if dictitems is None:
            coder.encodeObject_(None)
        else:
            coder.encodeObject_(dict(dictitems))
        coder.encodeObject_(state)

if sys.version_info[0] == 2:
    def save_inst(coder, obj):
        if hasattr(obj, '__getinitargs__'):
            args = obj.__getinitargs__()
            len(args) # Assert it's a sequence
        else:
            args = ()

        cls = obj.__class__

        if coder.allowsKeyedCoding():
            coder.encodeInt32_forKey_(kOP_INST, kKIND)
            coder.encodeObject_forKey_(cls, kCLASS)
            coder.encodeObject_forKey_(args, kARGS)

        else:
            coder.__pyobjc__encodeInt32_(kOP_INST)
            coder.encodeObject_(cls)
            coder.encodeObject_(args)

        try:
            getstate = obj.__getstate__
        except AttributeError:
            state = obj.__dict__

        else:
            state = getstate()

        if coder.allowsKeyedCoding():
            coder.encodeObject_forKey_(state, kSTATE)

        else:
            coder.encodeObject_(state)

    encode_dispatch[InstanceType] = save_inst


def save_none(coder, obj):      # pragma: no cover
    # NOTE: function isn't actually used because "None" is passed to 'encodeWithObject...' as 
    #       a null pointer, and that won't trigger a callback to 'pyobjectEncode'.
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_NONE, kKIND)
    else:
        coder.__pyobjc__encodeInt_(kOP_NONE)
encode_dispatch[type(None)] = save_none

def save_bool(coder, obj): # pragma: no cover
    # NOTE: function isn't actually used because "None" is passed to 'encodeWithObject...' as 
    #       an NSNumber value, and that won't trigger a callback to 'pyobjectEncode'.
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_BOOL, kKIND)
        coder.encodeBool_forKey_(bool(obj), kVALUE)
    else:
        coder.__pyobjc__encodeInt_(kOP_BOOL)
        coder.__pyobjc__encodeBool_(bool(obj))
encode_dispatch[bool] = save_bool

if sys.version_info[0] == 2:
    def save_int(coder, obj):
        if coder.allowsKeyedCoding():
            coder.encodeInt_forKey_(kOP_INT, kKIND)
            coder.encodeInt64_forKey_(obj, kVALUE)
        else:
            coder.__pyobjc__encodeInt_(kOP_INT)
            coder.__pyobjc__encodeInt64_(obj)
    encode_dispatch[int] = save_int

    def save_long(coder, obj):
        encoded = unicode(repr(obj))
        if encoded.endswith('L'):
            encoded = encoded[:-1]
        if coder.allowsKeyedCoding():
            coder.encodeInt_forKey_(kOP_LONG, kKIND)
            coder.encodeObject_forKey_(encoded, kVALUE)
        else:
            coder.__pyobjc__encodeInt_(kOP_LONG)
            coder.encodeObject_(encoded)

    encode_dispatch[long] = save_long

else: # pragma: no cover (py3k)
    def save_int(coder, obj):
        if coder.allowsKeyedCoding():
            coder.encodeInt_forKey_(kOP_LONG, kKIND)
            coder.encodeObject_forKey_(unicode(repr(obj)), kVALUE)
        else:
            coder.__pyobjc__encodeInt_(kOP_LONG)
            coder.encodeObject_(unicode(repr(obj)))
    encode_dispatch[int] = save_int

def save_float(coder, obj):
    # Encode floats as strings, this seems to be needed to get
    # 100% reliable round-trips.
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_FLOAT_STR, kKIND)
        coder.encodeObject_forKey_(unicode(repr(obj)), kVALUE)
    else:
        coder.__pyobjc__encodeInt_(kOP_FLOAT_STR)
        coder.encodeObject_(unicode(repr(obj)))
    #coder.encodeDouble_forKey_(obj, kVALUE)
encode_dispatch[float] = save_float

def save_string(coder, obj): # pragma: no cover
    # String values passed to NSArchiver as instances of OC_PythonUnicode,
    # a subclass of NSString that can be encoded without calling back to 
    # pyobjectEncode. Subklasses of str and unicode will call back to pyobjectEncode,
    # but the actual string data is still a str/unicode that is encoded without
    # calling this function.
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_STRING, kKIND)
        coder.encodeBytes_length_forKey_(obj, len(obj), kVALUE)
    else:
        encodeInt_(kOP_STRING)
        coder.encodeBytes_length_(obj, len(obj))

encode_dispatch[str] = save_string


def save_tuple(coder, obj): # pragma: no cover
    # Tuples are saved by C code in OC_PythonArray.
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_TUPLE, kKIND)
        coder.encodeObject_forKey_(NSArray.arrayWithArray_(obj), kVALUE)

    else:
        coder.__pyobjc__encodeInt_(kOP_TUPLE)
        coder.encodeObject_(NSArray.arrayWithArray_(obj))
encode_dispatch[tuple] = save_tuple

def save_list(coder, obj): # pragma: no cover
    # Lists are saved by C code in OC_PythonArray.
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_LIST, kKIND)
        coder.encodeObject_forKey_(NSArray.arrayWithArray_(obj), kVALUE)

    else:
        coder.__pyobjc__encodeInt_(kOP_LIST)
        coder.encodeObject_(NSArray.arrayWithArray_(obj))
encode_dispatch[list] = save_list

def save_dict(coder, obj): # pragma: no cover
    # Dicts are saved by C code in OC_PythonDict
    if coder.allowsKeyedCoding():
        coder.encodeInt_forKey_(kOP_DICT, kKIND)
        v = NSDictionary.dictionaryWithDictionary_(obj)
        coder.encodeObject_forKey_(v, kVALUE)
    else:
        coder.__pyobjc__encodeInt_(kOP_DICT)
        v = NSDictionary.dictionaryWithDictionary_(obj)
        coder.encodeObject_(v)

encode_dispatch[dict] = save_dict

def save_global(coder, obj, name=None):
    if name is None:
        name = obj.__name__

    module = getattr(obj, "__module__", None)
    if module is None:
        module = whichmodule(obj, name)

    try:
        __import__ (module)
        mod = sys.modules[module]
        klass= getattr(mod, name)

    except (ImportError, KeyError, AttributeError):
        raise PicklingError(
                  "Can't pickle %r: it's not found as %s.%s" %
                  (obj, module, name))
    else:
        if klass is not obj:
            raise PicklingError(
                "Can't pickle %r: it's not the same object as %s.%s" %
                (obj, module, name))

    code = copyreg._extension_registry.get((module, name))

    if coder.allowsKeyedCoding():
        if code:
            coder.encodeInt_forKey_(kOP_GLOBAL_EXT, kKIND)
            coder.encodeInt_forKey_(code, kCODE)

        else:
            coder.encodeInt_forKey_(kOP_GLOBAL, kKIND)
            coder.encodeObject_forKey_(unicode(module), kMODULE)
            coder.encodeObject_forKey_(unicode(name), kNAME)

    else:
        if code:
            coder.__pyobjc__encodeInt_(kOP_GLOBAL_EXT)
            coder.__pyobjc__encodeInt_(code)

        else:
            coder.__pyobjc__encodeInt_(kOP_GLOBAL)
            coder.encodeObject_(unicode(module))
            coder.encodeObject_(unicode(name))

if sys.version_info[0] == 2:
    encode_dispatch[ClassType] = save_global
encode_dispatch[type(save_global)] = save_global
encode_dispatch[type(dir)] = save_global
encode_dispatch[type] = save_global


decode_dispatch = {}

def load_none(coder, setValue): #pragma: no cover
    # Decoding 'None' doesn't trigger Python code, for NSArchiver
    # 'None' is a nil pointer.
    return None
decode_dispatch[kOP_NONE] = load_none

def load_bool(coder, setValue): # pragma: no cover
    # Decoding booleans doesn't trigger python code because
    # they are stored in the archive as NSNumber instances.
    if coder.allowsKeyedCoding():
        return coder.decodeBoolForKey_(kVALUE)
    else:
        return coder.__pyobjc__decodeBool()

decode_dispatch[kOP_BOOL] = load_bool

def load_int(coder, setValue):
    if coder.allowsKeyedCoding():
        return int(coder.decodeInt64ForKey_(kVALUE))
    else:
        return int(coder.__pyobjc__decodeInt64())
decode_dispatch[kOP_INT] = load_int

def load_long(coder, setValue):
    if coder.allowsKeyedCoding():
        return long(coder.decodeObjectForKey_(kVALUE))
    else:
        return long(coder.decodeObject())
decode_dispatch[kOP_LONG] = load_long

def load_float(coder, setValue): # pragma: no cover
    # Only used with old versions of PyObjC (before 2.3), keep
    # for backward compatibility.
    if coder.allowsKeyedCoding():
        return coder.decodeFloatForKey_(kVALUE)
    else:
        raise RuntimeError("Unexpected encoding")
decode_dispatch[kOP_FLOAT] = load_float

def load_float_str(coder, setValue):
    if coder.allowsKeyedCoding():
        return float(coder.decodeObjectForKey_(kVALUE))
    else:
        return float(coder.decodeObject())
decode_dispatch[kOP_FLOAT_STR] = load_float_str

def load_tuple(coder, setValue): # pragma: no cover
    # Tuples are decoded in OC_PythonArray
    if coder.allowsKeyedCoding():
        return tuple(coder.decodeObjectForKey_(kVALUE))
    else:
        return tuple(coder.decodeObject())

decode_dispatch[kOP_TUPLE] = load_tuple

def load_list(coder, setValue): # pragma: no cover
    # Lists are decoded in OC_PythonArray
    if coder.allowsKeyedCoding():
        return list(coder.decodeObjectForKey_(kVALUE))
    else:
        return list(coder.decodeObject())
decode_dispatch[kOP_LIST] = load_list

def load_dict(coder, setValue): # pragma: no cover
    # Dicts are decoded in OC_PythonDict
    if coder.allowsKeyedCoding():
        return dict(coder.decodeObjectForKey_(kVALUE))
    else:
        return dict(coder.decodeObject())
decode_dispatch[kOP_DICT] = load_dict

def load_global_ext(coder, setValue):
    if coder.allowsKeyedCoding():
        code = coder.decodeIntForKey_(kCODE)
    else:
        code = coder.__pyobjc__decodeInt()
    nil = []
    obj = copyreg._extension_cache.get(code, nil)
    if obj is not nil:
        return obj
    key = copyreg._inverted_registry.get(code)
    if not key:
        raise ValueError("unregistered extension code %d" % code)

    module, name = key
    __import__(module)
    mod = sys.modules[module]
    klass = getattr(mod, name)
    copyreg._extension_cache[code] = klass
    return klass
decode_dispatch[kOP_GLOBAL_EXT] = load_global_ext

def load_global(coder, setValue):
    if coder.allowsKeyedCoding():
        module = coder.decodeObjectForKey_(kMODULE)
        name = coder.decodeObjectForKey_(kNAME)
    else:
        module = coder.decodeObject()
        name = coder.decodeObject()

    __import__(module)
    mod = sys.modules[module]
    klass = getattr(mod, name)
    return klass

decode_dispatch[kOP_GLOBAL] = load_global


def load_inst(coder, setValue):
    if coder.allowsKeyedCoding():
        cls = coder.decodeObjectForKey_(kCLASS)
        initargs = coder.decodeObjectForKey_(kARGS)
    else:
        cls = coder.decodeObject()
        initargs = coder.decodeObject()


    if (sys.version_info[0] == 2 and not initargs and
            type(cls) is ClassType and
            not hasattr(cls, "__getinitargs__")):
        value = _EmptyClass()
        value.__class__ = cls

    else:
        try:
            value = cls(*initargs)
        except TypeError as err:
            raise TypeError("in constructor for %s: %s" % (
                cls.__name__, str(err)), sys.exc_info()[2])


    # We now have the object, but haven't set the correct
    # state yet.  Tell the bridge about this value right
    # away, that's needed because `value` might be part
    # of the object state which we'll retrieve next.
    setValue(value)

    if coder.allowsKeyedCoding():
        state = coder.decodeObjectForKey_(kSTATE)
    else:
        state = coder.decodeObject()
    setstate = getattr(value, "__setstate__", None)
    if setstate is not None:
        setstate(state)
        return value

    slotstate = None
    if isinstance(state, tuple) and len(state) == 2:
        state, slotstate = state

    if state:
        # Note: pickle.py catches RuntimeError here,
        # that's for supporting restricted mode and
        # is not relevant for PyObjC.
        inst_dict = value.__dict__
        for k in state:
            v = state[k]
            if type(k) == str:
                inst_dict[intern(k)] = v
            else:
                inst_dict[k] = v


    if slotstate:
        for k, v in slotstate.items():
            if isinstance(k, objc.pyobjc_unicode):
                k = unicode(k)
            setattr(value, intern(k), v)

    return value
decode_dispatch[kOP_INST] = load_inst


def load_reduce(coder, setValue):
    if coder.allowsKeyedCoding():
        func = coder.decodeObjectForKey_(kFUNC)
        args = coder.decodeObjectForKey_(kARGS)
    else:
        func = coder.decodeObject()
        args = coder.decodeObject()

    value = func(*args)

    # We now have the object, but haven't set the correct
    # state yet.  Tell the bridge about this value right
    # away, that's needed because `value` might be part
    # of the object state which we'll retrieve next.
    setValue(value)

    if coder.allowsKeyedCoding():
        listitems = coder.decodeObjectForKey_(kLIST)
        dictitems = coder.decodeObjectForKey_(kDICT)
        state = coder.decodeObjectForKey_(kSTATE)
    else:
        listitems = coder.decodeObject()
        dictitems = coder.decodeObject()
        state = coder.decodeObject()

    setstate = getattr(value, "__setstate__", None)
    if setstate:
        setstate(state)
        return value

    slotstate = None
    if isinstance(state, tuple) and len(state) == 2:
        state, slotstate = state

    if state:
        # NOTE: picke.py catches RuntimeError here
        # to support restricted execution, that is not
        # relevant for PyObjC.
        inst_dict = value.__dict__

        for k in state:
            v = state[k]
            if type(k) == str:
                inst_dict[intern(k)] = v
            else:
                inst_dict[k] = v


    if slotstate:
        for k, v in slotstate.items():
            if isinstance(k, objc.pyobjc_unicode):
                k = unicode(k)
            setattr(value, intern(k), v)

    if listitems:
        for a in listitems:
            value.append(a)

    if dictitems:
        for k, v in dictitems.items():
            value[k] = v

    return value
decode_dispatch[kOP_REDUCE] = load_reduce


def pyobjectEncode(self, coder):
    t = type(self)

    # Find builtin support
    f = encode_dispatch.get(t)
    if f is not None:
        f(coder, self)
        return

    # Check for a class with a custom metaclass
    # XXX: pickle.py catches TypeError here, that's for
    #      compatibility with ancient versions of Boost 
    #      (before Python 2.2) and is not needed here.
    issc = issubclass(t, type)

    if issc:
        save_global(coder, self)
        return

    # Check copyreg.dispatch_table
    reduce = copyreg.dispatch_table.get(t)
    if reduce is not None:
        rv = reduce(self)

    else:
        reduce = getattr(self, "__reduce_ex__", None)
        if reduce is not None:
            rv = reduce(2)

        else: # pragma: no cover
            # This path will never be used because object implements 
            # __reduce_ex__ (at least in python2.6 and later)
            rv = getattr(self, "__reduce__", None)
            if reduce is not None:
                rv = reduce()

            else:
                raise PicklingError("Can't pickle %r object: %r" %
                        (t.__name__, self))

    if type(rv) is str:
        save_global(coder, self, rv)
        return

    if type(rv) is not tuple:
        raise PicklingError("%s must return string or tuple" % reduce)

    l = len(rv)
    if not (2 <= l <= 5):
        raise PicklingError("Tuple returned by %s must have two to "
                "five elements" % reduce)

    save_reduce(coder, *rv)

def pyobjectDecode(coder, setValue):
    if coder.allowsKeyedCoding():
        tp = coder.decodeIntForKey_(kKIND)
    else:
        tp = coder.__pyobjc__decodeInt()
    f = decode_dispatch.get(tp)
    if f is None:
        raise UnpicklingError("Unknown object kind: %s"%(tp,))

    return f(coder, setValue)

# An finally register the coder/decoder
OC_PythonObject.setVersion_coder_decoder_copier_(
        1, pyobjectEncode, pyobjectDecode, copy.copy)
