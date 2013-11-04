#!/usr/bin/env python

import sys
import numpy as np
from collections import namedtuple, defaultdict

sys.path.insert(1,"..")
from myrandom import random
choice = random.choice
from landmark import Landmark, ObjectClass, Color
from representation import PointRepresentation
from itertools import product
from copy import deepcopy
from utils import categorical_sample
# from new_relation import *
from intermediate_relations import *

import pprint
pp = pprint.PrettyPrinter(indent=4)

Semantic = namedtuple('Semantic', ['perspective', 'relation', 'landmark'])

class Teacher(object):

    relation_set = [SomewhatFarFrom,
                    FarFrom,
                    VeryFarFrom,
                    SomewhatNearTo,
                    NearTo,
                    VeryNearTo,
                    On,
                    InFront,
                    SomewhatFarInFront,
                    FarInFront,
                    VeryFarInFront,
                    Behind,
                    SomewhatFarBehind,
                    FarBehind,
                    VeryFarBehind,
                    LeftOf,
                    SomewhatFarLeftOf,
                    FarLeftOf,
                    VeryFarLeftOf,
                    RightOf,
                    SomewhatFarRightOf,
                    FarRightOf,
                    VeryFarRightOf]

    class_to_words = {
        ObjectClass.TABLE:    {'N' : ['table']},
        ObjectClass.CHAIR:    {'N' : ['chair']},
        ObjectClass.CUP:      {'N' : ['cup']},
        ObjectClass.BOTTLE:   {'N' : ['bottle']},
        ObjectClass.PRISM:    {'N' : ['prism', 'triangle']},
        ObjectClass.BOX:      {'N' : ['box','rectangle','block']},
        ObjectClass.CYLINDER: {'N' : ['cylinder']},
        ObjectClass.SPHERE:   {'N' : ['sphere']},
        Color.RED:            {'A' : ['red']},
        Color.GREEN:          {'A' : ['green']},
        Color.PURPLE:         {'A' : ['purple']},
        Color.BLUE:           {'A' : ['blue']},
        Color.PINK:           {'A' : ['pink']},
        Color.ORANGE:         {'A' : ['orange']},
        Color.YELLOW:         {'A' : ['yellow']},
        Color.BLACK:          {'A' : ['black']},
        Color.WHITE:          {'A' : ['white']},
        Landmark.EDGE:     {'N' : ['edge']},
        Landmark.EDGE+Landmark.LINE:     {'N' : ['edge']},
        Landmark.EDGE+Landmark.SURFACE:     {'N' : ['edge']},
        Landmark.CORNER:   {'N' : ['corner']},
        Landmark.CORNER+Landmark.POINT:   {'N' : ['corner']},
        Landmark.CORNER+Landmark.SURFACE:   {'N' : ['corner']},
        Landmark.MIDDLE:   {'N' : ['middle']},
        Landmark.MIDDLE+Landmark.POINT:   {'N' : ['middle']},
        Landmark.MIDDLE+Landmark.SURFACE:   {'N' : ['middle']},
        Landmark.HALF:     {'N' : ['half']},
        Landmark.END:      {'N' : ['end']},
        Landmark.SIDE:     {'N' : ['side']},
        Landmark.LINE:     {'N' : ['line']},
        Landmark.POINT:    {'N' : ['point']},
        FromRelation:      {'P' : ['from']},
        ToRelation:        {'P' : ['to']},
        OnRelation:        {'P' : ['on','in']},
        InFrontRelation:   {'P' : ['in front of'], 'A' : ['front', 'near']},
        BehindRelation:    {'P' : ['behind'], 'A' : ['back', 'far']},
        LeftRelation:      {'P' : ['to the left of'], 'A' : ['left']},
        RightRelation:     {'P' : ['to the right of'], 'A' : ['right']},
        Degree.NONE:       {'R' : ['']},
        Degree.SOMEWHAT:   {'R' : ['somewhat']},
        Degree.VERY:       {'R' : ['very']},
        Distance.FAR:   {'A' : ['far']},
        Distance.NEAR:  {'A' : ['near', 'close']},
    }

    scene_sorted_meaning_lists = {}
    scene_object_meaning_applicabilities = {}
    scene_object_meaning_scores = {}

    def __init__(self, location):
        self.set_location(location)

    def set_location(self, location):
        self.location = location
        
    def get_head_on_viewpoint(self, landmark):
        axes = landmark.get_primary_axes()
        if len(axes) > 0:
            axis = axes[ np.argmin([axis.distance_to(self.location) for axis in axes]) ]
            return axis.project(self.location)
        else:
            print "Not getting head on viewpoint!!!"
            return self.location

    def get_sorted_meaning_lists(self, scene):

        if scene not in self.scene_sorted_meaning_lists:

            landmarks = self.get_landmarks(scene)
            object_landmarks = self.get_object_landmarks(scene)

            object_meaning_applicabilities = defaultdict(dict)
            self.scene_object_meaning_applicabilities[scene] = defaultdict(dict)

            # for object1 in object_landmarks:
            #     for object2 in object_landmarks:
            #         print object1, object2, \
            #                 object1.distance_to(object2.representation)


            for object_landmark in object_landmarks:
                different_landmarks = landmarks[:]
                different_landmarks.remove(object_landmark)
                for landmark in different_landmarks:
                    # print 'location', self.location
                    # print 'center', landmark.representation.middle
                    perspective = self.get_head_on_viewpoint(landmark)
                    # print 'perspective', perspective
                    for relation in self.relation_set:
                        sem = Semantic(perspective, relation, landmark)
                        app = relation.applicability(perspective, 
                                                     landmark, 
                                                     object_landmark)
                        # print 'trajector:',object_landmark
                        # print 'landmark:',landmark
                        # print 'relation:',relation
                        # print 'applicability:', app
                        # print
                        object_meaning_applicabilities[sem][object_landmark]=app
                        self.scene_object_meaning_applicabilities\
                        [scene][sem][object_landmark] = app
                    # raw_input()

            for meaning_dict in object_meaning_applicabilities.values():
                total = sum( meaning_dict.values() )
                if total != 0:
                    for obj_lmk in meaning_dict.keys():
                        meaning_dict[obj_lmk] *= meaning_dict[obj_lmk]/total

            sorted_meaning_lists = {}

            for m in object_meaning_applicabilities.keys():
                for obj_lmk in object_meaning_applicabilities[m].keys():
                    if obj_lmk not in sorted_meaning_lists:
                        sorted_meaning_lists[obj_lmk] = []
                    sorted_meaning_lists[obj_lmk].append( 
                        (object_meaning_applicabilities[m][obj_lmk], m) )
            for obj_lmk in sorted_meaning_lists.keys():
                sorted_meaning_lists[obj_lmk].sort(reverse=True)

            self.scene_sorted_meaning_lists[scene] = sorted_meaning_lists
            self.scene_object_meaning_scores[scene] = \
                                                object_meaning_applicabilities

        return self.scene_sorted_meaning_lists[scene]

    def get_applicability(self, scene, relation, landmark, trajector):
        self.get_sorted_meaning_lists(scene)
        applicabilities = self.scene_object_meaning_applicabilities[scene]
        perspective = self.get_head_on_viewpoint(landmark)
        sem = Semantic(perspective, relation, landmark)
        # print 'teacher.py:170',sem
        # print 'teacher.py:171',applicabilities[sem]
        return applicabilities[sem][trajector]

    def get_score(self, scene, relation, landmark, trajector):
        self.get_sorted_meaning_lists(scene)
        scores = self.scene_object_meaning_scores[scene]
        perspective = self.get_head_on_viewpoint(landmark)
        sem = Semantic(perspective, relation, landmark)
        # print 'teacher.py:179',sem
        # print 'teacher.py:180',scores[sem]
        return scores[sem][trajector]

    def sample_trajector(self, scene):
        obj_lmks = [lmk for lmk in scene.landmarks.values() 
                            if lmk.name != 'table']
        return choice(obj_lmks)

    def sample_meaning(self, scene, trajector):

        sorted_meaning_list = self.get_sorted_meaning_lists(scene)[trajector]
        scores, meanings = zip(*sorted_meaning_list)

        sample_index = categorical_sample(np.array(scores))
        sampled_meaning = meanings[ sample_index ]

        # pp.pprint(meaning)
        # d = self.scene_object_meaning_applicabilities[scene][meaning]
        # pp.pprint(d)
        # pp.pprint(meaning.landmark.representation.get_geometry())
        # for lmk in d.keys():
        #     pp.pprint(lmk)
        #     pp.pprint(lmk.representation.get_geometry())
        #     print
        
        # semantic_applicabilities = sorted(semantic_applicabilities)
        # applicabilities, semantics = zip(*semantic_applicabilities)
        
        return sampled_meaning

    @staticmethod
    def get_landmarks(scene):
        all_lmks = scene.landmarks.values() + \
                    scene.landmarks['table'].representation.landmarks.values()
        return all_lmks

    @staticmethod
    def get_object_landmarks(scene):
        return [lmk for lmk in scene.landmarks.values() if lmk.name != 'table']



    def get_landmark_description(self, perspective, landmark):
        noun = choice(self.class_to_words[landmark.object_class]['N']) + ' '
        desc = 'the' + ' '

        ori = color = nounclass = True

        if ori:
            ori_relations = [InFront, Behind, LeftOf, RightOf]

            if landmark.parent and landmark.parent.parent_landmark:
                middle_lmk = Landmark('', 
                                      PointRepresentation(
                                        landmark.parent.middle), 
                                      landmark.parent, 
                                      None)
                options = [type(rel) for rel in ori_relations
                           if rel.applicability(perspective, 
                                                middle_lmk,
                                                landmark) > 0.5]

                # par_lmk = landmark.parent.parent_landmark
                # if par_lmk.parent and par_lmk.parent.parent_landmark:
                #     par_middle_lmk = Landmark('', PointRepresentation(par_lmk.parent.middle), par_lmk.parent, None)
                #     trajector = Landmark('', PointRepresentation(par_lmk.representation.middle), None, None)
                #     par_options = OrientationRelationSet.get_applicable_relations(perspective, par_middle_lmk, trajector, use_distance=False)
                # else:
                #     par_options = []

                for option in options:
                    desc += choice( self.class_to_words[option]['A'] ) + ' '

        desc += (choice(self.class_to_words[landmark.color]['A']) \
                + ' ' if color and landmark.color else '') \
                + (noun if nounclass else '')

        if landmark.parent and landmark.parent.parent_landmark:
            p_desc = self.get_landmark_description(perspective, landmark.parent.parent_landmark)
            if p_desc:
                desc += 'of' + ' ' + p_desc

        return desc

    def get_relation_description(self, relation, delimit_chunks=False):
        desc = ''
        if hasattr(relation, 'measurement'):
            m = relation.measurement
            degree = choice(self.class_to_words[m.degree]['R'])
            distance = choice(self.class_to_words[m.distance_class]['A'])
            desc += degree   + ( ' ' if degree else '') + \
                    distance + ( ' ' if distance else '')
        return desc + choice(self.class_to_words[type(relation)]['P']) + ' '

    def describe_meaning(self, meaning):
        return self.get_relation_description(meaning.relation) + \
               self.get_landmark_description(meaning.perspective, meaning.landmark)

    def describe(self, scene, trajector):
        meaning = self.sample_meaning(scene, trajector)

        return self.describe_meaning(meaning)

    def describe_trajector(self, scene, trajector):
        perspective = self.get_head_on_viewpoint(trajector)
        return self.get_landmark_description(perspective, trajector)