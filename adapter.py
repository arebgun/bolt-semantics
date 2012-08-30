from planar import Vec2, BoundingBox
import numpy as np
from cluster_util import PhysicalObject
import SceneEval
import landmark


objects = []
def adapt(scene):
    '''takes a scene object and returns a list of lists of objects that form groups'''
    landmarkDict = dict()
    for l in scene.landmarks:
        landmarkDict[scene.landmarks[l].uuid]=scene.landmarks[l]
        o =PhysicalObject(scene.landmarks[l].uuid,
                       np.array(scene.landmarks[l].representation.middle),
                        np.array(scene.landmarks[l].representation.rect.min_point),
                        np.array(scene.landmarks[l].representation.rect.max_point),scene.landmarks[l].uuid)
        objects.append(o)
    results = SceneEval.sceneEval(objects)
    for i in results:
        listOfLandmarksInGroup = []
        for member in i:
            print member
            listOfLandmarksInGroup.append(landmarkDict.get(member))
        group = landmark.GroupRectangleRepresentation(listOfLandmarksInGroup)
    return  results

