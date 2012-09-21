from planar import Vec2
from planar import BoundingBox
from planar import Polygon
from planar.line import LineSegment
from planar.line import Line

import numpy as np
from landmark import Landmark

from geometry import (
    Circle,
    seg_to_seg_distance,
    poly_to_edges,
    poly_to_vec_distance,
    poly_to_seg_distance,
    bb_to_bb_distance,
    poly_to_poly_distance
)

class AbstractRepresentation(object):
    def __init__(self, alt_of=None):
        self.alt_representations = []
        self.parent_landmark = None
        self.landmarks = {}
        self.num_dim = -1
        self.alt_of = alt_of

    def get_primary_axes(self):
        raise NotImplementedError

    def get_alt_representations(self):
        result = self.alt_representations

        for al in self.alt_representations:
            result.extend(al.get_alt_representations())

        return result

    def get_points(self):
        raise NotImplementedError

    def project_point(self, point):
        if self.parent_landmark is None or self.parent_landmark.parent is None:
            return self.my_project_point(point)
        else:
            return self.parent_landmark.parent.project_point(point)

    def my_project_point(self, point):
        raise NotImplementedError

    def distance_to(self, rep):
        ''' Takes Representation, returns float '''
        raise NotImplementedError

    def get_landmarks(self, max_level=-1):
        if max_level == 0: return []
        result = self.landmarks.values()

        for landmark in self.landmarks.values():
            result.extend( landmark.representation.get_landmarks(max_level-1) )

        return result

    def contains(self, other):
        ''' Takes Representation, returns boolean '''
        raise NotImplementedError

    def contains_point(self, xy):
        raise NotImplementedError

class PointRepresentation(AbstractRepresentation):
    def __init__(self, point, alt_of=None):
        super(PointRepresentation, self).__init__(alt_of)
        self.location = point
        self.alt_representations = []
        self.landmarks = {}
        self.num_dim = 0
        self.middle = point

    def my_project_point(self, point):
        return Vec2(self.location.x, self.location.y)

    def distance_to(self, rep):
        geo = rep.get_geometry()
        if isinstance(geo, BoundingBox):
            return poly_to_vec_distance(geo.to_polygon(), self.location)
        elif isinstance(geo, Polygon):
            return poly_to_vec_distance(geo, self.location)
        else:
            return geo.distance_to(self.location)

    def distance_to_point(self, xy):
        return self.location.distance_to( xy )

    def contains(self, other):
        ''' If PointRepresentation return True if approx. equal.
            Return False if any other representation. '''
        if other.num_dim > self.num_dim: return False
        return self.location.almost_equals(other.location)

    def contains_point(self, xy):
        return self.location.almost_equals(xy)

    def get_points(self):
        return [self.location]

    def get_geometry(self):
        return self.location

    def get_primary_axes(self):
        return [Line(self.location, Vec2(1,0)), Line(self.location, Vec2(0,1))]


class LineRepresentation(AbstractRepresentation):
    def __init__(self, ratio=None, line=LineSegment.from_points([Vec2(0, 0), Vec2(1, 0)]), alt_of=None):
        super(LineRepresentation, self).__init__(alt_of)
        self.line = line
        # extend the LineSegment to include a bounding_box field, planar doesn't have that originally
        self.line.bounding_box = BoundingBox.from_points(self.line.points)
        self.num_dim = 1
        self.middle = line.mid
        self.alt_representations = [PointRepresentation(self.line.mid, self)]
        self.ratio_limit = 2


        if ratio is None or ratio >= self.ratio_limit:
            self.landmarks = {
                'start':  Landmark('start',  PointRepresentation(self.line.start), self, Landmark.END),
                'middle': Landmark('middle', PointRepresentation(self.line.mid),   self, Landmark.MIDDLE),
                'end':    Landmark('end',    PointRepresentation(self.line.end),   self, Landmark.END),
            }
        else:
            self.landmarks = {
                'start':  Landmark('start',  PointRepresentation(self.line.start), self, Landmark.SIDE),
                'end':    Landmark('end',    PointRepresentation(self.line.end),   self, Landmark.SIDE)
            }

    def my_project_point(self, point):
        return self.line.project(point)

    def distance_to(self, rep):
        geo = rep.get_geometry()
        if isinstance(geo,Vec2):
            return self.line.distance_to(geo)
        elif isinstance(geo,LineSegment):
            return seg_to_seg_distance(self.line, geo)
        elif isinstance(geo,BoundingBox):
            return poly_to_seg_distance(geo.to_polygon(), self.line)
        elif isinstance(geo,Polygon):
            return poly_to_seg_distance(geo, self.line)

    def distance_to_point(self, xy):
        return self.line.distance_to( xy )

    def contains(self, other):
        if other.num_dim > self.num_dim: return False

        # Point
        if other.num_dim == 0:
            return self.line.contains_point(other.location)
        # Line
        elif other.num_dim == 1:
            return self.line.contains_point(other.line.start) and self.line.contains_point(other.line.end)

    def contains_point(self, xy):
        return self.line.contains_point( xy )

    def get_geometry(self):
        return self.line

    def get_points(self):
        return [self.line.start,self.line.end]

    def get_primary_axes(self):
        return [self.line.line, self.line.line.perpendicular(self.line.mid)]

