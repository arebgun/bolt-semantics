'''
Created on Jul 5, 2012

@author: colinwinslow
'''

#tiny change

import numpy as np

from scipy.spatial import distance
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
import cluster_util
from planar import Vec2,BoundingBox
import landmark


def clustercost(data):
    #    data is a tuple of two dictionaries: core cluster data first, then larger and more permissive clusters\
    # this func needs to return a unified list of possible clusters using both dictionaries in the style of the chain finder function
    # quick and dirty:

    smallClusters = []
    bigClusters = []

    #cores
    for i in data[0].viewvalues():
        corecluster=cluster_util.GroupBundle(i,len(i)*.8)
        smallClusters.append(corecluster)
    for i in data[1].viewvalues():
        bigcluster = cluster_util.GroupBundle(i,len(i)*.8)
        bigClusters.append(bigcluster)

    return (smallClusters,bigClusters)

    #cores+fringes



def dbscan(data):
    X,ids,bbmin,bbmax = zip(*data)
    distance_array=cluster_util.create_distance_matrix(data)

    D = distance.squareform(distance.pdist(X))
    
    S = 1 - (distance_array / np.max(distance_array))
    db = DBSCAN(min_samples=4).fit(S)
    core_samples = db.core_sample_indices_
    labels = db.labels_
    clusterlist = zip(labels, ids)
    shortclusterlist = zip(labels,ids)

    fringedict = dict()
    coredict = dict()

    for i in core_samples:
        ikey = int(clusterlist[i][0])
        ival = clusterlist[i][1]
        try:
            coredict[ikey].append(ival)
            fringedict[ikey].append(ival)
        except:
            coredict[ikey]=[]
            fringedict[ikey]=[]
            coredict[ikey].append(ival)
            fringedict[ikey].append(ival)
        shortclusterlist.remove(clusterlist[i])

    for i in shortclusterlist:
        try:
            fringedict[int(i[0])].append(i[1])
        except:
            fringedict[int(i[0])]=[]
            fringedict[int(i[0])].append(i[1])
    return (coredict,fringedict)
