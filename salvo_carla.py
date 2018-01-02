import pymel.core as pm
import maya.api.OpenMaya as om

class Finger:
    def __init__(folds=2, axis='X', flippedAxis=False)
        self.folds=folds
        self.axis=axis
        self.flipedAxis =flippedAxis


    def doRig():
        base=pm.xform ('base', q=True,ws=True, t=True)
        tip=pm.xform ('tip', q=True,ws=True, t=True)
        palm=pm.xform ('palm', q=True,ws=True, t=True)
        fold1=pm.xform ('fold1', q=True,ws=True, t=True)
        
        #coordenadas dos 3 guides default para calculo da normal do plano de rotacao do dedo
        A=om.MVector(base)
        B=om.MVector(fold1)
        C=om.MVector(tip)
        
        if self.flipedAxis:
            AB=A-B
            BC=B-C
        else:
            AB=B-A
            BC=C-B
        
        n = AB^BC
          
        #conforme o numero de dobras, especifica as guides
        #atualmente podem ser 0,1 ou 2 dobras
        if self.folds==2:
            fold2=pm.xform ('fold2', q=True,ws=True, t=True)
            guide=[palm,base,fold1,fold2,tip]
        elif self.folds==1:
            guide=[palm,base,fold1,tip]
        elif self.folds==0:
            guide=[palm,base,tip]
        
        #cria os joints conforme a orientacao
        fingerJnts = []  
        pm.select(cl=True) 
        for i in range(0,len(guide)-1):
            A=om.MVector(guide[i])
            B=om.MVector(guide[i+1])
            if self.flipedAxis:
                AB=A-B
            else:
                AB=B-A   
            x = n.normal() ^ AB.normal()
            t = x.normal() ^ n.normal()  
              
            if self.axis=='Y':    
                list = [ n.normal().x, n.normal().y, n.normal().z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, A.x, A.y,A.z,1]
            elif self.axis=='Z':
                list = [ x.x, x.y, x.z, 0,n.normal().x, n.normal().y, n.normal().z, 0,t.x, t.y, t.z, 0, A.x, A.y,A.z,1]
            else:
                list = [ t.x, t.y, t.z, 0,n.normal().x, n.normal().y, n.normal().z, 0, x.x*-1, x.y*-1, x.z*-1, 0, A.x, A.y,A.z,1]
                 
            m= om.MMatrix (list)
            j1 = pm.joint()
            fingerJnts.append(j1)
            pm.xform (j1, m = m, ws=True) 
            pm.makeIdentity (j1, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        j1 = pm.joint()
        fingerJnts.append(j1)
        pm.xform (j1, m = m, ws=True)
        pm.xform (j1, t =C, ws=True) 
        pm.makeIdentity (j1, apply=True, r=1, t=0, s=1, n=0, pn=0)
        last=None
        cntrl0= cntrlCrv(connType='orientConstraint',obj=fingerJnts[0] )    
        cntrl1 = cntrlCrv(connType='orientConstraint',obj=fingerJnts[1] )
        pm.parent(cntrl1.getParent(),cntrl0)
        last=cntrl1
        
        if self.folds>0:
            cntrl1.addAttr('curl1',k=1,at=float,dv=0)
            cntrl2 = cntrlCrv(connType='orientConstraint', obj=fingerJnts[2],offsets=1)
            pm.parent (cntrl2.getParent(2),cntrl1)
            cntrl1.curl1 >> cntrl2.getParent().rotateY
        if self.folds > 1:
            cntrl1.addAttr('curl2',k=1,at=float,dv=0)
            cntrl3 = cntrlCrv(connType='orientConstraint', obj=fingerJnts[3],offsets=1)
            pm.parent (cntrl3.getParent(2),cntrl2)
            cntrl1.curl2 >> cntrl3.getParent().rotateY
            
        fingerMoveall = pm.group (em=True)
        pm.xform (fingerMoveall,t=palm,ws=True)
        pm.parent (fingerJnts[0],cntrl0.getParent(),fingerMoveall)

    #guide 
    def doGuide(self):
        fingerGuideMoveall = pm.group(em=True)
        palmGuide = pm.spaceLocator (p=(0,0,0))
        baseGuide = pm.spaceLocator (p=(0,0,0))
        baseGuide.translate.set(4,0,0)
        tipGuide = pm.spaceLocator (p=(0,0,0))
        tipGuide.translate.set(12,0,0)
        pm.parent (tipGuide, baseGuide,palmGuide, fingerGuideMoveall)
        
        if self.folds==2:
            fold1Guide = pm.spaceLocator (p=(0,0,0))        
            fold1GuideGrp = pm.group(fold1Guide)
            fold1GuideGrp.translate.set(7,0,0)
         
            fold2Guide = pm.spaceLocator (p=(0,0,0))        
            fold2GuideGrp = pm.group(fold2Guide)
            fold2GuideGrp.translate.set(10,0,0) 
        
            pm.aimConstraint(fold1Guide,baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(fold2Guide,fold1Guide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(fold2Guide,tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(tipGuide, fold2GuideGrp, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
        
            cns=pm.pointConstraint( baseGuide, tipGuide , fold1GuideGrp, mo=False)
            print cns
            weightAttr = cns.target.connections(p=True, t='pointConstraint')
            pm.setAttr (weightAttr[0],0.6)
            pm.setAttr (weightAttr[1],0.4)
            pm.pointConstraint(fold1Guide,tipGuide, fold2GuideGrp, mo=False)
            pm.parent (fold1GuideGrp,fold2GuideGrp, fingerGuideMoveall)
            
        elif self.folds==1:
            fold1Guide = pm.spaceLocator (p=(0,0,0))        
            fold1GuideGrp = pm.group(fold1Guide)
            fold1GuideGrp.translate.set(7,0,0)
         
            pm.aimConstraint(fold1Guide, baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(tipGuide,fold1GuideGrp, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(fold1Guide,tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            cns=pm.pointConstraint(baseGuide, tipGuide , fold1GuideGrp, mo=False)
            weightAttr = cns.target.connections(p=True, t='pointConstraint')  
            pm.parent (fold1GuideGrp, fingerGuideMoveall)
            
        elif self.folds==0:    
            fold1Guide = pm.spaceLocator (p=(0,0,0))        
            fold1GuideGrp = pm.group(fold1Guide)
            fold1GuideGrp.translate.set(7,0,0)
         
            pm.aimConstraint(fold1Guide, baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(tipGuide,fold1GuideGrp, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(fold1Guide,tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            cns=pm.pointConstraint(baseGuide, tipGuide , fold1GuideGrp, mo=False)
            weightAttr = cns.target.connections(p=True, t='pointConstraint')  
            fold1Guide.translate.set(0,0.1,0)
            fold1Guide.visibility.set(0)
            pm.parent (fold1GuideGrp, fingerGuideMoveall)