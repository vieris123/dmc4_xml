# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class MtTypes(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self

    def _read(self):
        pass


    def _fetch_instances(self):
        pass


    def _write__seq(self, io=None):
        super(MtTypes, self)._write__seq(io)


    def _check(self):
        pass

    class Vec4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Vec4, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.w)


        def _check(self):
            pass


    class Point(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_s4le()
            self.y = self._io.read_s4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Point, self)._write__seq(io)
            self._io.write_s4le(self.x)
            self._io.write_s4le(self.y)


        def _check(self):
            pass


    class Size(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.w = self._io.read_s4le()
            self.h = self._io.read_s4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Size, self)._write__seq(io)
            self._io.write_s4le(self.w)
            self._io.write_s4le(self.h)


        def _check(self):
            pass


    class Rect(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.l = self._io.read_s4le()
            self.t = self._io.read_s4le()
            self.r = self._io.read_s4le()
            self.b = self._io.read_s4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Rect, self)._write__seq(io)
            self._io.write_s4le(self.l)
            self._io.write_s4le(self.t)
            self._io.write_s4le(self.r)
            self._io.write_s4le(self.b)


        def _check(self):
            pass


    class Mat4x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = MtTypes.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = MtTypes.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = MtTypes.Vec3(self._io, self, self._root)
            self.r2._read()
            self.r3 = MtTypes.Vec3(self._io, self, self._root)
            self.r3._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(MtTypes.Mat4x3, self)._write__seq(io)
            self.r0._write__seq(self._io)
            self.r1._write__seq(self._io)
            self.r2._write__seq(self._io)
            self.r3._write__seq(self._io)


        def _check(self):
            pass
            if self.r0._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r0", self.r0._root, self._root)
            if self.r0._parent != self:
                raise kaitaistruct.ConsistencyError(u"r0", self.r0._parent, self)
            if self.r1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r1", self.r1._root, self._root)
            if self.r1._parent != self:
                raise kaitaistruct.ConsistencyError(u"r1", self.r1._parent, self)
            if self.r2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r2", self.r2._root, self._root)
            if self.r2._parent != self:
                raise kaitaistruct.ConsistencyError(u"r2", self.r2._parent, self)
            if self.r3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r3", self.r3._root, self._root)
            if self.r3._parent != self:
                raise kaitaistruct.ConsistencyError(u"r3", self.r3._parent, self)


    class Color(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r = self._io.read_f4le()
            self.g = self._io.read_f4le()
            self.b = self._io.read_f4le()
            self.a = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Color, self)._write__seq(io)
            self._io.write_f4le(self.r)
            self._io.write_f4le(self.g)
            self._io.write_f4le(self.b)
            self._io.write_f4le(self.a)


        def _check(self):
            pass


    class Mat4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = MtTypes.Vec4(self._io, self, self._root)
            self.r0._read()
            self.r1 = MtTypes.Vec4(self._io, self, self._root)
            self.r1._read()
            self.r2 = MtTypes.Vec4(self._io, self, self._root)
            self.r2._read()
            self.r3 = MtTypes.Vec4(self._io, self, self._root)
            self.r3._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(MtTypes.Mat4x4, self)._write__seq(io)
            self.r0._write__seq(self._io)
            self.r1._write__seq(self._io)
            self.r2._write__seq(self._io)
            self.r3._write__seq(self._io)


        def _check(self):
            pass
            if self.r0._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r0", self.r0._root, self._root)
            if self.r0._parent != self:
                raise kaitaistruct.ConsistencyError(u"r0", self.r0._parent, self)
            if self.r1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r1", self.r1._root, self._root)
            if self.r1._parent != self:
                raise kaitaistruct.ConsistencyError(u"r1", self.r1._parent, self)
            if self.r2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r2", self.r2._root, self._root)
            if self.r2._parent != self:
                raise kaitaistruct.ConsistencyError(u"r2", self.r2._parent, self)
            if self.r3._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r3", self.r3._root, self._root)
            if self.r3._parent != self:
                raise kaitaistruct.ConsistencyError(u"r3", self.r3._parent, self)


    class Mat3x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = MtTypes.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = MtTypes.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = MtTypes.Vec3(self._io, self, self._root)
            self.r2._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()


        def _write__seq(self, io=None):
            super(MtTypes.Mat3x3, self)._write__seq(io)
            self.r0._write__seq(self._io)
            self.r1._write__seq(self._io)
            self.r2._write__seq(self._io)


        def _check(self):
            pass
            if self.r0._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r0", self.r0._root, self._root)
            if self.r0._parent != self:
                raise kaitaistruct.ConsistencyError(u"r0", self.r0._parent, self)
            if self.r1._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r1", self.r1._root, self._root)
            if self.r1._parent != self:
                raise kaitaistruct.ConsistencyError(u"r1", self.r1._parent, self)
            if self.r2._root != self._root:
                raise kaitaistruct.ConsistencyError(u"r2", self.r2._root, self._root)
            if self.r2._parent != self:
                raise kaitaistruct.ConsistencyError(u"r2", self.r2._parent, self)


    class Vec3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.padding = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(MtTypes.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.padding)


        def _check(self):
            pass


    class MtStr(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_string = False
            self.string__to_write = True

        def _read(self):
            self.ptr = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.string


        def _write__seq(self, io=None):
            super(MtTypes.MtStr, self)._write__seq(io)
            self._should_write_string = self.string__to_write
            self._io.write_u4le(self.ptr)


        def _check(self):
            pass

        @property
        def string(self):
            if self._should_write_string:
                self._write_string()
            if hasattr(self, '_m_string'):
                return self._m_string

            _pos = self._io.pos()
            self._io.seek(self.ptr)
            self._m_string = (self._io.read_bytes_term(0, False, True, True)).decode("UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_string', None)

        @string.setter
        def string(self, v):
            self._m_string = v

        def _write_string(self):
            self._should_write_string = False
            _pos = self._io.pos()
            self._io.seek(self.ptr)
            self._io.write_bytes((self.string).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)


        def _check_string(self):
            pass
            if (KaitaiStream.byte_array_index_of((self.string).encode(u"UTF-8"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"string", KaitaiStream.byte_array_index_of((self.string).encode(u"UTF-8"), 0), -1)