class CircleRepresentation(AbstractRepresentation):
    def __init__(self, circ, alt_of=None):
        self.circ = circ
        self.num_dim = 2
        self.middle = circ.center
        self.alt_representations = [PointRepresentation(self.middle, self)]

        self.landmarks = {
            'middle': Landmark('middle', PointRepresentation(self.middle), self, Landmark.MIDDLE)
        }

    def my_project_point(self, point):
        return point

    def distance_to(self, rep):
        geo = rep.get_geometry()
        if isinstance(geo,Vec2):
            return self.circ.distance_to(geo)
        elif isinstance(geo,LineSegment):
            distance = geo.distance_to(self.circ.center) - self.circ.radius
        elif isinstance(geo,BoundingBox):
            distance = poly_to_vec_distance(geo.to_polygon(), self.circ.center) - self.circ.radius
        elif isinstance(geo,Polygon):
            distance = poly_to_vec_distance(geo, self.circ.center) - self.circ.radius
        elif isinstance(geo,Circle):
            self.circ.distance_to(geo.center) - geo.radius
        return distance if distance > 0 else 0

    def distance_to_point(self, xy):
        return self.circ.distance_to( xy )

    def contains(self, other):
        if other.num_dim > self.num_dim: return False
        if other.num_dim == 0:
            return self.circ.contains_point(other.location)
        if other.num_dim == 1:
            return self.circ.contains_point(other.line.start) and self.circ.contains_point(other.line.end)
        if other.num_dim == 2:
            if isinstance(other,Circle):
                return True if self.circ.center.distance_to(other.circ.center) + other.circ.radius < self.circ.radius else False
            for p in other.get_points():
                if not self.circ.contains_point(p): return False
            return True

    def contains_point(self, xy):
        return self.circ.contains_point( xy )

    def get_geometry(self):
        return self.circ

