from uuid import uuid4
import json

import sys
sys.path.insert(1,"..")
from myrandom import random
choice = random.choice

import numpy as np


class Color(object):
    BLACK = 'BLACK'
    BLUE = 'BLUE'
    GREEN = 'GREEN'
    ORANGE = 'ORANGE'
    PINK = 'PINK'
    PURPLE = 'PURPLE'
    RED = 'RED'
    TEAL = 'TEAL'
    WHITE = 'WHITE'
    YELLOW = 'YELLOW'

    all = [BLACK, BLUE, GREEN, ORANGE, PINK, PURPLE, RED, TEAL, WHITE, YELLOW]


class ObjectClass(object):
    TABLE = 'TABLE'
    CHAIR = 'CHAIR'
    CUP = 'CUP'
    BOTTLE = 'BOTTLE'
    PRISM= 'PRISM'
    BOX = 'BOX'
    CYLINDER = 'CYLINDER'
    SPHERE = 'SPHERE'

    all = [TABLE, CHAIR, CUP, BOTTLE, PRISM, BOX, CYLINDER, SPHERE]

class Landmark(object):
    EDGE = 'EDGE'
    CORNER = 'CORNER'
    MIDDLE = 'MIDDLE'
    HALF = 'HALF'
    END = 'END'
    SIDE = 'SIDE'
    LINE = 'LINE'
    POINT = 'POINT'
    SURFACE = 'SURFACE'

    all = [EDGE,CORNER,MIDDLE,HALF,END,SIDE,LINE,POINT]

    def __init__(self, name, representation, parent, object_class=None, color=None):
        self.name = name
        self.representation = representation
        self.parent = parent
        self.object_class = object_class
        self.color = color
        self.uuid = uuid4()
        self.ori_relations = set()

        self.representation.parent_landmark = self

        for alt_repr in representation.get_alt_representations():
            alt_repr.parent_landmark = self

    def to_dict(self):
        return {
            'name': self.name,
            'representation': self.representation.to_dict() if self.representation else None,
            'parent': self.parent.to_dict() if self.parent else None,
            'object_class': self.object_class,
            'color': self.color,
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def from_json(desc):
        od = json.loads(desc)
        return Landmark.from_dict(od)

    def get_primary_axes(self, perspective=None):
        return self.get_top_parent().get_primary_axes()

    def distance_to(self, rep):
        top_parent = self.get_top_parent()
        min_dist = float('inf')

        for p in rep.get_points():
            tpd = top_parent.distance_to_point(p)
            if self.parent: p = self.parent.project_point(p)
            d = self.representation.distance_to_point(p)
            d = np.sqrt( d*d + tpd*tpd )
            if d < min_dist: min_dist = d

        return min_dist

    def distance_to_point(self, p):
        top_parent = self.get_top_parent()
        tpd = top_parent.distance_to_point(p)
        if self.parent: p = self.parent.project_point(p)
        d = self.representation.distance_to_point(p)
        d = np.sqrt( d*d + tpd*tpd )
        return d

    def distance_to_points(self, ps):
        top_parent = self.get_top_parent()
        tpds = top_parent.distance_to_points(ps)

        if self.parent:
            ps = self.parent.project_points(ps)

        ds = self.representation.distance_to_points(ps)
        ds = np.sqrt( ds**2 + tpds**2)
        return ds

    def get_top_parent(self):
        top = self.parent
        if top is None: return self.representation
        if top.parent_landmark is None: self.representation
        return top.parent_landmark.get_top_parent()

    def get_ancestor_count(self):
        top = self.parent
        if top is None: return 0
        if top.parent_landmark is None: return 0
        return 1 + top.parent_landmark.get_ancestor_count()

    def fetch_landmark(self, uuid):
        # print 'Fetching ',uuid, '  My uuid: ',self.uuid
        if self.uuid == uuid:
            result = self
        else:
            result = None
            for representation in [self.representation] + self.representation.alt_representations:
                for landmark in representation.landmarks.values():
                    result = landmark.fetch_landmark(uuid)
                    if result:
                        return result
        return result

    def __repr__(self):
        return self.name+' '+str(self.color)+' '+str(self.object_class)

