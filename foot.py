import pymel.core as pm
import maya.api.OpenMaya as om

class Foot:
    """
        Cria um pe
        Parametros: 
            name (string): nome do novo pe            
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
                 
    """ 
    #IMPLEMENTAR:
    #guides com restricao de rotacao
    
    def __init__(self,name='foot',flipedAxis=False, axis='X',**kwargs):
    
        self.name=name
        self.flipedAxis=flipedAxis
        self.axis=axis
        self.footDict={}
        self.footDict['moveallCntrlSetup']={'nameTempl':self.name+'MoveAll', 'icone':'circuloX','size':1.8,'color':(1,1,0) }    
        self.footDict['centerCntrlSetup'] = {'nameTempl':self.name+'Center', 'icone':'circuloX','size':2,'color':(1,1,0) }    
        self.footDict['tipCntrlSetup'] = {'nameTempl':self.name+'Tip', 'icone':'bola','size':0.5,'color':(0,1,1)}
        self.footDict['heelCntrlSetup'] = {'nameTempl':self.name+'Heel', 'icone':'bola', 'size':0.5, 'color':(0,1,1) }
        self.footDict['ankleCntrlSetup'] = {'nameTempl':self.name+'Ankle', 'icone':'cubo', 'size':1, 'color':(0,1,1) }
        self.footDict['ballCntrlSetup'] = {'nameTempl':self.name+'Ball', 'icone':'circuloX', 'size':1.5, 'color':(1,1,0) }
        self.footDict['inCntrlSetup'] = {'nameTempl':self.name+'In', 'icone':'bola', 'size':0.4, 'color':(0,1,1)}
        self.footDict['outCntrlSetup'] = {'nameTempl':self.name+'Out', 'icone':'bola', 'size':0.4, 'color':(0,1,1)}
        self.footDict['rollCntrlSetup'] = {'nameTempl':self.name+'Roll', 'icone':'cubo', 'size':0.4, 'color':(0,0,1)}
        self.footDict['baseCntrlSetup'] = {'nameTempl':self.name+'Base', 'icone':'circuloY', 'size':3, 'color':(0,1,0)}
        self.footDict['slideCntrlSetup'] = {'nameTempl':self.name+'Slide', 'icone':'bola', 'size':0.4, 'color':(1,0,0)}
        self.footDict['jointCntrlSetup'] = {'nameTempl':self.name+'Joint', 'icone':'bola', 'size':0.5, 'color':(1,1,0)}
        self.footDict['toeCntrlSetup'] = {'nameTempl':self.name+'Toe', 'icone':'circuloX', 'size':1.0, 'color':(1,1,0)}
          
        self.footDict['nodeTree'] = {}
        self.footDict['nameConventions'] = None
                
    def doGuide(self,**kwargs):
        self.footGuideDict={'center':[0,0,0],'tip':[3,0,0],'heel':[-1,0,0],'ankle':[0,1,0],'ball':[2,0.5,0],'in':[2,0,-1],'out':[2,0,1]}
        self.footGuideDict.update(kwargs)
        
        guideName=self.footDict['moveallCntrlSetup']['nameTempl']+'_guide' 
        
        if pm.objExists(guideName):
            pm.delete (guideName)
          
        self.footGuideMoveall=pm.group (n=guideName ,em=True)
        
        guideName=self.footDict['centerCntrlSetup']['nameTempl']+'_guide'
        self.centerGuide=pm.spaceLocator (n=guideName, p=(0,0,0))
        self.centerGuide.localScale.set(.2,.2,.2)
        self.centerGuide.displayHandle.set(1)
        
        guideName=self.footDict['tipCntrlSetup']['nameTempl']+'_guide'
        self.tipGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.tipGuide.translate.set(self.footGuideDict['tip'])
        self.tipGuide.localScale.set(.2,.2,.2)
        self.tipGuide.displayHandle.set(1)
                
        guideName=self.footDict['heelCntrlSetup']['nameTempl']+'_guide'
        self.heelGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.heelGuide.translate.set(self.footGuideDict['heel'])
        self.heelGuide.localScale.set(.2,.2,.2)
        self.heelGuide.displayHandle.set(1)
        
        guideName=self.footDict['ankleCntrlSetup']['nameTempl']+'_guide'
        self.ankleGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.ankleGuide.translate.set(self.footGuideDict['ankle'])
        self.ankleGuide.localScale.set(.2,.2,.2)
        self.ankleGuide.displayHandle.set(1)
        
        guideName=self.footDict['ballCntrlSetup']['nameTempl']+'_guide'
        self.ballGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.ballGuide.translate.set(self.footGuideDict['ball'])
        self.ballGuide.localScale.set(.2,.2,.2)
        self.ballGuide.displayHandle.set(1)
        
        guideName=self.footDict['inCntrlSetup']['nameTempl']+'_guide'
        self.inGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.inGuide.translate.set(self.footGuideDict['in'])
        self.inGuide.localScale.set(.2,.2,.2)
        self.inGuide.displayHandle.set(1)
        
        guideName=self.footDict['outCntrlSetup']['nameTempl']+'_guide'
        self.outGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.outGuide.translate.set(self.footGuideDict['out'])
        self.outGuide.localScale.set(.2,.2,.2)
        self.outGuide.displayHandle.set(1)
        
        pm.parent (self.centerGuide,self.tipGuide,self.heelGuide,self.ankleGuide,self.ballGuide,self.inGuide,self.outGuide, self.footGuideMoveall)

    def doRig(self):

        cntrlName=self.footDict['moveallCntrlSetup']['nameTempl']
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
            

        
        center=pm.xform (self.centerGuide, q=True,ws=True, t=True)
        tip=pm.xform (self.tipGuide, q=True,ws=True, t=True)
        ankle=pm.xform (self.ankleGuide, q=True,ws=True, t=True)
        ball=pm.xform (self.ballGuide, q=True,ws=True, t=True)
        
        A=om.MVector(ankle)
        B=om.MVector(center)
        C=om.MVector(tip)
        D=om.MVector(ball)
        
        if self.flipedAxis:
            AB=A-B
            BC=B-C
            AD=A-D
            CD=D-C
        else:
            AB=B-A
            BC=C-B
            AD=D-A 
            CD=C-D
            
        n =BC^AB 
        pm.select(cl=True) 
        
        x = n.normal() ^ AD.normal()
        t = x.normal() ^ n.normal()  
          
        if self.axis=='Y':    
            list = [ n.normal().x, n.normal().y, n.normal().z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, A.x, A.y,A.z,1]
        elif self.axis=='Z':
            list = [ x.x, x.y, x.z, 0,n.normal().x, n.normal().y, n.normal().z, 0,t.x, t.y, t.z, 0, A.x, A.y,A.z,1]
        else:
            list = [ t.x, t.y, t.z, 0,n.normal().x, n.normal().y, n.normal().z, 0, x.x*-1, x.y*-1, x.z*-1, 0, A.x, A.y,A.z,1]
              
        m= om.MMatrix (list)
        j1 = pm.joint()
        pm.xform (j1, m = m, ws=True) 
        pm.makeIdentity (j1, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        x = n.normal() ^ CD.normal()
        t = x.normal() ^ n.normal()  
          
        if self.axis=='Y':    
            list = [ n.normal().x, n.normal().y, n.normal().z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, D.x, D.y,D.z,1]
        elif self.axis=='Z':
            list = [ x.x, x.y, x.z, 0,n.normal().x, n.normal().y, n.normal().z, 0,t.x, t.y, t.z, 0, D.x, D.y,D.z,1]
        else:
            list = [ t.x, t.y, t.z, 0,n.normal().x, n.normal().y, n.normal().z, 0, x.x*-1, x.y*-1, x.z*-1, 0, D.x, D.y,D.z,1]
            
        m= om.MMatrix (list)
        j2 = pm.joint()
        pm.xform (j2, m = m, ws=True) 
        pm.makeIdentity (j2, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        j3 = pm.joint()
        pm.xform (j3, m = m, ws=True)
        pm.xform (j3, t =C, ws=True) 
        pm.makeIdentity (j3, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        ballIkh = pm.ikHandle (sj=j1, ee=j2, sol="ikRPsolver")
        tipIkh = pm.ikHandle (sj=j2, ee=j3, sol="ikRPsolver")
        
        footMoveall=pm.group (em=True,n=cntrlName)
        footMoveall.translate.set(center)
        
        displaySetup= self.footDict['jointCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        j1Cntrl=cntrlCrv(name=cntrlName,obj=j1,connType='parentConstraint', **displaySetup)

        #base cntrl
        displaySetup= self.footDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        baseCntrl=cntrlCrv(name=cntrlName,obj=self.centerGuide, **displaySetup)
        pm.xform (baseCntrl, rp=ankle, ws=True)
        
        #slidePivot
        displaySetup= self.footDict['slideCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        slideCntrl=cntrlCrv(name=cntrlName,obj=self.centerGuide, **displaySetup)
        slideCompensateGrp=pm.group(em=True)
        pm.parent (slideCompensateGrp, slideCntrl, r=True)
        slideMulti=pm.createNode ('multiplyDivide')
        slideCntrl.translate >> slideMulti.input1
        slideMulti.input2.set(-1,-1,-1)
        slideMulti.output >> slideCompensateGrp.translate
        
        # bank cntrls
        displaySetup= self.footDict['inCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        inCntrl = cntrlCrv(name=cntrlName,obj=self.inGuide, **displaySetup)
        
        displaySetup= self.footDict['inCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        outCntrl = cntrlCrv(name=cntrlName,obj=self.outGuide,**displaySetup)
        
        #tip/heel
        displaySetup= self.footDict['tipCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        tipCntrl=cntrlCrv(name=cntrlName,obj=self.tipGuide, **displaySetup)

        displaySetup= self.footDict['heelCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        heelCntrl=cntrlCrv(name=cntrlName,obj=self.heelGuide, **displaySetup)
        
        #toe
        displaySetup= self.footDict['toeCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        toeCntrl=cntrlCrv(name=cntrlName,obj=self.ballGuide, **displaySetup)
        toeCntrl.translate.set(0.5,0,0)
        pm.makeIdentity (toeCntrl, apply=True, r=0, t=1, s=0, n=0, pn=0)
        pm.xform (toeCntrl, rp=(-0.5,0,0), r=True)
        
        #ball
        displaySetup= self.footDict['ballCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        ballCntrl=cntrlCrv(name=cntrlName,obj=self.ballGuide, **displaySetup)
        
        #rollCntrl
        displaySetup= self.footDict['rollCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        rollCntrl=cntrlCrv(name=cntrlName,obj=self.ballGuide, **displaySetup)
        rollCntrl.getParent().translateBy((0,2,0))
        
        #hierarquia
        pm.parent (ballCntrl.getParent(), toeCntrl.getParent(), heelCntrl)
        heelCntrl.getParent().setParent(tipCntrl)
        tipCntrl.getParent().setParent(outCntrl)
        outCntrl.getParent().setParent(inCntrl)
        inCntrl.getParent().setParent(slideCompensateGrp)
        rollCntrl.getParent().setParent(slideCompensateGrp)
        slideCntrl.getParent().setParent(baseCntrl)
        ballIkh[0].setParent (ballCntrl)
        tipIkh[0].setParent (toeCntrl)
        j1Cntrl.getParent().setParent (ballCntrl)
        pm.parent (j1,baseCntrl.getParent(),footMoveall)
        
        #rollCntrl
        rollCntrl.addAttr ('heelLimit',dv=50,k=1,at='float')
        rollBlend=pm.createNode('blendColors')
        rollCntrl.heelLimit >> rollBlend.color1.color1R
        
        #setDrivens
        animUU=pm.createNode('animCurveUU')
        multi=pm.createNode('multDoubleLinear')
        multi.input2.set(-1)
        pm.setKeyframe(animUU, float=float(0), value=float(0), itt='Linear',ott='Linear')
        pm.setKeyframe(animUU, float=float(1.5), value=float(1), itt='Linear',ott='Linear')
        pm.setKeyframe(animUU, float=float(3), value=float(0), itt='Linear',ott='Linear')
        rollCntrl.translateX >> animUU.input
        animUU.output >> rollBlend.blender
        rollBlend.outputR >> multi.input1
        multi.output >> ballCntrl.getParent().rotateZ
        
        animUA=pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(-3), value=float(75), itt='Linear',ott='Linear')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear',ott='Linear')
        rollCntrl.translateX >> animUA.input
        animUA.output >> heelCntrl.getParent().rotateZ
        
        animUA=pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(1.5), value=float(0), itt='Linear',ott='Linear')
        pm.setKeyframe(animUA, float=float(7), value=float(-180), itt='Linear',ott='Linear')
        rollCntrl.translateX >> animUA.input
        animUA.output >> tipCntrl.getParent().rotateZ
        
        animUA=pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear',ott='Linear')
        pm.setKeyframe(animUA, float=float(2.5), value=float(120), itt='Linear',ott='Linear')
        rollCntrl.translateZ >> animUA.input
        animUA.output >> outCntrl.getParent().rotateX
        
        animUA=pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear',ott='Linear')
        pm.setKeyframe(animUA, float=float(-2.5), value=float(-120), itt='Linear',ott='Linear')
        rollCntrl.translateZ >> animUA.input
        animUA.output >> inCntrl.getParent().rotateX
