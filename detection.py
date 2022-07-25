
import networkx as nx
import json
import sys
import time
from datetime import datetime
import operator
import argparse

parser = argparse.ArgumentParser(description='Detecting groups')
parser.add_argument('--metadata' , help = 'path to metadata') 
parser.add_argument('--rc' , help = 'path to reviewContent')
parser.add_argument('--dg' , help = 'path to detected groups')

args = parser.parse_args()

CC_mapper={}
class Review:
    def __init__(self,userid,useridmapped,prodid,prodidmapped,rating,label,date):
        self.userid=userid
        self.useridmapped=useridmapped
        self.prodid=prodid
        self.prodidmapped=prodidmapped
        self.rating=rating
        self.label=label
        self.date=date

    def __repr__(self):
        return '({},{})'.format(self.userid)
    
    def __hash__(self):
        return hash((self.userid))

    def __eq__(self, other):
        return self.userid== other.userid

    def __ne__(self, other):
        return not self.__eq__(other)
    
   

def isAdjacent(e1,e2):
    if e1[0]==e2[0] or e1[1]==e2[0] or e1[0]==e2[1] or e1[1]==e2[1]:
        return True
    return False

def degree(G,edge):
    return G.degree[edge[0]]+G.degree[edge[1]]-1

def canbeincluded(userset):
    if len(userset)==0:
        return 0
    union=set()
    intersection=allusers[list(userset)[0]]
    for u in userset:
        union=union.union(allusers[u])
        intersection=intersection.intersection(allusers[u])
        jaccard=len(intersection)/len(union)*1.0
        if jaccard>0.5:
            return 1
        return 0

text={}
textf=open(args.rc,'r')
for row in textf:

    userid=int(row.split("\t")[1].strip())
    prodid=int(row.split("\t")[0].strip())
    if userid not in text:
        text[userid]={}
    if prodid not in text[userid]:
        text[userid][prodid]=row.split("\t")[3].strip()


minn={}
d={}
fake=set()
filee=open(args.metadata,'r')
for f in filee:
    
    fsplit=f.split("\t")
    
    userid=fsplit[0]
    prodid=fsplit[1]
    rating=int(round(float(fsplit[2])))  
    label=fsplit[3]
   
    if int(label)==-1:
        fake.add(userid)

    date=fsplit[4].strip()
    if prodid not in d:
        minn[prodid]=0
        d[prodid]=datetime.strptime(date, "%Y-%m-%d").date()
      
    minn[prodid]=datetime.strptime(date, "%Y-%m-%d").date()
    if minn[prodid]<d[prodid]:
        d[prodid]=minn[prodid]       
filee.close()


G = nx.Graph()
reviewsperproddata={}
nodedetails={}
prodlist={}
dictprod={}
dictprodr={}
mainnodelist=set()
count=0
filee=open(args.metadata,'r')
for f in filee:
    
    fsplit=f.split("\t")
    
    userid=fsplit[0]      
    prodid=fsplit[1]
    rating=str(int(round(float(fsplit[2]))))
    label=fsplit[3]
    date=fsplit[4].strip()
    newdate=datetime.strptime(date, "%Y-%m-%d").date()    
    datetodays=(newdate-d[prodid]).days
    review=Review(userid,'',prodid,'',rating,label,datetodays)
    
    if prodid+"_"+rating not in reviewsperproddata:
        count=count+1
        reviewsperproddata[prodid+"_"+rating]=set()
        dictprod[count]=prodid+"_"+rating
        dictprodr[prodid+"_"+rating]=count
        prodlist[prodid+"_"+rating]=[]
        G.add_node(count)

    prodlist[prodid+"_"+rating].append(review)

    reviewsperproddata[prodid+"_"+rating].add(review)
filee.close()


