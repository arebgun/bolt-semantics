from planar import Vec2, BoundingBox
import numpy as np
from cluster_util import PhysicalObject
import SceneEval
import landmark


objects = []
def adapt(landmarks):
    '''takes a scene object and returns a list of lists of objects that form groups'''
    landmarkDict = dict()

    for l in landmarks:
        landmarkDict[l.uuid]=l
        o = PhysicalObject(l.uuid,
                           np.array(l.representation.middle),
                           np.array(l.representation.rect.min_point),
                           np.array(l.representation.rect.max_point),
                           l.uuid)
        objects.append(o)
        
    bundles = SceneEval.sceneEval(objects)

    for i in bundles:
       print i.convert(landmarkDict)

    results = [bundle.convert(landmarkDict) for bundle in bundles]
    return  results

