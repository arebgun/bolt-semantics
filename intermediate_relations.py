import sys
sys.path.insert(1,"..")
from myrandom import random
choice = random.choice

# from myrandom import nprandom as random
# from numpy import array, zeros, maximum, logical_and as land, logical_not as lnot
import numpy as np
# from scipy.stats import norm
import scipy.stats as st
# from planar import Vec2, Affine
# from planar.line import LineSegment, Ray
import planar as pl
# from representation import PointRepresentation, SurfaceRepresentation
import representation as rep
# from itertools import product
# import itertools as it

# from numpy.testing import assert_allclose


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
        ps = st.norm.cdf(distances, mu * (mult ** sign), std)
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
           or isinstance(landmark.representation, rep.SurfaceRepresentation)):
            distance = landmark.distance_to(trajector.representation)
            return self.measurement.applicability(distance)
        else:
            return 0.0

    def applicabilities(self, perspective, landmark, point_array):
        distances = np.zeros( point_array.shape[0] )

        if isinstance(landmark.representation, rep.SurfaceRepresentation):
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
        return float(trajector.representation.overlap_fraction(
            landmark.representation))

    @staticmethod
    def applicabilities(self, perspective, landmark, point_array):
        contains = np.array(landmark.representation.contains_points(point_array),
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


def angle_diff(angles1, angle2):
    return np.abs((angles1-angle2+np.pi)%(2*np.pi)-np.pi)

def decay_envelope(x, mu, sigma):
    return np.exp(-angle_diff(x,mu)/(2*sigma))

class OrientationRelation(Relation):

    kappa = 6.66
    sigma = 8.0
    def __init__(self, orientation, degree=None):
        self.mu = np.radians(orientation)
        self.mu_vec = pl.Vec2.polar(orientation)
        if degree:
            self.measurement = Measurement(degree=degree, 
                                           distance_class=Distance.FAR)

    def applicability(self, perspective, landmark, trajector):

        if isinstance(landmark.representation, rep.SurfaceRepresentation):
            return 0.0

        p_ray = self.get_perspective_ray(perspective, landmark)
        # print 'p_ray',p_ray

        if landmark.parent is not None:
            projected = landmark.parent.project_point(
                                           trajector.representation.middle)
        else:
            projected = trajector.representation.middle

        p = projected-p_ray.anchor
        # print 'projected-p_ray.anchor', p
        # print 'p.angle',p.angle
        # print 'p_ray._direction.angle',p_ray._direction.angle
        angle = np.radians(p_ray.angle_to(p))
        # print 'angle', angle, np.degrees(angle)

        angle_norm = st.vonmises.pdf(self.mu, self.kappa, loc=self.mu)
        angle_applicability = st.vonmises.pdf(angle, self.kappa, loc=self.mu)/\
                              angle_norm
        # print 'angle_applicability',angle_applicability

        if hasattr(self,'measurement'):
            distance = landmark.distance_to_point(projected)
            angle_vec = pl.Vec2.polar(np.degrees(angle), length=distance)
            new_vec = self.mu_vec.project(angle_vec)
            distance = new_vec.length if new_vec.angle==self.mu_vec.angle else 0
            # print 'distance',distance
            distance_applicability = self.measurement.applicability(distance)
            # print 'distance_applicability', distance_applicability
            return distance_applicability*angle_applicability
        else:
            return angle_applicability
            
    # def applicabilities(self, perspective, landmark, point_array):

    #     if isinstance(landmark.representation, rep.SurfaceRepresentation):
    #         return np.zeros( point_array.shape[0] )

    #     p_ray = self.get_perspective_ray(perspective, 
    #                                      landmark)

    #     if landmark.parent is not None:
    #         projected_array = landmark.parent.project_points(point_array)
    #     else:
    #         projected_array = point_array

    #     angles=np.radians(p_ray.angle_to_points(projected_array, p_ray.anchor))
        
    #     angle_norm = st.vonmises.pdf(self.mu, self.kappa, loc=self.mu)
    #     angle_applicabilities=st.vonmises.pdf(angles, self.kappa, loc=self.mu)/\
    #                           angle_norm
        
    #     if hasattr(self,'measurement'):
    #         distances = landmark.distance_to_points(projected_array)
    #         return self.measurement.applicability(distances)*\
    #             angle_applicabilities
    #     else:
    #         return angle_applicabilities

    @staticmethod
    def get_perspective_ray(perspective, landmark):
        top_primary_axes = landmark.get_top_parent().get_primary_axes()

        our_axis = None
        for axis in top_primary_axes:
            # print 'axis',axis
            if axis.contains_point(perspective):
                our_axis = axis
        assert( our_axis != None )
        # print 'our_axis', our_axis

        new_axis = our_axis.parallel(landmark.representation.middle)
        new_perspective = new_axis.project(perspective)

        p_ray=pl.line.Ray.from_points([landmark.representation.middle, 
                                       new_perspective])

        return p_ray

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
        super(InFrontRelation, self).__init__(orientation=0.0, 
                                              degree=degree)


class BehindRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(BehindRelation, self).__init__(orientation=180.0, 
                                              degree=degree)


class LeftRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(LeftRelation, self).__init__(orientation=-90.0,
                                              degree=degree)


class RightRelation(OrientationRelation):
    def __init__(self, degree=None):
        super(RightRelation, self).__init__(orientation=90.0, 
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

