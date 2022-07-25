from scipy.spatial import distance
import operator
import json
import numpy as np
import sys
import math
import argparse

parser = argparse.ArgumentParser(description='Ranking groups')
parser.add_argument('--groups' , help = 'path to groups')
parser.add_argument('--ef' , help = 'path to reviewer embeddings')
parser.add_argument('--rankedgroups' , help = 'path to ranked groups')

args = parser.parse_args()

class Groups:
    def __init__(self,users,prods,score,scoregt,id):
        self.users=users
        self.prods=prods
        self.score=score
        self.scoregt=scoregt
        self.id=id

    def __lt__(self, other):
        return len(self.users) < len(other.users)

c=0
groups=set()
grps={}
grpmapping={}
avggrpsize=0
size=0
with open(args.groups, 'r') as fp:
    finalgrps = json.load(fp)

filee=open(args.ef,'r')
mapping={}
c=0
for f in filee:
	c=c+1
	if c==1:
		continue
	fsplit=f.strip().split(" ")
	if fsplit[0] not in mapping:
		mapping[int(fsplit[0])]=map(float, fsplit[1:])
		emb_size=len(fsplit[1:])
filee.close()


userset=set()
gtscore={}
size={}
grpusers={}
for g1 in finalgrps:
	finalgrps[g1]['users']=map(int,finalgrps[g1]['users'])
	finalgrps[g1]['prods']=map(int,finalgrps[g1]['prods'])

	group=Groups(finalgrps[g1]['users'],finalgrps[g1]['prods'],finalgrps[g1]['fakegt'],finalgrps[g1]['scoregt'],finalgrps[g1]['id'])
	if len(finalgrps[g1]['users']) not in size:
		size[len(finalgrps[g1]['users'])]=0
	size[len(finalgrps[g1]['users'])]=size[len(finalgrps[g1]['users'])]+1

	groups.add(group)

	grpmapping[finalgrps[g1]['id']]=group
	if finalgrps[g1]['id'] not in grpusers:
	    grpusers[finalgrps[g1]['id']]=finalgrps[g1]['users']

	avggrpsize=avggrpsize+len(finalgrps[g1]['users'])


r_gt=[]
avggrpsize=avggrpsize/(len(groups)*1.0)
score={}

def density():
	for gm in grpmapping:
		g=grpmapping[gm]
		avg=[0 for i in range(emb_size)]
		ans=0
		for u in g.users:
			if u in mapping:
				avg=[avg[i]+mapping[u][i] for i in range(emb_size)]

		avg=[(a*1.0)/len(g.users) for a in avg]
		for u in g.users:
			if u in mapping:
				ans=ans+distance.euclidean(mapping[u], avg)
		if gm not in score:
			score[gm]=ans/(1.0*len(g.users))
	sorted_score=sorted(score.items(), key=operator.itemgetter(1))
	return sorted_score
			
def rank():
	sorted_score=density()
	filew=open(args.rankedgroups,'w')
	for grp in sorted_score:
		filew.write(str(grp[0])+"\n")
	filew.close()
	
rank()
print 'end'
