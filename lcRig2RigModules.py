import pymel.core as pm
import maya.api.OpenMaya as om

class Limb():
    """
        Cria um Limb
        Parametros: 
            name (string): nome do novo limb            
            ikCntrl (string): nome 
            startCntrl (string): nome
            midCntrl (string): nome
            endCntrl (string): nome
            poleCntrl (string): nome
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            handJoint (boolean): se exite joint da mao
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
                 
    """  
    ## IMPLEMENTAR:
    #  setagem de parametros e formatacao de nomes 
    #  grupos de spaceSwitch acima dos controles
 
    #self.twoJoints=False RETIREI CODIGO DE ARTICULACAO DE DOIS JOINTS. PRECISA FAZER IMPLEMENTACAO COMPLETA 
                 
    def __init__ (self,name='limb',axis='X',flipAxis=False,handJoint=True, **kwargs):

        self.limbDict={'name':name,
                       'ikCntrl':None,
                       'startCntrl':None,
                       'midCntrl':None,
                       'endCntrl':None,
                       'poleCntrl':None,
                       'flipAxis':flipAxis,
                       'handJoint':handJoint,
                       'axis':axis,
                       'moveAll1Cntrl':None} #valores default

        self.limbDict.update(kwargs) # atualiza com o q foi entrado
        self.GuideColor=(1,0,1)
        self.name = name
        self.flipAxis = flipAxis
        self.axis = axis
        self.handJoint = handJoint
        self.limbGuideDict = {'start':[0,0,0], 'mid':[3,0,-1],'end':[6,0,0], 'hand':[7,0,0]} 
        self.startGuide=None   
        self.endGuide=None   
        self.midGuide=None   
        self.handGuide=None
        self.limbGuideMoveall=None
                   
        ##setups visuais dos controles
        self.limbDict['moveAll1CntrlSetup']={'nameTempl':self.name+'moveAll1', 'icone':'circuloX','size':1.8,'color':(1,1,0) }    
        self.limbDict['ikCntrlSetup'] = {'nameTempl':self.name+'Ik', 'icone':'bola','size':1,'color':(1,1,0) }    
        self.limbDict['startCntrlSetup'] = {'nameTempl':self.name+'FkStart', 'icone':'cubo','size':0.5,'color':(0,1,0) }
        self.limbDict['midCntrlSetup'] = {'nameTempl':self.name+'FkMid', 'icone':'cubo', 'size':0.5, 'color':(0,1,0)}
        self.limbDict['endCntrlSetup'] = {'nameTempl':self.name+'FkEnd', 'icone':'cubo', 'size':0.5, 'color':(0,1,0)}
        self.limbDict['poleVecCntrlSetup'] = {'nameTempl':self.name+'PoleVec', 'icone':'bola', 'size':0.4, 'color':(1,0,0)}
        self.limbDict['nodeTree'] = {}
        self.limbDict['nameConventions'] = None
        ##IMPLEMENTAR padroes de nome 



    def doGuide(self,**kwargs): 
        self.limbGuideDict.update(kwargs)
         ## cria guia se não existir  

        if pm.objExists(self.name+'Moveall_guide'):
            pm.delete (self.name+'Moveall_guide')
        
        self.limbGuideMoveall=pm.group(n=self.name+'Moveall_guide', em=True)
        self.startGuide = pm.spaceLocator (n=self.name+'Start_guide', p=(0,0,0))
        pm.xform (self.startGuide, t=self.limbGuideDict['start'], ws=True)
        self.startGuide.displayHandle.set(1)
        self.midGuide = pm.spaceLocator (n=self.name+'Mid_guide', p=(0,0,0))
        pm.xform (self.midGuide, t=self.limbGuideDict['mid'], ws=True)
        self.midGuide.displayHandle.set(1)
        self.endGuide = pm.spaceLocator (n=self.name+'End_guide', p=(0,0,0))
        pm.xform (self.endGuide, t=self.limbGuideDict['end'], ws=True)
        self.endGuide.displayHandle.set(1)
        
        pm.parent (self.startGuide, self.midGuide, self.endGuide, self.limbGuideMoveall)
               
        if self.handJoint:
            self.handGuide = pm.spaceLocator (n=self.name+'Hand_guide', p=(0,0,0))
            pm.xform (self.handGuide, t=self.limbGuideDict['hand'], ws=True)
            pm.parent (self.handGuide, self.endGuide)
            self.handGuide.displayHandle.set(1)
            
        #cria a curva da direcao do plano
        arrow=cntrlCrv(obj=self.startGuide,name=self.name+'PlaneDir',icone='seta', size=.35, color=(0,1,1))
        arrow.getParent().setParent(self.startGuide)
        pm.aimConstraint(self.endGuide,arrow, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 0, -1),worldUpObject=self.midGuide, worldUpType='object')

                      
    def doRig(self):
        if not self.limbGuideMoveall:
            self.doGuide()
            
        #apagar todos os node ao reconstruir                      
        if pm.objExists(self.name+'Moveall'):
            pm.delete (self.name+'Moveall')
            
        #Cria o grupo moveAll
        limbMoveAll = pm.group(empty=True, n=self.name+'Moveall')
        limbMoveAll.addAttr('ikfk', at='float',min=0, max=1,dv=1, k=1)

        
        #define pontos do guide como vetores usando api para faciitar os calculos
        p1 = pm.xform (self.startGuide, q=True, t=True, ws=True)
        p2 = pm.xform (self.midGuide, q=True, t=True, ws=True)
        p3 = pm.xform (self.endGuide, q=True, t=True, ws=True)
        
        A= om.MVector(p1)
        B= om.MVector(p2)
        C= om.MVector(p3)
        
        if self.handJoint:
            p4=pm.xform (self.handGuide, q=True, t=True, ws=True)
            D=om.MVector(p4)
        
        #Calculando a normal do plano definido pelo guide
        #invertendo inverte a direcao do eixo ao longo do vetor        
        if self.flipAxis:
            AB = A-B
            BC = B-C
            CD = C-D
        else:
            AB = B-A
            BC = C-B
            CD = D-C
            
        n = BC^AB
        
        m = orientMatrix (mvector=AB,normal=n,pos=A, axis=self.axis)            
        #cria joint1
        pm.select(cl=True)
        self.startJnt = pm.joint()
        pm.xform (self.startJnt, m = m, ws=True) 
        pm.makeIdentity (self.startJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
        
        #cria joint2
        #criando a matriz do joint conforme a orientacao setada
        m = orientMatrix (mvector=BC,normal=n,pos=B, axis=self.axis)  
        pm.select(cl=True)
        self.midJnt= pm.joint()
        pm.xform (self.midJnt, m = m, ws=True) 
        pm.makeIdentity (self.midJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
        
        #cria joint3
        #aqui so translada o joint, usa a mesma orientacao
        pm.select(cl=True)
        self.endJnt=pm.joint()
        pm.xform (self.endJnt, m = m, ws=True) 
        pm.xform (self.endJnt, t= C, ws=True)
        pm.makeIdentity (self.endJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
        
        #hierarquia
        pm.parent (self.midJnt, self.startJnt)
        pm.parent (self.endJnt, self.midJnt)
        self.startJnt.setParent (limbMoveAll)
        
        ##joint4(hand) se estiver setado nas opcoes      
        if self.handJoint:
            #joint4
            # Faz a orientacao do ultimo bone independente da normal do braco
            # Se o cotovelo estiver para frente inverte a normal
            # limitacao: se o limb for criado no eixo Z o calculo nao eh preciso                     
            if self.flipAxis:
                if n.y<0:
                    Z=om.MVector(0,0,1)
                else:
                    Z=om.MVector(0,0,-1)
            else:
                if n.y>0:
                    Z=om.MVector(0,0,-1)
                else:
                    Z=om.MVector(0,0,1)    
            n=CD^Z            
           
            m = orientMatrix (mvector=CD,normal=n,pos=C, axis=self.axis)              
            pm.select(cl=True)
            self.handJnt= pm.joint()
            pm.xform (self.handJnt, m = m, ws=True) 
            pm.makeIdentity (self.handJnt, apply=True, r=1, t=0, s=0, n=0, pn=0) 
            
            #cria joint5 e so move
            pm.select(cl=True)
            self.handTipJnt=pm.joint()
            pm.xform (self.handTipJnt, m = m, ws=True) 
            pm.xform (self.handTipJnt, t=D, ws=True)
            pm.makeIdentity (self.handTipJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)        
            
            #hierarquia        
            pm.parent (self.handJnt, self.endJnt)
            pm.parent (self.handTipJnt, self.handJnt)            
                
        ##Estrutura FK
        if self.axis=='Y'  or self.axis=='Z' or self.axis=='X':
            axisName=self.axis
        else:
            axisName='X'
        
        displaySetup= self.limbDict['moveAll1CntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']

        moveAll1Cntrl = cntrlCrv( name = cntrlName, obj= self.startJnt , **displaySetup)
        
        displaySetup= self.limbDict['endCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                  
        endCntrl = cntrlCrv (name=cntrlName, obj=self.startJnt,connType='parentConstraint', **displaySetup )
        
        endCntrl.addAttr('manualStretch', at='float',min=.1,dv=1, k=1)
        
        displaySetup=self.limbDict['midCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        midCntrl = cntrlCrv (name=cntrlName,obj=self.midJnt,connType = 'orientConstraint',**displaySetup)
        midCntrl.addAttr('manualStretch', at='float',min=.1,dv=1, k=1)
        
        pm.pointConstraint (self.midJnt, midCntrl.getParent(), mo=True)
        
        ##Estrutura IK
        ikH = pm.ikHandle (sj=self.startJnt, ee=self.endJnt, sol="ikRPsolver")

        displaySetup=self.limbDict['ikCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        ikCntrl = cntrlCrv(name = cntrlName, obj=ikH[0],**displaySetup)
        
        #orienta o controle ik de modo a ter aproximadamente a orientacao do eixo global
        #mas aponta o eixo X para a ponta do ultimo bone               
        mat=pm.xform (ikCntrl.getParent(), q=True, m=True, ws=True)
        matrix= om.MMatrix (mat)
        Zcomponent = om.MVector (0,0,-1)
        Zaxis = matrix * Zcomponent
        normal = CD^Zaxis

        #CD eh o vetor de direcao do ultimo joint                
        ori = orientMatrix(CD, normal, C, self.axis)       
        pm.xform (ikCntrl.getParent(), m=ori, ws=True)
        ikH[0].setParent(ikCntrl)
        ikCntrl.addAttr ('pin', at='float',min=0, max=1,dv=0, k=1)
        ikCntrl.addAttr ('bias', at='float',min=-0.9, max=0.9, k=1)
        ikCntrl.addAttr ('autoStretch', at='float',min=0, max=1,dv=1, k=1)
        ikCntrl.addAttr ('manualStretch', at='float',dv=1, k=1)
        ikCntrl.addAttr ('twist', at='float',dv=0, k=1)        
            
        #pole vector
        displaySetup=self.limbDict['poleVecCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        poleVec = cntrlCrv(name=cntrlName, obj=self.midJnt,**displaySetup)
        
        #calcula a direcao q deve ficar o polevector
        BA=B-A
        CA=C-A
        U=BA*CA.normal()
        dist=CA.length()
        V=U/dist*dist
        T=A+V*CA.normal()
        D=B-T
        Pole=(D.normal()*1.2)+B
        
        #test=pm.spaceLocator (p=(0,0,0)) # locator de teste de onde calculou o ponto mais proximo
        #pm.xform (test, t=T)
        
        pm.xform (poleVec.getParent() , t=Pole) 
        pm.xform (poleVec.getParent() , ro=(0,0,0)) 
        pm.poleVectorConstraint (poleVec, ikH[0])
        pm.parent (midCntrl.getParent(), endCntrl)
        pm.parent (endCntrl.getParent(), moveAll1Cntrl)
        pm.parent (moveAll1Cntrl.getParent(), poleVec.getParent(), ikCntrl.getParent(), limbMoveAll)

        #handCntrls se houver
        if self.handJoint:
            displaySetup=self.limbDict['startCntrlSetup']
            cntrlName=displaySetup['nameTempl']
            startCntrl = cntrlCrv (name=cntrlName, obj=self.handJnt,**displaySetup)
            buf=pm.group (em=True)
            matrix=pm.xform (self.handJnt, q=True, ws=True, m=True)
            pm.xform (buf, m=matrix, ws=True)
            pm.parent (buf,ikCntrl)
            handCnst = pm.orientConstraint (buf,startCntrl, self.handJnt, mo=False)
            pm.pointConstraint (self.endJnt,startCntrl.getParent(), mo=True)
            pm.parent (startCntrl.getParent(), midCntrl)
        
        #display
        ikH[0].visibility.set(0)
               
        #grupos de stretch
        startGrp = pm.group (empty=True)
        endGrp=pm.group (empty=True)
        pm.parent (endGrp,ikCntrl,r=True)
        pm.xform (startGrp , t=p1, ws=True)
        pm.parent (startGrp,endCntrl)
        
        ##NODE TREE#######               
        #Pin
        p5 = pm.xform (poleVec.getParent(), q=True, t=True, ws=True)
        E=om.MVector (p5)
        
        AE = A - E
        CE = E - C
        distMax=AB.length()+BC.length() #distancia somada dos bones    
        pinScaleJnt1 = AE.length()/AB.length()
        pinScaleJnt2 = CE.length()/BC.length()
               
        pinDist1 = pm.createNode ('distanceBetween',n='pinDist1') #distance do pole vector a ponta do joint1
        pinDist2 = pm.createNode ('distanceBetween',n='pinDist2') #distance do pole vector a ponta do joint2
        pinNorm1 = pm.createNode ('multiplyDivide',n='pinNorm1')  #normalizador distancia1 para escala
        pinNorm2 = pm.createNode ('multiplyDivide',n='pinNorm2')  #normalizador distancia2 para escala
        pinMultiScale1 = pm.createNode ('multDoubleLinear',n='pinMultiScale1') #multiplicador da distancia inicial pela escala Global
        pinMultiScale2 = pm.createNode ('multDoubleLinear',n='pinMultiScale2') #multiplicador da distancia inicial pela escala Global
        pinMultiOffset1 = pm.createNode ('multDoubleLinear',n='pinMultiOffset1') #multiplicador escala para chegar ao pole vec pela escala Global
        pinMultiOffset2 = pm.createNode ('multDoubleLinear',n='pinMultiOffset2') #multiplicador escala para chegar ao pole vec pela escala Global
        pinMulti1 = pm.createNode ('multDoubleLinear',n='pinMulti1') #multiplicador do normalizador
        pinMulti2 = pm.createNode ('multDoubleLinear',n='pinMulti2') #multiplicador do normalizador
               
        startGrp.worldMatrix[0] >> pinDist1.inMatrix1
        endGrp.worldMatrix[0] >> pinDist2.inMatrix1
        
        poleVec.worldMatrix[0]  >> pinDist1.inMatrix2
        poleVec.worldMatrix[0]  >> pinDist2.inMatrix2
        
        limbMoveAll.scaleX >> pinMultiScale1.input1
        limbMoveAll.scaleX >> pinMultiScale2.input1
        
        pinMultiScale1.input2.set (AE.length())
        pinMultiScale2.input2.set (CE.length())
        
        pinMultiOffset1.input2.set (pinScaleJnt1)
        pinMultiOffset2.input2.set (pinScaleJnt2)
        pinMultiOffset1.input1.set (1)
        pinMultiOffset2.input1.set (1)
        
        pinDist1.distance >> pinNorm1.input1X
        pinDist2.distance >> pinNorm2.input1X
        pinMultiScale1.output >> pinNorm1.input2X
        pinMultiScale2.output >> pinNorm2.input2X
        pinNorm1.operation.set(2)
        pinNorm2.operation.set(2)
        
        pinNorm1.outputX >> pinMulti1.input1
        pinNorm2.outputX >> pinMulti2.input1
        pinMultiOffset1.output >> pinMulti1.input2
        pinMultiOffset2.output >> pinMulti2.input2
         
        ##Stretch
        stretchDist = pm.createNode ('distanceBetween',n='stretchDist') #distance
        stretchNorm = pm.createNode ('multiplyDivide',n='stretchNorm')  #normalizador
        stretchMultiScale = pm.createNode ('multDoubleLinear',n='stretchMultiScale') #mutiplica valor maximo pela escala do moveAll
        stretchCond = pm.createNode ('condition',n='stretchCond') # condicao so estica se for maior q distancia maxima
        
        ##Manual Stretch
        stretchManualStretch1 = pm.createNode ('multDoubleLinear',n='stretchManualStretch1') #mutiplica valor maximo pela escala do moveAll
        stretchManualStretch2 = pm.createNode ('multDoubleLinear',n='stretchManualStretch2') #mutiplica valor maximo pela escala do moveAll
        stretchManualStretch3 = pm.createNode ('multDoubleLinear',n='stretchManualStretch3') #mutiplica valor maximo pela escala do moveAll
        
        startGrp.worldMatrix[0] >> stretchDist.inMatrix1
        endGrp.worldMatrix[0] >> stretchDist.inMatrix2
        
        limbMoveAll.scaleX >> stretchMultiScale.input1
        stretchMultiScale.input2.set (distMax)
        stretchMultiScale.output >> stretchManualStretch1.input2
        stretchManualStretch1.output >> stretchNorm.input2X
        stretchNorm.operation.set(2)
        
        stretchDist.distance >>  stretchNorm.input1X    
        
        stretchNorm.outputX >> stretchCond.colorIfTrue.colorIfTrueR
        stretchNorm.outputX >> stretchCond.firstTerm
        stretchCond.operation.set (2)
        stretchCond.secondTerm.set (1)
        stretchCond.colorIfFalseR.set (1)
                
        ##AutoStretch switch
        autoStretchSwitch = pm.createNode ('blendTwoAttr',n='autoStretchSwitch') 
        stretchCond.outColor.outColorR >> autoStretchSwitch.input[1]
        autoStretchSwitch.input[0].set(1)
        
        ##Bias
        biasAdd1 =  pm.createNode ('plusMinusAverage',n='biasAdd1')
        biasAdd2 =  pm.createNode ('plusMinusAverage',n='biasAdd2')
        biasMulti1 = pm.createNode ('multDoubleLinear',n='biasMult1') 
        biasMulti2  = pm.createNode ('multDoubleLinear',n='biasMult2')
        
        biasAdd1.input1D[1].set(1)
        biasAdd1.operation.set(1)
        biasAdd1.output1D >> biasMulti1.input1
        autoStretchSwitch.output >> biasMulti1.input2
        biasMulti1.output >> stretchManualStretch2.input2
        biasAdd2.input1D[0].set(1)
        biasAdd2.operation.set(2)
        biasAdd2.output1D >> biasMulti2.input1
        autoStretchSwitch.output >> biasMulti2.input2
        biasMulti2.output >> stretchManualStretch3.input2
        
        ##Twist offset
        twistBlend1 = pm.createNode ('blendTwoAttr', n='twistBlend')
        twistBlend1.input[0].set(1)
        twistBlend1.output >> ikH[0].twist
        
        ##Blend stretch e pin
        stretchPinBlend1 = pm.createNode ('blendTwoAttr',n='stretchPinBlend1') 
        stretchPinBlend2 = pm.createNode ('blendTwoAttr',n='stretchPinBlend2')
        stretchManualStretch2.output >> stretchPinBlend1.input[0]
        stretchManualStretch3.output >> stretchPinBlend2.input[0]
        pinMulti1.output >> stretchPinBlend1.input[1]
        pinMulti2.output >> stretchPinBlend2.input[1]
        
        ##Blend ikfk
        ikfkBlend1 = pm.createNode ('blendTwoAttr',n='ikfkBlend1')
        ikfkBlend2 = pm.createNode ('blendTwoAttr',n='ikfkBlend2')
        ikfkReverse = pm.createNode ('reverse',n='ikfkReverse')
        stretchPinBlend1.output >> ikfkBlend1.input[0]
        stretchPinBlend2.output >> ikfkBlend2.input[0]
               
        endCntrl.manualStretch >> ikfkBlend1.input[1]
        midCntrl.manualStretch >> ikfkBlend2.input[1]
       
        limbMoveAll.ikfk >> ikfkReverse.inputX
        ikfkReverse.outputX >> ikfkBlend1.attributesBlender
        ikfkReverse.outputX >> ikfkBlend2.attributesBlender
        
        cnstrConn = midCntrl.connections(t='orientConstraint', d=True, s=False)[0] ## arriscando em pegar o primeiro...
        weightAttr = cnstrConn.target.connections(p=True, t='orientConstraint') ##Descobre o parametro de peso do constraint        
        ikfkReverse.outputX >> weightAttr[0]
        
        if self.handJoint:
            handTargetAttrs = handCnst.target.connections(p=True, t='orientConstraint')
            ikfkReverse.outputX >> handTargetAttrs [1]
            limbMoveAll.ikfk >> handTargetAttrs [0]
        
        limbMoveAll.ikfk >> ikH[0].ikBlend      
        ikfkBlend1.output >> self.startJnt.attr('scale'+axisName) 
        ikfkBlend2.output >> self.midJnt.attr('scale'+axisName)
        
        
        ##ikfk visibility
        ikCntrlVisCond = pm.createNode ('condition',n='ikVisCond')
        fkCntrlVisCond = pm.createNode ('condition',n='fkVisCond')
        limbMoveAll.ikfk >> ikCntrlVisCond.ft
        ikCntrlVisCond.secondTerm.set (0)
        ikCntrlVisCond.operation.set (1)
        ikCntrlVisCond.colorIfTrueR.set (1)
        ikCntrlVisCond.colorIfFalseR.set (0)
        limbMoveAll.ikfk >> fkCntrlVisCond.ft
        fkCntrlVisCond.secondTerm.set (1)
        fkCntrlVisCond.operation.set (1)
        fkCntrlVisCond.colorIfTrueR.set (1)
        fkCntrlVisCond.colorIfFalseR.set (0)
        
        ikCntrlVisCond.outColor.outColorR >> ikCntrl.getParent().visibility
        ikCntrlVisCond.outColor.outColorR >> poleVec.getParent().visibility
        fkCntrlVisCond.outColor.outColorR >> endCntrl.getParent().visibility
                       
        ##Atributos e conexoes do controle ik
        ikCntrl.bias >> biasAdd2.input1D[1]
        ikCntrl.bias >> biasAdd1.input1D[0]
        ikCntrl.pin >> stretchPinBlend1.attributesBlender
        ikCntrl.pin >> stretchPinBlend2.attributesBlender
        ikCntrl.manualStretch >> stretchManualStretch1.input1
        ikCntrl.manualStretch >> stretchManualStretch2.input1
        ikCntrl.manualStretch >> stretchManualStretch3.input1
        ikCntrl.autoStretch >> autoStretchSwitch.attributesBlender
        ikCntrl.pin >> twistBlend1.attributesBlender
        ikCntrl.twist >> twistBlend1.input[0]

        ###Dicionario do Limb
        self.limbDict['ikCntrl'] = ikCntrl
        self.limbDict['midCntrl'] = midCntrl
        self.limbDict['endCntrl'] = endCntrl
        self.limbDict['poleVec'] = poleVec
        self.limbDict['joint1'] = self.startJnt
        self.limbDict['joint2'] = self.midJnt
        self.limbDict['joint3'] = self.endJnt
        if self.handJnt:
            self.limbDict['joint4'] = self.handJnt
        self.limbDict['limbMoveAll'] = limbMoveAll
        
class Finger:
    """
        Cria um dedo
        Parametros: 
            name (string): nome do novo dedo            
            folds (int:0 a 2): numero de dobras no dedo
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
                 
    """ 
    #IMPLEMENTAR:
    #poder passar o fingerDict no momento da criacao
    #passar locators por variaveis e nao pelo dicionario
    
    def __init__(self,name='finger',folds=2, axis='X', flipAxis=False, **kwargs):
        self.name=name
        self.folds=folds
        self.axis=axis
        self.flipAxis =flipAxis
        self.fingerGuideMoveall=None
        self.fingerMoveall=None
        self.palmGuide=None
        self.baseGuide=None
        self.tipGuide=None
        self.fold1Guide=None
        self.fold2Guide=None
        self.fingerGuideDict={'moveall':[0,0,0],'palm':[0,0,0],'base':[1,0,0],'tip':[2,0,0], 'fold1':[0,0.05,0],'fold2':[0,0,0]}
        self.fingerGuideDict.update(kwargs) # atualiza com o q foi entrado

        
        
        ##setaqens de aparencia dos controles
        self.fingerDict={}
        self.fingerDict['moveallCntrlSetup']={'nameTempl':self.name+'MoveAll', 'icone':'circuloX','size':0.1,'color':(1,1,0) }    
        self.fingerDict['palmCntrlSetup']={'nameTempl':self.name+'palm', 'icone':'cubo','size':0.2,'color':(1,0,0) }    
        self.fingerDict['baseCntrlSetup']={'nameTempl':self.name+'base', 'icone':'cubo','size':0.3,'color':(1,1,0) }    
        self.fingerDict['tipCntrlSetup']={'nameTempl':self.name+'tip', 'icone':'circuloX','size':0.3,'color':(0,1,1) }    
        self.fingerDict['fold1CntrlSetup']={'nameTempl':self.name+'fold1', 'icone':'circuloX','size':0.3,'color':(0,1,1) }    
        self.fingerDict['fold2CntrlSetup']={'nameTempl':self.name+'fold2', 'icone':'circuloX','size':0.3,'color':(0,1,1) }    

    #guide 
    def doGuide(self, **kwargs):

        self.fingerGuideDict.update(kwargs) # atualiza com o q foi entrado
        
        guideName= self.fingerDict['moveallCntrlSetup']['nameTempl']+'_guide'
        
        #se existir apaga
        if pm.objExists (guideName):
            pm.delete (guideName)
        
        #grupos    
        self.fingerGuideMoveall = pm.group(n=guideName,em=True)
        guideName=self.fingerDict['palmCntrlSetup']['nameTempl']+'_guide'
        self.palmGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.palmGuide.displayHandle.set(1)
        self.palmGuide.localScale.set(0.1,0.1,0.1) 

        guideName=self.fingerDict['baseCntrlSetup']['nameTempl']+'_guide'
        self.baseGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.baseGuide.displayHandle.set(1)
        self.baseGuide.translate.set(1.3,0,0)
        self.baseGuide.localScale.set(0.1,0.1,0.1)
        
        guideName=self.fingerDict['tipCntrlSetup']['nameTempl']+'_guide'
        self.tipGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.tipGuide.displayHandle.set(1)
        self.tipGuide.translate.set(1.7,0,0)
        self.tipGuide.localScale.set(0.1,0.1,0.1)
        pm.parent (self.tipGuide, self.baseGuide,self.palmGuide, self.fingerGuideMoveall)
       
        #cria conforme o numero de dobras       
        if self.folds==2:
            guideName=self.fingerDict['fold1CntrlSetup']['nameTempl']+'_guide'
            self.fold1Guide = pm.spaceLocator (n=guideName,p=(0,0,0))
            self.fold1Guide.displayHandle.set(1)        
            fold1GuideGrp = pm.group(self.fold1Guide)
            fold1GuideGrp.translate.set(1.3,0,0)
            self.fold1Guide.localScale.set(0.1,0.1,0.1)

            guideName=self.fingerDict['fold2CntrlSetup']['nameTempl']+'_guide'
            self.fold2Guide = pm.spaceLocator (n=guideName,p=(0,0,0))  
            self.fold2Guide.displayHandle.set(1)       
            fold2GuideGrp = pm.group(self.fold2Guide)
            fold2GuideGrp.translate.set(1.7,0,0)
            self.fold2Guide.localScale.set(0.1,0.1,0.1)
                    
            pm.aimConstraint(self.fold1Guide,self.baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.fold2Guide,self.fold1Guide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.fold2Guide,self.tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.tipGuide, fold2GuideGrp, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
        
            cns=pm.pointConstraint( self.baseGuide, self.tipGuide , fold1GuideGrp, mo=False)
            weightAttr = cns.target.connections(p=True, t='pointConstraint')
            pm.setAttr (weightAttr[0],0.6)
            pm.setAttr (weightAttr[1],0.4)
            pm.pointConstraint(self.fold1Guide,self.tipGuide, fold2GuideGrp, mo=False)
            pm.parent (fold1GuideGrp,fold2GuideGrp, self.fingerGuideMoveall)
            
        elif self.folds==1:
            guideName=self.fingerDict['fold1CntrlSetup']['nameTempl']+'_guide'
            self.fold1Guide = pm.spaceLocator (n=guideName,p=(0,0,0))        
            self.fold1Guide.displayHandle.set(1) 
            fold1GuideGrp = pm.group(self.fold1Guide)
            fold1GuideGrp.translate.set(1.3,0,0)
            self.fold1Guide.localScale.set(0.1,0.1,0.1)
            
            pm.aimConstraint(self.fold1Guide,self. baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.tipGuide,fold1GuideGrp, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.fold1Guide,self.tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            cns=pm.pointConstraint(self.baseGuide, self.tipGuide , fold1GuideGrp, mo=False)

            pm.parent (fold1GuideGrp, self.fingerGuideMoveall)
            
        elif self.folds==0:    
            guideName=self.fingerDict['fold1CntrlSetup']['nameTempl']+'_guide'
            self.fold1Guide = pm.spaceLocator (n=guideName,p=(0,0,0))        
            self.fold1Guide.displayHandle.set(1) 
            fold1GuideGrp = pm.group(self.fold1Guide)
            fold1GuideGrp.translate.set(1.3,0,0)
            self.fold1Guide.localScale.set(0.1,0.1,0.1)
             
            pm.aimConstraint(self.tipGuide, self.baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.baseGuide,self.tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            cns=pm.pointConstraint(self.baseGuide, self.tipGuide , fold1GuideGrp, mo=False)
            self.fold1Guide.translate.set(0,0.05,0)
            self.fold1Guide.visibility.set(0)
            pm.parent (fold1GuideGrp, self.fingerGuideMoveall)
        
        #move para lugar definido nos parametros    
        self.fingerGuideMoveall.translate.set( self.fingerGuideDict['moveall'])
        self.palmGuide.translate.set( self.fingerGuideDict['palm'])
        self.baseGuide.translate.set( self.fingerGuideDict['base'])
        self.tipGuide.translate.set( self.fingerGuideDict['tip'])
        self.fold1Guide.translate.set( self.fingerGuideDict['fold1'])
        if self.folds==2:
            self.fold2Guide.translate.set( self.fingerGuideDict['fold2'])
            


    def doRig(self):
        # se nao existir guide, cria um default
        if not pm.objExists (self.fingerDict['moveallCntrlSetup']['nameTempl']+'_guide'):
            self.doGuide()
            
        # se existir um modulo igual, apaga
        moveallName = self.fingerDict['moveallCntrlSetup']['nameTempl']
        if pm.objExists(moveallName):
            pm.delete(moveallName)
 
        base=pm.xform (self.baseGuide, q=True,ws=True, t=True)
        tip=pm.xform (self.tipGuide, q=True,ws=True, t=True)
        palm=pm.xform (self.palmGuide, q=True,ws=True, t=True)
        fold1=pm.xform (self.fold1Guide, q=True,ws=True, t=True)
        
        #coordenadas dos 3 guides default para calculo da normal do plano de rotacao do dedo
        A=om.MVector(base)
        B=om.MVector(fold1)
        C=om.MVector(tip)
        
        if self.flipAxis:
            AB=A-B
            BC=B-C
        else:
            AB=B-A
            BC=C-B
        
        n = AB^BC
          
        #conforme o numero de dobras, especifica as guides
        #atualmente podem ser 0,1 ou 2 dobras
        if self.folds==2:
            fold2=pm.xform (self.fold2Guide, q=True,ws=True, t=True)
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
            if self.flipAxis:
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

        #cria os controles
        last=None
        displaySetup= self.fingerDict['palmCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                  
        cntrl0= cntrlCrv(name=cntrlName, connType='orientConstraint',obj=fingerJnts[0], **displaySetup)    

        displaySetup= self.fingerDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        cntrl1 = cntrlCrv(name=cntrlName, connType='orientConstraint',obj=fingerJnts[1], **displaySetup )

        pm.parent(cntrl1.getParent(),cntrl0)
        last=cntrl1
        
        #cria os controles conforme a o numero setado de dobras
        if self.folds>0:
            cntrl1.addAttr('curl1',k=1,at=float,dv=0)
            displaySetup= self.fingerDict['fold1CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl']
            cntrl2 = cntrlCrv(name=cntrlName,connType='orientConstraint', obj=fingerJnts[2],offsets=1, **displaySetup )
            pm.parent (cntrl2.getParent(2),cntrl1)
            cntrl1.curl1 >> cntrl2.getParent().rotateY
        if self.folds > 1:
            cntrl1.addAttr('curl2',k=1,at=float,dv=0)
            displaySetup= self.fingerDict['fold2CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl']
            cntrl3 = cntrlCrv(name=cntrlName,connType='orientConstraint', obj=fingerJnts[3],offsets=1, **displaySetup )
            pm.parent (cntrl3.getParent(2),cntrl2)
            cntrl1.curl2 >> cntrl3.getParent().rotateY


        cntrlName = self.fingerDict['moveallCntrlSetup']['nameTempl']            
        fingerMoveall = pm.group (name=cntrlName,em=True)
        pm.xform (fingerMoveall,t=palm,ws=True)
        pm.parent (fingerJnts[0],cntrl0.getParent(),fingerMoveall)
        
        self.fingerMoveall=fingerMoveall
        


class Hand:
    """
        Cria uma mao
        Parametros: 
            name (string): nome da mao
            folds (int): quantas dobras os dedos terao
            fingerNum (int): quantos dedos tera a mao           
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone             
    """  
    ## IMPLEMENTAR:
    #  os nomes derivados do handDict
    #  um handDict melhor q possa ser passado como parametro
    #  funcionalidades do conjunto da mao como curl lateral e offset para abrir e fechar todos os dedos
    
    def __init__(self, name='hand', axis='X', flipAxis=False, folds=2, fingerNum=5, **kwargs):
        
        self.name=name
        self.axis=axis
        self.flipAxis=flipAxis
        self.folds=folds
        self.fingerNum = fingerNum
        self.handGuideMoveall=None
        self.handDict={}
        self.handDict['fingers']={}
        self.handDict['moveall']=[0,0,0]
        for i in range(fingerNum):
            fingerName='dedo'+str(i)#IMPLEMENTAR nomes dos dedos            
            self.handDict['fingers']['finger'+str(i+1)] = {'name':fingerName,
                                                'fingerGuideDict':{'moveall':[0,0,(((fingerNum/2)*-.3)+(i*.3))],'palm':[0,0,0],'base':[1,0,0],'tip':[2,0,0], 'fold1':[0,0.05,0],'fold2':[0,0,0]},
                                                'instance':None
                                                }
        self.handDict.update(kwargs)
        
        for finger in self.handDict['fingers']:                                                       
            f=Finger(name=self.handDict['fingers'][finger]['name'],axis=self.axis,flipAxis=self.flipAxis,folds=self.folds)                                 
            self.handDict['fingers'][finger]['instance']=f
            
    def doGuide(self, **kwargs):
        #IMPLEMENTAR update do handDict - talvez handGuideDict
         
        if pm.objExists (self.name+'Moveall_guide'):
            pm.delete (self.name+'Moveall_guide')
    
        self.handGuideMoveall = pm.group(n=self.name+'Moveall_guide',em=True)
        pm.xform (self.handGuideMoveall, ws=True, t=self.handDict['moveall'])
        for finger in self.handDict['fingers']:                                                                                  
            f = self.handDict['fingers'][finger]['instance']
            dict=self.handDict['fingers'][finger]['fingerGuideDict']
            f.doGuide(**dict)
            pm.parent (f.fingerGuideMoveall,self.handGuideMoveall)

    def doRig(self, **kwargs):
        if not self.handGuideMoveall:
            self.doGuide()

        if pm.objExists (self.name+'Moveall'):
            pm.delete (self.name+'Moveall')
        
        handMoveall =pm.group(n=self.name+'Moveall',em=True)
        pm.xform (handMoveall, ws=True, t=self.handDict['moveall'])
        for finger in self.handDict['fingers']:                                                                                  
            f = self.handDict['fingers'][finger]['instance']
            dict=self.handDict['fingers'][finger]['fingerGuideDict']
            f.doRig()
            pm.parent (f.fingerMoveall, handMoveall)


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
    #Dedos do pe
    
    def __init__(self,name='foot',flipAxis=False, axis='X',**kwargs):
    
        self.name=name
        self.flipAxis=flipAxis
        self.axis=axis
        self.footGuideDict={'center':[0,0,0],'tip':[3,0,0],'heel':[-1,0,0],'ankle':[0,1,0],'ball':[2,0.5,0],'in':[2,0,-1],'out':[2,0,1]}
        self.footGuideMoveall=None
        
        #definicoes da aparencia dos controles
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
        self.footDict['joint1FkCntrlSetup'] = {'nameTempl':self.name+'Joint1Fk', 'icone':'cubo', 'size':1.0, 'color':(0,1,0)}
        self.footDict['joint2FkCntrlSetup'] = {'nameTempl':self.name+'Joint2Fk', 'icone':'cubo', 'size':1.0, 'color':(0,1,0)}
          
        self.footDict['nodeTree'] = {}
        self.footDict['nameConventions'] = None
                
    def doGuide(self,**kwargs):
        #atualiza o footGuideDict com o q for entrado aqui nesse metodo
        #ex: doGuide (center=[0,0,0], tip=[10,10,0]
         
        self.footGuideDict.update(kwargs)
        
        
        guideName=self.footDict['moveallCntrlSetup']['nameTempl']+'_guide' 
        # deleta se existir
        if pm.objExists(guideName):
            pm.delete (guideName)
          
        self.footGuideMoveall=pm.group (n=guideName ,em=True)
        
        #cria guides segundo os nomes dos controles e nas posicoes definidas no dicionario footGuideDict 
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
        if not self.footGuideMoveall:
            self.doGuide()

        cntrlName=self.footDict['moveallCntrlSetup']['nameTempl']
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
            

        #esqueleto
        center=pm.xform (self.centerGuide, q=True,ws=True, t=True)
        tip=pm.xform (self.tipGuide, q=True,ws=True, t=True)
        ankle=pm.xform (self.ankleGuide, q=True,ws=True, t=True)
        ball=pm.xform (self.ballGuide, q=True,ws=True, t=True)
        
        A=om.MVector(ankle)
        B=om.MVector(center)
        C=om.MVector(tip)
        D=om.MVector(ball)
        
        #calcula a normal do sistema no triangulo entre center, ankle e tip. 
        # pode ser q isso de problemas se mal colocados. 
        #IMPLEMENTAR limites dos guides para evitar ma colocacao
        
        if self.flipAxis:
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
        
        #cria os joints     
        m= om.MMatrix (list)
        j2 = pm.joint()
        pm.xform (j2, m = m, ws=True) 
        pm.makeIdentity (j2, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        j3 = pm.joint()
        pm.xform (j3, m = m, ws=True)
        pm.xform (j3, t =C, ws=True) 
        pm.makeIdentity (j3, apply=True, r=1, t=0, s=1, n=0, pn=0)
        #e faz os ikhandles
        ballIkh = pm.ikHandle (sj=j1, ee=j2, sol="ikRPsolver")
        tipIkh = pm.ikHandle (sj=j2, ee=j3, sol="ikRPsolver")
        
        footMoveall=pm.group (em=True,n=cntrlName)
        footMoveall.translate.set(center)
        
        #esse controle deve levar o controle ik da ponta do limb para funcionar o pe 
        displaySetup= self.footDict['jointCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        j1Cntrl=cntrlCrv(name=cntrlName,obj=j1,connType='parentConstraint', **displaySetup)

        #base cntrl
        displaySetup= self.footDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        baseCntrl=cntrlCrv(name=cntrlName,obj=self.centerGuide, **displaySetup)
        pm.xform (baseCntrl, rp=ankle, ws=True)
        baseCntrl.addAttr ('extraRollCntrls',min=0, max=1, dv=0, k=1)
        
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
        baseCntrl.extraRollCntrls >> inCntrl.getParent().visibility        
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
        
        #setDrivens do controle do Roll
        animUU=pm.createNode('animCurveUU') # cria curva
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

        #controles fk
        displaySetup= self.footDict['joint1FkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        joint1FkCntrl=cntrlCrv(name=cntrlName,obj=j1,connType='parentConstraint', **displaySetup)

        displaySetup= self.footDict['joint2FkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        joint2FkCntrl=cntrlCrv(name=cntrlName,obj=j2,connType='orientConstraint', **displaySetup)
        
        joint2FkCntrl.getParent().setParent(joint1FkCntrl)
        joint1FkCntrl.getParent().setParent(footMoveall) 
        
        #node tree ikfk Blend
        footMoveall.addAttr ('ikfk',at='float', min=0, max=1,dv=1,k=1)
        ikfkRev=pm.createNode('reverse')
        ikfkVisCond1=pm.createNode('condition')
        ikfkVisCond2=pm.createNode('condition')
        
        #visibilidade ik fk
        footMoveall.ikfk >> ikfkRev.inputX
        footMoveall.ikfk >> ballIkh[0].ikBlend  
        footMoveall.ikfk >> tipIkh[0].ikBlend 
        footMoveall.ikfk >> ikfkVisCond1.firstTerm        
        ikfkVisCond1.secondTerm.set (0)
        ikfkVisCond1.operation.set (2)
        ikfkVisCond1.colorIfTrueR.set (1)
        ikfkVisCond1.colorIfFalseR.set (0)
        ikfkVisCond1.outColorR >> baseCntrl.getParent().visibility
        
        #blend dos constraints 
        footMoveall.ikfk >> ikfkVisCond2.firstTerm
        ikfkVisCond2.secondTerm.set (1)
        ikfkVisCond2.operation.set (4)
        ikfkVisCond2.colorIfTrueR.set (1)
        ikfkVisCond2.colorIfFalseR.set (0)
        ikfkVisCond2.outColorR >> joint1FkCntrl.getParent().visibility
        parCnstr = j1.connections (type='parentConstraint')[0] #descobre constraint
        weightAttr = parCnstr.target.connections(p=True, t='parentConstraint') #descobre parametros
        footMoveall.ikfk >> weightAttr[0]
        ikfkRev.outputX >> weightAttr[1]
        
        
class Spine:
    """
        Cria uma espinha
        Parametros: 
            name (string): nome da espinha           
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
                 
    """ 
    #IMPLEMENTAR:
        #fkCntrls
        # qual o comportamento do hip? 
        # no fk o hip deve ficar parado?
        # um so hip para ik e fk?
             
    def __init__(self, name='spine',flipAxis=False,axis='X',**kwargs):
        self.startGuide = None
        self.midGuide = None
        self.endGuide = None
        self.endTipGuide=None
        self.startTipGuide=None
        
        self.spineGuideDict={'start':[0,0,0],'mid':[0,4,0],'end':[0,8,0], 'startTip':[0,-2,0],'endTip':[0,11,0]}
        self.name=name
        self.flipAxis=flipAxis
        self.axis=axis
        self.spineGuideMoveall=None
        
        #dicionario q determina a aparencia dos controles
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
        #se existir apaga
        if pm.objExists (self.name+'Moveall_guide'):
            pm.delete (self.name+'Moveall_guide')
        ##cria os locators dos guides e liga a visualizacao do handle
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
        midGuideGrp=pm.group (em=True)
        pm.pointConstraint (self.startGuide, self.endGuide, midGuideGrp, mo=False)
        self.midGuide.setParent(midGuideGrp)

        self.endTipGuide = pm.spaceLocator (n=self.name+'EndTip_guide', p=(0,0,0))
        self.endTipGuide.translate.set(self.spineGuideDict['endTip'])
        self.endTipGuide.displayHandle.set(1)        
        self.endTipGuide.localScale.set(.5,.5,.5) 
        self.endTipGuide.setParent(self.endGuide)
        self.startTipGuide = pm.spaceLocator (n=self.name+'StartTip_guide', p=(0,0,0))
        self.startTipGuide.translate.set(self.spineGuideDict['startTip'])
        self.startTipGuide.displayHandle.set(1)        
        self.startTipGuide.localScale.set(.5,.5,.5) 
        self.startTipGuide.setParent(self.startGuide)

        pm.parent (self.startGuide,midGuideGrp,self.endGuide, self.spineGuideMoveall)
        
    def doRig(self):
        #se nao tiver guide, faz
        if not self.spineGuideMoveall:
            self.doGuide()
        #se ja existir rig, apaga   
        if pm.objExists (self.spineDict['moveallSetup']['nameTempl']):
            pm.delete (self.spineDict['moveallSetup']['nameTempl'])
            
        spineRibbon=None
        
        #cria controles fk com nomes e setagem de display vindas do spineDict
        displaySetup= self.spineDict['spine0CntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        spine0FkCntrl = cntrlCrv(name=cntrlName , obj=self.startGuide,**displaySetup) 
        
        displaySetup= self.spineDict['startFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        startFkCntrl = cntrlCrv(name=cntrlName, obj=self.startGuide,**displaySetup)
        startFkCntrl.getParent().setParent(spine0FkCntrl)
        
        displaySetup= self.spineDict['midFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        midFkCntrl = cntrlCrv(name=cntrlName, obj=self.midGuide,**displaySetup)
        
        displaySetup= self.spineDict['midFkOffsetCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        midFkOffsetCntrl = cntrlCrv(name=cntrlName, obj=self.midGuide,**displaySetup) #esse controle faz o offset do ribbon e permanece orientado corretamente
        midFkOffsetCntrl.getParent().setParent(midFkCntrl)
        midFkCntrl.getParent().setParent(startFkCntrl)
        
        displaySetup= self.spineDict['endFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        endFkCntrl = cntrlCrv(name=cntrlName, obj=self.endGuide,**displaySetup)
        endFkCntrl.getParent().setParent(midFkCntrl)
        
        #cria controles ik com nomes e setagem de display vindas do spineDict
        displaySetup= self.spineDict['startIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        startIkCntrl = cntrlCrv(name=cntrlName, obj=self.startGuide,**displaySetup)

        displaySetup= self.spineDict['midIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        midIkCntrl = cntrlCrv(name=cntrlName, obj=self.midGuide,**displaySetup)

        displaySetup= self.spineDict['endIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        endIkCntrl = cntrlCrv(name=cntrlName, obj=self.endGuide,**displaySetup)
        
        #Cria os joints orientados em X down
        start=pm.xform(self.startGuide,q=True,t=True,ws=True)
        startTip=pm.xform(self.startTipGuide,q=True,t=True,ws=True)
        pm.select(cl=True)
        self.startZeroJnt=pm.joint(p=(0,0,0))
        pm.select(cl=True)
        self.startJnt=pm.joint(p=(0,0,0))
        pm.select(cl=True)
        self.startTipJnt=pm.joint(p=(0,0,0))
     
        A=om.MVector(start)
        B=om.MVector(startTip)
        Z=om.MVector(0,0,1)
        AB=B-A
        
        dot = Z.normal()*AB.normal() #se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        # vai acontecer qnd usarem a guide horizontal
        if abs(dot)>.95:
            Z=om.MVector(0,1,0)
   

        n=AB^Z
        x = n.normal() ^ AB.normal()
        t = x.normal() ^ n.normal()      
        if self.axis=='Y':            
            list = [ n.normal().x, n.normal().y, n.normal().z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, A.x, A.y,A.z,1]
        elif self.axis=='Z':
            list = [ x.x, x.y, x.z, 0,n.normal().x, n.normal().y, n.normal().z, 0,t.x, t.y, t.z, 0, A.x, A.y,A.z,1]
        else:
            list = [ t.x, t.y, t.z, 0,n.normal().x, n.normal().y, n.normal().z, 0, x.x*-1, x.y*-1, x.z*-1, 0, A.x, A.y,A.z,1]
        m= om.MMatrix (list)
        pm.xform (self.startZeroJnt, m = m, ws=True) 
        pm.xform (self.startJnt, m = m, ws=True) 
        pm.xform (self.startTipJnt, m = m, ws=True) 
        pm.xform (self.startTipJnt, t= B, ws=True) 
        pm.parent (self.startJnt,self.startZeroJnt)
        pm.parent (self.startTipJnt, self.startJnt)
        
        end=pm.xform(self.endGuide,q=True,t=True,ws=True)
        endTip=pm.xform(self.endTipGuide,q=True,t=True,ws=True)
        pm.select(cl=True)
        self.endZeroJnt=pm.joint(p=(0,0,0))
        pm.select(cl=True)
        self.endJnt=pm.joint(p=(0,0,0))
        pm.select(cl=True)
        self.endTipJnt=pm.joint(p=(0,0,0))

        A=om.MVector(end)
        B=om.MVector(endTip)
        Z=om.MVector(0,0,1)
        AB=B-A
        
        dot = Z.normal()*AB.normal() #se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot)>.95:
            Z=om.MVector(0,1,0)
            
        n=AB^Z
        x = n.normal() ^ AB.normal()
        t = x.normal() ^ n.normal()      
        if self.axis=='Y':            
            list = [ n.normal().x, n.normal().y, n.normal().z, 0, t.x, t.y, t.z, 0, x.x, x.y, x.z, 0, A.x, A.y,A.z,1]
        elif self.axis=='Z':
            list = [ x.x, x.y, x.z, 0,n.normal().x, n.normal().y, n.normal().z, 0,t.x, t.y, t.z, 0, A.x, A.y,A.z,1]
        else:
            list = [ t.x, t.y, t.z, 0,n.normal().x, n.normal().y, n.normal().z, 0, x.x*-1, x.y*-1, x.z*-1, 0, A.x, A.y,A.z,1]
        m= om.MMatrix (list)
        pm.xform (self.endZeroJnt, m = m, ws=True) 
        pm.xform (self.endJnt, m = m, ws=True) 
        pm.xform (self.endTipJnt, m = m, ws=True) 
        pm.xform (self.endTipJnt, t= B, ws=True) 
        pm.parent (self.endJnt,self.endZeroJnt)
        pm.parent (self.endTipJnt, self.endJnt)
        
        #cria os extratores de twist dos joints inicial e final
        #IMPLEMENTAR: twist do controle do meio
        twistExtractor1= twistExtractor(self.startJnt)
        twistExtractor2= twistExtractor(self.endJnt)
        twistExtractor1.extractorGrp.visibility.set(False)
        twistExtractor2.extractorGrp.visibility.set(False)
        
        #ribbon
        #calcular a distancia entre os guides pra fazer ribbon do tamanho certo
        A=om.MVector(start)
        B=om.MVector(end)
        Z=om.MVector(0,0,-1)  
        AB=B-A  
        
        dot = Z.normal()*AB.normal() #se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot)>.95:
            Z=om.MVector(0,-1,0)
 
        spineRibbon = RibbonBezierSimple(name=self.name+'Ribbon_',size=AB.length())
        spineRibbon.doRig()
        
        #cria o sistema que vai orientar o controle do meio por calculo vetorial
        aimTwist = AimTwistDivider()
        aimTwist.start.setParent (spineRibbon.startCntrl,r=True)
        aimTwist.end.setParent (spineRibbon.endCntrl,r=True)
        aimTwist.mid.setParent (spineRibbon.moveall,r=True)

        #calculo para determinar a rotacao do ribbon
        #hardcoded orientacao X down do ribbon para funcionar com o extractor
        n=AB^Z
        x = n.normal() ^ AB.normal()
        t = x.normal() ^ n.normal()      
        list = [ t.x, t.y, t.z, 0,n.normal().x, n.normal().y, n.normal().z, 0, x.x*-1, x.y*-1, x.z*-1, 0, A.x, A.y,A.z,1]
        m= om.MMatrix (list)
        pm.xform (spineRibbon.moveall, m = m, ws=True) 
                  
        ##Liga os controles do meio do ik e do meioOffset fk no aimTwist
        #eles trabalharam somente por translacao
        pm.pointConstraint (startIkCntrl, endIkCntrl, midIkCntrl.getParent(), mo=True)
        pm.orientConstraint (aimTwist.mid, midIkCntrl, mo=True)
        midIkCntrl.rotate.lock()
        midIkCntrl.rotate.setKeyable(0)
        pm.orientConstraint (aimTwist.mid, midFkOffsetCntrl, mo=True)
        midFkOffsetCntrl.rotate.lock()
        midFkOffsetCntrl.rotate.setKeyable(0)
        
        #faz os constraints do ribbon nos controles ik e fk pra fazer blend
        cns1=pm.parentConstraint (startFkCntrl, startIkCntrl, spineRibbon.startCntrl, mo=True)
        mid=pm.xform(self.midGuide,q=True,t=True,ws=True)
        pm.xform (spineRibbon.midCntrl.getParent(), t=mid, ws=True)
        cns2=pm.parentConstraint (midFkOffsetCntrl, midIkCntrl, spineRibbon.midCntrl, mo=True)
        cns3=pm.parentConstraint (endFkCntrl, endIkCntrl, spineRibbon.endCntrl, mo=True)
        
        #parenteia os joints das pontas nos controles do ribbon
        self.startZeroJnt.setParent (spineRibbon.startCntrl.getParent())
        self.endZeroJnt.setParent (spineRibbon.endCntrl.getParent())
        #e cria os constraints point no start joint zero e orient no start joint
        #o joint zero eh necessario para o twist extractor
        pm.pointConstraint (spineRibbon.startCntrl, self.startZeroJnt, mo=True)
        pm.orientConstraint (spineRibbon.startCntrl, self.startJnt, mo=True)
        pm.pointConstraint (spineRibbon.endCntrl, self.endZeroJnt, mo=True)
        pm.orientConstraint (spineRibbon.endCntrl, self.endJnt, mo=True)
        
        #cria o moveall da espinha
        displaySetup= self.spineDict['moveallSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        spineMoveall=pm.group(n=cntrlName, em=True)
        
        #e parenteia todo mundo
        pm.parent (twistExtractor1.extractorGrp, twistExtractor2.extractorGrp, spineRibbon.moveall, startIkCntrl.getParent(),midIkCntrl.getParent(),endIkCntrl.getParent(),spine0FkCntrl.getParent(), spineMoveall)


        #conecta os twist extractors nos twists do ribbon
        twistExtractor1.extractor.extractTwist >> spineRibbon.startCntrl.twist
        twistExtractor2.extractor.extractTwist >> spineRibbon.endCntrl.twist
        
        #cria o node tree do blend ikfk
        spineMoveall.addAttr ('ikfk', at='float', max=1, min=0, dv=1, k=1)
        ikfkRev = pm.createNode('reverse')
        ikfkCond1 = pm.createNode('condition')
        ikfkCond2 = pm.createNode('condition')
        spineMoveall.ikfk >> ikfkCond1.firstTerm
        spineMoveall.ikfk >> ikfkCond2.firstTerm
        spineMoveall.ikfk >> ikfkRev.inputX
        
        #visibilidade ik fk        
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

        #blend dos constraints         
        weightAttr = cns1.target.connections(p=True, t='parentConstraint') #descobre parametros
        spineMoveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns2.target.connections(p=True, t='parentConstraint') #descobre parametros
        spineMoveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns3.target.connections(p=True, t='parentConstraint') #descobre parametros
        spineMoveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]

class Chain:
    """
        Cria uma cadeia de joints com controles fk
        Parametros: 
            name (string): nome do novo limb            
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
            numDiv (int): numero de joints da cadeia
                             
    """  
    ## IMPLEMENTAR:
    #  nomes dos joints
    #  talvez conexoes diretas dos controles?
    #  algum tipo de controle ik para a cadeia
        
    def __init__(self, name='chain', flipAxis=False, numDiv=2, axis='X', **kwargs):
        self.axis=axis
        self.flipAxis=flipAxis
        self.name=name
        self.chainGuideDict={}
        self.numDiv=numDiv
        self.chainGuideMoveall=None
        for i in range (self.numDiv):
            self.chainGuideDict['guide'+str(i+1)]=[0+i,0,0]
        #parametros de aparencia dos controles
        self.chainDict={}
        self.chainDict['moveAllCntrlSetup']={'nameTempl':self.name+'Moveall', 'icone':'circuloX','size':1.8,'color':(1,1,0) }    
        self.chainDict['fkCntrlSetup'] = {'nameTempl':self.name+'Fk', 'icone':'cubo','size':.8,'color':(0,1,0) }    

    def doGuide(self, **kwargs):
        self.chainGuideDict.update(kwargs)
        
        #apaga se existir
        cntrlName=self.chainDict['moveAllCntrlSetup']['nameTempl']+'_guide'
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
        self.chainGuideMoveall=pm.group(n=cntrlName, em=True)

        self.guideList=[]
        for i in range(len(self.chainGuideDict.keys())):
            guideName= self.name+str(i)+'_guide'
            guide= pm.spaceLocator (n=guideName,p=(0,0,0))
            self.guideList.append (guide)
            pm.xform(guide, t=self.chainGuideDict['guide'+str(i+1)], ws=True)
            pm.parent(guide, self.chainGuideMoveall)
            
    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.chainGuideMoveall:
            self.doGuide()
            
        #apagar se ja houver um grupo moveall
        cntrlName=self.chainDict['moveAllCntrlSetup']['nameTempl']                     
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
        self.chainMoveAll = pm.group(empty=True, n=cntrlName)

        
        A=[]
        AB=[]
        last=None
        for obj in self.guideList:
            p=pm.xform (obj, q=True, t=True, ws=True)
            P=om.MVector(p)
            #guarda na lista A as posicoes dos guides como MVector
            A.append(P)
            #calcula vetores de direcao entre os guides
            #guarda na lista AB
            if last:
                if self.flipAxis:
                    V=last-P
                else:    
                    V=P-last
                AB.append(V)
            last=P

        if self.flipAxis:
            Z=om.MVector(0,0,1)
            X=om.MVector(-1,0,0)  
        else:
            Z=om.MVector(0,0,-1)
            X=om.MVector(1,0,0)
            
        m=[ 1,0,0,0,
            0,1,0,0,
            0,0,1,0,
            0,0,0,1]
            
        last=None
        self.jntList=[]
        for i in range(len(AB)):
            #se a o vetor do bone coincidir com o eixo Z usa o eixo X de secundario
            dot=AB[i].normal()*Z
            print dot
            if abs(dot) < 0.95:
                normal=AB[i]^Z
            else:
                normal=AB[i]^X
            
            # descobre a matriz de transformacao orientada e desenha os joints     
            m=orientMatrix(AB[i], normal, A[i], self.axis)
            pm.select(cl=True)
            jnt = pm.joint()
            self.jntList.append(jnt)
            pm.xform (jnt, m = m, ws=True) 
            pm.makeIdentity (jnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
            if last:
                pm.parent (jnt, last)
            last=jnt
        
        # desenha o ultimo joint (ou o unico)
        pm.select(cl=True)
        jnt = pm.joint()
        self.jntList.append(jnt)
        pm.xform (jnt, m = m, ws=True)
        pm.xform (jnt, t=A[-1], ws=True) 
        pm.makeIdentity (jnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        pm.parent (jnt, last)
        
        pm.parent (self.jntList[0], self.chainMoveAll)
        
        #faz controles para os joints exceto o da ponta
        cntrlTodo=[]
        if len(self.jntList)>1:            
            cntrlToDo=self.jntList[:-1]
          
        self.cntrlList=[]        
        last=None
        for jnt in cntrlToDo:
            displaySetup=self.chainDict['fkCntrlSetup'].copy()
            cntrlName=self.chainDict['fkCntrlSetup']['nameTempl']
            cntrl=cntrlCrv (name= cntrlName, obj=jnt, connType='parentConstraint', **displaySetup)
            self.cntrlList.append (cntrl)
            if last:
                pm.parent (cntrl.getParent(), last)
            last=cntrl    
            
        pm.parent (self.cntrlList[0].getParent(), self.chainMoveAll)