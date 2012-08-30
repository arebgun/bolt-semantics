from planar import Vec2, BoundingBox
import numpy as np
from cluster_util import PhysicalObject
import SceneEval


objects = []
def adapt(scene):
    '''takes a scene object and returns a list of lists of objects that form groups'''
    for l in scene.landmarks:
        o =PhysicalObject(scene.landmarks[l].uuid,
                       np.array(scene.landmarks[l].representation.middle),
                        np.array(scene.landmarks[l].representation.rect.min_point),
                        np.array(scene.landmarks[l].representation.rect.max_point))
        objects.append(o)
    results = SceneEval.sceneEval(objects)
    print results
    return  results
