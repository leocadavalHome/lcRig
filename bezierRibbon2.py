import pymel.core as pm
import maya.api.OpenMaya as om


class RibbonBezierSimple:
    """
        Cria um ribbon bezier de uma superficie somente
        Parametros: 
            name:
            size:
            numJoints:
           
    """ 
    ##IMPLEMENTAR:
    #controle de twist fique liberado pra q o usuario de offset, principalmente no inicio
    #stretch/squash com distancia ja no ribbon
        
    def __init__(self, **kwargs ):
        
        ribbonDict = {}
                
        ribbonDict['size']=kwargs.pop('size', 5)
        ribbonDict['name']=kwargs.pop('name','ribbonBezier')
        ribbonDict['numJnts']=kwargs.pop('numJnts',5)

        self.name = ribbonDict['name']
        self.size = ribbonDict['size']
        self.numJnts = ribbonDict['numJnts']
        
        ribbonDict['cntrlSetup']={'nameTempl':'cntrl','icone':'circuloX','size':0.6,'color':(0,0,1)}       
        ribbonDict['cntrlTangSetup']={'nameTempl':'cntrl','icone':'bola','size':0.3,'color':(0,1,1)}        
        ribbonDict['cntrlExtraSetup']={'nameTempl':'cntrlExtra','icone':'circuloX','size':0.2}        
        
                   
    def doRig(self): 
        anchorList = []
        cntrlList =[]
        locList =[]
        
        if pm.objExists(self.name+'NoMove'):
            pm.delete (self.name+'NoMove')
        if pm.objExists(self.name+'MoveAll'):
            pm.delete (self.name+'MoveAll')
                           
        ###Estrutura que nao deve ter transformacao       
        noMoveSpace = pm.group (empty=True, n=self.name+'NoMove')
        noMoveSpace.visibility.set(0)
        noMoveBend1 = pm.nurbsPlane ( p=(self.size*0.5,0,0), ax=(0,0,1), w=self.size, lr = 0.1 , d = 3, u =5, v =1)        
        noMoveCrvJnt = pm.curve ( bezier=True, d=3, p=[(self.size*-0.5,0,0),(self.size*-0.4,0,0),(self.size*-0.1,0,0),(0,0,0),(self.size*0.1,0,0),(self.size*0.4,0,0),(self.size*0.5,0,0)], k=[0,0,0,1,1,1,2,2,2])        
        noMoveCrvJnt.translate.set(self.size*0.5,0,0) 
        
        #Deformers das superficies noMove
        twist1 = pm.nonLinear(noMoveBend1[0],  type='twist')         #twist das superficies noMove
        twist1[1].rotateZ.set(90)
        #IMPLEMENTAR O TWIST DO MEIO
        
        wireDef = pm.wire (noMoveBend1[0], w=noMoveCrvJnt, dds=[(0, 50)]) #Wire das superficies noMove
        wireDef[0].rotation.set(1) #seta rotacao pra acontecer
        baseWire = [x for x in wireDef[0].connections() if 'BaseWire' in x.name()]
        pm.group (baseWire, noMoveCrvJnt, noMoveBend1[0], p=noMoveSpace)
        pm.parent (twist1[1], noMoveSpace) 
        
        ###Estrutura que pode ser movida
        cntrlsSpace = pm.group (empty=True, n=self.name+'MoveAll')
        bendSurf1 = pm.nurbsPlane ( p=(self.size*-0.5,0,0), ax=(0,0,1), w=self.size*0.5, lr = .1 , d = 3, u =5, v =1)
        
        blend1 = pm.blendShape (noMoveBend1[0], bendSurf1[0])
        pm.blendShape (blend1, e=True, w=[(0, 1)])
        pm.parent (bendSurf1[0], cntrlsSpace ) 
        
        ##Cntrls                
        for i in range (0, 7):
            anchor = pm.cluster (noMoveCrvJnt.name()+'.cv['+str(i)+']')
            clsHandle = anchor [1]
            anchorGrp = pm.group (em=True, n='clusterGrp'+str (i))
            anchorDrn = pm.group (em=True, n='clusterDrn'+str (i),p=anchorGrp)
            pos = pm.xform (anchor, q=True, ws=True, rp=True)  
            pm.xform (anchorGrp, t=pos, ws=True)
            pm.parent (anchor[1], anchorDrn)   
            anchorList.append (anchor[1])
                                    
            if i==0 or i==3 or i==6:
                displaySetup= ribbonDict['cntrlSetup'].copy()                               
                cntrlName = displaySetup['nameTempl']+str(i)           
                cntrl = cntrlCrv (name=cntrlName, obj=anchor[1],**displaySetup)
            else:
                displaySetup= ribbonDict['cntrlTangSetup'].copy()                               
                cntrlName = displaySetup['nameTempl']+str(i) 
                cntrl = cntrlCrv (name=cntrlName, obj=anchor[1],**displaySetup)
                        
            #Nao pode fazer conexao na criacao do controle, pois tera conexao direta
            pm.xform (cntrl.getParent(), t=pos, ws=True)
            
            #estrutura de buffers para conexao direta
            auxLocGrp = pm.group (em=True)
            auxLoc = pm.group (em=True, p=auxLocGrp) 
            pm.xform (auxLocGrp, t=pos, ws=True)
            loc = pm.PyNode (auxLoc)
            
            if i==1 or i==4:
                pm.xform (anchorGrp, s=(-1,1,1), r=True)
                pm.xform (cntrl.getParent(), s=(-1,1,1), r=True)
                pm.xform (loc.getParent(), s=(-1,1,1), r=True)
            
            #Conexoes dos buffers cm os clusters e com os controles
            pm.parentConstraint (cntrl, loc )                    
            loc.translate >> anchorDrn.translate
            loc.rotate >> anchorDrn.rotate
            cntrlList.append(cntrl)
            locList.append (loc)
        
        cntrlsSpace.addAttr ('cntrlsVis', at='double', dv=1, k=False, h=True)
        cntrlsSpace.addAttr ('extraCntrlsVis', at='double', dv=0, k=False, h=True)            
        cntrlList[0].addAttr ('twist', at='double', dv=0, k=True)
        cntrlList[0].addAttr ('stretchDist', at='double', dv=0, k=True)
        cntrlList[0].addAttr ('autoVolumStregth', at='double', dv=0, k=True)
        cntrlList[3].addAttr ('twist', at='double', dv=0, k=True)
        cntrlList[3].addAttr ('autoVolume', at='double', dv=0, k=True)
        cntrlList[6].addAttr ('twist', at='double', dv=0, k=True)
        cntrlList[6].addAttr ('stretchDist', at='double', dv=0, k=True)
        cntrlList[6].addAttr ('autoVolumStregth', at='double', dv=0, k=True)
        
        cntrlList[0].twist >> twist1[0].endAngle
        cntrlList[3].twist >> twist1[0].startAngle
        #cntrlList[3].twist >> twist2[0].endAngle
        #cntrlList[6].twist >> twist2[0].startAngle 
        
        #hierarquia                
        pm.parent (anchorList[1].getParent(2), anchorList[0])       
        pm.parent (anchorList[5].getParent(2), anchorList[6]) 
        pm.parent (anchorList[2].getParent(2),anchorList[4].getParent(2), anchorList[3])
        pm.parent (cntrlList[1].getParent(), cntrlList[0])       
        pm.parent (cntrlList[5].getParent(), cntrlList[6]) 
        pm.parent (cntrlList[2].getParent(), cntrlList[4].getParent(), cntrlList[3]) 
        pm.parent (cntrlList[3].getParent(), cntrlList[0].getParent(), cntrlList[6].getParent(), cntrlsSpace)
        pm.parent (locList[1].getParent(), locList[0])       
        pm.parent (locList[5].getParent(), locList[6]) 
        pm.parent (locList[2].getParent(),locList[4].getParent(), locList[3]) 
        pm.parent (locList[3].getParent(), locList[0].getParent(),locList[6].getParent(), cntrlsSpace)
        pm.parent (anchorList[3].getParent(2), anchorList[0].getParent(2),anchorList[6].getParent(2), noMoveSpace)        
        
        #Skin joints do ribbon
        skinJntsGrp = pm.group (em=True)
        follGrp = pm.group (em=True)
        
        #cria ramps para controlar o perfil de squash e stretch       
        ramp1 = pm.createNode ('ramp')
        ramp1.attr('type').set(1)
        
        #ramp2 = pm.createNode ('ramp')
        #ramp2.attr('type').set(1)
        
        expre1 = "float $dummy = "+ramp1.name()+".outAlpha;float $output[];float $color[];"
        #expre2 = "float $dummy = "+ramp2.name()+".outAlpha;float $output[];float $color[];"
        
        extraCntrlsGrp = pm.group (em=True,r=True, p=cntrlsSpace) 
        
        #loop pra fazer os colocar o numero escolhido de joints ao longo do ribbon.
        #cria tmb node tree pro squash/stretch
        #e controles extras 
          
        for i in range (1,self.numJnts+1):
            #cria estrutura pra superficie 1
            pm.select (cl=True)
            jnt1 = pm.joint (p=(0,0,0))
            
            displaySetup = ribbonDict['cntrlExtraSetup'].copy()                               
            cntrlName = displaySetup['nameTempl']+'A'+str(i) 
            cntrl1 = cntrlCrv (name = cntrlName, obj=jnt1, connType='parentConstraint',**displaySetup)   
                  
            #node tree
            blend1A = pm.createNode ('blendTwoAttr')
            blend1B = pm.createNode ('blendTwoAttr')
            gammaCorr1 = pm.createNode ('gammaCorrect')    
            cntrlList[0].attr ('autoVolumStregth') >> gammaCorr1.gammaX
            cntrlList[0].attr ('stretchDist') >> gammaCorr1.value.valueX
            blend1A.input[0].set (1)
            gammaCorr1.outValueX >> blend1A.input[1]
            blend1B.input[0].set(1)
            blend1A.output >> blend1B.input[1];
            cntrlList[3].attr('autoVolume') >> blend1B.attributesBlender
            blend1B.output >> cntrl1.getParent().scaleY
            blend1B.output >> cntrl1.getParent().scaleZ  
            #expressao que le a rampa para setar valores da escala de cada joint quando fizer squash/stretch        
            expre1=expre1+"$color = `colorAtPoint -o RGB -u "+str ((i/float(self.numJnts))-(1/float(self.numJnts)))+" -v 0.5 "+ramp1.name()+" `;$output["+str (i)+"] = $color[0];"+blend1A.name()+".attributesBlender=$output["+str (i)+"];"            
               
            #prende joints nas supeficies com follicules
            foll1= self.attachObj (cntrl1.getParent(), bendSurf1[0], (i/float(self.numJnts))-(1/float(self.numJnts)), 0.5, 4)
            
            pm.parent (cntrl1.getParent(),extraCntrlsGrp)
            pm.parent (jnt1, skinJntsGrp)
            pm.parent (foll1, follGrp)       
        
        #seta expressoes para so serem avaliadas por demanda             
        pm.expression (s=expre1, ae=False)
        
        pm.parent (skinJntsGrp, cntrlsSpace)
        pm.parent (follGrp, noMoveSpace)
        
        #hideCntrls
        pm.toggle (bendSurf1[0], g=True)
        #skinJntsGrp.visibility.set(0)
        cntrlsSpace.extraCntrlsVis >> extraCntrlsGrp.visibility
        cntrlsSpace.cntrlsVis >> cntrlList[0].getParent().visibility
        cntrlsSpace.cntrlsVis >> cntrlList[3].getParent().visibility
        cntrlsSpace.cntrlsVis >> cntrlList[6].getParent().visibility
              
        #povoa ribbon Dict        
        ribbonDict['name']= 'bezierRibbon'
        ribbonDict['ribbonMoveAll']= cntrlsSpace
        for i in range (0, 7):
            ribbonDict['cntrl'+str(i)] = cntrlList[i]

    #Metodo para colar objetos por follicules                    
    def attachObj (self,obj, mesh, u, v, mode=1):
        foll = pm.createNode ('follicle')
        follDag = foll.firstParent()
        mesh.worldMatrix[0] >> foll.inputWorldMatrix
        if pm.objectType (mesh) == 'mesh':
            mesh.outMesh >> foll.inputMesh
        else:
            mesh.local >> foll.inputSurface
              
        foll.outTranslate >> follDag.translate
        foll.outRotate >> follDag.rotate
        follDag.translate.lock()
        follDag.rotate.lock()
        follDag.parameterU.set (u)
        follDag.parameterV.set (v)
        if mode==1:
            pm.parent (obj, follDag)
        elif mode==2:
            pm.parentConstraint (follDag, obj, mo=True)
        elif mode==3:
            pm.pointConstraint (follDag, obj, mo=True)
        elif mode==4:
            pm.parentConstraint (follDag, obj, mo=False)
        return follDag       
    
    #Metodo para descobrir ponto mais proximo da superficie onde devem objeto deve ser colado      
    def hookJntsOnCurve(self,jntList, upList, jntCrv, upCrv):
        jntNPoC = pm.createNode ('nearestPointOnCurve')
        jntGrpA  = pm.group (empty=True)
        jntCrv.worldSpace[0] >> jntNPoC.inputCurve
        
        jntGrpA.translate >> jntNPoC.inPosition
    
        upNPoC = pm.createNode ('nearestPointOnCurve')
        upGrpA  = pm.group (empty=True)
        upCrv.worldSpace[0] >> upNPoC.inputCurve
        upGrpA.translate >> upNPoC.inPosition
        
        for jnt, up in zip(jntList, upList):
            wp= pm.xform (jnt, t=True, ws=True, q=True)
            pm.xform (jntGrpA, t=wp, ws=True)
            hookPoci = pm.createNode ('pointOnCurveInfo')
            jntCrv.worldSpace[0] >> hookPoci.inputCurve
            hookPoci.position >> jnt.translate
            hookPar = jntNPoC.parameter.get()
            hookPoci.parameter.set(hookPar)
            pm.tangentConstraint (jntCrv, jnt, aimVector=(-1, 0, 0),upVector=(0,1, 0),worldUpType="object",worldUpObject =up )
    
            wp= pm.xform (up, t=True, ws=True, q=True)
            pm.xform (upGrpA, t=wp, ws=True)
            hookPoci = pm.createNode ('pointOnCurveInfo')
            upCrv.worldSpace[0] >> hookPoci.inputCurve
            hookPoci.position >> up.translate
            hookPar = upNPoC.parameter.get()
            hookPoci.parameter.set(hookPar)
    
        pm.delete (upNPoC, upGrpA , jntNPoC, jntGrpA)

