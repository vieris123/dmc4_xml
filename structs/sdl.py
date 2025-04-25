# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Sdl(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_tracks = False
        self.tracks__to_write = True

    def _read(self):
        self.header = Sdl.BaseHeader(self._io, self, self._root)
        self.header._read()


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.tracks
        for i in range(len(self._m_tracks)):
            pass
            self.tracks[i]._fetch_instances()



    def _write__seq(self, io=None):
        super(Sdl, self)._write__seq(io)
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
            super(Sdl.Vec4, self)._write__seq(io)
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
            super(Sdl.Point, self)._write__seq(io)
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
            super(Sdl.Size, self)._write__seq(io)
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
            super(Sdl.Rect, self)._write__seq(io)
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
            self._should_write_timing_frames = False
            self.timing_frames__to_write = True

        def _read(self):
            self.type = self._io.read_u1()
            self.prop_type = self._io.read_u1()
            self.num_frames = self._io.read_u2le()
            self.parent = self._io.read_u4le()
            self.name_ofs = self._io.read_u4le()
            self.dti_ref = self._io.read_u4le()
            self.timing_ref = self._io.read_u4le()
            self.data_ref = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.name
            if  (((self.data_ref > 0)) and ((self.type > 5))) :
                pass
                _ = self.data
                for i in range(len(self._m_data)):
                    pass
                    _on = self.prop_type
                    if _on == 14:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 10:
                        pass
                    elif _on == 4:
                        pass
                    elif _on == 6:
                        pass
                    elif _on == 20:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 7:
                        pass
                    elif _on == 12:
                        pass
                    elif _on == 58:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 3:
                        pass
                    elif _on == 5:
                        pass
                    elif _on == 15:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 8:
                        pass
                    elif _on == 40:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 9:
                        pass
                    elif _on == 21:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 34:
                        pass
                        self.data[i]._fetch_instances()
                    elif _on == 22:
                        pass
                        self.data[i]._fetch_instances()


            _ = self.timing_frames
            for i in range(len(self._m_timing_frames)):
                pass
                self.timing_frames[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Sdl.Track, self)._write__seq(io)
            self._should_write_name = self.name__to_write
            self._should_write_data = self.data__to_write
            self._should_write_timing_frames = self.timing_frames__to_write
            self._io.write_u1(self.type)
            self._io.write_u1(self.prop_type)
            self._io.write_u2le(self.num_frames)
            self._io.write_u4le(self.parent)
            self._io.write_u4le(self.name_ofs)
            self._io.write_u4le(self.dti_ref)
            self._io.write_u4le(self.timing_ref)
            self._io.write_u4le(self.data_ref)


        def _check(self):
            pass

        @property
        def size_(self):
            if hasattr(self, '_m_size_'):
                return self._m_size_

            self._m_size_ = 24
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
            self._io.seek((self.name_ofs + self._root.header.name_offset))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode("UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek((self.name_ofs + self._root.header.name_offset))
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
                self._m_data = []
                for i in range(self.num_frames):
                    _on = self.prop_type
                    if _on == 14:
                        pass
                        _t__m_data = Sdl.MtStr(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 10:
                        pass
                        self._m_data.append(self._io.read_s4le())
                    elif _on == 4:
                        pass
                        self._m_data.append(self._io.read_u1())
                    elif _on == 6:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 20:
                        pass
                        _t__m_data = Sdl.Vec3(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 7:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 12:
                        pass
                        self._m_data.append(self._io.read_f4le())
                    elif _on == 58:
                        pass
                        _t__m_data = Sdl.Resource(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 3:
                        pass
                        self._m_data.append(self._io.read_u1())
                    elif _on == 5:
                        pass
                        self._m_data.append(self._io.read_u2le())
                    elif _on == 15:
                        pass
                        _t__m_data = Sdl.Color(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 8:
                        pass
                        self._m_data.append(self._io.read_s1())
                    elif _on == 40:
                        pass
                        _t__m_data = Sdl.MtEasecurve(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 9:
                        pass
                        self._m_data.append(self._io.read_u4le())
                    elif _on == 21:
                        pass
                        _t__m_data = Sdl.Vec4(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 34:
                        pass
                        _t__m_data = Sdl.Float2(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)
                    elif _on == 22:
                        pass
                        _t__m_data = Sdl.Vec4(self._io, self, self._root)
                        _t__m_data._read()
                        self._m_data.append(_t__m_data)

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
                for i in range(len(self._m_data)):
                    pass
                    _on = self.prop_type
                    if _on == 14:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 10:
                        pass
                        self._io.write_s4le(self.data[i])
                    elif _on == 4:
                        pass
                        self._io.write_u1(self.data[i])
                    elif _on == 6:
                        pass
                        self._io.write_u4le(self.data[i])
                    elif _on == 20:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 7:
                        pass
                        self._io.write_u4le(self.data[i])
                    elif _on == 12:
                        pass
                        self._io.write_f4le(self.data[i])
                    elif _on == 58:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 3:
                        pass
                        self._io.write_u1(self.data[i])
                    elif _on == 5:
                        pass
                        self._io.write_u2le(self.data[i])
                    elif _on == 15:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 8:
                        pass
                        self._io.write_s1(self.data[i])
                    elif _on == 40:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 9:
                        pass
                        self._io.write_u4le(self.data[i])
                    elif _on == 21:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 34:
                        pass
                        self.data[i]._write__seq(self._io)
                    elif _on == 22:
                        pass
                        self.data[i]._write__seq(self._io)

                self._io.seek(_pos)



        def _check_data(self):
            pass
            if  (((self.data_ref > 0)) and ((self.type > 5))) :
                pass
                if (len(self.data) != self.num_frames):
                    raise kaitaistruct.ConsistencyError(u"data", len(self.data), self.num_frames)
                for i in range(len(self._m_data)):
                    pass
                    _on = self.prop_type
                    if _on == 14:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 10:
                        pass
                    elif _on == 4:
                        pass
                    elif _on == 6:
                        pass
                    elif _on == 20:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 7:
                        pass
                    elif _on == 12:
                        pass
                    elif _on == 58:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 3:
                        pass
                    elif _on == 5:
                        pass
                    elif _on == 15:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 8:
                        pass
                    elif _on == 40:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 9:
                        pass
                    elif _on == 21:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 34:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)
                    elif _on == 22:
                        pass
                        if self.data[i]._root != self._root:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._root, self._root)
                        if self.data[i]._parent != self:
                            raise kaitaistruct.ConsistencyError(u"data", self.data[i]._parent, self)



        @property
        def timing_frames(self):
            if self._should_write_timing_frames:
                self._write_timing_frames()
            if hasattr(self, '_m_timing_frames'):
                return self._m_timing_frames

            _pos = self._io.pos()
            self._io.seek(self.timing_ref)
            self._m_timing_frames = []
            for i in range(self.num_frames):
                _t__m_timing_frames = Sdl.TimingFrame(self._io, self, self._root)
                _t__m_timing_frames._read()
                self._m_timing_frames.append(_t__m_timing_frames)

            self._io.seek(_pos)
            return getattr(self, '_m_timing_frames', None)

        @timing_frames.setter
        def timing_frames(self, v):
            self._m_timing_frames = v

        def _write_timing_frames(self):
            self._should_write_timing_frames = False
            _pos = self._io.pos()
            self._io.seek(self.timing_ref)
            for i in range(len(self._m_timing_frames)):
                pass
                self.timing_frames[i]._write__seq(self._io)

            self._io.seek(_pos)


        def _check_timing_frames(self):
            pass
            if (len(self.timing_frames) != self.num_frames):
                raise kaitaistruct.ConsistencyError(u"timing_frames", len(self.timing_frames), self.num_frames)
            for i in range(len(self._m_timing_frames)):
                pass
                if self.timing_frames[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"timing_frames", self.timing_frames[i]._root, self._root)
                if self.timing_frames[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"timing_frames", self.timing_frames[i]._parent, self)



    class Mat4x3(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Sdl.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = Sdl.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = Sdl.Vec3(self._io, self, self._root)
            self.r2._read()
            self.r3 = Sdl.Vec3(self._io, self, self._root)
            self.r3._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(Sdl.Mat4x3, self)._write__seq(io)
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


    class TimingFrame(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.val = self._io.read_s4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl.TimingFrame, self)._write__seq(io)
            self._io.write_s4le(self.val)


        def _check(self):
            pass

        @property
        def frame(self):
            if hasattr(self, '_m_frame'):
                return self._m_frame

            self._m_frame = (self.val & 16777215)
            return getattr(self, '_m_frame', None)

        def _invalidate_frame(self):
            del self._m_frame
        @property
        def type(self):
            if hasattr(self, '_m_type'):
                return self._m_type

            self._m_type = (self.val >> 24)
            return getattr(self, '_m_type', None)

        def _invalidate_type(self):
            del self._m_type

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
            super(Sdl.Color, self)._write__seq(io)
            self._io.write_f4le(self.r)
            self._io.write_f4le(self.g)
            self._io.write_f4le(self.b)
            self._io.write_f4le(self.a)


        def _check(self):
            pass


    class Float2(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl.Float2, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)


        def _check(self):
            pass


    class Mat4x4(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.r0 = Sdl.Vec4(self._io, self, self._root)
            self.r0._read()
            self.r1 = Sdl.Vec4(self._io, self, self._root)
            self.r1._read()
            self.r2 = Sdl.Vec4(self._io, self, self._root)
            self.r2._read()
            self.r3 = Sdl.Vec4(self._io, self, self._root)
            self.r3._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()
            self.r3._fetch_instances()


        def _write__seq(self, io=None):
            super(Sdl.Mat4x4, self)._write__seq(io)
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
            super(Sdl.Resource, self)._write__seq(io)
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
            self.r0 = Sdl.Vec3(self._io, self, self._root)
            self.r0._read()
            self.r1 = Sdl.Vec3(self._io, self, self._root)
            self.r1._read()
            self.r2 = Sdl.Vec3(self._io, self, self._root)
            self.r2._read()


        def _fetch_instances(self):
            pass
            self.r0._fetch_instances()
            self.r1._fetch_instances()
            self.r2._fetch_instances()


        def _write__seq(self, io=None):
            super(Sdl.Mat3x3, self)._write__seq(io)
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
            super(Sdl.Vec3, self)._write__seq(io)
            self._io.write_f4le(self.x)
            self._io.write_f4le(self.y)
            self._io.write_f4le(self.z)
            self._io.write_f4le(self.padding)


        def _check(self):
            pass


    class MtEasecurve(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.p1 = self._io.read_f4le()
            self.p2 = self._io.read_f4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl.MtEasecurve, self)._write__seq(io)
            self._io.write_f4le(self.p1)
            self._io.write_f4le(self.p2)


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
            super(Sdl.MtStr, self)._write__seq(io)
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


    class BaseHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not (self.magic == b"\x53\x44\x4C\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x44\x4C\x00", self.magic, self._io, u"/types/base_header/seq/0")
            self.version = self._io.read_u2le()
            self.num_tracks = self._io.read_u2le()
            self.frames = self._io.read_u4le()
            self.dti_table_offset = self._io.read_u4le()
            self.name_offset = self._io.read_u4le()


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Sdl.BaseHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.version)
            self._io.write_u2le(self.num_tracks)
            self._io.write_u4le(self.frames)
            self._io.write_u4le(self.dti_table_offset)
            self._io.write_u4le(self.name_offset)


        def _check(self):
            pass
            if (len(self.magic) != 4):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 4)
            if not (self.magic == b"\x53\x44\x4C\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x53\x44\x4C\x00", self.magic, None, u"/types/base_header/seq/0")


    @property
    def tracks(self):
        if self._should_write_tracks:
            self._write_tracks()
        if hasattr(self, '_m_tracks'):
            return self._m_tracks

        _pos = self._io.pos()
        self._io.seek(20)
        self._m_tracks = []
        for i in range(self.header.num_tracks):
            _t__m_tracks = Sdl.Track(self._io, self, self._root)
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
        self._io.seek(20)
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



