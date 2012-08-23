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
    
    #need to change this to use IDs instead of coordinates.

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



def dbscan(data,distanceMatrix):
#    print "starting dbscan"
#    print "dbscan input:", data
    X,ids,bbmin,bbmax = zip(*data)
    S = 1 - (distanceMatrix / np.max(distanceMatrix))
    db = DBSCAN(min_samples=4).fit(S)
    core_samples = db.core_sample_indices_
    labels = db.labels_
    clusterlist = zip(labels, X)
    shortclusterlist = zip(labels,X)


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
#        print clusterlist[i]
        shortclusterlist.remove(clusterlist[i])

    for i in shortclusterlist:
        try:
            fringedict[int(i[0])].append(i[1])
        except:
            fringedict[int(i[0])]=[]
            fringedict[int(i[0])].append(i[1])
            
#    print "dbscan output", (coredict,fringedict)
    return (coredict,fringedict)