class AimTwistDivider:
    """
        Cria um sistema q orienta o grupo mid segundo a posicao e twist de start e end.
        fazendo a media
        Limitado a 180 graus
        Parametros: 
            start:
            mid:
            end:
           
    """ 
    ##IMPLEMENTAR:
    #outras orientações. Atualmente somente X down
        
    def __init__(self, start=None, end=None, mid=None): 
        if not start:   
            start = pm.group (em=True, n='start')
        if not end:
            end = pm.group (em=True, n='end')
        if not mid:
            mid = pm.group (em=True, n='mid') 
            
        #cria nodes    
        vecProd1=pm.createNode ('vectorProduct')
        vecProd2=pm.createNode ('vectorProduct')
        vecProd3=pm.createNode ('vectorProduct')
        vecProd4=pm.createNode ('vectorProduct')
        add1=pm.createNode ('plusMinusAverage')
        add2=pm.createNode ('plusMinusAverage')
        matrix4by4=pm.createNode ('fourByFourMatrix')
        decomposeMatrix1 = pm.createNode ('decomposeMatrix')
        decomposeMatrix2 = pm.createNode ('decomposeMatrix') 
        decomposeMatrix3 = pm.createNode ('decomposeMatrix')
        decomposeMatrix3 = pm.createNode ('decomposeMatrix')
        multiMatrix =  pm.createNode ('multMatrix')
        
        
        #ver se funciona so com worldMatrix
        start.worldMatrix[0] >> vecProd1.matrix
        vecProd1.input1.set ((0,1,0))
        vecProd1.operation.set (3)
        end.worldMatrix[0] >> vecProd2.matrix
        vecProd2.input1.set ((0,-1,0))
        vecProd2.operation.set (3)
        
        vecProd1.output >> add1.input3D[0]
        vecProd2.output >> add1.input3D[1]
        add1.operation.set (2)
        
        start.worldMatrix[0] >> decomposeMatrix1.inputMatrix
        decomposeMatrix1.outputTranslate >> add2.input3D[1]

        end.worldMatrix[0] >> decomposeMatrix2.inputMatrix
        decomposeMatrix2.outputTranslate >> add2.input3D[0]
         
        add1.output3D >> vecProd3.input2
        add2.output3D >> vecProd3.input1
        vecProd3.operation.set(2)
        
        vecProd3.output >> vecProd4.input1
        add2.output3D >> vecProd4.input2
        vecProd4.operation.set(2)
        
        add2.output3Dx >> matrix4by4.in00
        add2.output3Dy >> matrix4by4.in01
        add2.output3Dz >> matrix4by4.in02
        
        vecProd4.outputX >> matrix4by4.in10
        vecProd4.outputY >> matrix4by4.in11
        vecProd4.outputZ >> matrix4by4.in12
        
        matrix4by4.output >> multiMatrix.matrixIn[0]
        mid.parentInverseMatrix[0] >> multiMatrix.matrixIn[1]
        multiMatrix.matrixSum >> decomposeMatrix3.inputMatrix

        decomposeMatrix3.outputRotate >> mid.rotate
        pm.pointConstraint (start,end,mid,mo=False)
    
    
x=  AimTwist()  
        
    
    
