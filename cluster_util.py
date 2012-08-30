from collections import namedtuple
#from bwdb import *
import numpy as np
from uuid import uuid4
import math
from planar import BoundingBox,Vec2,Polygon
import landmark


def totuple(a):
    '''converts nested iterables into tuples'''
    try:
        return tuple(totuple(i) for i in a)
    except TypeError:
        return a
    
class PhysicalObject:
    def __init__(self,id,position,bbmin,bbmax):  
        self.id = id
        self.position = position
        self.bbmin = bbmin
        self.bbmax = bbmax
        self.uuid = uuid4()
        self.listOfFields = [self.id,self.position,self.bbmin,self.bbmax]
    def __iter__(self):
        for i in self.listOfFields:
            yield i
    
#PhysicalObject = namedtuple('physicalObject', ['id', 'position', 'bbmin', 'bbmax'])  
ClusterParams = namedtuple("ClusterParams",['chain_distance_limit', 'angle_limit', 'min_line_length',
               'anglevar_weight', 'distvar_weight','dist_weight',
               'allow_intersection','beam_width','attempt_dnc'])
#GroupAttributes = namedtuple('groupAttributes',['cost','type','density'])

class successorTuple:
    def __init__(self,cost,members,uuid):  
        self.cost=cost
        self.members = members
        self.uuid = uuid
        self.listOfFields = [self.cost,self.members,self.uuid]
    def __iter__(self):
        for i in self.listOfFields:
            yield i
    
    
def create_distance_matrix(data):
    BoundingBoxes = convert_to_bboxes(data)
    distance_array=[]
    for i in BoundingBoxes:
        row = []
        for j in BoundingBoxes:
            row.append(landmark.bb_to_bb_distance(i,j))
        distance_array.append(row)
    return distance_array

def convex_hull(data):
    BoundingBoxes = convert_to_bboxes(data)
    points = map(lambda x: x.center,BoundingBoxes)
    return points
    
def area(p):
    return 0.5 * abs(sum(x0*y1 - x1*y0
                         for ((x0, y0), (x1, y1)) in segments(p)))

def segments(p):
    return zip(p, p[1:] + [p[0]])
    
        
def convert_to_bboxes(data):
    BoundingBoxes = []
    for i in data:
        minvec = Vec2(i.bbmin[0],i.bbmin[1])
        maxvec = Vec2(i.bbmax[0],i.bbmax[1])
        BoundingBoxes.append(BoundingBox((minvec,maxvec)))
    return BoundingBoxes
        
def findDistance(vector1,vector2):
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)
    '''euclidian distance between 2 points'''
    return np.round(math.sqrt(np.sum(np.square(vector2-vector1))),3) 

def findAngle(vector1, vector2):
    '''difference between two vectors, in radians'''
    preArc=np.dot(vector1, vector2) / np.linalg.norm(vector1) / np.linalg.norm(vector2)
    return np.arccos(np.round(preArc, 5))

def find_pairs(l):
    '''returns a list of all possible pairings of list elements'''
    pairs = []
    for i in range(len(l)):
        for j in range(len(l))[i + 1:]:
            pairs.append((l[i], l[j]))
    return pairs

class Bundle(object):
    def __init__(self,members,cost,uuid=-1):
        self.members = members
        self.cost = cost
        self.cardinality = len(members)
        if uuid == -1:
            self.uuid = uuid4()
        else: self.uuid = uuid
    def __getitem__(self,item):
        return self.members[item]
    def __iter__(self):
        for i in self.members:
            yield i
    def __len__(self):
        return len(self.members)
        
class LineBundle(Bundle):
    def __init__(self,members,cost):
        self.bundleType='line'
        super(LineBundle,self).__init__(members,cost)
        
class SingletonBundle(Bundle):
    def __init__(self,members,cost,uuid):
        self.bundleType='singleton'
        super(SingletonBundle,self).__init__(members,cost,uuid)
        
class GroupBundle(Bundle):
    def __init__(self,members,cost):
        self.bundleType='group'
        super(GroupBundle,self).__init__(members,cost)
        