edgedetails={}
cmnrevrsedges={}
cmnrevrslist={}
cmnrevrslistr={}
cmnrevrsedgeslen={}
countt=0
visited={}
mark={}
graphlist=list(G.nodes())
cr={}
for node1i in range(len(graphlist)):
    node1=graphlist[node1i]
    if node1 not in cr:
        cr[node1]=[]
    for u1i in range(len(prodlist[dictprod[node1]])): 
        u1=prodlist[dictprod[node1]][u1i] 
        cr11=set()     
        cr11.add(u1)     
        for u2i in range(u1i+1,len(prodlist[dictprod[node1]])):
            u2=prodlist[dictprod[node1]][u2i]
            if abs(u1.date-u2.date)<10:
                cr11.add(u2)
        cr[node1].append(cr11)  
    cr[node1].sort(key=len,reverse=True)

edgecount={}
for node1i in range(len(graphlist)):

    node1=graphlist[node1i]
    for node2i in range(node1i+1,len(graphlist)):
        node2=graphlist[node2i]

        maxx=0
        maxxcr=set()
        
        cr1=cr[node1]
        cr2=cr[node2]   
        crlist=set()
        f=0
        for cri1 in cr1:
            if len(cri1)<2:
                break
            for cri2 in cr2:
                if len(cri2)<2:
                    f=1
                    break
                crr=cri1.intersection(cri2)
                crr=frozenset(crr)
                if len(crr)>1:
                    crlist.add(crr)

            if f==1:
                break
        
        crlist=list(crlist)
        crlist.sort(key=len,reverse=True)

        for commonreviewers in crlist:
            if len(commonreviewers)>1:
                
                if commonreviewers not in cmnrevrslistr:
                    countt=countt+1
                    cmnrevrslist[countt]=commonreviewers
                    cmnrevrslistr[commonreviewers]=countt
                    maincount=countt
                else:
                    maincount=cmnrevrslistr[commonreviewers]
                if node1<node2:
                    n1=node1
                    n2=node2
                else:
                    n1=node2
                    n2=node1

                if maincount not in cmnrevrsedges:
                    cmnrevrsedges[maincount]=[]
               
                
                    
                if (n1,n2) not in edgecount:
                     edgecount[(n1,n2)]=0
                     G.add_edge(n1,n2)
                     edgedetails[(n1,n2)]=crlist

                if (n1,n2) not in cmnrevrsedges[maincount]:
                    cmnrevrsedges[maincount].append((n1,n2))
                    edgecount[(n1,n2)]=edgecount[(n1,n2)]+1
              

    
for node in G.nodes():
    if G.degree[node]==0:
        k=frozenset(reviewsperproddata[dictprod[node]])
        if k not in CC_mapper:
            CC_mapper[k]=str(dictprod[node])
        else:
            CC_mapper[k]=CC_mapper[k]+':'+str(dictprod[node])
       
poppinglist=[]
for item in cmnrevrsedges:
    if len(cmnrevrsedges[item])==1:
         poppinglist.append(item)

for p in poppinglist:
    cmnrevrsedges.pop(p)

for c in cmnrevrsedges:
    if c not in cmnrevrsedgeslen:
        mark[c]=0
        cmnrevrsedgeslen[c]=0
    cmnrevrsedgeslen[c]=len(cmnrevrsedges[c])
sorted_cmnrevrsedgeslen=sorted(cmnrevrsedgeslen.items(), key=operator.itemgetter(1))
cmnrevrsedgeslen=sorted_cmnrevrsedgeslen

