# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Xfs(ReadWriteKaitaiStruct):
    def __init__(self, _io=None, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._should_write_objects = False
        self.objects__to_write = True
        self._should_write_data_buffer = False
        self.data_buffer__to_write = True

    def _read(self):
        self.header = Xfs.XfsHeader(self._io, self, self._root)
        self.header._read()


    def _fetch_instances(self):
        pass
        self.header._fetch_instances()
        _ = self.objects
        for i in range(len(self._m_objects)):
            pass
            self.objects[i]._fetch_instances()

        _ = self.data_buffer


    def _write__seq(self, io=None):
        super(Xfs, self)._write__seq(io)
        self._should_write_objects = self.objects__to_write
        self._should_write_data_buffer = self.data_buffer__to_write
        self.header._write__seq(self._io)


    def _check(self):
        pass
        if self.header._root != self._root:
            raise kaitaistruct.ConsistencyError(u"header", self.header._root, self._root)
        if self.header._parent != self:
            raise kaitaistruct.ConsistencyError(u"header", self.header._parent, self)

    class XfsHeader(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.magic = self._io.read_bytes(4)
            if not (self.magic == b"\x58\x46\x53\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x58\x46\x53\x00", self.magic, self._io, u"/types/xfs_header/seq/0")
            self.major_ver = self._io.read_u2le()
            self.minor_ver = self._io.read_u2le()
            self.object_num = self._io.read_u4le()
            self.data_size = self._io.read_u4le()
            self.obj_pos = []
            for i in range(self.object_num):
                self.obj_pos.append(self._io.read_u4le())



        def _fetch_instances(self):
            pass
            for i in range(len(self.obj_pos)):
                pass



        def _write__seq(self, io=None):
            super(Xfs.XfsHeader, self)._write__seq(io)
            self._io.write_bytes(self.magic)
            self._io.write_u2le(self.major_ver)
            self._io.write_u2le(self.minor_ver)
            self._io.write_u4le(self.object_num)
            self._io.write_u4le(self.data_size)
            for i in range(len(self.obj_pos)):
                pass
                self._io.write_u4le(self.obj_pos[i])



        def _check(self):
            pass
            if (len(self.magic) != 4):
                raise kaitaistruct.ConsistencyError(u"magic", len(self.magic), 4)
            if not (self.magic == b"\x58\x46\x53\x00"):
                raise kaitaistruct.ValidationNotEqualError(b"\x58\x46\x53\x00", self.magic, None, u"/types/xfs_header/seq/0")
            if (len(self.obj_pos) != self.object_num):
                raise kaitaistruct.ConsistencyError(u"obj_pos", len(self.obj_pos), self.object_num)
            for i in range(len(self.obj_pos)):
                pass



    class Obj(ReadWriteKaitaiStruct):
        def __init__(self, i, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self.i = i
            self._should_write_data = False
            self.data__to_write = True

        def _read(self):
            pass


        def _fetch_instances(self):
            pass
            _ = self.data
            self.data._fetch_instances()


        def _write__seq(self, io=None):
            super(Xfs.Obj, self)._write__seq(io)
            self._should_write_data = self.data__to_write


        def _check(self):
            pass

        @property
        def data(self):
            if self._should_write_data:
                self._write_data()
            if hasattr(self, '_m_data'):
                return self._m_data

            _pos = self._io.pos()
            self._io.seek((self._root.header.obj_pos[self.i] + 16))
            self._m_data = Xfs.ObjectData(self._io, self, self._root)
            self._m_data._read()
            self._io.seek(_pos)
            return getattr(self, '_m_data', None)

        @data.setter
        def data(self, v):
            self._m_data = v

        def _write_data(self):
            self._should_write_data = False
            _pos = self._io.pos()
            self._io.seek((self._root.header.obj_pos[self.i] + 16))
            self.data._write__seq(self._io)
            self._io.seek(_pos)


        def _check_data(self):
            pass
            if self.data._root != self._root:
                raise kaitaistruct.ConsistencyError(u"data", self.data._root, self._root)
            if self.data._parent != self:
                raise kaitaistruct.ConsistencyError(u"data", self.data._parent, self)


    class ObjectData(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.dti = self._io.read_u4le()
            self.prop_num = self._io.read_bits_int_le(15)
            self.init = self._io.read_bits_int_le(1) != 0
            self.reserved = self._io.read_u2le()
            self.prop = []
            for i in range(self.prop_num):
                _t_prop = Xfs.MtProperty(self._io, self, self._root)
                _t_prop._read()
                self.prop.append(_t_prop)



        def _fetch_instances(self):
            pass
            for i in range(len(self.prop)):
                pass
                self.prop[i]._fetch_instances()



        def _write__seq(self, io=None):
            super(Xfs.ObjectData, self)._write__seq(io)
            self._io.write_u4le(self.dti)
            self._io.write_bits_int_le(15, self.prop_num)
            self._io.write_bits_int_le(1, int(self.init))
            self._io.write_u2le(self.reserved)
            for i in range(len(self.prop)):
                pass
                self.prop[i]._write__seq(self._io)



        def _check(self):
            pass
            if (len(self.prop) != self.prop_num):
                raise kaitaistruct.ConsistencyError(u"prop", len(self.prop), self.prop_num)
            for i in range(len(self.prop)):
                pass
                if self.prop[i]._root != self._root:
                    raise kaitaistruct.ConsistencyError(u"prop", self.prop[i]._root, self._root)
                if self.prop[i]._parent != self:
                    raise kaitaistruct.ConsistencyError(u"prop", self.prop[i]._parent, self)



    class MtProperty(ReadWriteKaitaiStruct):
        def __init__(self, _io=None, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root
            self._should_write_name = False
            self.name__to_write = True

        def _read(self):
            self.name_ofs = self._io.read_u4le()
            self.type = self._io.read_u1()
            self.attr = self._io.read_u1()
            self.bytes = self._io.read_bits_int_le(15)
            self.disable = self._io.read_bits_int_le(1) != 0
            self.getter = self._io.read_u4le()
            self.getcount = self._io.read_u4le()
            self.setter = self._io.read_u4le()
            self.setcount = self._io.read_u4le()


        def _fetch_instances(self):
            pass
            _ = self.name


        def _write__seq(self, io=None):
            super(Xfs.MtProperty, self)._write__seq(io)
            self._should_write_name = self.name__to_write
            self._io.write_u4le(self.name_ofs)
            self._io.write_u1(self.type)
            self._io.write_u1(self.attr)
            self._io.write_bits_int_le(15, self.bytes)
            self._io.write_bits_int_le(1, int(self.disable))
            self._io.write_u4le(self.getter)
            self._io.write_u4le(self.getcount)
            self._io.write_u4le(self.setter)
            self._io.write_u4le(self.setcount)


        def _check(self):
            pass

        @property
        def name(self):
            if self._should_write_name:
                self._write_name()
            if hasattr(self, '_m_name'):
                return self._m_name

            _pos = self._io.pos()
            self._io.seek((self.name_ofs + 16))
            self._m_name = (self._io.read_bytes_term(0, False, True, True)).decode("UTF-8")
            self._io.seek(_pos)
            return getattr(self, '_m_name', None)

        @name.setter
        def name(self, v):
            self._m_name = v

        def _write_name(self):
            self._should_write_name = False
            _pos = self._io.pos()
            self._io.seek((self.name_ofs + 16))
            self._io.write_bytes((self.name).encode(u"UTF-8"))
            self._io.write_u1(0)
            self._io.seek(_pos)


        def _check_name(self):
            pass
            if (KaitaiStream.byte_array_index_of((self.name).encode(u"UTF-8"), 0) != -1):
                raise kaitaistruct.ConsistencyError(u"name", KaitaiStream.byte_array_index_of((self.name).encode(u"UTF-8"), 0), -1)

        @property
        def parent_index(self):
            if hasattr(self, '_m_parent_index'):
                return self._m_parent_index

            self._m_parent_index = self._parent._parent.i
            return getattr(self, '_m_parent_index', None)

        def _invalidate_parent_index(self):
            del self._m_parent_index

    @property
    def objects(self):
        if self._should_write_objects:
            self._write_objects()
        if hasattr(self, '_m_objects'):
            return self._m_objects

        self._m_objects = []
        for i in range(self.header.object_num):
            _t__m_objects = Xfs.Obj(i, self._io, self, self._root)
            _t__m_objects._read()
            self._m_objects.append(_t__m_objects)

        return getattr(self, '_m_objects', None)

    @objects.setter
    def objects(self, v):
        self._m_objects = v

    def _write_objects(self):
        self._should_write_objects = False
        for i in range(len(self._m_objects)):
            pass
            self.objects[i]._write__seq(self._io)



    def _check_objects(self):
        pass
        if (len(self.objects) != self.header.object_num):
            raise kaitaistruct.ConsistencyError(u"objects", len(self.objects), self.header.object_num)
        for i in range(len(self._m_objects)):
            pass
            if self.objects[i]._root != self._root:
                raise kaitaistruct.ConsistencyError(u"objects", self.objects[i]._root, self._root)
            if self.objects[i]._parent != self:
                raise kaitaistruct.ConsistencyError(u"objects", self.objects[i]._parent, self)
            if (self.objects[i].i != i):
                raise kaitaistruct.ConsistencyError(u"objects", self.objects[i].i, i)


    @property
    def data_buffer(self):
        if self._should_write_data_buffer:
            self._write_data_buffer()
        if hasattr(self, '_m_data_buffer'):
            return self._m_data_buffer

        _pos = self._io.pos()
        self._io.seek((self.header.data_size + 16))
        self._m_data_buffer = self._io.read_bytes_full()
        self._io.seek(_pos)
        return getattr(self, '_m_data_buffer', None)

    @data_buffer.setter
    def data_buffer(self, v):
        self._m_data_buffer = v

    def _write_data_buffer(self):
        self._should_write_data_buffer = False
        _pos = self._io.pos()
        self._io.seek((self.header.data_size + 16))
        self._io.write_bytes(self.data_buffer)
        if not self._io.is_eof():
            raise kaitaistruct.ConsistencyError(u"data_buffer", self._io.size() - self._io.pos(), 0)
        self._io.seek(_pos)


    def _check_data_buffer(self):
        pass


