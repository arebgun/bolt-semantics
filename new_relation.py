import sys
sys.path.insert(1,"..")
from myrandom import random
choice = random.choice

from myrandom import nprandom as random
from numpy import array, zeros, maximum, logical_and as land, logical_not as lnot
from scipy.stats import norm
from planar import Vec2, Affine
from planar.line import LineSegment, Ray
from representation import PointRepresentation, SurfaceRepresentation
from itertools import product

from numpy.testing import assert_allclose


class Relation(object):
    pass

class RelationSet(object):
    pass


class Degree(object):
    NONE     = 'DegreeNone'
    SOMEWHAT = 'DegreeSomewhat'
    VERY     = 'DegreeVery'

    all = [NONE, SOMEWHAT, VERY]
    
class Distance(object):
#    NONE = 'MeasurementNone'
    FAR  = 'MeasurementFar'
    NEAR = 'MeasurementNear'

    all = [FAR, NEAR]


class Measurement(object):

    distance_classes = {
#        Distance.NONE: (-100, 0.05, 1),
        Distance.FAR:  (0.55, 0.05, 1),
        Distance.NEAR: (0.15, 0.05, -1),
    }

    degree_classes = {
        Degree.NONE: 1,
        Degree.SOMEWHAT: 0.75,
        Degree.VERY: 1.5,
    }
    
    def __init__(self, degree, distance_class):
        self.degree = degree
        self.distance_class = distance_class
        
    def applicability(self, distance_s_):
        return self.get_applicability(distance_s_, 
                                      self.distance_class, 
                                      self.degree)

    @staticmethod
    def get_applicability(distances, distance_class, degree_class):
        mu,std,sign = Measurement.distance_classes[distance_class]
        mult = Measurement.degree_classes[degree_class]
        ps = norm.cdf(distances, mu * (mult ** sign), std)
        if sign < 0: ps = 1 - ps
        return ps
        
    def __repr__(self):
        return '<%s, %s>' % (self.degree, self.distance_class)
        
    def __hash__(self):
        return self.__repr__()


class DistanceRelation(Relation):
    def __init__(self, degree, distance_class):
        super(DistanceRelation, self).__init__()
        self.measurement = Measurement(degree, distance_class)

    def applicability(self, perspective, landmark, trajector):
        if not (landmark.representation.contains( trajector.representation )
           or isinstance(landmark.representation, SurfaceRepresentation)):
            distance = landmark.distance_to(trajector.representation)
            return self.measurement.applicability(distance)
        else:
            return 0.0

    def applicabilities(self, perspective, landmark, point_array):
        distances = zeros( point_array.shape[0] )

        if isinstance(landmark.representation, SurfaceRepresentation):
            return distances #return zeros

        distances = landmark.distance_to_points(point_array)
        return self.measurement.applicability(distances)

    def __repr__(self):
        return self.__class__.__name__ + ' ' + self.measurement.__repr__()

    def __hash__(self):
        return hash(self.__repr__())

    def __cmp__(self, other):
        return cmp(self.__hash__(), other.__hash__())
        

class ToRelation(DistanceRelation):
    def __init__(self, degree):
        super(ToRelation, self).__init__(degree, distance_class=Distance.NEAR)

class FromRelation(DistanceRelation):
    def __init__(self, degree):
        super(FromRelation, self).__init__(degree, distance_class=Distance.FAR)


class ContainmentRelation(Relation):
    def __init__(self):
        super(ContainmentRelation, self).__init__()

    @staticmethod
    def applicability(perspective, landmark, trajector):
        return float(landmark.representation.contains(trajector.representation))

    @staticmethod
    def applicabilities(self, perspective, landmark, point_array):
        contains = array(landmark.representation.contains_points(point_array),
                         dtype=float)
        return contains

    def __repr__(self):
        return self.__class__.__name__

    def __hash__(self):
        return hash(self.__repr__())

    def __cmp__(self, other):
        return cmp(self.__hash__(), other.__hash__())

class OnRelation(ContainmentRelation):
    def __init__(self):
        super(OnRelation, self).__init__()


