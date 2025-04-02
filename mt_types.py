from typing import Type

class XmlPropSerializer:
    def __init__(self):
        pass

    def read(self, src):
        for i in self.__annotations__:
            setattr(self, i, getattr(src, i))


class Float2(XmlPropSerializer):
    x: float
    y: float


class Float3(Float2):
    x: float
    y: float
    z: float


class Float4(Float3):
    x: float
    y: float
    z: float
    w: float

class Color(XmlPropSerializer):
    r: float
    g: float
    b: float
    a: float

class Vector3(XmlPropSerializer):
    x: float
    y: float
    z: float
    padding: float

class Vector4(Float4):
    pass

class Quaternion(Float4):
    pass

class Float3x3(XmlPropSerializer):
    r0: Float3
    r1: Float3
    r2: Float3

class Float4x4(XmlPropSerializer):
    r0: Float4
    r1: Float4
    r2: Float4
    r3: Float4

class Matrix(Float4x4):
    pass

class Float3x4(XmlPropSerializer):
    r0: Float4
    r1: Float4
    r2: Float4

class EaseCurve(XmlPropSerializer):
    p1: float
    p2: float

class Line(XmlPropSerializer): #TODO: reflect in template
    origin: Vector3
    dir: Vector3

class LineSegment(XmlPropSerializer):
    p1: Vector3
    p2: Vector3

class Ray(Line):
    pass

class Plane(XmlPropSerializer):
    normal: Float3
    dist: float

class Sphere(XmlPropSerializer):
    pos: Float3
    r: float

class Capsule(LineSegment):
    r: float

class AABB(XmlPropSerializer):
    minpos: Vector3
    maxpos: Vector3

class OBB(XmlPropSerializer):
    coord: Matrix
    extent: Vector3

class Cylinder(LineSegment):
    r: float
    pad: float

class Range(XmlPropSerializer):
    s: int
    r: int

class RangeF(XmlPropSerializer):
    s: float
    r: float

type_to_class = {
    0xF: Color,
    0x14: Vector3,
    0x15: Vector4,
    0x16: Quaternion,
    0x22: Float2,
    0x23: Float3,
    0x24: Float4,
    0x25: Float3x3,
    0x27: Matrix,  # Float4x4 is inherited by Matrix
    0x26: Float3x4,
    0x28: EaseCurve,
    0x29: Line,
    0x2A: LineSegment,
    0x2B: Ray,  # Line is inherited by Ray
    0x2C: Plane,
    0x2D: Sphere,
    0x2E: Capsule,
    0x2F: AABB,
    0x30: OBB,
    0x31: Cylinder,
    0x36: Range,
    0x37: RangeF,
}

type_to_class_name = {
    0xF: 'Color',
    0x22: "Float2",
    0x23: "Float3",
    0x24: "Float4",
    0x14: "Vector3",
    0x15: "Vector4",
    0x16: "Quaternion",
    0x25: "Float3x3",
    0x27: "Matrix",  # Float4x4 is inherited by Matrix
    0x26: "Float3x4",
    0x28: "EaseCurve",
    0x29: "Line",
    0x2A: "LineSegment",
    0x2B: "Ray",  # Line is inherited by Ray
    0x2C: "Plane",
    0x2D: "Sphere",
    0x2E: "Capsule",
    0x2F: "AABB",
    0x30: "OBB",
    0x31: "Cylinder",
    0x36: "Range",
    0x37: "RangeF"
}