for ci in range(len(cmnrevrsedgeslen)):
    userset=set()
    prodset=set()
    f=0
    i=set(cmnrevrslist[cmnrevrsedgeslen[ci][0]])
    for cj in range(ci+1,len(cmnrevrsedgeslen)):
        j=set(cmnrevrslist[cmnrevrsedgeslen[cj][0]])
        if i.difference(j)==0:
            if canbeincluded(j):
                mark[cmnrevrsedgeslen[ci][0]]=1
                mark[cmnrevrsedgeslen[cj][0]]=1
                userset=userset.union(i.union(j))
                
                for edge in cmnrevrsedges[cmnrevrsedgeslen[cj][0]]:
                   
                    if cmnrevrslist[cmnrevrsedgeslen[cj][0]] in edgedetails[(edge[0],edge[1])]:
                        edgecount[(edge[0],edge[1])]=edgecount[(edge[0],edge[1])]-1
                        edgedetails[(edge[0],edge[1])].remove(cmnrevrslist[cmnrevrsedgeslen[cj][0]])
                        if edgecount[(edge[0],edge[1])]==0:
                            G.remove_edge(edge[0],edge[1])
                        f=1
            else:
                uset=set()
                pset=set()
                ss=''
                k=j.difference(i)
                
                if canbeincluded(k):
                    uset=k
                    k=frozenset(k)
                    pset=allusers[list(uset)[0]]
                    for u in uset:
                        pset=pset.intersection(allusers[u])
                    
                    for p in pset:
                        ss=ss+str(p)+'_0'+':'

                    ss=ss[0:len(ss)-1]
                    if k not in CC_mapper:
                        CC_mapper[k]=str(ss)
                    else:
                        CC_mapper[k]=CC_mapper[k]+':'+ss
                    f=1
            
            if f==1:
                for edge in cmnrevrsedges[cmnrevrsedgeslen[ci][0]]:   
                        if cmnrevrslist[cmnrevrsedgeslen[ci][0]] in edgedetails[(edge[0],edge[1])]:
                            edgecount[(edge[0],edge[1])]=edgecount[(edge[0],edge[1])]-1
                            edgedetails[(edge[0],edge[1])].remove(cmnrevrslist[cmnrevrsedgeslen[ci][0]])
                            if edgecount[(edge[0],edge[1])]==0:
                                G.remove_edge(edge[0],edge[1])


    ss=''
    if len(userset)>0:
        prodset=allusers[list(userset)[0]]
        for u in userset:
            prodset=prodset.intersection(allusers[u])
        for p in prodset:
            ss=ss+str(p)+'_0'+':'

        ss=ss[0:len(ss)-1]  
        k=frozenset(userset)
        if k not in CC_mapper:
            CC_mapper[k]=str(ss)
        else:
            CC_mapper[k]=CC_mapper[k]+':'+ss

GG=nx.Graph()      
for cmnrvr in cmnrevrsedges:
    nodes=[]
    ss=''
    for edge in cmnrevrsedges[cmnrvr]:
        if edge[0] not in  nodes:
            nodes.append(edge[0])
            ss=ss+dictprod[edge[0]]+":"

        if edge[1] not in  nodes:
            nodes.append(edge[1])
            ss=ss+dictprod[edge[1]]+":"
        edgecount[(edge[0],edge[1])]=edgecount[(edge[0],edge[1])]-1
        edgedetails[(edge[0],edge[1])].remove(cmnrevrslist[cmnrvr])
        if edgecount[(edge[0],edge[1])]==0:
            G.remove_edge(edge[0],edge[1])
    ss=ss[0:len(ss)-1]  
    k=frozenset(cmnrevrslist[cmnrvr])
    if k not in CC_mapper:
        CC_mapper[k]=str(ss)
    else:
        CC_mapper[k]=CC_mapper[k]+':'+ss


