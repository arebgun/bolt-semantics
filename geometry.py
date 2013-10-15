from math import sqrt

from planar import Vec2
from planar import BoundingBox
from planar.line import LineSegment


# Let's pretend we're importing this from planar
class Circle(object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        rad_point = Vec2(radius,radius)
        self.bounding_box = BoundingBox([self.center - rad_point, self.center + rad_point])

    def distance_to_edge(self, point):
        return self.center.distance_to(point) - self.radius

    def distance_to(self, point):
        distance = self.distance_to_edge(point)
        return distance if distance >= 0 else 0

    def contains_point(self, point):
        return True if self.distance_to_edge(point) < 0 else False


def ccw(A,B,C):
    ccw = (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)
    return 1 if ccw > 0.0 else -1 if ccw < 0.0 else 0


def intersect(seg1,seg2):
    A,B = seg1.points
    C,D = seg2.points
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def pairwise(l):
    pairs = []
    for i in range(1, len(l)):
        pairs.append( (l[i-1], l[i]) )
    return pairs


def seg_to_seg_distance(seg1, seg2):
    if intersect(seg1,seg2):
        return 0
    else:
        dists = []
        dists.append( seg1.distance_to(
            +seg2.start) )
        dists.append( seg1.distance_to(seg2.end) )
        dists.append( seg2.distance_to(seg1.start) )
        dists.append( seg2.distance_to(seg1.end) )
        return min(dists)


def bb_to_bb_manhattan_distance(bb1, bb2):
    N = 2 # cardinality of points

    result = 0
    for i in range(N):
        delta = 0
        # print bb1.min_point[i], bb2.max_point[i], bb1.min_point[i] > bb2.max_point[i]
        # print bb2.min_point[i], bb1.max_point[i], bb2.min_point[i] > bb1.max_point[i]
        if bb1.min_point[i] > bb2.max_point[i]:
            delta = bb2.max_point[i] - bb1.min_point[i]
        elif bb2.min_point[i] > bb1.max_point[i]:
            delta = bb1.max_point[i] - bb2.min_point[i]

        result += delta * delta

    return result


def poly_to_edges(poly):
    edges = []
    for i in range(1, len(poly)):
        edges.append( LineSegment.from_points([poly[i-1],poly[i]]) )
    edges.append( LineSegment.from_points([poly[i],poly[0]]) )
    return edges


def poly_to_vec_distance(poly, vec):
    if poly.contains_point( vec ):
        return 0

    dists = []
    for edge in poly_to_edges(poly):
        dists.append( edge.distance_to(vec) )

    return min(dists)


def poly_to_seg_distance(poly, seg):
    dists = []

    for edge in poly_to_edges(poly):
        dists.append(  seg_to_seg_distance( edge, seg )  )

    return min(dists)


def bb_to_bb_distance(bb1, bb2):
    return sqrt(bb_to_bb_manhattan_distance(bb1,bb2))


def poly_to_poly_distance(poly1, poly2):
    dists = []
    for e1 in poly_to_edges(poly1):
        dists.append(poly_to_seg_distance(poly2, e1))
    return min(dists)
