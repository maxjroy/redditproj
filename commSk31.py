import requests, json, time

class cThread(object):
   def __init__(self, tree, data):
      self.data=data
      self.tree=tree
      self.selfPost=self.checkIsSelf()
      self.subreddit=self.getSub()
      self.OP=self.getOP()
      self.thScore=self.getScore()
      self.thTimeUTC=self.getTimestamp()
      self.id=self.getID()
      self.edited=self.checkEdited()
      self.listedCommCount=self.getListedCount()
      self.title=self.getTitle()
      
      self.ttlComms=0
      self.ttlKarma=0
      self.delCount=0
      self.uniqueUsers=0
      self.OPCount=0
      self.maxDepth=0
      self.avgDepth=0

      self.percCommsByDepth=[]
      self.percKarmaByDepth=[]
      self.percInTopComm=0
      
   def checkIsSelf(self):
      return self.data['children'][0]['data']['is_self']
   def getSub(self):
      return self.data['children'][0]['data']['subreddit']
   def getOP(self):
      return self.data['children'][0]['data']['author']
   def getID(self):
      return self.data['children'][0]['data']['name']
   def getScore(self):
      return self.data['children'][0]['data']['score']
   def checkEdited(self):
      return self.data['children'][0]['data']['edited']
   def getListedCount(self):
      return self.data['children'][0]['data']['num_comments']
   def getTimestamp(self):
      return self.data['children'][0]['data']['created_utc']
   def getTitle(self):
      return self.data['children'][0]['data']['title']

   def DFSCounter(self, t):
      uniqueU=[];  OPcount=0;  delCount=0;  ttlKarma=0; depthTtl=0;

      currDepth=0;
      depthScores={0:[], 1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[]};
      #depthScores=[]             

      visited=[]
      S=[]
      S+=t
      while len(S)>0:
         v=S.pop()
         if v not in visited:
            visited.append(v)
            #if v.depth>11:
               #continue
            #else:
            if v.user != '[deleted]' and v.user not in uniqueU:
               uniqueU.append(v.user)
            if v.user == self.OP:
               OPcount+=1
            if v.user == '[deleted]':
               delCount+=1
            depthScores[v.depth].append(abs(v.score))
            depthTtl+=v.depth
            ttlKarma+=v.score
            
            for k in v.kids:
               S.append(k)

      self.ttlComms=len(visited)
      self.ttlKarma=ttlKarma
      self.uniqueUsers=len(uniqueU)
      self.OPCount=OPcount
      self.delCount=delCount
      self.avgDepth=float('%.4f'%(1.0*depthTtl/self.ttlComms))
      #self.avgDepth=float('%.4f'%(1.0*depthTtl/self.ttlComms))
      
      return depthScores

   def karmaAnalyzer(self, d):
      ttlKarmaAtDepth=[]

      for i in d.keys():
         ttlKarmaAtDepth.append(sum(d[i]))

      pKarmAtDepth=[]
      for i in ttlKarmaAtDepth:
         pKarmAtDepth.append(float('%.4f'%(1.0*i/self.ttlKarma)))
         #pKarmAtDepth.append(float('%.4f'%(1.0*i/self.listedCommCount)))
      self.percKarmaByDepth=pKarmAtDepth

   def depthsAnalyzer(self, d):
      lensAtDepth=[]

      for i in d.keys():
         lensAtDepth.append(len(d[i]))
         
      pCommsByDepth=[]
      for i in lensAtDepth:
         pCommsByDepth.append(float('%.4f'%(1.0*i/self.ttlComms)))
         #pCommsByDepth.append(float('%.4f'%(1.0*i/self.listedCommCount)))
      self.percCommsByDepth=pCommsByDepth

      maxD=0;
      for ii in d.keys():
         if len(d[ii])==0:
            maxD=ii-1;
            break;
         maxD=ii
      self.maxDepth=maxD  

      n=self.tree[0].countAllKids()
      self.percInTopComm=float('%.4f'%(1.0*n/self.ttlComms))
      #self.percInTopComm=float('%.4f'%(1.0*n/self.listedCommCount))
      
      return lensAtDepth
   def analThread(self):
      dfs=self.DFSCounter(self.tree)
      d=self.depthsAnalyzer(dfs)
      k=self.karmaAnalyzer(dfs)
      return (dfs,d)