class RectangleRepresentation(AbstractRepresentation):
    def __init__(self, rect=BoundingBox([Vec2(0, 0), Vec2(1, 2)]),
                 landmarks_to_get=['ll_corner','ur_corner','lr_corner','ul_corner','middle','l_edge','r_edge','n_edge','f_edge','l_surf','r_surf','n_surf','f_surf','m_surf'],
                 alt_of=None):
        super(RectangleRepresentation, self).__init__(alt_of)
        self.rect = rect
        self.num_dim = 2
        self.middle = rect.center
        vert_ratio = self.rect.height / self.rect.width
        horiz_ratio = self.rect.width / self.rect.height
        self.alt_representations = [LineRepresentation( horiz_ratio,
                                                        LineSegment.from_points([Vec2(self.rect.min_point.x, self.rect.center.y),
                                                                                 Vec2(self.rect.max_point.x, self.rect.center.y)],),
                                                        self),
                                    LineRepresentation( vert_ratio,
                                                        LineSegment.from_points([Vec2(self.rect.center.x, self.rect.min_point.y),
                                                                                 Vec2(self.rect.center.x, self.rect.max_point.y)]),
                                                        self)]

        lrc = Vec2(self.rect.min_point.x + self.rect.width, self.rect.min_point.y)
        ulc = Vec2(self.rect.max_point.x - self.rect.width, self.rect.max_point.y)

        landmark_constructors = {
                'll_corner': '''Landmark('ll_corner', PointRepresentation(self.rect.min_point), self, Landmark.CORNER)''',
                'ur_corner': '''Landmark('ur_corner', PointRepresentation(self.rect.max_point), self, Landmark.CORNER)''',
                'lr_corner': '''Landmark('lr_corner', PointRepresentation(lrc), self, Landmark.CORNER)''',
                'ul_corner': '''Landmark('ul_corner', PointRepresentation(ulc), self, Landmark.CORNER)''',
                'middle':    '''Landmark('middle',    PointRepresentation(self.rect.center), self, Landmark.MIDDLE)''',
                'l_edge':    '''Landmark('l_edge',    LineRepresentation(vert_ratio, LineSegment.from_points([self.rect.min_point, ulc])), self, Landmark.EDGE)''',
                'r_edge':    '''Landmark('r_edge',    LineRepresentation(vert_ratio, LineSegment.from_points([lrc, self.rect.max_point])), self, Landmark.EDGE)''',
                'n_edge':    '''Landmark('n_edge',    LineRepresentation(horiz_ratio, LineSegment.from_points([self.rect.min_point, lrc])), self, Landmark.EDGE)''',
                'f_edge':    '''Landmark('f_edge',    LineRepresentation(horiz_ratio, LineSegment.from_points([ulc, self.rect.max_point])), self, Landmark.EDGE)''',

                'l_surf':    '''Landmark('l_surf',    SurfaceRepresentation( BoundingBox([rect.min_point,
                                                                                       Vec2(rect.min_point.x+rect.width/2.0,
                                                                                            rect.max_point.y)]),
                                                                          landmarks_to_get=['ll_corner','ul_corner','l_edge']),
                                      self, Landmark.HALF)''',
                'r_surf':    '''Landmark('r_surf',    SurfaceRepresentation( BoundingBox([Vec2(rect.min_point.x+rect.width/2.0,
                                                                                            rect.min_point.y),
                                                                                       rect.max_point]),
                                                                          landmarks_to_get=['lr_corner','ur_corner','r_edge']),
                                      self, Landmark.HALF)''',
                'n_surf':    '''Landmark('n_surf',    SurfaceRepresentation( BoundingBox([rect.min_point,
                                                                                       Vec2(rect.max_point.x,
                                                                                            rect.min_point.y+rect.height/2.0)]),
                                                                          landmarks_to_get=['ll_corner','lr_corner','n_edge']),
                                      self, Landmark.HALF)''',
                'f_surf':    '''Landmark('f_surf',    SurfaceRepresentation( BoundingBox([Vec2(rect.min_point.x,
                                                                                            rect.min_point.y+rect.height/2.0),
                                                                                       rect.max_point]),
                                                                          landmarks_to_get=['ul_corner','ur_corner','f_edge']),
                                      self, Landmark.HALF)''',

                'm_surf':    '''Landmark('m_surf',    SurfaceRepresentation( BoundingBox([Vec2(rect.min_point.x+rect.width/4.0,
                                                                                            rect.min_point.y+rect.height/4.0),
                                                                                       Vec2(rect.max_point.x-rect.width/4.0,
                                                                                            rect.max_point.y-rect.height/4.0)])), self, Landmark.MIDDLE)''',
        }

        self.landmarks = {}
        for lmk_name in landmarks_to_get:
            if lmk_name in landmark_constructors:
                self.landmarks[lmk_name] = eval(landmark_constructors[lmk_name])

    def my_project_point(self, point):
        if self.contains_point( point ):
            return point
        else:
            edges = poly_to_edges(self.rect.to_polygon())
            min_dist = float('inf')
            for edge in edges:
                dist = edge.distance_to(point)
                if dist < min_dist:
                    min_dist = dist
                    closest = edge
            return closest.project(point)


    def distance_to(self, rep):
        geo = rep.get_geometry()
        if isinstance(geo,Vec2):
            return poly_to_vec_distance(self.rect.to_polygon(), geo)
        elif isinstance(geo,LineSegment):
            return poly_to_seg_distance(self.rect.to_polygon(), geo)
        elif isinstance(geo,BoundingBox):
            return bb_to_bb_distance(self.rect, geo)
        elif isinstance(geo,Polygon):
            return poly_to_poly_distance(self.rect.to_polygon(), geo)

    def distance_to_point(self, xy):
        return poly_to_vec_distance( self.rect.to_polygon(), xy )

    def contains(self, other):
        if other.num_dim > self.num_dim: return False
        if other.num_dim == 0:
            return self.rect.contains_point(other.location)
        if other.num_dim == 1:
            return self.rect.contains_point(other.line.start) and self.rect.contains_point(other.line.end)
        if other.num_dim == 2:
            for p in other.get_points():
                if not self.rect.contains_point(p): return False
            return True

    def contains_point(self, xy):
        return self.rect.contains_point( xy )

    def get_geometry(self):
        return self.rect

    def get_points(self):
        return list(self.rect.to_polygon())

    def get_primary_axes(self):
        return [Line.from_points([Vec2(self.rect.min_point.x, self.rect.center.y),
                                  Vec2(self.rect.max_point.x, self.rect.center.y)]),
                Line.from_points([Vec2(self.rect.center.x, self.rect.min_point.y),
                                  Vec2(self.rect.center.x, self.rect.max_point.y)])]


