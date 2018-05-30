# load data files
import sys
import os
import csv
import math
import igraph
from igraph import *
import matplotlib.pyplot as plt
import numpy
import hashlib as hlb

# Returns the Median of the list.
def Median(lst):
    return numpy.median(numpy.array(lst))
	
# Returns the feature list and takes graph as input
def GraphToWeightedList(g,pagerank):
	L = {}
	i = 0
	feature = 0
	for ver in g.vs():
		## Add a vertice to feature list
		L[feature] = pagerank[i]
		feature = feature+1
		## Add normalized pagerank for each incident edge to feature list
		incidentEdges = g.incident(ver)
		lenIncidentEdges = len(incidentEdges)
		for edge in incidentEdges:
			L[feature] = pagerank[i]/lenIncidentEdges
			feature = feature+1
		#print incidentEdges
		#break
		i = i+1
	return L
	pass

# Return finger print h from a high dimension vector L
def FingerPrint(L):
	#print len(L)
	h = [0 for x in range(32)]
	for feature in L:
		#randomInteger = int(random.getrandbits(32))
		#binary = bin(randomInteger)[2:].zfill(32)#"{0:32b}".format(randomInteger)
		# 32 bit random number
		b = getBinary(feature)
		#Calculate fingerprint of graph
		for i,bit in enumerate(b):
			if bit == '0':
				bit = '-1'
			h[i] = h[i] + (float(bit) * L[feature])
	binaryH = map(lambda x : 0 if x < 0 else 1,h)		
	#print len(h)
	#print binaryH
	return binaryH
	pass

#returns Binary of the random hash number
def getBinary(wi):
	binary = bin(int(hlb.md5(str(wi)).hexdigest(),16))
	return str(binary)[2:34]
	
# return hamming distance
def Hamming(h1,h2):
	return len([x for x, y in zip(h1, h2) if x == y])

# Returns SimHash of h1 and h2
def SimHash(h1,h2):
	return 1.0 - (Hamming(h1,h2)/32.0)
#Main funtion of the program
def main(argv):
	dataFolder = str(argv)
	##### Read Directory Information ######
	fileList = []
	timeSeries = []
	h = []
	#dataFolder = "datasets/autonomous/"
	if not os.path.exists(dataFolder):
		print "Invalid Directory"
		return
	print dataFolder
	fileList = os.listdir(dataFolder)
	fileList = sorted(fileList,key = lambda str :int(str.split("_")[0]))
	fileList = [dataFolder + files for files in fileList]
	#print fileList
	##### Read Graphs from text files ######
	## finger print for 1st file :
	g1 = igraph.Graph()
	g1 = g1.Read_Edgelist(fileList[0])
	g1PageRank = g1.pagerank()
	L1 = GraphToWeightedList(g1,g1PageRank)
	#h1 = FingerPrint(L1)
	h.append (FingerPrint(L1))
	for i in range(1,len(fileList)):
		# h1 is always presaved in List of List
		h1 = h[i-1]
		#igraph.plot(g1)
		g2 = igraph.Graph()
		g2 = g2.Read_Edgelist(fileList[i])
		g2PageRank = g2.pagerank()
		L2 = GraphToWeightedList(g2,g2PageRank)
		h2 = FingerPrint(L2)
		h.append(h2)
		simHash = SimHash(h1,h2)
		#print simHash
		timeSeries.append(simHash)
	# Create File to store timeseries
	f = open("timeseries.txt","w")
	for item in timeSeries:
  		f.write("%s\n" % item)
	#print timeSeries
	## Calculate Threshold ##
	sumMi = 0
	for i in range(1,len(timeSeries)):
		Mi = math.fabs(timeSeries[i] - timeSeries[i-1])
		sumMi = sumMi + Mi
	M = sumMi / (len(timeSeries) - 1)
	median = Median(timeSeries)
	print "Threshold = "
	print median - 3*M
	print median + 3*M
	x = range(len(timeSeries))
	uthreshold = [median + 3*M] * len(timeSeries)
	lthreshold = [median - 3*M] * len(timeSeries)
	
	## plots the timeseries graph
	plt.plot(x,timeSeries,'b',x,lthreshold,'r--',x,uthreshold,'r--')
	plt.show()
	#print len(g2PageRank)
	#print list(g2.vs())[0]
	#igraph.plot(g2)

if __name__ == "__main__":
	if(len(sys.argv) == 2):  
		main(sys.argv[1])
	else :
		print "Invalid no. of arguments"