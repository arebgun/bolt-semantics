#!/usr/bin/env python
from speaker import Speaker
from planar import Vec2, BoundingBox
from landmark import RectangleRepresentation, SurfaceRepresentation, Scene, Landmark
from random import random

if __name__ == '__main__':
    # poi = Vec2(float(sys.argv[1]), 0)
    # l = LineRepresentation()

    # f = l.get_line_features(poi)

    # print 'dist_start = {dist_start}, dist_end = {dist_end}, dist_mid = {dist_mid}'.format(**f)
    # print 'dir_start = {dir_start}, dir_end = {dir_end}, dir_mid = {dir_mid}'.format(**f)

    # print 'Distance from POI to Start landmark is %f' % l.landmarks['start'].distance_to(poi)
    # print 'Distance from POI to End landmark is %f' % l.landmarks['end'].distance_to(poi)
    # print 'Distance from POI to Mid landmark is %f' % l.landmarks['mid'].distance_to(poi)

    speaker = Speaker(Vec2(5.5,4.5))
    scene = Scene(3)

    table = Landmark('table',
                 RectangleRepresentation(rect=BoundingBox([Vec2(5,5), Vec2(6,7)]), descriptions=['table', 'table surface']),
                 None,
                 ['table', 'table surface'])

    obj1 = Landmark('obj1',
                 RectangleRepresentation(rect=BoundingBox([Vec2(5,5), Vec2(5.1,5.1)]), descriptions=['cup']),
                 None,
                 ['cup'])

    obj2 = Landmark('obj2',
                 RectangleRepresentation(rect=BoundingBox([Vec2(5.5,6), Vec2(5.6,6.1)]), descriptions=['bottle']),
                 None,
                 ['bottle'])

    obj3 = Landmark('obj3',
                 RectangleRepresentation(rect=BoundingBox([Vec2(4.5,4.5), Vec2(4.8,4.8)]), descriptions=['chair']),
                 None,
                 ['chair'])

    scene.add_landmark(table)
    scene.add_landmark(obj1)
    scene.add_landmark(obj2)
    scene.add_landmark(obj3)

    dozen = 12
    couple = 2
    for i in range(couple * dozen):
        location = Vec2(random()+5,random()*2+5)#Vec2(5.68, 5.59)##Vec2(5.3, 5.5)
        speaker.describe(location, scene)
    #speaker.demo(location, scene)
    # all_desc = speaker.get_all_descriptions(location, scene)

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
