#!/usr/bin/env python
from automain import automain
from run import construct_training_scene
import numpy as np
from anchors import (CenterPointAnchor,
                     ConvexHullAnchor,
                     CenteredRayAnchor,
                     FrontedRayAnchor,
                     ShadowAnchor,
                     ConnectingLineAnchor,
                     BridgesAnchor)

class OrientationType(object):
    Intrinsic             = 'O_Intrinsic'
    Perspectival          = 'O_Perspectival'
    Extrinsic             = 'O_Extrinsic'
    ExtrinsicPerspectival = 'O_ExtrinsicPerspectival'

class FrontType(object):
    Intrinsic             = 'F_Intrinsic'
    Perspectival          = 'F_Perspectival'
    Extrinsic             = 'F_Extrinsic'
    ExtrinsicPerspectival = 'F_ExtrinsicPerspectival'

class OrientationAxes(object):

    def __init__(self):
        # angle in radians
        self.angle
        self.angleOrigin
        self.frontOrigin
        self.extrinsicOrientingLandmark
        self.perspective

    @property
    def semiAxes(self):
        raise NotImplementedError

class SemiAxis(object):
    def __init__(self):
        # angle in radians
        self.angle
        self.angleOrigin
        self.frontOrigin
        self.relativeDirection
        self.extrinsicOrientingLandmark
        self.perspective

class Measure(object):
    requirements = []
    def __init__(self, anchor):
        self.anchor = anchor

class Distance(Measure):
    def __call__(self, trajector):
        return self.anchor.distance_to( trajector )

class Angle(Measure):
    requirements = [ lambda x: hasattr(x, 'ends') and x.ends is not [] ]
    def __call__(self, anchor):
        pass

class MeasureFactory(object):
    measures = [Distance, Angle]

    def instantiate_measures(anchor):
        instances = []
        for measure in MeasureFactory.measures:
            if np.all( [req(anchor) for req in measure.requirements] ):
                instances.append( measure(anchor) )
        return instances


class SemanticThing:
    def __init__(self):
        self.anchoredMeasures = []
        self.math # = lambda x,y,z : 
        self.applicabilityFunction



def get_qualifying_axes(landmark, perspective, scene):

    axes = []

    axes.append( OrientationAxes.fromPerspective(landmark, perspective) )

    if landmark.intrinsicAxes is not None:
        if landmark.intrinsicAxes.frontOrigin == FrontType.Intrinsic:
            axes.append( landmark.intrinsicAxes )
        axes.append( landmark.intrinsicAxes.perspectivalFrontFrom( perspective ) )

    # Inherit axes from extrinsic landmarks
    for extrinsic_landmark in scene.landmarks:
        if extrinsic_landmark.contains( landmark ): # TODO better conditions

            new_axes = OrientationAxes.fromPerspective(extrinsic_landmark, perspective)
            axes.append( new_axes.bequeath() )

            if extrinsic_landmark.intrinsicAxes is not None:
                if extrinsic_landmark.intrinsicAxes.frontOrigin == FrontType.Intrinsic:
                    axes.append( extrinsic_landmark.intrinsicAxes.bequeath() )
                axes.append( extrinsic_landmark.intrinsicAxes.perspectivalFrontFrom( perspective ) )


def get_single_anchors(landmark, perspective, scene):
    pass

def get_double_anchors(landmarks, perspective, scene):
    pass


@automain
def main():
    
    scene, speaker = construct_training_scene()
    perspective = speaker.location

    anchors = []
    for i,landmark in enumerate(scene.landmarks.values()+
                                scene.groups.values()): #TODO add viewer to landmarks

        for anchorType in [CenterPointAnchor, ConvexHullAnchor]:
            # try:
            anchors.append( anchorType(landmarks=[landmark]) )
            # except AssertionError:
            #     pass

        for axis in get_qualifying_axes(landmark, perspective, scene):
            for semiAxis in axis.semiAxes:
                for anchorType in [CenteredRayAnchor,
                                   FrontedRayAnchor,
                                   ShadowAnchor]:
                    # try:
                    anchors.append( anchorType(landmarks=[landmark],
                                               semiAxis=semiAxis) )
                    # except AssertionError:
                    #     pass

        for second_landmark in (scene.landmarks.values()+
                                        scene.groups.values())[i:]:
            for anchorType in [ConnectingLineAnchor, BridgesAnchor]:
                # try:
                anchors.append( 
                    anchorType(landmarks=[landmark, second_landmark]) )
                # except AssertionError:
                #     pass

    anchoredMeasures = []
    for anchor in anchors:
        anchoredMeasures.extend( MeasureFactory.instantiate_measures(anchor) )

    #Now mathematical combinations