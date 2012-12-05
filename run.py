#!/usr/bin/env python
from random import random
from planar import Vec2, BoundingBox
from speaker import Speaker
from scene import Scene
import serialize

from landmark import (
    Landmark,
    ObjectClass,
    Color
)

from representation import (
    PointRepresentation,
    RectangleRepresentation,
)

#from configurations import adapter

def randrange(lower,upper):
    width = upper-lower
    return random() * width + lower

def too_close(p1,p2):
    return (abs(p1[0] - p2[0]) <= 0.035) and (abs(p1[1] - p2[1]) <= 0.045)

def construct_training_scene(random=False):
    speaker = Speaker(Vec2(0,0))
    scene = Scene(3)

    table_ll = (-0.4,0.4)
    table_ur = (0.4,1.6)
    if random:
        x_range = (table_ll[0]+0.035, table_ur[0]-0.035)
        y_range = (table_ll[1]+0.045, table_ur[1]-0.045)
        centers = []
        for _ in range(5):
            condition = True
            while condition:
                new_point = (randrange(*x_range),randrange(*y_range))
                condition = (sum( [too_close(new_point,p) for p in centers] ) > 0)
            centers.append( new_point )
    else:
        centers = [(0.05, 0.9), (0.05, 0.7), (0, 0.55), (-0.3,0.7), (0.3,0.7)]

    table = Landmark('table',
                     RectangleRepresentation(rect=BoundingBox([Vec2(*table_ll), Vec2(*table_ur)])),
                     None,
                     ObjectClass.TABLE)

    obj1 = Landmark('green_cup',
                    RectangleRepresentation(rect=BoundingBox([Vec2(centers[0][0]-0.035,centers[0][1]-0.035),
                                                              Vec2(centers[0][0]+0.035,centers[0][1]+0.035)]), landmarks_to_get=[]),
                    None,
                    ObjectClass.CUP,
                    Color.GREEN)

    obj2 = Landmark('blue_cup',
                    RectangleRepresentation(rect=BoundingBox([Vec2(centers[1][0]-0.035,centers[1][1]-0.035), 
                                                              Vec2(centers[1][0]+0.035,centers[1][1]+0.035)]), landmarks_to_get=[]),
                    None,
                    ObjectClass.CUP,
                    Color.BLUE)

    obj3 = Landmark('pink_cup',
                    RectangleRepresentation(rect=BoundingBox([Vec2(centers[2][0]-0.035,centers[2][1]-0.035), 
                                                              Vec2(centers[2][0]+0.035,centers[2][1]+0.035)]), landmarks_to_get=[]),
                    None,
                    ObjectClass.CUP,
                    Color.PINK)

    obj4 = Landmark('purple_prism',
                    RectangleRepresentation(rect=BoundingBox([Vec2(centers[3][0]-0.035,centers[3][1]-0.045), 
                                                              Vec2(centers[3][0]+0.035,centers[3][1]+0.045)]), landmarks_to_get=[]),
                    None,
                    ObjectClass.PRISM,
                    Color.PURPLE)

    obj5 = Landmark('orange_prism',
                    RectangleRepresentation(rect=BoundingBox([Vec2(centers[4][0]-0.035,centers[4][1]-0.045), 
                                                              Vec2(centers[4][0]+0.035,centers[4][1]+0.045)]), landmarks_to_get=[]),
                    None,
                    ObjectClass.PRISM,
                    Color.ORANGE)

    # t_rep = table.to_dict()
    scene.add_landmark(table)
    # scene.add_landmark(serialize.landmark_from_dict(t_rep))

    for obj in (obj1, obj2, obj3, obj4, obj5):
        # o_rep = obj.to_dict()
        obj.representation.alt_representations = []
        scene.add_landmark(obj)
        # scene.add_landmark(serialize.landmark_from_dict(o_rep))

    return scene, speaker

if __name__ == '__main__':
    scene, speaker = construct_training_scene()

#    lmks = [lmk for lmk in scene.landmarks.values() if not lmk.name == 'table']
#    groups = adapter.adapt(lmks)
#
#    for i,g in enumerate(groups):
#        scene.add_landmark(Landmark('ol%d'%i, g, None, Landmark.LINE))

    #perspectives = [ Vec2(5.5,4.5), Vec2(6.5,6.0)]
    #speaker.talk_to_baby(scene, perspectives, how_many_each=10)

    dozen = 12
    couple = 1
    for i in range(couple * dozen):
        location = Landmark( 'point', PointRepresentation(Vec2(random()*0.8-0.4,random()*0.6+0.4)), None, Landmark.POINT)
        trajector = location#obj2
        speaker.describe(trajector, scene, True, 1)
        # speaker.get_all_meaning_descriptions(trajector, scene, 1)
    # location = Vec2(5.68, 5.59)##Vec2(5.3, 5.5)
    # speaker.demo(location, scene)
    # all_desc = speaker.get_all_descriptions(location, scene, 1)


    # for i in range(couple * dozen):
    #     speaker.communicate(scene, False)

    # for desc in all_desc:
    #     print desc

    # r = RectangleRepresentation(['table'])
    # lmk = r.landmarks['l_edge']
    # print lmk.get_description()
    # print lmk.representation.landmarks['end'].get_description()
    # print r.landmarks['ul_corner'].get_description()

    # print r.landmarks['ul_corner'].distance_to( Vec2(0,0) )

    # representations = [r]
    # representations.extend(r.get_alt_representations())

    # location = Vec2(0,0)
    # landmarks_distances = []
    # for representation in representations:
    #     for lmk in representation.get_landmarks():
    #         landmarks_distances.append([lmk, lmk.distance_to(location)])

    # print 'Distance from POI to LLCorner landmark is %f' % r.landmarks['ll_corner'].distance_to(poi)
    # print 'Distance from POI to URCorner landmark is %f' % r.landmarks['ur_corner'].distance_to(poi)
    # print 'Distance from POI to LRCorner landmark is %f' % r.landmarks['lr_corner'].distance_to(poi)
    # print 'Distance from POI to ULCorner landmark is %f' % r.landmarks['ul_corner'].distance_to(poi)
    # print 'Distance from POI to Center landmark is %f' % r.landmarks['center'].distance_to(poi)
    # print 'Distance from POI to LEdge landmark is %f' % r.landmarks['l_edge'].distance_to(poi)
    # print 'Distance from POI to REdge landmark is %f' % r.landmarks['r_edge'].distance_to(poi)
    # print 'Distance from POI to NEdge landmark is %f' % r.landmarks['n_edge'].distance_to(poi)
    # print 'Distance from POI to FEdge landmark is %f' % r.landmarks['f_edge'].distance_to(poi)