co=0
while len(G.edges())>0:

    co=co+1
    print (str(co)+"\t"+str(len(G.edges())))

    cmnrevrsedges2={}
    cmnrevrslist2={}
    cmnrevrslistr2={}
    countt2=0
    visited={}
    edgedetails2={}
    edgecount2={}
    edgelist=list(G.edges())
    for edge1i in range(len(edgelist)):
        edge1=edgelist[edge1i]

        if edge1[0]<edge1[1]:
            e10=edge1[0]
            e11=edge1[1]
        else:
            e10=edge1[1]
            e11=edge1[0]
            
        s1=str(dictprod[e10])+":"+str(dictprod[e11])

        if edge1i==0:
            count=count+1
            node1=count
            dictprod[count]=s1
            dictprodr[s1]=count
            GG.add_node(count)
            reviewsperproddata[s1]=edgedetails[(e10,e11)]
        else:
            node1=dictprodr[s1]
        
        for edge2i in range(edge1i+1,len(edgelist)):
            edge2=edgelist[edge2i]

            if edge2[0]<edge2[1]:
                e20=edge2[0]
                e21=edge2[1]
            else:
                e20=edge2[1]
                e21=edge2[0]
                
            s2=str(dictprod[e20])+":"+str(dictprod[e21])

            if edge1i==0:
                count=count+1
                node2=count
                dictprod[count]=s2
                dictprodr[s2]=count
                GG.add_node(count)
                reviewsperproddata[s2]=edgedetails[(e20,e21)]
            else:
                node2=dictprodr[s2]

            if isAdjacent(edge1,edge2):
                cr1=set(reviewsperproddata[dictprod[node1]])
                cr2=set(reviewsperproddata[dictprod[node2]])
                
                crlist=set()
                f=0
                for cri1 in cr1:
                    if len(cri1)<2:
                        break
                    for cri2 in cr2:
                        if len(cri2)<2:
                            f=1
                            break
                        crr=cri1.intersection(cri2)
                        crr=frozenset(crr)
                        if len(crr)>1:
                            crlist.add(crr)
                    if f==1:
                        break
                
                crlist=list(crlist)
                crlist.sort(key=len,reverse=True)

                for commonreviewers in crlist:
                        
                    if len(commonreviewers)>1 and commonreviewers not in cmnrevrslistr:
                        if commonreviewers not in cmnrevrslistr2:
                            countt2=countt2+1
                            cmnrevrslist2[countt2]=commonreviewers
                            cmnrevrslistr2[commonreviewers]=countt2
                            maincount=countt2
                        else:
                            maincount=cmnrevrslistr2[commonreviewers]

                        if maincount not in cmnrevrsedges2:
                                cmnrevrsedges2[maincount]=[]

                      

                        if (node1,node2) not in edgecount2:
                                GG.add_edge(node1,node2)
                                edgecount2[(node1,node2)]=0
                                edgedetails2[(node1,node2)]=crlist
                        if (node1,node2) not in cmnrevrsedges2[maincount]:                              
                                cmnrevrsedges2[maincount].append((node1,node2))
                                edgecount2[(node1,node2)]=edgecount2[(node1,node2)]+1
                        


    for node in GG.nodes():
        if GG.degree[node]==0:

            k=reviewsperproddata[dictprod[node]][0]
            if k not in CC_mapper:
                CC_mapper[k]=str(dictprod[node])
            else:
                CC_mapper[k]=CC_mapper[k]+':'+str(dictprod[node])

    G=GG
    cmnrevrsedges=cmnrevrsedges2
    cmnrevrslist=cmnrevrslist2
    cmnrevrslistr=cmnrevrslistr2
    edgedetails=edgedetails2
    edgecount=edgecount2
    cmnrevrsedgeslen={}
    mark={}
    
    poppinglist=[]
    for item in cmnrevrsedges:
        if len(cmnrevrsedges[item])==1:
             poppinglist.append(item)

    for p in poppinglist:
        cmnrevrsedges.pop(p)
    
    for c in cmnrevrsedges:
        if c not in cmnrevrsedgeslen:
            cmnrevrsedgeslen[c]=0
            mark[c]=0
        cmnrevrsedgeslen[c]=len(cmnrevrsedges[c])
    sorted_cmnrevrsedgeslen=sorted(cmnrevrsedgeslen.items(), key=operator.itemgetter(1))
    cmnrevrsedgeslen=sorted_cmnrevrsedgeslen

    for ci in range(len(cmnrevrsedgeslen)):
        userset=set()
        prodset=set()
        f=0
        i=set(cmnrevrslist[cmnrevrsedgeslen[ci][0]])
        for cj in range(ci+1,len(cmnrevrsedgeslen)):
            j=set(cmnrevrslist[cmnrevrsedgeslen[cj][0]])
            if i.difference(j)==0:
                if canbeincluded(j):
                    mark[cmnrevrsedgeslen[ci][0]]=1
                    mark[cmnrevrsedgeslen[cj][0]]=1
                    userset=userset.union(i.union(j))
                    for edge in cmnrevrsedges[cmnrevrsedgeslen[cj][0]]:
                       
                        if cmnrevrslist[cmnrevrsedgeslen[cj][0]] in edgedetails[(edge[0],edge[1])]:
                            edgecount[(edge[0],edge[1])]=edgecount[(edge[0],edge[1])]-1
                            edgedetails[(edge[0],edge[1])].remove(cmnrevrslist[cmnrevrsedgeslen[cj][0]])
                            if edgecount[(edge[0],edge[1])]==0:
                                G.remove_edge(edge[0],edge[1])
                            f=1
                else:
                    uset=set()
                    pset=set()
                    ss=''
                    k=j.difference(i)
                    if canbeincluded(k):
                        uset=k
                        k=frozenset(k)
                        pset=allusers[list(uset)[0]]
                        for u in uset:
                            pset=pset.intersection(allusers[u])
                        
                        for p in pset:
                            ss=ss+str(p)+'_0'+':'

                        ss=ss[0:len(ss)-1]
                        if k not in CC_mapper:
                            CC_mapper[k]=str(ss)
                        else:
                            CC_mapper[k]=CC_mapper[k]+':'+ss
                        f=1
                if f==1:
                  for edge in cmnrevrsedges[cmnrevrsedgeslen[ci][0]]:   
                      if cmnrevrslist[cmnrevrsedgeslen[ci][0]] in edgedetails[(edge[0],edge[1])]:
                          edgecount[(edge[0],edge[1])]=edgecount[(edge[0],edge[1])]-1
                          edgedetails[(edge[0],edge[1])].remove(cmnrevrslist[cmnrevrsedgeslen[ci][0]])
                          if edgecount[(edge[0],edge[1])]==0:
                              G.remove_edge(edge[0],edge[1])

        ss=''
        if len(userset)>0:
            prodset=allusers[list(userset)[0]]
            for u in userset:
                prodset=prodset.intersection(allusers[u])
            for p in prodset:
                ss=ss+str(p)+'_0'+':'

            ss=ss[0:len(ss)-1]  
            k=frozenset(userset)
            if k not in CC_mapper:
                CC_mapper[k]=str(ss)
            else:
                CC_mapper[k]=CC_mapper[k]+':'+ss

    GG=nx.Graph()

    for cmnrvr in cmnrevrsedges:
        nodes=[]
        ss=''
        for edge in cmnrevrsedges[cmnrvr]:
            if edge[0] not in  nodes:
                nodes.append(edge[0])
                ss=ss+dictprod[edge[0]]+":"

            if edge[1] not in  nodes:
                nodes.append(edge[1])
                ss=ss+dictprod[edge[1]]+":"
            edgecount[(edge[0],edge[1])]=edgecount[(edge[0],edge[1])]-1
            edgedetails[(edge[0],edge[1])].remove(cmnrevrslist[cmnrvr])
            if edgecount[(edge[0],edge[1])]==0:
                G.remove_edge(edge[0],edge[1])
        ss=ss[0:len(ss)-1]  
        k=frozenset(cmnrevrslist[cmnrvr])
        if k not in CC_mapper:
            CC_mapper[k]=str(ss)
        else:
            CC_mapper[k]=CC_mapper[k]+':'+str(ss)

grps={}
co=0
for us in CC_mapper:
    c=0
    denom=0
    userset=set()
    prodset=set()
    for u in us:
        userset.add(int(u.userid))
    prods=CC_mapper[us].split(':')
    for p in prods:
        prodset.add(int(p.split('_')[0]))


    if len(grps) not in grps and len(prodset)>0 and len(userset)>1:
        grps[len(grps)]={'id':len(grps),'users':list(userset),'prods':list(prodset),'scorepred':0, 'scoregt':0, 'fakegt':0,'fakepred':0}
    
with open(args.dg, 'w') as fp:
    json.dump(grps, fp) 

print ('end')            

    
