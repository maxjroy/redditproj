import requests, json, time

class Comment(object):
      def __init__(self, jComm, parent=None):
         self.parent=parent
         self.jComm=jComm
         self.kind=self.jComm['kind']
         self.fullName=self.getName()
         self.parentID=self.getParentID()
         self.user=self.getUser()
         #self.gilded=self.checkGilded()
         #self.score=self.getScore()
         self.depth=self.getDepth()
         #self.time=self.getTime()

         self.kids=self.getKids()
            
         #print self.depth*'  ', self.user
      def __str__(self):
         print '{}'.format(self.user)
      def getName(self):
         return self.jComm['data']['name']
      def getUser(self):
            if self.kind == 't1':
               return self.jComm['data']['author'] 
            else:
               pass
               #print '<NO AUTH ', self.jComm['kind'], self.jComm['data']['id'], '>' #print '\n', self.jComm['parent_id'], '\n'
               #print '   ', self.jComm['data']['name']
      def getScore(self):
         return self.jComm['data']['score']
      def getParentID(self):
         return self.jComm['data']['parent_id']
      def getTime(self):
         return self.jComm['data']['created_utc']
     # def checkGilded(self):
           # if self.jComm['data']['guilded']
      def getKids(self):
         result=[]
         if self.kind == 't1':
            #print 'aaa: ', type(self.jComm['data'])
            if (len(self.jComm['data']['replies'])>0):
               for k in self.jComm['data']['replies']['data']['children']:
                  if k['kind'] == 't1':
                     result.append(Comment(k, parent=self))
                     #print 'dict', k['data'].keys()
                  elif k['kind']=='more':
                     for ch in k['data']['children']:
                        #print '  ch: ', ch, k['data']['parent_id']
                        result+=self.handleMore(ch)
            else:
               pass
         elif self.kind == 'more':
            #print '<more>'
            temp=[]
            for k in self.jComm['data']['children']:
               #print "  k: ", k, type(k)
               temp+=self.handleMore(k)
               #print 't: ', type(temp[0])
              
               #result+=self.handleMore(k)
            result+=temp
         else:
              print 'h8888'
         return result

#~~~~~~~~~~~~~~~~
##      def getKids(self):
##         result=[]
##         if self.kind == 't1':
##            #print 'aaa: ', type(self.jComm['data'])
##            if (len(self.jComm['data']['replies'])>0):
##               for k in self.jComm['data']['replies']['data']['children']:
##                  temp=[]
##                  if k['kind'] == 't1':
##                     temp+=Comment(k, parent=self)
##                     #print 'dict', k['data'].keys()
##                  return temp
##                  elif self.kind=='more':
##                     temp=[]
##                     for ch in k['data']['children']:
##                        print 'ch in inn: ', ch, 'p:', k['data']['parent_id']
##                        temp+=haldneMore(ch)
##                     print '----------------'
##                     return temp
##            else:
##               return []
##         elif self.kind == 'more':
##            #print '<more>'
##            temp=[]
##            for k in self.jComm['data']['children']:
##               #print "  k: ", k, type(k)
##               temp+=self.handleMore(k)
##               print 'ch out: ', type(temp[0])
##              
##               #result+=self.handleMore(k)
##            return temp
##         else:
##              print 'h8888'
##              return -1

            
      def getDepth(self):
         if self.parent is None:
            return 0
         else:
            return 1+self.parent.getDepth()
      def handleMore(self, deepID):
         result=[]
         #print 'hmc: ', deepID
         rr=requests.get(URL+deepID+r'/.json', headers=headers)
         tempJData=rr.json()
         tempJData=tempJData[1]['data']['children']
         for k in tempJData:
            #cc=Comment(k['data'])
            result.append(Comment(k, parent=self))   
         return result
#================
def makeTree(topList):
   t=[]
   for ii in topList:
      t.append(Comment(ii))
   return t

def printTree(t):
   for c in t:
      print c.depth*'  ', c.user
      printTree(c.kids)
def treePoop(t):
      visited=[]
      S=[]
      S+=t
      while len(S)>0:
         v=S.pop()
         if v not in visited:
            visited.append(v)
            for k in v.kids:
               S.append(k)
      print len(visited)
      return None
#===========
def main():
   print time.clock()
   global URL, headers
   headers={'User-Agent':'Reddit python proj from u/narfarnst'}
   #URL=r'http://www.reddit.com/r/pics/comments/2gc49u/monk_stays_with_man_who_passed_away/'
   #URL=r'http://www.reddit.com/r/pics/comments/2gdgqt/outrunning_a_wave/'
   #URL=r'http://www.reddit.com/r/pics/comments/2ge283/yesterday_i_bought_perhaps_the_prettiest_table/'
   URL=r'http://www.reddit.com/r/pics/comments/92dd8/test_post_please_ignore/'
   sort=r'?sort=top/'
   #URL=URL+sort+'/.json'
   tries=0
   ok=False
   r=requests.get(URL+r'.json', headers=headers)
   jData=r.json()
   if (type(jData) is dict):
         print 'poooooo'
   #print type(jData)
   ch0=jData[1]['data']['children']
   topComm=ch0[0]
   
   tc=Comment(topComm)
   t=makeTree(ch0)
   treePoop(t)
   #print len(t)
   print time.clock()
   return t
if __name__=='__main__':
   main()