class OrientationRelation(Relation):

    def __init__(self, orientation, degree=None):
        self.orientation = orientation
        if degree:
            self.measurement = Measurement(degree=degree, 
                                           distance_class=Distance.FAR)

    def applicability(self, perspective, landmark, trajector):

        if isinstance(landmark.representation, SurfaceRepresentation):
            return 0.0

        ori_ray = self.get_orientation_ray(self.orientation, 
                                           perspective, 
                                           landmark)

        # TODO make sure this works using .middle
        if landmark.parent is not None:
            point = landmark.parent.project_point(
                                                trajector.representation.middle)
        else:
            point = trajector.representation.middle
        projected = ori_ray.line.project(point)

        distance = ori_ray.start.distance_to(projected)
        
        if ori_ray.contains_point(projected) and not \
            landmark.representation.contains_point(projected):
            if hasattr(self,'measurement'):
                return self.measurement.applicability(distance)
            else:
                return 1.0
        else:
            return 0.0
            
    def applicabilities(self, perspective, landmark, point_array):

        if isinstance(landmark.representation, SurfaceRepresentation):
            return zeros( point_array.shape[0] )

        ori_ray = self.get_orientation_ray(self.orientation, 
                                           perspective, 
                                           landmark)
        projected_array = ori_ray.line.project_points(point_array)
        
        applies = array(land( self.ori_ray.contains_points(projected_array),
                              lnot( self.landmark.representation.
                                         contains_points(projected_array)) ), 
                        dtype=float)
        
        distances = ori_ray.start.distance_to_points(
                                       ori_ray.line.project_points(point_array))
        return self.measurement.applicability(distances)*applies

    @staticmethod
    def get_orientation_ray(orientation, perspective, landmark):

        standard_direction = Vec2(0,1)

        top_primary_axes = landmark.get_top_parent().get_primary_axes()

        our_axis = None
        for axis in top_primary_axes:
            if axis.contains_point(perspective):
                our_axis = axis
        assert( our_axis != None )

        new_axis = our_axis.parallel(landmark.representation.middle)
        new_perspective = new_axis.project(perspective)

        p_segment = LineSegment.from_points( [new_perspective, 
                                              landmark.representation.middle] )

        angle = standard_direction.angle_to(p_segment.vector)
        rotation = Affine.rotation(angle)
        o = [orientation]
        rotation.itransform(o)
        direction = o[0]
        ori_ray = Ray(p_segment.end, direction)

        return ori_ray

    def __repr__(self):
        return self.__class__.__name__ + \
                (' ' + self.measurement.__repr__() 
                    if hasattr(self,'measurement')
                    else '')

    def __hash__(self):
        return hash(self.__repr__())

    def __cmp__(self, other):
        return cmp(self.__hash__(), other.__hash__())


class InFrontRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(InFrontRelation, self).__init__(orientation=Vec2(0,-1), 
                                              degree=degree)


class BehindRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(BehindRelation, self).__init__(orientation=Vec2(0,1), 
                                              degree=degree)


class LeftRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(LeftRelation, self).__init__(orientation=Vec2(-1,0),
                                              degree=degree)


class RightRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(RightRelation, self).__init__(orientation=Vec2(1,0), 
                                              degree=degree)






SomewhatFarFrom = FromRelation(degree=Degree.SOMEWHAT)
FarFrom         = FromRelation(degree=Degree.NONE)
VeryFarFrom     = FromRelation(degree=Degree.VERY)

SomewhatNearTo = ToRelation(degree=Degree.SOMEWHAT)
NearTo         = ToRelation(degree=Degree.NONE)
VeryNearTo     = ToRelation(degree=Degree.VERY)

On = OnRelation()

InFront            = InFrontRelation()
SomewhatFarInFront = InFrontRelation(degree=Degree.SOMEWHAT)
FarInFront         = InFrontRelation(degree=Degree.NONE)
VeryFarInFront     = InFrontRelation(degree=Degree.VERY)

Behind            = BehindRelation()
SomewhatFarBehind = BehindRelation(degree=Degree.SOMEWHAT)
FarBehind         = BehindRelation(degree=Degree.NONE)
VeryFarBehind     = BehindRelation(degree=Degree.VERY)

LeftOf            = LeftRelation()
SomewhatFarLeftOf = LeftRelation(degree=Degree.SOMEWHAT)
FarLeftOf         = LeftRelation(degree=Degree.NONE)
VeryFarLeftOf     = LeftRelation(degree=Degree.VERY)

RightOf            = RightRelation()
SomewhatFarRightOf = RightRelation(degree=Degree.SOMEWHAT)
FarRightOf         = RightRelation(degree=Degree.NONE)
VeryFarRightOf     = RightRelation(degree=Degree.VERY)