class PolygonRepresentation(AbstractRepresentation):
    def __init__(self, poly, alt_of=None):
        super(PolygonRepresentation, self).__init__(alt_of)
        self.poly = poly
        self.num_dim = 2
        self.middle = poly.centroid
        self.landmarks = {
            'middle': Landmark('middle', PointRepresentation(self.middle), self, Landmark.MIDDLE)
        }

    def my_project_point(self, point):
        return point

    def distance_to(self, rep):
        geo = rep.get_geometry()
        if isinstance(geo,Vec2):
            return poly_to_vec_distance(self.poly, geo)
        elif isinstance(geo,LineSegment):
            return poly_to_seg_distance(self.poly, geo)
        elif isinstance(geo,BoundingBox):
            return poly_to_poly_distance(self.poly, geo.to_polygon())
        elif isinstance(geo, Polygon):
            return poly_to_poly_distance(self.poly, geo)

    def distance_to_point(self, xy):
        return poly_to_vec_distance( self.poly, xy )

    def contains(self, other):
        if other.num_dim > self.num_dim: return False
        if other.num_dim == 0:
            return self.poly.contains_point(other.location)
        if other.num_dim == 1:
            return self.poly.contains_point(other.line.start) and self.poly.contains_point(other.line.end)
        if other.num_dim == 2:
            for p in other.get_points():
                if not self.poly.contains_point(p): return False
            return True

    def contains_point(self, xy):
        return self.poly.contains_point( xy )

    def get_geometry(self):
        return self.poly

    def get_points(self):
        return list(self.poly)

    def get_primary_axes(self):
        return []


class SurfaceRepresentation(RectangleRepresentation):
    def __init__(self, rect=BoundingBox([Vec2(0, 0), Vec2(1, 2)]), landmarks_to_get=[]):
        super(SurfaceRepresentation, self).__init__(rect, landmarks_to_get)
        self.alt_representations = []


class GroupLineRepresentation(LineRepresentation):
    def __init__(self, lmk_group, alt_of=None):
        centers = np.array([lmk.representation.middle for lmk in lmk_group])
        x = centers[:,0]
        y = centers[:,1]
        A = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(A, y)[0]
        lxy = zip(x, m*x + c)
        points = [Vec2(px,py) for px,py in sorted(lxy)]

        super(GroupLineRepresentation, self).__init__(line=LineSegment.from_points(points),alt_of=alt_of)

        sorted_idx = sorted(range(len(lxy)), key=lxy.__getitem__)
        self.landmark_group = [lmk_group[idx] for idx in sorted_idx]


class GroupRectangleRepresentation(RectangleRepresentation):
    def __init__(self, lmk_group, alt_of=None):
        shapes = [lmk.representation.get_geometry() for lmk in lmk_group]
        super(GroupRectangleRepresentation, self).__init__(rect=BoundingBox.from_shapes(shapes),
                                                           landmarks_to_get=['middle'],
                                                           alt_of=alt_of)
        self.alt_representations = []
        self.landmark_group = lmk_group

