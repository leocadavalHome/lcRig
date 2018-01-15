class EyeBrow:
    
    def __init__(self, name='eyeBrow', flipAxis=False):
        ##def doRig(self):
        self.name=name
        self.guideMoveall=None
        self.browGuideNames = ['inTip1', 'inTip2', 'in', 'out', 'outTip2', 'outTip1']
        self.browGuideDict = {'inTip1':[0.3,0,0],'inTip2':[0,0,0], 'in':[.08,.09,0], 'out':[-.08,.09,0], 'outTip2':[0,0,0], 'outTip1':[-0.3,0,0]}
        self.guideList=[]
        self.flipAxis=flipAxis
                
    def doGuide(self):#doGuide
        self.guideMoveall=pm.group(em=True,n=self.name+'Moveall_guide')
        
        self.guideList=[]
        
        for name in self.browGuideNames:
            guide = pm.spaceLocator (n=self.name+name)
            guide.setParent (self.guideMoveall)
            guide.translate.set (self.browGuideDict[name])
            guide.localScale.set (0.1,0.1,0.1)
            self.guideList.append(guide)
        
        grp1=pm.group (self.guideList[1])
        grp2=pm.group (self.guideList[4])
        
        pm.pointConstraint (self.guideList[0],self.guideList[2],grp1, mo=False)
        pm.pointConstraint (self.guideList[0], grp1, e=True, w=.7)
        pm.pointConstraint (self.guideList[2], grp1, e=True, w=.3)
        
        pm.pointConstraint (self.guideList[5],self.guideList[3], grp2, mo=False)
        pm.pointConstraint (self.guideList[5], grp2, e=True, w=.7)
        pm.pointConstraint (self.guideList[3], grp2, e=True, w=.3)
 
    def mirrorConnectGuide(self, brow):

        if not self.guideMoveall:
            self.doGuide()   
                  
        if not brow.guideMoveall:
            brow.doGuide()

        if pm.objExists(self.name+'MirrorGuide_grp'):
            pm.delete (self.name+'MirrorGuide_grp')

        self.mirrorGuide= pm.group (em=True, n=self.name+'MirrorGuide_grp') 
              
        self.guideMoveall.setParent (self.mirrorGuide)
        self.mirrorGuide.scaleX.set (-1)
        self.mirrorGuide.template.set (1)   
        
        brow.guideMoveall.translate >> self.guideMoveall.translate 
        brow.guideMoveall.rotate >> self.guideMoveall.rotate 
        brow.guideMoveall.scale >> self.guideMoveall.scale

        for guide1, guide2 in zip (self.guideList, brow.guideList):
            guide2.translate >> guide1.translate
            guide2.rotate >> guide1.rotate
            guide2.scale >> guide1.scale
            
        if brow.flipAxis:
            self.flipAxis=False
        else:
            self.flipAxis=True


    def getGuideFromScene(self):
        self.guideMoveall=pm.PyNode(self.name+'Moveall_guide')
        self.guideList
        for name in self.browGuideNames:
            guide=pm.PyNode(self.name+name)
            self.guideList.append(guide)
        
    def doRig(self, mesh=None):
        
        self.browMoveall=pm.group (em=True, n=self.name+'Moveall')
                
        p=[]
        V=[]
        for guide in self.guideList:
            pos=pm.xform (guide, q=True, ws=True, t=True)
            p.append (pos)
            v=om.MVector (pos)
            V.append(v)

        self.wireCrv = pm.curve (n='wirecrv',p=p)
        
        clsInTip= pm.cluster (self.wireCrv.cv[0:1], n=self.name+'InTip')
        clsIn= pm.cluster (self.wireCrv.cv[2], n=self.name+'In')
        clsOut= pm.cluster (self.wireCrv.cv[3], n=self.name+'Out')
        clsOutTip= pm.cluster (self.wireCrv.cv[4:5], n=self.name+'OutTip')
        
        clsList=[clsInTip[1], clsIn[1], clsOut[1], clsOutTip[1]]
        pm.parent (self.wireCrv, clsList, self.browMoveall)
        
        self.mesh=mesh
        self.cntrlList=[]

        self.cntrlAll= cntrlCrv (name=self.name,obj=self.guideList[2], size=0.2)        
        self.cntrlAll.getParent().setParent (self.browMoveall)
        for cls in clsList:
            grp=pm.group(em=True, n=cls.name()+'Aux_grp')
            aux=pm.group(em=True, n=cls.name()+'_aux', p=grp)
            pos=pm.xform (cls, q=True, ws=True, rp=True)
            pm.xform (aux, t=pos, ws=True)
            pm.geometryConstraint (self.mesh,aux)
            pm.parentConstraint (aux, cls, mo=True)
            cntrl= cntrlCrv (name=cls.name(),obj=aux, size=0.1)
            if self.flipAxis:
                cntrl.getParent().scaleX.set(-1)
            else:
                cntrl.getParent().scaleX.set(1) 
            pm.parentConstraint (cntrl,aux,mo=True)           
            self.cntrlList.append (cntrl)
            pm.parent (cntrl.getParent(), self.cntrlAll)
            pm.parent (grp,aux, self.browMoveall)
        
     
x=EyeBrow(name='L_brow')   
x.getGuideFromScene()
#x.doGuide()
print x.guideMoveall
y=EyeBrow(name='R_brow', flipAxis=True)
y.mirrorConnectGuide(x)
x.doRig(mesh='corpo1')
y.doRig(mesh='corpo1')