#======================
class Comment(object):
   def __init__(self, jComm, parent=None):
      self.parent=parent
      self.jComm=jComm
      self.kind=self.jComm['kind']
      self.fullName=self.getName()
      self.parentID=self.getParentID()
      self.user=self.getUser()
      self.golden=self.checkGold()
      self.score=self.getScore()
      self.depth=self.getDepth()
      self.time=self.getTime()
      self.kids=self.getKids()
         
   def __str__(self):
      print '{}'.format(self.user, self.depth)
   def getName(self):
      return self.jComm['data']['name']
   def getUser(self):
      if self.kind == 't1':
         return self.jComm['data']['author'] 
      else:
         pass
   def getScore(self):
      if self.kind=='t1':
         return self.jComm['data']['score']
   def getParentID(self):
      return self.jComm['data']['parent_id']
   def getTime(self):
      if self.kind=='t1':
         return self.jComm['data']['created_utc']
   def getDepth(self):
      if self.parent is None:
         return 0
      else:
         return 1+self.parent.getDepth()
   def checkGold(self):
      if self.kind=='t1':
         if self.jComm['data']['gilded']:
            return True
         else:
            return False
   def getKids(self):
      result=[]

      if self.depth<11:
         if self.kind == 't1':
            if (len(self.jComm['data']['replies'])>0):
               for k in self.jComm['data']['replies']['data']['children']:
                  if k['kind'] == 't1':
                     result.append(Comment(k, parent=self))
                  elif k['kind']=='more':
                     for ch in k['data']['children']:
                        result+=self.handleMore(ch)
            else:
               pass
         elif self.kind == 'more':
            temp=[]
            for k in self.jComm['data']['children']:
               temp+=self.handleMore(k)
            result+=temp
         else:
              print 'something has gone very wrong'
      else:
         pass

      return result
   def handleMore(self, deepID):
      result=[]
      rr=requests.get(URL+deepID+r'/.json', headers=headers)
      #print rr.elapsed.total_seconds(), self.depth
      time.sleep(4*rr.elapsed.total_seconds())
      tempJData=rr.json()
      tempJData=tempJData[1]['data']['children']
      for k in tempJData:
         result.append(Comment(k, parent=self))   
      return result
   def countAllKids(self):
      res=0
      if len(self.kids)==0:
         pass
      else:
         for k in self.kids:
            res+=1+k.countAllKids()
      return res
#================
def makeTree(topList):
   t=[]
   for ii in topList:
      if ii['kind']=='t1':
         t.append(Comment(ii))
      else:
         for ii in topList[-1]['data']['children']:
            rr=requests.get(URL+ii+'/.json'+sort, headers=headers)
            time.sleep(.33)
            tempJData=rr.json()
            tempJData=tempJData[1]['data']['children']
            for k in tempJData:
               t.append(Comment(k))   

   return t

def printTree(t):
   for c in t:
      print c.depth*'  ', c.user, '(', c.fullName, ')'
      printTree(c.kids)

#===========
def main():
   print time.clock()
   global URL, headers, sort
   headers={'User-Agent':'Reddit python proj from u/narfarnst'}
   URL=r'http://www.reddit.com/r/technology/comments/2ndo2b/mark_cuban_made_billions_from_an_open_internet/'
   #URL=r'http://www.reddit.com/r/LifeProTips/comments/2ne54e/lpt_if_you_havent_already_started_thawing_your/'
   sort=r'?sort=top'
   tries=0
   ok=False
   r=requests.get(URL+r'.json'+sort, headers=headers)
   jData=r.json()

   ch0=jData[1]['data']['children']
   thMeta=jData[0]['data']
   topComm=ch0[0]
   
   t=makeTree(ch0)

   thr=cThread(t, thMeta)
   a=thr.analThread()
   print a[1]
   
   print time.clock()
   return thr

if __name__=='__main__':
   thr=main()

