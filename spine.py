import pymel.core as pm
import maya.api.OpenMaya as om

class Spine:
    
    def __init__(self, name='spine',flipAxis=False,axis='X',**kwargs):
        self.startGuide = None
        self.midGuide = None
        self.endGuide = None
        self.spineGuideDict={'start':[0,0,0],'mid':[0,4,0],'end':[0,8,0]}
        self.name=name
        self.flipAxis=flipAxis
        self.axis=axis
        
        self.spineDict={}
        self.spineDict['moveallSetup']={'nameTempl':self.name+'MoveAll', 'icone':'circuloX','size':1.8,'color':(1,1,0) }    
        self.spineDict['spine0CntrlSetup'] = {'nameTempl':self.name+'spine0', 'icone':'circuloY','size':4,'color':(0,0,1) }    
        self.spineDict['startFkCntrlSetup'] = {'nameTempl':self.name+'StartFk', 'icone':'cubo','size':1,'color':(0,1,0)}
        self.spineDict['midFkOffsetCntrlSetup'] = {'nameTempl':self.name+'MidFkOff', 'icone':'circuloY', 'size':2, 'color':(1,1,0) }
        self.spineDict['midFkCntrlSetup'] = {'nameTempl':self.name+'MidFk', 'icone':'cubo', 'size':1, 'color':(0,1,0) }
        self.spineDict['endFkCntrlSetup'] = {'nameTempl':self.name+'EndFk', 'icone':'cubo', 'size':1, 'color':(0,1,0) }
        self.spineDict['startIkCntrlSetup'] = {'nameTempl':self.name+'StartIk', 'icone':'cubo', 'size':2, 'color':(1,0,0)}
        self.spineDict['midIkCntrlSetup'] = {'nameTempl':self.name+'MidIk', 'icone':'circuloY', 'size':2, 'color':(1,1,0)}
        self.spineDict['endIkCntrlSetup'] = {'nameTempl':self.name+'EndIk', 'icone':'cubo', 'size':2, 'color':(1,0,0)}
          
        self.spineDict['nodeTree'] = {}
        self.spineDict['nameConventions'] = None        


    def doGuide(self, **kwargs):
        self.spineGuideDict.update(kwargs)
        
        if pm.objExists (self.name+'Moveall_guide'):
            pm.delete (self.name+'Moveall_guide')
        
        self.spineGuideMoveall=pm.group (n=self.name+'Moveall_guide', em=True)
        self.startGuide = pm.spaceLocator (n=self.name+'Start_guide', p=(0,0,0))
        self.startGuide.translate.set(self.spineGuideDict['start'])
        self.startGuide.displayHandle.set(1)
        self.midGuide = pm.spaceLocator (n=self.name+'Mid_guide',p=(0,0,0))
        self.midGuide.translate.set(self.spineGuideDict['mid'])
        self.midGuide.displayHandle.set(1)
        self.endGuide = pm.spaceLocator (n=self.name+'End_guide', p=(0,0,0))
        self.endGuide.translate.set(self.spineGuideDict['end'])
        self.endGuide.displayHandle.set(1)
        
        pm.parent (self.startGuide,self.midGuide,self.endGuide, self.spineGuideMoveall)
        
    def doRig(self):
        
        if not pm.objExists (self.name+'Moveall_guide'):
            self.doGuide()
            
        if pm.objExists (self.spineDict['moveallSetup']['nameTempl']):
            pm.delete (self.spineDict['moveallSetup']['nameTempl'])
            
        spineRibbon=None

        #fkCntrls
        # qual o comportamento do hip? 
        # no fk o hip deve ficar parado?
        # um so hip para ik e fk?
        
        displaySetup= self.spineDict['spine0CntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        spine0FkCntrl = cntrlCrv(n=cntrlName , obj=self.startGuide,**displaySetup) 
        displaySetup= self.spineDict['startFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        startFkCntrl = cntrlCrv(n=cntrlName, obj=self.startGuide,**displaySetup)
        startFkCntrl.getParent().setParent(spine0FkCntrl)
        displaySetup= self.spineDict['midFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        midFkCntrl = cntrlCrv(n=cntrlName, obj=self.midGuide,**displaySetup)
        displaySetup= self.spineDict['midFkOffsetCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        midFkOffsetCntrl = cntrlCrv(n=cntrlName, obj=self.midGuide,**displaySetup)
        midFkOffsetCntrl.getParent().setParent(midFkCntrl)
        midFkCntrl.getParent().setParent(startFkCntrl)
        displaySetup= self.spineDict['endFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        endFkCntrl = cntrlCrv(n=cntrlName, obj=self.endGuide,**displaySetup)
        endFkCntrl.getParent().setParent(midFkCntrl)
        
        #ikCntrls
        displaySetup= self.spineDict['startIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        startIkCntrl = cntrlCrv(n=cntrlName, obj=self.startGuide,**displaySetup)
        displaySetup= self.spineDict['midIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        midIkCntrl = cntrlCrv(n=cntrlName, obj=self.midGuide,**displaySetup)
        displaySetup= self.spineDict['endIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        endIkCntrl = cntrlCrv(n=cntrlName, obj=self.endGuide,**displaySetup)
        
        #joints
        pm.select(cl=True)
        start=pm.xform(self.startGuide,q=True,t=True)
        startZeroJnt=pm.joint(p=(0,0,0))
        startJnt=pm.joint(p=(0,0,0))
        starttipJnt=pm.joint(p=(-2,0,0))
        
        pm.select(cl=True)
        end=pm.xform(self.endGuide,q=True,t=True)
        endZeroJnt=pm.joint(p=(0,0,0))
        endJnt=pm.joint(p=(0,0,0))
        endtipJnt=pm.joint(p=(4,0,0))
        
        twistExtractor1= twistExtractor(startJnt)
        twistExtractor2= twistExtractor(endJnt)
        
        #ribbon
        #implementar:calcular a distancia entre os guides pra fazer ribbon do tamanho certo
        
        spineRibbon = RibbonBezierSimple(size=8)
        spineRibbon.doRig()
        
        aimTwist = AimTwistDivider()
        aimTwist.start.setParent (spineRibbon.startCntrl,r=True)
        aimTwist.end.setParent (spineRibbon.endCntrl,r=True)
        aimTwist.mid.setParent (spineRibbon.moveall,r=True)
        
        spineRibbon.moveall.rotate.set(0,0,90)
        ## implementar calculo para determinar a rotacao do ribbon
        
        
        ##constraints
        pm.pointConstraint (startIkCntrl, endIkCntrl, midIkCntrl.getParent(), mo=True)
        pm.orientConstraint (aimTwist.mid, midIkCntrl, mo=True)
        midIkCntrl.rotate.lock()
        midIkCntrl.rotate.setKeyable(0)
        pm.orientConstraint (aimTwist.mid, midFkOffsetCntrl, mo=True)
        midFkOffsetCntrl.rotate.lock()
        midFkOffsetCntrl.rotate.setKeyable(0)
        
        
        cns1=pm.parentConstraint (startFkCntrl, startIkCntrl, spineRibbon.startCntrl, mo=True)
        cns2=pm.parentConstraint (midFkOffsetCntrl, midIkCntrl, spineRibbon.midCntrl, mo=True)
        cns3=pm.parentConstraint (endFkCntrl, endIkCntrl, spineRibbon.endCntrl, mo=True)
        
        startZeroJnt.setParent (spineRibbon.startCntrl.getParent(), r=True)
        endZeroJnt.setParent (spineRibbon.endCntrl.getParent(), r=True)
        
        pm.pointConstraint (spineRibbon.startCntrl, startZeroJnt, mo=True)
        pm.orientConstraint (spineRibbon.startCntrl, startJnt, mo=True)
        pm.pointConstraint (spineRibbon.endCntrl, endZeroJnt, mo=True)
        pm.orientConstraint (spineRibbon.endCntrl, endJnt, mo=True)
        
        displaySetup= self.spineDict['moveallSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        spineMoveall=pm.group(n=cntrlName, em=True)

        pm.parent (twistExtractor1.extractorGrp, twistExtractor2.extractorGrp, spineRibbon.moveall, startIkCntrl.getParent(),midIkCntrl.getParent(),endIkCntrl.getParent(),spine0FkCntrl.getParent(), spineMoveall)
        
        #blend ikfk
        spineMoveall.addAttr ('ikfk', at='float', max=1, min=0, dv=1, k=1)
        ikfkRev = pm.createNode('reverse')
        ikfkCond1 = pm.createNode('condition')
        ikfkCond2 = pm.createNode('condition')
        spineMoveall.ikfk >> ikfkCond1.firstTerm
        spineMoveall.ikfk >> ikfkCond2.firstTerm
        spineMoveall.ikfk >> ikfkRev.inputX
        
        twistExtractor1.extractor.extractTwist >> spineRibbon.startCntrl.twist
        twistExtractor2.extractor.extractTwist >> spineRibbon.endCntrl.twist
        
        ikfkCond1.secondTerm.set (0)
        ikfkCond1.operation.set (2)
        ikfkCond1.colorIfTrueR.set (1)
        ikfkCond1.colorIfFalseR.set (0)
        ikfkCond1.outColorR >> startIkCntrl.getParent().visibility
        ikfkCond1.outColorR >> midIkCntrl.getParent().visibility
        ikfkCond1.outColorR >> endIkCntrl.getParent().visibility
        
        ikfkCond2.secondTerm.set (1)
        ikfkCond2.operation.set (4)
        ikfkCond2.colorIfTrueR.set (1)
        ikfkCond2.colorIfFalseR.set (0)
        ikfkCond2.outColorR >> startFkCntrl.getParent().visibility
         
        weightAttr = cns1.target.connections(p=True, t='parentConstraint') #descobre parametros
        spineMoveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns2.target.connections(p=True, t='parentConstraint') #descobre parametros
        spineMoveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns3.target.connections(p=True, t='parentConstraint') #descobre parametros
        spineMoveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
