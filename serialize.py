import sys

from planar import Vec2
from planar import BoundingBox
from planar import Polygon
from planar.line import LineSegment
from geometry import Circle

from landmark import Landmark
import representation


def vec2_to_dict(vec2):
    return {'x': vec2.x, 'y': vec2.y}

def vec2_from_dict(dikt):
    return Vec2(dikt['x'], dikt['y'])

def linesegment_to_dict(line):
    return {'points': [vec2_to_dict(p) for p in line.points]}

def linesegment_from_dict(dikt):
    return LineSegment.from_points([vec2_from_dict(v) for v in dikt['points']])

def circle_to_dict(circ):
    return {'center': vec2_to_dict(circ.center), 'radius': circ.radius}

def circle_from_dict(dikt):
    return Circle(vec2_from_dict(dikt['center']), dikt['radius'])

def bbox_to_dict(bbox):
    return {'min_point': vec2_to_dict(bbox.min_point), 'max_point': vec2_to_dict(bbox.max_point)}

def bbox_from_dict(dikt):
    return BoundingBox([vec2_from_dict(dikt['min_point']), vec2_from_dict(dikt['max_point'])])

def poly_to_dict(poly):
    return {'points': [vec2_to_dict(p) for p in poly.points]}

def poly_from_dict(dikt):
    return Polygon.from_points([vec2_from_dict(v) for v in dikt['points']])

def representation_from_dict(dikt):
    class_ = getattr(sys.modules['representation'], dikt['class'])
    return class_.from_dict(dikt)

def landmark_from_dict(dikt):
    name = dikt['name']
    repres = representation_from_dict(dikt['representation']) if dikt['representation'] else None
    parent = representation_from_dict(dikt['parent']) if dikt['parent'] else None
    object_class = dikt['object_class']
    color = dikt['color']

    return Landmark(name, repres, parent, object_class, color)
