# from itertools import combinations


class Anchor(object):
    pass

#################
class PointAnchor(Anchor):
    def __init__(self, point):
        self.point = point

class CenterPointAnchor(PointAnchor):
    def __init__(self, landmarks):
        assert len(landmarks)==1
        assert hasattr(landmarks[0].representation, 'middle'), landmarks[0]
        super(CenterPointAnchor,self).__init__(landmarks[0].representation.middle)
        self.landmarks = landmarks

#################
class ConvexHullAnchor(Anchor):
    def __init__(self, landmarks):
        assert len(landmarks)==1
        assert hasattr(landmarks[0],'convex_hull')
        self.landmarks = landmarks


#################
class RayAnchor(Anchor):
    def __init__(self, end, direction):
        self.ends = [end]
        self.direction = direction

class CenteredRayAnchor(RayAnchor):
    def __init__(self, landmarks, semiAxis):
        assert len(landmarks)==1
        assert hasattr(landmarks[0].representation, 'middle'), landmarks[0]
        self.landmark = landmarks[0]
        super(CenteredRayAnchor,self).__init__(self.landmark.middle, 
                                               semiAxis.direction)
        self.landmarks = landmarks
        self.origin = ['semiAxis',
                       semiAxis.angleOrigin,
                       semiAxis.frontOrigin,
                       semiAxis.relativeDirection]

class FrontedRayAnchor(RayAnchor):
    def __init__(self, landmarks, semiAxis):
        assert len(landmarks)==1
        self.landmark = landmarks[0]
        super(FrontedRayAnchor,self).__init__(
            self.landmark.farthest_point(semiAxis.direction), 
            semiAxis.direction)
        self.landmarks = landmarks
        self.origin = ['semiAxis',
                       semiAxis.angleOrigin,
                       semiAxis.frontOrigin,
                       semiAxis.relativeDirection]


class ShadowAnchor(Anchor):
    def __init__(self, landmarks, semiAxis):
        assert len(landmarks)==1
        self.landmarks = landmarks
        self.origin = ['semiAxis',
               semiAxis.angleOrigin,
               semiAxis.frontOrigin,
               semiAxis.relativeDirection]


################
class LineSegmentAnchor(Anchor):
    def __init__(self, ends):
        assert len(ends)==2
        self.ends = ends

class ConnectingLineAnchor(LineSegmentAnchor):
    def __init__(self, landmarks):
        assert len(landmarks)==2
        assert hasattr(landmarks[0].representation, 'middle'), landmarks[0]
        assert hasattr(landmarks[1].representation, 'middle'), landmarks[1]
        super(ConnectingLineAnchor,self).__init__(landmarks[0].representation.middle,
                                                  landmarks[1].representation.middle)
        self.landmarks = landmarks


class BridgesAnchor(Anchor):
    def __init__(self, landmarks):
        assert len(landmarks)==2
        self.landmarks = landmarks


anchorTypes = [CenterPointAnchor,
               ConvexHullAnchor,
               CenteredRayAnchor,
               FrontedRayAnchor,
               ShadowAnchor,
               ConnectingLineAnchor,
               BridgesAnchor]

##################################
# class AnchorFactory(object):
    

#     def initAnchors(landmarks, N=2):

#         #Get all permutations of landmarks with self from 1 to N
#         # landmark_permutations = sum(map(combinations,range(1,N+1)),[])
#         pass


