# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Pla(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_tracks = False
        self.tracks__to_write = True

    def _read(self):
        self.header = Pla.BaseHeader(self._io, self, self._root)
        self.header._read()


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.tracks
        for i in range(len(self._m_tracks)):
            pass
            self.tracks[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Pla, self)._write__seq(io)
        self._should_write_tracks = self.tracks__to_write
        self.header._write__seq(self._io)


    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)

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
            super(Pla.Vec4, self)._write__seq(io)
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
            super(Pla.Point, self)._write__seq(io)
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
            super(Pla.Size, self)._write__seq(io)
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
            super(Pla.Rect, self)._write__seq(io)
            self._io.write_s4le(self.l)
            self._io.write_s4le(self.t)
            self._io.write_s4le(self.r)
            self._io.write_s4le(self.b)


        def _check(self):
            pass


    class Track(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__to_write = True
            self._should_write_data = False
            self.data__to_write = True

        def _read(self):
            self.type = self._io.read_u4le()
            self.prop_type = self._io.read_u4le()
            self.parent = self._io.read_u4le()
            self.move_line = self._io.read_u4le()
            self.class_ofs = self._io.read_u4le()
            self.dti_ref = self._io.read_u4le()
            self.data_ref = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.name
            if  (((self.data_ref > 0)) and ((self.type > 5))) :
                pass
                _ = self.data
                _on = self.type
                if _on == 10:
                    pass
                elif _on == 6:
                    pass
                elif _on == 7:
                    pass
                elif _on == 11:
                    pass
                    self.data._fetch_instances()
                elif _on == 8:
                    pass
                elif _on == 9:
                    pass



        def _write__seq(self, io=None):
            super(Pla.Track, self)._write__seq(io)
            self._should_write_name = self.name__to_write
            self._should_write_data = self.data__to_write
            self._io.write_u4le(self.type)
            self._io.write_u4le(self.prop_type)
            self._io.write_u4le(self.parent)
            self._io.write_u4le(self.move_line)
            self._io.write_u4le(self.class_ofs)
            self._io.write_u4le(self.dti_ref)
            self._io.write_u4le(self.data_ref)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 28
            return getattr(self, '_m_size_', None)

        def _invalidate_size_(self):
            del self._m_size_
        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self.class_ofs + self._root.header.name_offset))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode("UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek((self.class_ofs + self._root.header.name_offset))
            self._io.write_bytes((self.name).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)


        def _check_name(self):
            pass
            if (KaitaiStream.byte_array_index_of((self.name).encode(u"UTF-8"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"name", KaitaiStream.byte_array_index_of((self.name).encode(u"UTF-8"), 0), -1)

        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            if  (((self.data_ref > 0)) and ((self.type > 5))) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.data_ref)
                _on = self.type
                if _on == 10:
                    pass
                    self._m_data = self._io.read_u4le()
                elif _on == 6:
                    pass
                    self._m_data = self._io.read_u4le()
                elif _on == 7:
                    pass
                    self._m_data = self._io.read_u4le()
                elif _on == 11:
                    pass
                    self._m_data = Pla.Resource(self._io, self, self._root)
                    self._m_data._read()
                elif _on == 8:
                    pass
                    self._m_data = self._io.read_u4le()
                elif _on == 9:
                    pass
                    self._m_data = self._io.read_u4le()
                self._io.seek(_pos)

            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            if  (((self.data_ref > 0)) and ((self.type > 5))) :
                pass
                _pos = self._io.pos()
                self._io.seek(self.data_ref)
                _on = self.type
                if _on == 10:
                    pass
                    self._io.write_u4le(self.data)
                elif _on == 6:
                    pass
                    self._io.write_u4le(self.data)
                elif _on == 7:
                    pass
                    self._io.write_u4le(self.data)
                elif _on == 11:
                    pass
                    self.data._write__seq(self._io)
                elif _on == 8:
                    pass
                    self._io.write_u4le(self.data)
                elif _on == 9:
                    pass
                    self._io.write_u4le(self.data)
                self._io.seek(_pos)



        def _check_data(self):
            pass
            if  (((self.data_ref > 0)) and ((self.type > 5))) :
                pass
                _on = self.type
                if _on == 10:
                    pass
                elif _on == 6:
                    pass
                elif _on == 7:
                    pass
                elif _on == 11:
                    pass
                    if self.data._root != self._root:
                        raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
                    if self.data._parent != self:
                        raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)
                elif _on == 8:
                    pass
                elif _on == 9:
                    pass



    class Mat4x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Pla.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = Pla.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = Pla.Vec3(self._io, self, self._root)
            self.r2._read()
            self.r3 = Pla.Vec3(self._io, self, self._root)
            self.r3._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(Pla.Mat4x3, self)._write__seq(io)
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
            super(Pla.Color, self)._write__seq(io)
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
            self.r0 = Pla.Vec4(self._io, self, self._root)
            self.r0._read()
            self.r1 = Pla.Vec4(self._io, self, self._root)
            self.r1._read()
            self.r2 = Pla.Vec4(self._io, self, self._root)
            self.r2._read()
            self.r3 = Pla.Vec4(self._io, self, self._root)
            self.r3._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(Pla.Mat4x4, self)._write__seq(io)
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


    class Resource(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_ref_dti = False
            self.ref_dti__to_write = True
            self._should_write_ref_path = False
            self.ref_path__to_write = True

        def _read(self):
            self.ref_ofs = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.ref_dti
            _ = self.ref_path


        def _write__seq(self, io=None):
            super(Pla.Resource, self)._write__seq(io)
            self._should_write_ref_dti = self.ref_dti__to_write
            self._should_write_ref_path = self.ref_path__to_write
            self._io.write_u4le(self.ref_ofs)


        def _check(self):
            pass

        @property
        def ref_dti(self):
            if self._should_write_ref_dti:
                self._write_ref_dti()
            if hasattr(self, '_m_ref_dti'):
                return self._m_ref_dti

            _pos = self._io.pos()
            self._io.seek((self.ref_ofs + self._root.header.name_offset))
            self._m_ref_dti = self._io.read_u4le()
            self._io.seek(_pos)
            return getattr(self, '_m_ref_dti', None)

        @ref_dti.setter
        def ref_dti(self, v):
            self._m_ref_dti = v

        def _write_ref_dti(self):
            self._should_write_ref_dti = False
            _pos = self._io.pos()
            self._io.seek((self.ref_ofs + self._root.header.name_offset))
            self._io.write_u4le(self.ref_dti)
            self._io.seek(_pos)


        def _check_ref_dti(self):
            pass

        @property
        def ref_path(self):
            if self._should_write_ref_path:
                self._write_ref_path()
            if hasattr(self, '_m_ref_path'):
                return self._m_ref_path

            _pos = self._io.pos()
            self._io.seek(((self.ref_ofs + self._root.header.name_offset) + 4))
            self._m_ref_path = (self._io.read_bytes_term(0, False, True, True)).decode("UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_ref_path', None)

        @ref_path.setter
        def ref_path(self, v):
            self._m_ref_path = v

        def _write_ref_path(self):
            self._should_write_ref_path = False
            _pos = self._io.pos()
            self._io.seek(((self.ref_ofs + self._root.header.name_offset) + 4))
            self._io.write_bytes((self.ref_path).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)


        def _check_ref_path(self):
            pass
            if (KaitaiStream.byte_array_index_of((self.ref_path).encode(u"UTF-8"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"ref_path", KaitaiStream.byte_array_index_of((self.ref_path).encode(u"UTF-8"), 0), -1)


    class Mat3x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Pla.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = Pla.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = Pla.Vec3(self._io, self, self._root)
            self.r2._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()


        def _write__seq(self, io=None):
            super(Pla.Mat3x3, self)._write__seq(io)
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


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Pla.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)


        def _check(self):
            pass


    class BaseHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not (self.magic == b"\x50\x4C\x41\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x50\x4C\x41\x00", self.magic, self._io, u"/types/base_header/seq/0")
            self.version = self._io.read_u2le()
            self.num_tracks = self._io.read_u2le()
            self.dti_table_offset = self._io.read_u4le()
            self.name_offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Pla.BaseHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.version)
            self._io.write_u2le(self.num_tracks)
            self._io.write_u4le(self.dti_table_offset)
            self._io.write_u4le(self.name_offset)


        def _check(self):
            pass
            if (len(self.magic) != 4):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 4)
            if not (self.magic == b"\x50\x4C\x41\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x50\x4C\x41\x00", self.magic, None, u"/types/base_header/seq/0")


    @property
    def tracks(self):
        if self._should_write_tracks:
            self._write_tracks()
        if hasattr(self, '_m_tracks'):
            return self._m_tracks

        _pos = self._io.pos()
        self._io.seek(16)
        self._m_tracks = []
        for i in range(self.header.num_tracks):
            _t__m_tracks = Pla.Track(self._io, self, self._root)
            _t__m_tracks._read()
            self._m_tracks.append(_t__m_tracks)

        self._io.seek(_pos)
        return getattr(self, '_m_tracks', None)

    @tracks.setter
    def tracks(self, v):
        self._m_tracks = v

    def _write_tracks(self):
        self._should_write_tracks = False
        _pos = self._io.pos()
        self._io.seek(16)
        for i in range(len(self._m_tracks)):
            pass
            self.tracks[i]._write__seq(self._io)

        self._io.seek(_pos)


    def _check_tracks(self):
        pass
        if (len(self.tracks) != self.header.num_tracks):
            raise kaitaistruct.ConsistencyError(u"tracks", len(self.tracks), self.header.num_tracks)
        for i in range(len(self._m_tracks)):
            pass
            if self.tracks[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"tracks", self.tracks[i]._root, self._root)
            if self.tracks[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"tracks", self.tracks[i]._parent, self)



