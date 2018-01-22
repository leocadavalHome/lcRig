import pymel.core as pm
import maya.api.OpenMaya as om

class Moveall:
    """
    cria um moveall com os grupos determinados
        Parametros: 
            name (string): nome do personagem            
            connType (string): determina se os sistemas ficarao filhos dos controles 
                               ou numa pasta separadas ligados por constraint 
    
    """
    
    def __init__(self, name='character',connType='parent', **kwargs):
        self.name=name
        self.conn=connType
        self.guideMoveall=None
        self.guideSulfix='_guide'
        self.moveallDict={'name':self.name,
                          'conn':self.conn,
                          'guideDict': {'moveall':[0,0,0]} }
        self.moveallGuideDict = {'moveall':[0,0,0]} 
        self.moveallDict['moveallGuideSetup']={'nameTempl':self.name+'MoveAll','size':8,'icone':'circuloPontaY', 'color':(1,0,0)}

        self.moveallDict.update(kwargs) 
        self.moveallGuideDict.update(self.moveallDict['guideDict']) 
        self.moveallDict['guideDict']=self.moveallGuideDict.copy()                
        
    def doGuide(self):
        guideName=self.moveallDict['moveallGuideSetup']['nameTempl']+self.guideSulfix
        if pm.objExists(guideName):
            pm.delete (guideName)                
        self.guideMoveall=pm.group(n=guideName, em=True)
        
        displaySetup= self.moveallDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        self.guideMoveallCrv = cntrlCrv(name=cntrlName, **displaySetup)
        self.guideMoveallCrv.getParent().setParent(self.guideMoveall)
        
        if pm.objExists('GUIDES'):
            self.guideGrp=pm.PyNode('GUIDES')
        else:    
            self.guideGrp = pm.group (em=True, n='GUIDES')
        pm.parent (self.guideMoveall, self.guideGrp)

    def getGuideFromScene(self):
        guideName=self.moveallDict['moveallGuideSetup']['nameTempl']+self.guideSulfix               

        self.guideMoveall=pm.PyNode(guideName)
        
        displaySetup= self.moveallDict['moveallGuideSetup'].copy()
        cntrlName = displaySetup['nameTempl']+'_cntrl'
        self.guideMoveallCrv = pm.PyNode(cntrlName)
        


    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()
        if pm.objExists('GUIDES'):
            self.guideGrp=pm.PyNode('GUIDES')
        else:    
            self.guideGrp = pm.group (em=True, n='GUIDES')
        if pm.objExists('MOVEALL'):
            self.moveallGrp = pm.PyNode('MOVEALL')
            self.moveallGrp.setParent(w=True)
        else:    
            self.moveallGrp = pm.group (em=True, n='MOVEALL')

        if pm.objExists('NOMOVE'):
            self.nomoveGrp=pm.PyNode('NOMOVE')
            self.nomoveGrp.setParent(w=True)
        else:    
            self.nomoveGrp = pm.group (em=True, n='NOMOVE')

        if pm.objExists('DATA'):
            self.dataGrp = pm.PyNode('DATA')
            self.dataGrp.setParent(w=True)
        else:    
            self.dataGrp = pm.group (em=True, n='DATA')

        if pm.objExists('MESH'):
            self.meshGrp=pm.PyNode('MESH')
            self.meshGrp.setParent(w=True)
        else:    
            self.meshGrp = pm.group (em=True, n='MESH')            

        if pm.objExists(self.name.upper()):
            pm.delete (self.name.upper())

                    
        self.moveall3 = cntrlCrv(name=self.name+'Moveall3', icone='circuloPontaY', size=10)
        self.moveall2 = cntrlCrv(name=self.name+'Moveall2', icone='circuloPontaY', size=8)
        self.moveall = cntrlCrv(name=self.name+'Moveall', icone='circuloPontaY', size=6)
        
        self.moveall.getParent().setParent(self.moveall2)
        self.moveall2.getParent().setParent(self.moveall3)
                     
        #aqui ver se eh melhor ter o o grupo MOVEALL na pasta DATA ou filho dos controles moveall
        #por default vai
        #self.guideGrp.setParent (self.dataGrp)
        self.nomoveGrp.setParent (self.dataGrp)
        rigGrp = pm.group (self.moveall3.getParent(),self.dataGrp,self.meshGrp,  n=self.name.upper())

        if self.conn=='parent':
            self.moveallGrp.setParent(self.moveall)
        else:
            self.moveallGrp.setParent(self.dataGrp)   
        
        self.guideGrp.visibility.set(0)
                    
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
            lastJoint (boolean): se exite joint da mao
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
                 
    """  
    ## IMPLEMENTAR:
    #  setagem de parametros e formatacao de nomes 
    #  grupos de spaceSwitch acima dos controles
 
    #self.twoJoints=False RETIREI CODIGO DE ARTICULACAO DE DOIS JOINTS. PRECISA FAZER IMPLEMENTACAO COMPLETA 
                 
    def __init__ (self,name='limb',axis='X',flipAxis=False, lastJoint=True, **kwargs):
        
        self.name = name
        self.flipAxis = flipAxis
        self.axis = axis
        self.lastJoint = lastJoint

        self.guideMoveall=None

        ##IMPLEMENTAR padroes de nome 
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        self.grpSulfix='_grp'
        self.GuideColor=(1,0,1)

        self.limbDict={'name':name,
                       'flipAxis':flipAxis,
                       'lastJoint':lastJoint,
                       'axis':axis}
                   
        ##setups visuais dos controles
        self.limbDict['moveAll1CntrlSetup']={'nameTempl':self.name+'MoveAll1', 'icone':'grp','size':1.8,'color':(1,1,0) }    
        self.limbDict['ikCntrlSetup'] = {'nameTempl':self.name+'Ik', 'icone':'circuloX','size':1,'color':(1,0,0) }    
        self.limbDict['startCntrlSetup'] = {'nameTempl':self.name+'FkStart', 'icone':'circuloX','size':1.5,'color':(0,1,0) }
        self.limbDict['midCntrlSetup'] = {'nameTempl':self.name+'FkMid', 'icone':'circuloX', 'size':1.5, 'color':(0,1,0)}
        self.limbDict['endCntrlSetup'] = {'nameTempl':self.name+'FkEnd', 'icone':'circuloX', 'size':1.5, 'color':(0,1,0)}
        self.limbDict['poleVecCntrlSetup'] = {'nameTempl':self.name+'PoleVec', 'icone':'bola', 'size':0.4, 'color':(1,0,0)}

        self.limbDict['startJntSetup'] = {'nameTempl':self.name+'Start', 'size':1}
        self.limbDict['midJntSetup'] = {'nameTempl':self.name+'Mid', 'size':1}
        self.limbDict['endJntSetup'] = {'nameTempl':self.name+'End', 'size':1}
        self.limbDict['lastJntSetup'] = {'nameTempl':self.name+'Last', 'size':1}
        
        self.limbDict['moveallGuideSetup']={'nameTempl':self.name+'MoveAll1','size':1, 'color':(1,1,0)}
        self.limbDict['startGuideSetup'] = {'nameTempl':self.name+'Start', 'size':1, 'color':(1,1,0)}
        self.limbDict['midGuideSetup'] = {'nameTempl':self.name+'Mid', 'size':1, 'color':(1,1,0)}
        self.limbDict['endGuideSetup'] = {'nameTempl':self.name+'End', 'size':1, 'color':(1,1,0)}
        self.limbDict['lastGuideSetup'] = {'nameTempl':self.name+'Last', 'size':1, 'color':(1,1,0)}
        self.limbDict['guideDict']={}
        #esquema para podermos entrar somente algumas keys do GuideDict, o restante e completada com os valores default
        self.limbGuideDict = {'moveall':[0,0,0],'start':[0,0,0], 'mid':[3,0,-1],'end':[6,0,0], 'last':[7,0,0]} 
        self.limbDict.update(kwargs) 
        self.limbGuideDict.update(self.limbDict['guideDict']) 
        self.limbDict['guideDict']=self.limbGuideDict.copy()
        #self.limbDict['nodeTree'] = {}
        #self.limbDict['nameConventions'] = None
        
    def doGuide(self,**kwargs):        
        self.limbGuideDict =  self.limbDict['guideDict'].copy()
        self.limbGuideDict.update(kwargs)
        
        ## cria guia se não existir 
        guideName=self.limbDict['moveallGuideSetup']['nameTempl']+self.guideSulfix
        if pm.objExists(guideName):
            pm.delete (guideName)                
        self.guideMoveall=pm.group(n=guideName, em=True)

        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')
                       
        guideName=self.limbDict['startGuideSetup']['nameTempl']+self.guideSulfix
        self.startGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        pm.xform (self.startGuide, t=self.limbGuideDict['start'], ws=True)
        self.startGuide.displayHandle.set(1)

        guideName=self.limbDict['midGuideSetup']['nameTempl']+self.guideSulfix
        self.midGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        pm.xform (self.midGuide, t=self.limbGuideDict['mid'], ws=True)
        self.midGuide.displayHandle.set(1)

        guideName=self.limbDict['endGuideSetup']['nameTempl']+self.guideSulfix
        self.endGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        pm.xform (self.endGuide, t=self.limbGuideDict['end'], ws=True)
        self.endGuide.displayHandle.set(1)
        
        pm.parent (self.startGuide, self.midGuide, self.endGuide, self.guideMoveall)
               
        if self.lastJoint:
            guideName=self.limbDict['lastGuideSetup']['nameTempl']+self.guideSulfix
            self.lastGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
            pm.xform (self.lastGuide, t=self.limbGuideDict['last'], ws=True)
            pm.parent (self.lastGuide, self.endGuide)
            self.lastGuide.displayHandle.set(1)
            
        #cria a curva da direcao do plano
        arrow=cntrlCrv(obj=self.startGuide,name=self.name+'PlaneDir',icone='seta', size=.35, color=(0,1,1))
        arrow.getParent().setParent(self.startGuide)
        pm.aimConstraint(self.endGuide,arrow, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 0, -1),worldUpObject=self.midGuide, worldUpType='object')

        self.guideMoveall.translate.set( self.limbGuideDict['moveall'])

    def getGuideFromScene(self):      
        try:
            guideName=self.limbDict['moveallGuideSetup']['nameTempl']+self.guideSulfix              
            self.guideMoveall=pm.PyNode(guideName)
            
            guideName=self.limbDict['startGuideSetup']['nameTempl']+self.guideSulfix
            self.startGuide = pm.PyNode(guideName)
    
            guideName=self.limbDict['midGuideSetup']['nameTempl']+self.guideSulfix
            self.midGuide = pm.PyNode(guideName)
    
            guideName=self.limbDict['endGuideSetup']['nameTempl']+self.guideSulfix
            self.endGuide =pm.PyNode(guideName)
                   
            if self.lastJoint:
                guideName=self.limbDict['lastGuideSetup']['nameTempl']+self.guideSulfix
                self.lastGuide = pm.PyNode(guideName)

        except:
            print 'algum nao funcionou'
            
    def mirrorConnectGuide(self, limb):
        if not self.guideMoveall:
            self.doGuide()        
        if not limb.guideMoveall:
            limb.doGuide()

        if pm.objExists(self.name+'MirrorGuide_grp'):
            pm.delete (self.name+'MirrorGuide_grp')

        self.mirrorGuide= pm.group (em=True, n=self.name+'MirrorGuide_grp') 
        if not pm.objExists('GUIDES'):
            pm.group ( self.name+'MirrorGuide_grp', n='GUIDES' )
        else:
            pm.parent ( self.name+'MirrorGuide_grp', 'GUIDES')
                        
               
        self.guideMoveall.setParent (self.mirrorGuide)
        self.mirrorGuide.scaleX.set (-1)
        self.mirrorGuide.template.set (1)   
        
        limb.guideMoveall.translate >>  self.guideMoveall.translate
        limb.guideMoveall.rotate >>  self.guideMoveall.rotate
        limb.guideMoveall.scale >>  self.guideMoveall.scale
        limb.startGuide.translate >>  self.startGuide.translate
        limb.startGuide.rotate >>  self.startGuide.rotate
        limb.startGuide.scale >>  self.startGuide.scale
        limb.midGuide.translate >>  self.midGuide.translate
        limb.midGuide.rotate >>  self.midGuide.rotate
        limb.midGuide.scale >>  self.midGuide.scale
        limb.endGuide.translate >>  self.endGuide.translate
        limb.endGuide.rotate >>  self.endGuide.rotate
        limb.endGuide.scale >>  self.endGuide.scale

        if limb.flipAxis:
            self.flipAxis=False
        else:
            self.flipAxis=True
                      
    def doRig(self):
        if not self.guideMoveall:
            self.doGuide()
            
        #apagar todos os node ao reconstruir                      
        if pm.objExists(self.name+'Moveall'):
            pm.delete (self.name+'Moveall')
            
        #Cria o grupo moveAll
        self.moveall = pm.group(empty=True, n=self.name+'Moveall')
        pos =pm.xform (self.guideMoveall, q=True, ws=True, t=True)
        pm.xform (self.moveall, ws=True, t=pos)
        if not pm.objExists('MOVEALL'):
            pm.group ( self.moveall, n='MOVEALL' )
        else:
            pm.parent (self.moveall, 'MOVEALL')

        self.moveall.addAttr('ikfk', at='float',min=0, max=1,dv=1, k=1)
        

        
        #define pontos do guide como vetores usando api para faciitar os calculos
        p1 = pm.xform (self.startGuide, q=True, t=True, ws=True)
        p2 = pm.xform (self.midGuide, q=True, t=True, ws=True)
        p3 = pm.xform (self.endGuide, q=True, t=True, ws=True)
        
        A= om.MVector(p1)
        B= om.MVector(p2)
        C= om.MVector(p3)
        
        if self.lastJoint:
            p4=pm.xform (self.lastGuide, q=True, t=True, ws=True)
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
        
        self.jointLength=AB.length()+BC.length() 
        
        m = orientMatrix (mvector=AB,normal=n,pos=A, axis=self.axis)            
        #cria joint1
        pm.select(cl=True)
        jntName= self.limbDict['startJntSetup']['nameTempl']+self.jntSulfix
        self.startJnt = pm.joint(n=jntName)
        pm.xform (self.startJnt, m = m, ws=True) 
        pm.makeIdentity (self.startJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
        
        #cria joint2
        #criando a matriz do joint conforme a orientacao setada
        m = orientMatrix (mvector=BC,normal=n,pos=B, axis=self.axis)  
        pm.select(cl=True)
        jntName= self.limbDict['midJntSetup']['nameTempl']+self.jntSulfix
        self.midJnt= pm.joint(n=jntName)
        pm.xform (self.midJnt, m = m, ws=True) 
        pm.makeIdentity (self.midJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
        
        #cria joint3
        #aqui so translada o joint, usa a mesma orientacao
        pm.select(cl=True)
        jntName= self.limbDict['endJntSetup']['nameTempl']+self.jntSulfix
        self.endJnt=pm.joint(n=jntName)
        pm.xform (self.endJnt, m = m, ws=True) 
        pm.xform (self.endJnt, t= C, ws=True)
        pm.makeIdentity (self.endJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)
        
        #hierarquia
        pm.parent (self.midJnt, self.startJnt)
        pm.parent (self.endJnt, self.midJnt)
        self.startJnt.setParent (self.moveall)
        
        ##joint4(hand) se estiver setado nas opcoes      
        if self.lastJoint:
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
            jntName= self.limbDict['lastJntSetup']['nameTempl']+self.jntSulfix
            self.lastJnt= pm.joint(n=jntName)
            pm.xform (self.lastJnt, m = m, ws=True) 
            pm.makeIdentity (self.lastJnt, apply=True, r=1, t=0, s=0, n=0, pn=0) 
            
            #cria joint5 e so move
            pm.select(cl=True)
            jntName= self.limbDict['lastJntSetup']['nameTempl']+self.tipJxtSulfix
            self.lastTipJnt=pm.joint(n=jntName)
            pm.xform (self.lastTipJnt, m = m, ws=True) 
            pm.xform (self.lastTipJnt, t=D, ws=True)
            pm.makeIdentity (self.lastTipJnt, apply=True, r=1, t=0, s=0, n=0, pn=0)        
            
            #hierarquia        
            pm.parent (self.lastJnt, self.endJnt)
            pm.parent (self.lastTipJnt, self.lastJnt)            
                
        ##Estrutura FK
        if self.axis=='Y'  or self.axis=='Z' or self.axis=='X':
            axisName=self.axis
        else:
            axisName='X'
        
        displaySetup= self.limbDict['moveAll1CntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.moveAll1Cntrl = cntrlCrv( name = cntrlName, obj= self.startJnt , **displaySetup)
        
        displaySetup= self.limbDict['endCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                  
        self.endCntrl = cntrlCrv (name=cntrlName, obj=self.startJnt,connType='parentConstraint', **displaySetup )       
        self.endCntrl.addAttr('manualStretch', at='float',min=.1,dv=1, k=1)
        
        displaySetup=self.limbDict['midCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.midCntrl = cntrlCrv (name=cntrlName,obj=self.midJnt,connType = 'orientConstraint',**displaySetup)
        self.midCntrl.addAttr('manualStretch', at='float',min=.1,dv=1, k=1)
        
        pm.pointConstraint (self.midJnt, self.midCntrl.getParent(), mo=True)
        
        ##Estrutura IK
        ikH = pm.ikHandle (sj=self.startJnt, ee=self.endJnt, sol="ikRPsolver")

        displaySetup=self.limbDict['ikCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.ikCntrl = cntrlCrv(name = cntrlName, obj=ikH[0],**displaySetup)
        
        #orienta o controle ik de modo a ter aproximadamente a orientacao do eixo global
        #mas aponta o eixo X para a ponta do ultimo bone               
        mat=pm.xform (self.ikCntrl.getParent(), q=True, m=True, ws=True)
        matrix= om.MMatrix (mat)
        Zcomponent = om.MVector (0,0,-1)
        Zaxis = matrix * Zcomponent
        normal = CD^Zaxis

        #CD eh o vetor de direcao do ultimo joint                
        ori = orientMatrix(CD, normal, C, self.axis)       
        pm.xform (self.ikCntrl.getParent(), m=ori, ws=True)
        ikH[0].setParent(self.ikCntrl)
        ikH[0].translate.lock()
        ikH[0].rotate.lock()
        
        self.ikCntrl.addAttr ('pin', at='float',min=0, max=1,dv=0, k=1)
        self.ikCntrl.addAttr ('bias', at='float',min=-0.9, max=0.9, k=1)
        self.ikCntrl.addAttr ('autoStretch', at='float',min=0, max=1,dv=1, k=1)
        self.ikCntrl.addAttr ('manualStretch', at='float',dv=1, k=1)
        self.ikCntrl.addAttr ('twist', at='float',dv=0, k=1)        
            
        #pole vector
        displaySetup=self.limbDict['poleVecCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.poleVec = cntrlCrv(name=cntrlName, obj=self.midJnt,**displaySetup)
        
        #calcula a direcao q deve ficar o polevector
        BA=B-A
        CA=C-A
        U=BA*CA.normal()
        dist=CA.length()
        V=U/dist*dist
        T=A+V*CA.normal()
        D=B-T
        Pole=(D.normal()*4)+B
        
        #test=pm.spaceLocator (p=(0,0,0)) # locator de teste de onde calculou o ponto mais proximo
        #pm.xform (test, t=T)
        
        pm.xform (self.poleVec.getParent() , t=Pole) 
        pm.xform (self.poleVec.getParent() , ro=(0,0,0)) 
        poleCnst = pm.poleVectorConstraint (self.poleVec, ikH[0])
        
        
        pm.parent (self.midCntrl.getParent(), self.endCntrl)
        pm.parent (self.endCntrl.getParent(), self.moveAll1Cntrl)
        pm.parent (self.moveAll1Cntrl.getParent(), self.poleVec.getParent(), self.ikCntrl.getParent(), self.moveall)

        #handCntrls se houver
        if self.lastJoint:
            displaySetup=self.limbDict['startCntrlSetup']
            cntrlName=displaySetup['nameTempl']
            self.startCntrl = cntrlCrv (name=cntrlName, obj=self.lastJnt,**displaySetup)
            buf=pm.group (em=True)
            matrix=pm.xform (self.lastJnt, q=True, ws=True, m=True)
            pm.xform (buf, m=matrix, ws=True)
            pm.parent (buf,self.ikCntrl)
            handCnst = pm.orientConstraint (buf,self.startCntrl, self.lastJnt, mo=False)
            pm.pointConstraint (self.endJnt,self.startCntrl.getParent(), mo=True)
            pm.parent (self.startCntrl.getParent(), self.midCntrl)
        
        #display
        ikH[0].visibility.set(0)
               
        #grupos de stretch
        startGrp = pm.group (empty=True)
        endGrp=pm.group (empty=True)
        pm.parent (endGrp,self.ikCntrl,r=True)
        pm.xform (startGrp , t=p1, ws=True)
        pm.parent (startGrp,self.endCntrl)
        
        ##NODE TREE####### 
        #cria um blend entre uso de poleVector ou so twist
        poleBlendColor= pm.createNode('blendColors', n='poleVecBlend')
        poleAdd = pm.createNode('addDoubleLinear',n='PoleAdd')
        poleCond = pm.createNode('condition', n='poleCond')
        poleCnst.constraintTranslate >> poleBlendColor.color1
        poleBlendColor.color2.set(0,0,0)
        #poleCnst.constraintTranslateX // ikH[0].poleVectorX
        #poleCnst.constraintTranslateY // ikH[0].poleVectorY
        #poleCnst.constraintTranslateZ // ikH[0].poleVectorZ
        poleBlendColor.outputR >> ikH[0].poleVectorX
        poleBlendColor.outputG >> ikH[0].poleVectorY
        poleBlendColor.outputB >> ikH[0].poleVectorZ
        self.moveall.addAttr ('poleVec', at='float', k=1, dv=0, max=1, min=0)
        self.moveall.poleVec >> poleAdd.input1
        self.ikCntrl.pin >> poleAdd.input2
        poleAdd.output >> poleCond.firstTerm
        poleCond.secondTerm.set(0)
        poleCond.operation.set(2)
        poleCond.colorIfFalseR.set(0)
        poleCond.colorIfTrueR.set(1)
        poleCond.outColorR  >> poleBlendColor.blender
        poleCond.outColorR >> self.poleVec.visibility 
              
        #Pin
        p5 = pm.xform (self.poleVec.getParent(), q=True, t=True, ws=True)
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
        
        self.poleVec.worldMatrix[0]  >> pinDist1.inMatrix2
        self.poleVec.worldMatrix[0]  >> pinDist2.inMatrix2
        
        self.moveall.scaleX >> pinMultiScale1.input1
        self.moveall.scaleX >> pinMultiScale2.input1
        
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
        
        stretchDecompMatrix = pm.createNode('decomposeMatrix')
        self.moveall.worldMatrix[0] >> stretchDecompMatrix.inputMatrix
        stretchDecompMatrix.outputScale.outputScaleX >> stretchMultiScale.input1
        
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
               
        self.endCntrl.manualStretch >> ikfkBlend1.input[1]
        self.midCntrl.manualStretch >> ikfkBlend2.input[1]
       
        self.moveall.ikfk >> ikfkReverse.inputX
        ikfkReverse.outputX >> ikfkBlend1.attributesBlender
        ikfkReverse.outputX >> ikfkBlend2.attributesBlender
        
        cnstrConn = self.midCntrl.connections(t='orientConstraint', d=True, s=False)[0] ## arriscando em pegar o primeiro...
        weightAttr = cnstrConn.target.connections(p=True, t='orientConstraint') ##Descobre o parametro de peso do constraint        
        ikfkReverse.outputX >> weightAttr[0]
        
        if self.lastJoint:
            handTargetAttrs = handCnst.target.connections(p=True, t='orientConstraint')
            ikfkReverse.outputX >> handTargetAttrs [1]
            self.moveall.ikfk >> handTargetAttrs [0]
        
        self.moveall.ikfk >> ikH[0].ikBlend      
        ikfkBlend1.output >> self.startJnt.attr('scale'+axisName) 
        ikfkBlend2.output >> self.midJnt.attr('scale'+axisName)
        
        
        ##ikfk visibility
        ikCntrlVisCond = pm.createNode ('condition',n='ikVisCond')
        fkCntrlVisCond = pm.createNode ('condition',n='fkVisCond')
        self.moveall.ikfk >> ikCntrlVisCond.ft
        ikCntrlVisCond.secondTerm.set (0)
        ikCntrlVisCond.operation.set (1)
        ikCntrlVisCond.colorIfTrueR.set (1)
        ikCntrlVisCond.colorIfFalseR.set (0)
        self.moveall.ikfk >> fkCntrlVisCond.ft
        fkCntrlVisCond.secondTerm.set (1)
        fkCntrlVisCond.operation.set (1)
        fkCntrlVisCond.colorIfTrueR.set (1)
        fkCntrlVisCond.colorIfFalseR.set (0)
        
        ikCntrlVisCond.outColor.outColorR >> self.ikCntrl.getParent().visibility
        ikCntrlVisCond.outColor.outColorR >> self.poleVec.getParent().visibility
        fkCntrlVisCond.outColor.outColorR >> self.endCntrl.getParent().visibility
                       
        ##Atributos e conexoes do controle ik
        self.ikCntrl.bias >> biasAdd2.input1D[1]
        self.ikCntrl.bias >> biasAdd1.input1D[0]
        self.ikCntrl.pin >> stretchPinBlend1.attributesBlender
        self.ikCntrl.pin >> stretchPinBlend2.attributesBlender
        self.ikCntrl.manualStretch >> stretchManualStretch1.input1
        self.ikCntrl.manualStretch >> stretchManualStretch2.input1
        self.ikCntrl.manualStretch >> stretchManualStretch3.input1
        self.ikCntrl.autoStretch >> autoStretchSwitch.attributesBlender
        self.ikCntrl.pin >> twistBlend1.attributesBlender
        self.ikCntrl.twist >> twistBlend1.input[0]

        #IMPLEMENTAR atualizar guideDict com valores atuais
        
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
        self.guideMoveall=None

        ##IMPLEMENTAR padroes de nome 
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        grpSulfix='_grp'
        
        ##setaqens de aparencia dos controles
        self.fingerDict={'name':name,'folds':folds, 'axis':axis, 'flipAxis':flipAxis}
        self.fingerDict['moveallCntrlSetup']={'nameTempl':self.name+'MoveAll', 'icone':'circuloX','size':0.1,'color':(1,1,0) }    
        self.fingerDict['palmCntrlSetup']={'nameTempl':self.name+'palm', 'icone':'cubo','size':0.2,'color':(1,0,0) }    
        if self.flipAxis:
            self.fingerDict['baseCntrlSetup']={'nameTempl':self.name+'base', 'icone':'dropZ','size':0.1,'color':(1,1,0) } 
        else:
            self.fingerDict['baseCntrlSetup']={'nameTempl':self.name+'base', 'icone':'dropMenosZ','size':0.1,'color':(1,1,0) }    
        #self.fingerDict['tipCntrlSetup']={'nameTempl':self.name+'tip', 'icone':'circuloX','size':0.3,'color':(0,1,1) }    
        self.fingerDict['fold1CntrlSetup']={'nameTempl':self.name+'fold1', 'icone':'circuloX','size':0.3,'color':(0,1,1) }    
        self.fingerDict['fold2CntrlSetup']={'nameTempl':self.name+'fold2', 'icone':'circuloX','size':0.3,'color':(0,1,1) }    

        self.fingerDict['moveallGuideSetup']={'nameTempl':self.name+'MoveAll','size':0.1,'color':(1,1,0) }    
        self.fingerDict['palmGuideSetup']={'nameTempl':self.name+'palm', 'size':0.2,'color':(1,0,0) }    
        self.fingerDict['baseGuideSetup']={'nameTempl':self.name+'base', 'size':0.3,'color':(1,1,0) }    
        self.fingerDict['tipGuideSetup']={'nameTempl':self.name+'tip', 'size':0.3,'color':(0,1,1) }    
        self.fingerDict['fold1GuideSetup']={'nameTempl':self.name+'fold1', 'size':0.3,'color':(0,1,1) }    
        self.fingerDict['fold2GuideSetup']={'nameTempl':self.name+'fold2', 'size':0.3,'color':(0,1,1) }    

        self.fingerDict['palmJntSetup']={'nameTempl':self.name+'Palm', 'icone':'Bone','size':0.2}    
        self.fingerDict['baseJntSetup']={'nameTempl':self.name+'Base', 'icone':'Bone','size':0.3}    
        self.fingerDict['tipJntSetup']={'nameTempl':self.name, 'icone':'Bone','size':0.3}    
        self.fingerDict['fold1JntSetup']={'nameTempl':self.name+'Fold1', 'icone':'Bone','size':0.3}    
        self.fingerDict['fold2JntSetup']={'nameTempl':self.name+'Fold2', 'icone':'Bone','size':0.3}    
        self.fingerDict['guideDict']={}
        self.fingerGuideDict = {'moveall':[0,0,0],'palm':[0,0,0],'base':[1,0,0],'tip':[2,0,0], 'fold1':[0,0.05,0],'fold2':[0,0,0]}
        self.fingerDict.update(kwargs) 
        self.fingerGuideDict.update(self.fingerDict['guideDict']) 
        self.fingerDict['guideDict']=self.fingerGuideDict.copy()
        
    #guide 
    def doGuide(self, **kwargs):
        self.fingerGuideDict = self.fingerDict['guideDict'].copy()
        self.fingerGuideDict.update(kwargs) # atualiza com o q foi entrado
                
        #se existir apaga
        guideName= self.fingerDict['moveallGuideSetup']['nameTempl']+self.guideSulfix
        if pm.objExists (guideName):
            pm.delete (guideName)        
        self.guideMoveall = pm.group(n=guideName,em=True)

        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')        

        guideName=self.fingerDict['palmGuideSetup']['nameTempl']+self.guideSulfix
        self.palmGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.palmGuide.displayHandle.set(1)
        self.palmGuide.localScale.set(0.1,0.1,0.1) 

        guideName=self.fingerDict['baseGuideSetup']['nameTempl']+self.guideSulfix
        self.baseGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.baseGuide.displayHandle.set(1)
        self.baseGuide.translate.set(1.3,0,0)
        self.baseGuide.localScale.set(0.1,0.1,0.1)
        
        guideName=self.fingerDict['tipGuideSetup']['nameTempl']+self.guideSulfix
        self.tipGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.tipGuide.displayHandle.set(1)
        self.tipGuide.translate.set(1.7,0,0)
        self.tipGuide.localScale.set(0.1,0.1,0.1)
        pm.parent (self.tipGuide, self.baseGuide,self.palmGuide, self.guideMoveall)
       
        #cria conforme o numero de dobras       
        if self.folds==2:
            guideName=self.fingerDict['fold1GuideSetup']['nameTempl']+self.guideSulfix
            self.fold1Guide = pm.spaceLocator (n=guideName,p=(0,0,0))
            self.fold1Guide.displayHandle.set(1)        
            fold1GuideGrp = pm.group(self.fold1Guide)
            fold1GuideGrp.translate.set(1.3,0,0)
            self.fold1Guide.localScale.set(0.1,0.1,0.1)

            guideName=self.fingerDict['fold2GuideSetup']['nameTempl']+self.guideSulfix
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
            pm.parent (fold1GuideGrp,fold2GuideGrp, self.guideMoveall)
            
        elif self.folds==1:
            guideName=self.fingerDict['fold1GuideSetup']['nameTempl']+self.guideSulfix
            self.fold1Guide = pm.spaceLocator (n=guideName,p=(0,0,0))        
            self.fold1Guide.displayHandle.set(1) 
            fold1GuideGrp = pm.group(self.fold1Guide)
            fold1GuideGrp.translate.set(1.3,0,0)
            self.fold1Guide.localScale.set(0.1,0.1,0.1)
            
            pm.aimConstraint(self.fold1Guide,self. baseGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.tipGuide,fold1GuideGrp, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            pm.aimConstraint(self.fold1Guide,self.tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')
            cns=pm.pointConstraint(self.baseGuide, self.tipGuide , fold1GuideGrp, mo=False)

            pm.parent (fold1GuideGrp, self.guideMoveall)
            
        elif self.folds==0:    
            guideName=self.fingerDict['fold1GuideSetup']['nameTempl']+self.guideSulfix
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
            pm.parent (fold1GuideGrp, self.guideMoveall)
        
        #move para lugar definido nos parametros    
        self.guideMoveall.translate.set( self.fingerGuideDict['moveall'])
        self.palmGuide.translate.set( self.fingerGuideDict['palm'])
        self.baseGuide.translate.set( self.fingerGuideDict['base'])
        self.tipGuide.translate.set( self.fingerGuideDict['tip'])
        self.fold1Guide.translate.set( self.fingerGuideDict['fold1'])
        if self.folds==2:
            self.fold2Guide.translate.set( self.fingerGuideDict['fold2'])


    def getGuideFromScene(self):
                
        #se existir apaga
        guideName= self.fingerDict['moveallGuideSetup']['nameTempl']+self.guideSulfix
        self.guideMoveall = pm.PyNode (guideName)
        
        guideName=self.fingerDict['palmGuideSetup']['nameTempl']+self.guideSulfix
        self.palmGuide = pm.PyNode (guideName)

        guideName=self.fingerDict['baseGuideSetup']['nameTempl']+self.guideSulfix
        self.baseGuide = pm.PyNode (guideName)
        
        guideName=self.fingerDict['tipGuideSetup']['nameTempl']+self.guideSulfix
        self.tipGuide = pm.PyNode (guideName)
      
        guideName=self.fingerDict['fold1GuideSetup']['nameTempl']+self.guideSulfix
        self.fold1Guide = pm.PyNode (guideName)

        if self.folds==2:
            guideName=self.fingerDict['fold2GuideSetup']['nameTempl']+self.guideSulfix
            self.fold2Guide = pm.PyNode (guideName) 



    def doRig(self):
        # se nao existir guide, cria um default
        if not self.guideMoveall:
            self.doGuide()
            
        # se existir um modulo igual, apaga
        moveallName = self.fingerDict['moveallCntrlSetup']['nameTempl']
        if pm.objExists(moveallName):
            pm.delete(moveallName)

        cntrlName = self.fingerDict['moveallCntrlSetup']['nameTempl']            
        self.moveall = pm.group (name=cntrlName,em=True)


        pos =pm.xform (self.guideMoveall, q=True, ws=True, t=True)
        pm.xform (self.moveall, ws=True, t=pos)
 
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
            jntNames= [self.fingerDict['palmJntSetup']['nameTempl'],self.fingerDict['baseJntSetup']['nameTempl'],self.fingerDict['fold1JntSetup']['nameTempl'],self.fingerDict['fold2JntSetup']['nameTempl'], self.fingerDict['tipJntSetup']['nameTempl']]
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
                           
            m= orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
            jntName=jntNames[i]+self.jntSulfix
            j1 = pm.joint(n=jntName)
            fingerJnts.append(j1)
            pm.xform (j1, m = m, ws=True) 
            pm.makeIdentity (j1, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        jntName=self.fingerDict['tipJntSetup']['nameTempl']+self.tipJxtSulfix
        j1 = pm.joint(n=jntName)
        fingerJnts.append(j1)
        pm.xform (j1, m = m, ws=True)
        pm.xform (j1, t =C, ws=True) 
        pm.makeIdentity (j1, apply=True, r=1, t=0, s=1, n=0, pn=0)

        #cria os controles
        last=None
        displaySetup= self.fingerDict['palmCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                  
        cntrl0= cntrlCrv(name=cntrlName, connType='parentConstraint',obj=fingerJnts[0], **displaySetup)    

        displaySetup= self.fingerDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        cntrl1 = cntrlCrv(name=cntrlName, connType='parentConstraint',obj=fingerJnts[1], **displaySetup )

        pm.parent(cntrl1.getParent(),cntrl0)
        last=cntrl1
        
        #cria os controles conforme a o numero setado de dobras
        if self.folds>0:
            cntrl1.addAttr('curl1',k=1,at=float,dv=0)
            displaySetup= self.fingerDict['fold1CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl']
            cntrl2 = cntrlCrv(name=cntrlName,connType='parentConstraint', obj=fingerJnts[2],offsets=1, **displaySetup )
            pm.parent (cntrl2.getParent(2),cntrl1)
            cntrl1.curl1 >> cntrl2.getParent().rotateY
        if self.folds > 1:
            cntrl1.addAttr('curl2',k=1,at=float,dv=0)
            displaySetup= self.fingerDict['fold2CntrlSetup'].copy()
            cntrlName = displaySetup['nameTempl']
            cntrl3 = cntrlCrv(name=cntrlName,connType='parentConstraint', obj=fingerJnts[3],offsets=1, **displaySetup )
            pm.parent (cntrl3.getParent(2),cntrl2)
            cntrl1.curl2 >> cntrl3.getParent().rotateY



        pm.parent (fingerJnts[0],cntrl0.getParent(),self.moveall)


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
        self.guideMoveall=None
        
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        grpSulfix='_grp'
        
        self.handDict={'name':name, 'axis':axis, 'flipAxis':flipAxis, 'folds':folds, 'fingerNum':fingerNum}
        self.handDict['fingers']={}
        self.handDict['guideDict']={'moveall':[0,0,0]}
        self.handDict['fingerNames']=['Thumb','Index','Middle','Ring', 'Pink', 'Other', 'Other1']
#       self.handDict['fingerNames']=[ 'Pink','Ring','Middle','Index', 'Thumb']

        for i in range(fingerNum):
            fingerName=self.name+self.handDict['fingerNames'][i]#IMPLEMENTAR nomes dos dedos            
            self.handDict['fingers']['finger'+str(i+1)] = {'name':fingerName,
                                                'fingerGuideDict':{'moveall':[0,0,(((fingerNum/2)*.3)-(i*.3))],'palm':[0,0,0],'base':[1,0,0],'tip':[2,0,0], 'fold1':[0,0.05,0],'fold2':[0,0,0]},
                                                'instance':None
                                                }
        self.handDict.update(kwargs)
        
        for finger in self.handDict['fingers']:                                                       
            f=Finger(name=self.handDict['fingers'][finger]['name'],axis=self.axis,flipAxis=self.flipAxis,folds=self.folds)                                 
            self.handDict['fingers'][finger]['instance'] = f
            
    def doGuide(self, **kwargs):
        #IMPLEMENTAR update do handDict - talvez handGuideDict
        self.handGuideDict = self.handDict['guideDict'].copy()
        self.handGuideDict.update(kwargs)
        if pm.objExists(self.name+'Moveall_guide'):
            pm.delete (self.name+'Moveall_guide')

        self.guideMoveall = pm.group(n=self.name+'Moveall_guide',em=True)
        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')              


        for finger in self.handDict['fingers']:                                                                                  
            f = self.handDict['fingers'][finger]['instance']
            dict = self.handDict['fingers'][finger]['fingerGuideDict']
            f.doGuide(**dict)
            pm.parent (f.guideMoveall,self.guideMoveall)

        pm.xform (self.guideMoveall, ws=True, t=self.handGuideDict['moveall'])

    def getGuideFromScene(self): 
        guideName=self.name+'Moveall_guide'           
        self.guideMoveall = pm.PyNode(guideName)
        for finger in self.handDict['fingers']:                                                                                  
            self.handDict['fingers'][finger]['instance'].getGuideFromScene()

        
    def mirrorConnectGuide(self, hand):
        if not self.guideMoveall:
            self.doGuide()        
        if not hand.guideMoveall:
            hand.doGuide()

        if pm.objExists(self.name+'MirrorGuide_grp'):
            pm.delete (self.name+'MirrorGuide_grp')

        self.mirrorGuide= pm.group (em=True, n=self.name+'MirrorGuide_grp') 
        if not pm.objExists('GUIDES'):
            pm.group ( self.name+'MirrorGuide_grp', n='GUIDES' )
        else:
            pm.parent ( self.name+'MirrorGuide_grp', 'GUIDES')
                    
        self.guideMoveall.setParent (self.mirrorGuide)
        self.mirrorGuide.scaleX.set (-1)
        self.mirrorGuide.template.set (1)   
        
        hand.guideMoveall.translate >>  self.guideMoveall.translate
        hand.guideMoveall.rotate >>  self.guideMoveall.rotate
        hand.guideMoveall.scale >>  self.guideMoveall.scale
        
        for a, b in zip(self.handDict['fingers'], hand.handDict['fingers']):
            f_mirror = self.handDict['fingers'][a]['instance']   
            f_origin = hand.handDict['fingers'][b]['instance']  

            f_origin.guideMoveall.translate >> f_mirror.guideMoveall.translate
            f_origin.guideMoveall.rotate >> f_mirror.guideMoveall.rotate
            f_origin.guideMoveall.scale >> f_mirror.guideMoveall.scale
            f_origin.palmGuide.translate >> f_mirror.palmGuide.translate
            f_origin.palmGuide.rotate >> f_mirror.palmGuide.rotate
            f_origin.palmGuide.scale >> f_mirror.palmGuide.scale
            f_origin.baseGuide.translate >> f_mirror.baseGuide.translate
            f_origin.baseGuide.rotate >> f_mirror.baseGuide.rotate
            f_origin.baseGuide.scale >> f_mirror.baseGuide.scale
            f_origin.tipGuide.translate >> f_mirror.tipGuide.translate
            f_origin.tipGuide.rotate >> f_mirror.tipGuide.rotate
            f_origin.tipGuide.scale >> f_mirror.tipGuide.scale
            f_origin.fold1Guide.translate >> f_mirror.fold1Guide.translate
            f_origin.fold1Guide.rotate >> f_mirror.fold1Guide.rotate
            f_origin.fold1Guide.scale >> f_mirror.fold1Guide.scale
            if self.folds==2:
                f_origin.fold2Guide.translate >> f_mirror.fold2Guide.translate
                f_origin.fold2Guide.rotate >> f_mirror.fold2Guide.rotate
                f_origin.fold2Guide.scale >> f_mirror.fold2Guide.scale  
                                                      
        #if hand.flipAxis:
        #    self.flipAxis=False
        #else:
        #    self.flipAxis=True


    def doRig(self, **kwargs):
        if not self.guideMoveall:
            self.doGuide()

        if pm.objExists (self.name+'Moveall'):
            pm.delete (self.name+'Moveall')
        
        self.moveall =pm.group(n=self.name+'Moveall',em=True)
        pos =pm.xform (self.guideMoveall, q=True, ws=True, t=True)
        pm.xform (self.moveall, ws=True, t=pos)
        
        if not pm.objExists('MOVEALL'):
            pm.group ( self.moveall, n='MOVEALL' )
        else:
            pm.parent (self.moveall, 'MOVEALL')
        
        for finger in self.handDict['fingers']:                                                                                  
            f = self.handDict['fingers'][finger]['instance']
            f.flipAxis = self.flipAxis
            dict=self.handDict['fingers'][finger]['fingerGuideDict']
            f.doRig()
            pm.parent (f.moveall, self.moveall)

        #IMPLEMENTAR atualizar o guideDict
        
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
    
    def __init__(self,name='foot',flipAxis=False, axis='X', folds=2, fingerNum=0, **kwargs):
    
        self.name=name
        self.flipAxis=flipAxis
        self.axis=axis
        self.folds=folds
        self.fingerNum=fingerNum
        self.guideMoveall=None
        
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        self.grpSulfix='_grp'
        
        #definicoes da aparencia dos controles
        self.footDict={'name':name, 'axis':axis, 'flipAxis':flipAxis}
        self.footDict['moveallCntrlSetup']={'nameTempl':self.name+'MoveAll', 'icone':'circuloX','size':1.8,'color':(1,1,0) }    
        self.footDict['centerCntrlSetup'] = {'nameTempl':self.name+'Center', 'icone':'circuloX','size':2,'color':(0,0,1) }    
        self.footDict['tipCntrlSetup'] = {'nameTempl':self.name+'Tip', 'icone':'bola','size':0.5,'color':(0,1,1)}
        self.footDict['heelCntrlSetup'] = {'nameTempl':self.name+'Heel', 'icone':'bola', 'size':0.5, 'color':(0,1,1) }
        self.footDict['ankleCntrlSetup'] = {'nameTempl':self.name+'Ankle', 'icone':'cubo', 'size':1, 'color':(0,1,1) }
        self.footDict['ballCntrlSetup'] = {'nameTempl':self.name+'Ball', 'icone':'circuloX', 'size':1.5, 'color':(1,1,0) }
        self.footDict['inCntrlSetup'] = {'nameTempl':self.name+'In', 'icone':'bola', 'size':0.4, 'color':(0,1,1)}
        self.footDict['outCntrlSetup'] = {'nameTempl':self.name+'Out', 'icone':'bola', 'size':0.4, 'color':(0,1,1)}
        self.footDict['rollCntrlSetup'] = {'nameTempl':self.name+'Roll', 'icone':'cubo', 'size':0.4, 'color':(0,.6,1)}
        self.footDict['baseCntrlSetup'] = {'nameTempl':self.name+'Base', 'icone':'quadradoY', 'size':3, 'color':(0,0,1)}
        self.footDict['slideCntrlSetup'] = {'nameTempl':self.name+'Slide', 'icone':'bola', 'size':0.4, 'color':(1,0,0)}
        self.footDict['toLimbCntrlSetup'] = {'nameTempl':self.name+'ToLimb', 'icone':'bola', 'size':0.5, 'color':(1,1,0)}
        self.footDict['toeCntrlSetup'] = {'nameTempl':self.name+'Toe', 'icone':'circuloX', 'size':1.0, 'color':(1,1,0)}

        self.footDict['ankleFkCntrlSetup'] = {'nameTempl':self.name+'TnkleFk', 'icone':'grp', 'size':1.0, 'color':(0,1,0)}
        self.footDict['toeFkCntrlSetup'] = {'nameTempl':self.name+'ToeFk', 'icone':'circuloX', 'size':1.0, 'color':(0,1,0)}

        self.footDict['moveallGuideSetup']={'nameTempl':self.name+'MoveAll', 'size':1.8,'color':(1,1,0) }    
        self.footDict['centerGuideSetup'] = {'nameTempl':self.name+'Center', 'size':2,'color':(1,1,0) }    
        self.footDict['tipGuideSetup'] = {'nameTempl':self.name+'Tip', 'size':0.5,'color':(0,1,1)}
        self.footDict['heelGuideSetup'] = {'nameTempl':self.name+'Heel','size':0.5, 'color':(0,1,1) }
        self.footDict['ankleGuideSetup'] = {'nameTempl':self.name+'Ankle', 'size':1, 'color':(0,1,1) }
        self.footDict['ballGuideSetup'] = {'nameTempl':self.name+'Ball',  'size':1.5, 'color':(1,1,0) }
        self.footDict['inGuideSetup'] = {'nameTempl':self.name+'In', 'size':0.4, 'color':(0,1,1)}
        self.footDict['outGuideSetup'] = {'nameTempl':self.name+'Out',  'size':0.4, 'color':(0,1,1)}
        self.footDict['rollGuideSetup'] = {'nameTempl':self.name+'Roll', 'size':0.4, 'color':(0,0,1)}
        self.footDict['baseGuideSetup'] = {'nameTempl':self.name+'Base', 'size':3, 'color':(0,1,0)}
        self.footDict['slideGuideSetup'] = {'nameTempl':self.name+'Slide', 'size':0.4, 'color':(1,0,0)}
        self.footDict['jointGuideSetup'] = {'nameTempl':self.name+'Joint', 'size':0.5, 'color':(1,1,0)}
        self.footDict['toeGuideSetup'] = {'nameTempl':self.name+'Toe', 'size':1.0, 'color':(1,1,0)}

        self.footDict['fingers']={}
        self.footDict['fingerNames']=['Thumb','Index','Middle','Ring', 'Pink', 'Other', 'Other1']
   
        self.footDict['ankleJntSetup'] = {'nameTempl':self.name+'Ankle', 'icone':'Bone', 'size':1.0}
        self.footDict['toeJntSetup'] = {'nameTempl':self.name+'Toe', 'icone':'Bone', 'size':1.0}
        self.footDict['guideDict'] = {}
        self.footGuideDict = {'moveall':[0,0,0],'center':[0,0,0],'tip':[3,0,0],'heel':[-1,0,0],'ankle':[0,1,0],'ball':[2,0.5,0],'in':[2,0,-1],'out':[2,0,1]}

        for i in range(fingerNum):
            fingerName=self.name+self.footDict['fingerNames'][i]#IMPLEMENTAR nomes dos dedos
            step = 1.8/fingerNum
            ini = 0.9 - step/2.0     
            self.footDict['fingers']['finger'+str(i+1)] = {'name':fingerName,
                                                'fingerGuideDict':{'moveall':[2,0,ini-(i*step)],'palm':[0,0,0],'base':[.3,0,0],'tip':[.8,0,0], 'fold1':[0,0.05,0],'fold2':[0,0,0]},
                                                'instance':None,
                                                'isHeelFinger':False}
        self.footDict.update(kwargs) 
        for finger in self.footDict['fingers']:                                                       
            f=Finger(name=self.footDict['fingers'][finger]['name'],axis=self.axis,flipAxis=self.flipAxis,folds=self.folds)                                 
            self.footDict['fingers'][finger]['instance'] = f
        self.footGuideDict.update(self.footDict['guideDict']) 
        self.footDict['guideDict']=self.footGuideDict.copy()
                       
    def doGuide(self,**kwargs):
        #atualiza o footGuideDict com o q for entrado aqui nesse metodo
        #ex: doGuide (center=[0,0,0], tip=[10,10,0]
        self.footGuideDict= self.footDict['guideDict'].copy() 
        self.footGuideDict.update(kwargs)
                
        guideName=self.footDict['moveallGuideSetup']['nameTempl']+'_guide' 
        # deleta se existir
        if pm.objExists(guideName):
            pm.delete (guideName)
          
        self.guideMoveall=pm.group (n=guideName ,em=True)
        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')
        #cria guides segundo os nomes dos controles e nas posicoes definidas no dicionario footGuideDict 

        guideName=self.footDict['centerGuideSetup']['nameTempl']+self.guideSulfix
        self.centerGuide=pm.spaceLocator (n=guideName, p=(0,0,0))
        self.centerGuide.localScale.set(.2,.2,.2)
        self.centerGuide.displayHandle.set(1)
        
        guideName=self.footDict['centerGuideSetup']['nameTempl']+self.grpSulfix
        self.centerGuideGrp=pm.group(self.centerGuide, n=guideName)
        
        guideName=self.footDict['tipGuideSetup']['nameTempl']+self.guideSulfix
        self.tipGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.tipGuide.translate.set(self.footGuideDict['tip'])
        self.tipGuide.localScale.set(.2,.2,.2)
        self.tipGuide.displayHandle.set(1)
                
        guideName=self.footDict['heelGuideSetup']['nameTempl']+self.guideSulfix
        self.heelGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.heelGuide.translate.set(self.footGuideDict['heel'])
        self.heelGuide.localScale.set(.2,.2,.2)
        self.heelGuide.displayHandle.set(1)
        
        guideName=self.footDict['ankleGuideSetup']['nameTempl']+self.guideSulfix
        self.ankleGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.ankleGuide.translate.set(self.footGuideDict['ankle'])
        self.ankleGuide.localScale.set(.2,.2,.2)
        self.ankleGuide.displayHandle.set(1)
        
        guideName=self.footDict['ballGuideSetup']['nameTempl']+self.guideSulfix
        self.ballGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.ballGuide.translate.set(self.footGuideDict['ball'])
        self.ballGuide.localScale.set(.2,.2,.2)
        self.ballGuide.displayHandle.set(1)
        
        guideName=self.footDict['inGuideSetup']['nameTempl']+self.guideSulfix
        self.inGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.inGuide.translate.set(self.footGuideDict['in'])
        self.inGuide.localScale.set(.2,.2,.2)
        self.inGuide.displayHandle.set(1)
        
        guideName=self.footDict['outGuideSetup']['nameTempl']+self.guideSulfix
        self.outGuide=pm.spaceLocator (n=guideName,p=(0,0,0))
        self.outGuide.translate.set(self.footGuideDict['out'])
        self.outGuide.localScale.set(.2,.2,.2)
        self.outGuide.displayHandle.set(1)

        for finger in self.footDict['fingers']:                                                                                  
            f = self.footDict['fingers'][finger]['instance']
            dict = self.footDict['fingers'][finger]['fingerGuideDict']
            f.doGuide(**dict)
            pm.parent (f.guideMoveall,self.tipGuide)
                    
        pm.pointConstraint (self.tipGuide,self.heelGuide, self.centerGuideGrp)
        pm.pointConstraint (self.tipGuide, self.centerGuideGrp, e=True, w=0.25)
        pm.pointConstraint (self.heelGuide, self.centerGuideGrp, e=True, w=0.75)

        pm.aimConstraint(self.heelGuide,self.tipGuide, weight=1, aimVector=(-1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')              
        pm.aimConstraint(self.tipGuide,self.centerGuide, weight=1, aimVector=(1, 0 ,0) , upVector=(0, 1, 0),worldUpVector=(0,1,0), worldUpType='scene')              
        
        pm.parent (self.ballGuide, self.inGuide,self.outGuide, self.tipGuide)
        self.ankleGuide.setParent (self.centerGuide)

        pm.parent (self.centerGuideGrp , self.tipGuide,self.heelGuide, self.guideMoveall)

        
        self.guideMoveall.translate.set(self.footGuideDict['moveall'])

    def getGuideFromScene(self):               
        guideName=self.footDict['moveallGuideSetup']['nameTempl']+'_guide'           
        self.guideMoveall=pm.PyNode(guideName)
        
        guideName=self.footDict['centerGuideSetup']['nameTempl']+self.guideSulfix
        self.centerGuide=pm.PyNode(guideName)
       
        guideName=self.footDict['centerGuideSetup']['nameTempl']+self.grpSulfix
        self.centerGuideGrp=pm.PyNode(guideName)
        
        guideName=self.footDict['tipGuideSetup']['nameTempl']+self.guideSulfix
        self.tipGuide=pm.PyNode(guideName)
                
        guideName=self.footDict['heelGuideSetup']['nameTempl']+self.guideSulfix
        self.heelGuide=pm.PyNode(guideName)
       
        guideName=self.footDict['ankleGuideSetup']['nameTempl']+self.guideSulfix
        self.ankleGuide=pm.PyNode(guideName)

        guideName=self.footDict['ballGuideSetup']['nameTempl']+self.guideSulfix
        self.ballGuide=pm.PyNode(guideName)
       
        guideName=self.footDict['inGuideSetup']['nameTempl']+self.guideSulfix
        self.inGuide=pm.PyNode(guideName)
        
        guideName=self.footDict['outGuideSetup']['nameTempl']+self.guideSulfix
        self.outGuide=pm.PyNode(guideName)

        for finger in self.footDict['fingers']:                                                                                  
            self.footDict['fingers'][finger]['instance'].getGuideFromScene()
        

    def mirrorConnectGuide(self,foot):
        if not self.guideMoveall:
            self.doGuide()
        if not foot.guideMoveall:
            foot.doGuide()

        if pm.objExists(self.name+'MirrorGuide_grp'):
            pm.delete (self.name+'MirrorGuide_grp')

        self.mirrorGuide= pm.group (em=True, n=self.name+'MirrorGuide_grp') 
        if not pm.objExists('GUIDES'):
            pm.group ( self.name+'MirrorGuide_grp', n='GUIDES' )
        else:
            pm.parent ( self.name+'MirrorGuide_grp', 'GUIDES')
                  
        self.guideMoveall.setParent (self.mirrorGuide)
        self.mirrorGuide.scaleX.set (-1)
        self.mirrorGuide.template.set (1)   
        
        foot.guideMoveall.translate >>  self.guideMoveall.translate
        foot.guideMoveall.rotate >>  self.guideMoveall.rotate
        foot.guideMoveall.scale >>  self.guideMoveall.scale

        foot.centerGuide.translate >>  self.centerGuide.translate
        foot.centerGuide.rotate >>  self.centerGuide.rotate
        foot.centerGuide.scale >>  self.centerGuide.scale

        foot.tipGuide.translate >>  self.tipGuide.translate
        foot.tipGuide.rotate >>  self.tipGuide.rotate
        foot.tipGuide.scale >>  self.tipGuide.scale

        foot.heelGuide.translate >>  self.heelGuide.translate
        foot.heelGuide.rotate >>  self.heelGuide.rotate
        foot.heelGuide.scale >>  self.heelGuide.scale

        foot.ankleGuide.translate >>  self.ankleGuide.translate
        foot.ankleGuide.rotate >>  self.ankleGuide.rotate
        foot.ankleGuide.scale >>  self.ankleGuide.scale

        foot.ballGuide.translate >>  self.ballGuide.translate
        foot.ballGuide.rotate >>  self.ballGuide.rotate
        foot.ballGuide.scale >>  self.ballGuide.scale

        foot.inGuide.translate >>  self.inGuide.translate
        foot.inGuide.rotate >>  self.inGuide.rotate
        foot.inGuide.scale >>  self.inGuide.scale

        foot.outGuide.translate >>  self.outGuide.translate
        foot.outGuide.rotate >>  self.outGuide.rotate
        foot.outGuide.scale >>  self.outGuide.scale

        for a, b in zip(self.footDict['fingers'], foot.footDict['fingers']):
            f_mirror = self.footDict['fingers'][a]['instance']   
            f_origin = foot.footDict['fingers'][b]['instance']  

            f_origin.guideMoveall.translate >> f_mirror.guideMoveall.translate
            f_origin.guideMoveall.rotate >> f_mirror.guideMoveall.rotate
            f_origin.guideMoveall.scale >> f_mirror.guideMoveall.scale
            f_origin.palmGuide.translate >> f_mirror.palmGuide.translate
            f_origin.palmGuide.rotate >> f_mirror.palmGuide.rotate
            f_origin.palmGuide.scale >> f_mirror.palmGuide.scale
            f_origin.baseGuide.translate >> f_mirror.baseGuide.translate
            f_origin.baseGuide.rotate >> f_mirror.baseGuide.rotate
            f_origin.baseGuide.scale >> f_mirror.baseGuide.scale
            f_origin.tipGuide.translate >> f_mirror.tipGuide.translate
            f_origin.tipGuide.rotate >> f_mirror.tipGuide.rotate
            f_origin.tipGuide.scale >> f_mirror.tipGuide.scale
            f_origin.fold1Guide.translate >> f_mirror.fold1Guide.translate
            f_origin.fold1Guide.rotate >> f_mirror.fold1Guide.rotate
            f_origin.fold1Guide.scale >> f_mirror.fold1Guide.scale
            if self.folds==2:
                f_origin.fold2Guide.translate >> f_mirror.fold2Guide.translate
                f_origin.fold2Guide.rotate >> f_mirror.fold2Guide.rotate
                f_origin.fold2Guide.scale >> f_mirror.fold2Guide.scale  

        #if foot.flipAxis:
        #    self.flipAxis=False
        #else:
        #    self.flipAxis=True
        
                       
    def doRig(self):
        if not self.guideMoveall:
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
        m= orientMatrix(mvector=AD, normal=n, pos=A, axis=self.axis)
        jntName=self.footDict['ankleJntSetup']['nameTempl']+self.jntSulfix
        j1 = pm.joint(n=jntName)
        pm.xform (j1, m = m, ws=True) 
        pm.makeIdentity (j1, apply=True, r=1, t=0, s=1, n=0, pn=0)
                
        #cria os joints     
        m= orientMatrix(mvector=CD, normal=n, pos=D, axis=self.axis)
        jntName=self.footDict['toeJntSetup']['nameTempl']+self.jntSulfix
        j2 = pm.joint(n=jntName)
        pm.xform (j2, m = m, ws=True) 
        pm.makeIdentity (j2, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        jntName=self.footDict['toeJntSetup']['nameTempl']+self.tipJxtSulfix
        j3 = pm.joint(n=jntName)
        pm.xform (j3, m = m, ws=True)
        pm.xform (j3, t =C, ws=True) 
        pm.makeIdentity (j3, apply=True, r=1, t=0, s=1, n=0, pn=0)
        #e faz os ikhandles
        ballIkh = pm.ikHandle (sj=j1, ee=j2, sol="ikRPsolver")
        tipIkh = pm.ikHandle (sj=j2, ee=j3, sol="ikRPsolver")
        
        self.moveall=pm.group (em=True,n=cntrlName)
        self.moveall.translate.set(center)
        if not pm.objExists('MOVEALL'):
            pm.group ( self.moveall, n='MOVEALL' )
        else:
            pm.parent (self.moveall, 'MOVEALL')

        
        #esse controle deve levar o controle ik da ponta do limb para funcionar o pe 
        displaySetup= self.footDict['toLimbCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.limbConnectionCntrl=cntrlCrv(name=cntrlName,obj=j1,connType='parentConstraint', **displaySetup)

        #base cntrl
        displaySetup= self.footDict['baseCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        self.baseCntrl=cntrlCrv(name=cntrlName,obj=self.centerGuide, **displaySetup)
        pm.move (.8,0,0, self.baseCntrl, r=True, os=True)
        pm.xform (self.baseCntrl, rp=ankle, ws=True)
        pm.scale (self.baseCntrl, [1,1,.5], r=True)
        pm.makeIdentity (self.baseCntrl, apply=True, r=0, t=1, s=1, n=0, pn=0)
        self.baseCntrl.addAttr ('extraRollCntrls',min=0, max=1, dv=0, k=1)
        
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
        self.baseCntrl.extraRollCntrls >> inCntrl.getParent().visibility        
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
        rollCntrl.getParent().translateBy((0,1.5,1))

        for finger in self.footDict['fingers']:                                                                                  
            f = self.footDict['fingers'][finger]['instance']
            f.flipAxis = self.flipAxis
            dict=self.footDict['fingers'][finger]['fingerGuideDict']
            f.doRig()
            if self.footDict['fingers'][finger]['isHeelFinger']:
                pm.parent (f.moveall, j1)
            else:
                pm.parent (f.moveall, j2)
                   
        
        #hierarquia
        pm.parent (ballCntrl.getParent(), toeCntrl.getParent(), heelCntrl)
        heelCntrl.getParent().setParent(tipCntrl)
        tipCntrl.getParent().setParent(outCntrl)
        outCntrl.getParent().setParent(inCntrl)
        inCntrl.getParent().setParent(slideCompensateGrp)
        rollCntrl.getParent().setParent(slideCompensateGrp)
        slideCntrl.getParent().setParent(self.baseCntrl)
        ballIkh[0].setParent (ballCntrl)
        ballIkh[0].visibility.set(0)
        tipIkh[0].setParent (toeCntrl)
        tipIkh[0].visibility.set(0)
        self.limbConnectionCntrl.getParent().setParent (ballCntrl)
        pm.parent (j1,self.baseCntrl.getParent(),self.moveall)
        
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
        #inverte se for mirror pq o controle tem 
        if self.flipAxis:
            animUA.output >> inCntrl.getParent().rotateX
        else:
            animUA.output >> outCntrl.getParent().rotateX
        
        animUA=pm.createNode('animCurveUA')
        pm.setKeyframe(animUA, float=float(0), value=float(0), itt='Linear',ott='Linear')
        pm.setKeyframe(animUA, float=float(-2.5), value=float(-120), itt='Linear',ott='Linear')
        rollCntrl.translateZ >> animUA.input
        if self.flipAxis:
            animUA.output >> outCntrl.getParent().rotateX
        else:
            animUA.output >> inCntrl.getParent().rotateX

        #controles fk
        displaySetup= self.footDict['ankleFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.ankleFkCntrl=cntrlCrv(name=cntrlName,obj=j1,connType='parentConstraint', **displaySetup)

        displaySetup= self.footDict['toeFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.toeFkCntrl=cntrlCrv(name=cntrlName,obj=j2,connType='orientConstraint', **displaySetup)
        
        self.toeFkCntrl.getParent().setParent(self.ankleFkCntrl)
        self.ankleFkCntrl.getParent().setParent(self.moveall) 
        
        #node tree ikfk Blend
        self.moveall.addAttr ('ikfk',at='float', min=0, max=1,dv=1,k=1)
        ikfkRev=pm.createNode('reverse')
        ikfkVisCond1=pm.createNode('condition')
        ikfkVisCond2=pm.createNode('condition')
        
        #visibilidade ik fk
        self.moveall.ikfk >> ikfkRev.inputX
        self.moveall.ikfk >> ballIkh[0].ikBlend  
        self.moveall.ikfk >> tipIkh[0].ikBlend 
        self.moveall.ikfk >> ikfkVisCond1.firstTerm        
        ikfkVisCond1.secondTerm.set (0)
        ikfkVisCond1.operation.set (2)
        ikfkVisCond1.colorIfTrueR.set (1)
        ikfkVisCond1.colorIfFalseR.set (0)
        ikfkVisCond1.outColorR >> self.baseCntrl.getParent().visibility
        
        #blend dos constraints 
        self.moveall.ikfk >> ikfkVisCond2.firstTerm
        ikfkVisCond2.secondTerm.set (1)
        ikfkVisCond2.operation.set (4)
        ikfkVisCond2.colorIfTrueR.set (1)
        ikfkVisCond2.colorIfFalseR.set (0)
        ikfkVisCond2.outColorR >> self.ankleFkCntrl.getParent().visibility
        parCnstr = j1.connections (type='parentConstraint')[0] #descobre constraint
        weightAttr = parCnstr.target.connections(p=True, t='parentConstraint') #descobre parametros
        self.moveall.ikfk >> weightAttr[0]
        ikfkRev.outputX >> weightAttr[1]

            
        #IMPLEMENTAR guardar a posicao dos guides
                
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
        
        
        self.name=name
        self.flipAxis=flipAxis
        self.axis=axis
        self.guideMoveall=None
        
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        self.zeroJxtSulfix='Zero_jxt'
        grpSulfix='_grp'
        
        #dicionario q determina a aparencia dos controles
        self.spineDict={'name':name, 'axis':axis, 'flipAxis':flipAxis}
        self.spineDict['moveallSetup']={'nameTempl':self.name+'MoveAll', 'icone':'grp','size':1.8,'color':(1,1,0) }    
        self.spineDict['hipCntrlSetup'] = {'nameTempl':self.name+'COG', 'icone':'cog','size':5.5,'color':(0,0,1) }
        self.spineDict['spineFkCntrlSetup'] = {'nameTempl':self.name+'WaistFk', 'icone':'circuloPontaY','size':4,'color':(0,1,0) }      
        self.spineDict['startFkCntrlSetup'] = {'nameTempl':self.name+'HipFk', 'icone':'circuloPontaY','size':3.0,'color':(1,1,0)}
        self.spineDict['midFkOffsetCntrlSetup'] = {'nameTempl':self.name+'AbdomenFkOff', 'icone':'circuloY', 'size':2.5, 'color':(1,1,0) }
        self.spineDict['midFkCntrlSetup'] = {'nameTempl':self.name+'AbdomenFk', 'icone':'circuloPontaY', 'size':4, 'color':(0,1,0) }
        self.spineDict['endFkCntrlSetup'] = {'nameTempl':self.name+'ChestFk', 'icone':'circuloPontaY', 'size':4, 'color':(0,1,0) }
        self.spineDict['startIkCntrlSetup'] = {'nameTempl':self.name+'HipIk', 'icone':'circuloPontaY', 'size':4, 'color':(1,0,0)}
        self.spineDict['midIkCntrlSetup'] = {'nameTempl':self.name+'AbdomenIk', 'icone':'circuloY', 'size':4, 'color':(1,1,0)}
        self.spineDict['endIkCntrlSetup'] = {'nameTempl':self.name+'ChestIk', 'icone':'circuloPontaY', 'size':4, 'color':(1,0,0)}      

        self.spineDict['moveallGuideSetup']={'nameTempl':self.name+'Moveall','size':1.8,'color':(1,1,0) }    
        self.spineDict['startGuideSetup'] = {'nameTempl':self.name+'Hip', 'size':1,'color':(0,1,0)}
        self.spineDict['midGuideSetup'] = {'nameTempl':self.name+'Abdomen',  'size':1, 'color':(0,1,0) }
        self.spineDict['endGuideSetup'] = {'nameTempl':self.name+'Chest',  'size':1, 'color':(0,1,0) }
        self.spineDict['startTipGuideSetup'] = {'nameTempl':self.name+'HipTip', 'size':1,'color':(0,1,0)}
        self.spineDict['endTipGuideSetup'] = {'nameTempl':self.name+'ChestTip',  'size':1, 'color':(0,1,0) }

        self.spineDict['startJntSetup'] = {'nameTempl':self.name+'Hip', 'icone':'Bone', 'size':2}
        self.spineDict['endJntSetup'] = {'nameTempl':self.name+'Chest', 'icone':'Bone', 'size':2}      
        
        self.spineDict['guideDict'] = {}
        self.spineGuideDict = {'moveall':[0,0,0],'start':[0,0,0],'mid':[0,4,0],'end':[0,8,0], 'startTip':[0,-1,0],'endTip':[0,10,0]}
        self.spineDict.update(kwargs) 
        self.spineGuideDict.update(self.spineDict['guideDict']) 
        self.spineDict['guideDict']=self.spineGuideDict.copy()

    def doGuide(self, **kwargs):
        self.spineGuideDict = self.spineDict['guideDict'].copy()
        self.spineGuideDict.update(kwargs)

        #se existir apaga
        guideName=self.spineDict['moveallGuideSetup']['nameTempl']+self.guideSulfix
        if pm.objExists (guideName):
            pm.delete (guideName)
        self.guideMoveall=pm.group (n=guideName, em=True)

        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')
                    
        guideName=self.spineDict['startGuideSetup']['nameTempl']+self.guideSulfix
        self.startGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        self.startGuide.translate.set(self.spineGuideDict['start'])
        self.startGuide.displayHandle.set(1)
        
        guideName=self.spineDict['midGuideSetup']['nameTempl']+self.guideSulfix               
        self.midGuide = pm.spaceLocator (n=guideName,p=(0,0,0))
        self.midGuide.translate.set(self.spineGuideDict['mid'])
        self.midGuide.displayHandle.set(1)

        guideName=self.spineDict['endGuideSetup']['nameTempl']+self.guideSulfix               
        self.endGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        self.endGuide.translate.set(self.spineGuideDict['end'])
        self.endGuide.displayHandle.set(1)
        midGuideGrp=pm.group (em=True)
        pm.pointConstraint (self.startGuide, self.endGuide, midGuideGrp, mo=False)
        self.midGuide.setParent(midGuideGrp)

        guideName=self.spineDict['endTipGuideSetup']['nameTempl']+self.guideSulfix               
        self.endTipGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        self.endTipGuide.translate.set(self.spineGuideDict['endTip'])
        self.endTipGuide.displayHandle.set(1)        
        self.endTipGuide.localScale.set(.5,.5,.5) 
        self.endTipGuide.setParent(self.endGuide)
        
        guideName=self.spineDict['startTipGuideSetup']['nameTempl']+self.guideSulfix               
        self.startTipGuide = pm.spaceLocator (n=guideName, p=(0,0,0))
        self.startTipGuide.translate.set(self.spineGuideDict['startTip'])
        self.startTipGuide.displayHandle.set(1)        
        self.startTipGuide.localScale.set(.5,.5,.5) 
        self.startTipGuide.setParent(self.startGuide)

        pm.parent (self.startGuide,midGuideGrp,self.endGuide, self.guideMoveall)
        self.guideMoveall.translate.set (self.spineGuideDict['moveall'])

    def getGuideFromScene(self):        
        guideName=self.spineDict['moveallGuideSetup']['nameTempl']+self.guideSulfix
        self.guideMoveall=pm.PyNode(guideName)
        
        guideName=self.spineDict['startGuideSetup']['nameTempl']+self.guideSulfix
        self.startGuide = pm.PyNode(guideName)
        
        guideName=self.spineDict['midGuideSetup']['nameTempl']+self.guideSulfix               
        self.midGuide = pm.PyNode(guideName)

        guideName=self.spineDict['endGuideSetup']['nameTempl']+self.guideSulfix               
        self.endGuide = pm.PyNode(guideName)

        guideName=self.spineDict['endTipGuideSetup']['nameTempl']+self.guideSulfix               
        self.endTipGuide = pm.PyNode(guideName)
        
        guideName=self.spineDict['startTipGuideSetup']['nameTempl']+self.guideSulfix               
        self.startTipGuide = pm.PyNode(guideName)
                
    def doRig(self):
        #se nao tiver guide, faz
        if not self.guideMoveall:
            self.doGuide()
        #se ja existir rig, apaga  
        cntrlName = self.spineDict['moveallSetup']['nameTempl']
        if pm.objExists (cntrlName):
            pm.delete (cntrlName)

        #cria o moveall da espinha
        self.moveall=pm.group(n=cntrlName, em=True)
        pos =pm.xform (self.guideMoveall, q=True, ws=True, t=True)
        pm.xform (self.moveall, ws=True, t=pos)
        if not pm.objExists('MOVEALL'):
            pm.group ( self.moveall, n='MOVEALL' )
        else:
            pm.parent (self.moveall, 'MOVEALL')            
        spineRibbon=None
        
        #cria controles fk com nomes e setagem de display vindas do spineDict
        displaySetup= self.spineDict['hipCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        self.cogCntrl = cntrlCrv(name=cntrlName , obj=self.startGuide,**displaySetup) 

        displaySetup= self.spineDict['spineFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl'] 
        self.spineFkCntrl = cntrlCrv(name=cntrlName , obj=self.startGuide,**displaySetup) 
        self.spineFkCntrl.getParent().setParent(self.cogCntrl)
        
        displaySetup= self.spineDict['startFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        self.startFkCntrl = cntrlCrv(name=cntrlName, obj=self.startGuide,**displaySetup)
        self.startFkCntrl.getParent().setParent(self.cogCntrl)
        
        displaySetup= self.spineDict['midFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        self.midFkCntrl = cntrlCrv(name=cntrlName, obj=self.midGuide,**displaySetup)
        
        displaySetup= self.spineDict['midFkOffsetCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        self.midFkOffsetCntrl = cntrlCrv(name=cntrlName, obj=self.midGuide,**displaySetup) #esse controle faz o offset do ribbon e permanece orientado corretamente
        self.midFkOffsetCntrl.getParent().setParent(self.midFkCntrl)
        self.midFkCntrl.getParent().setParent(self.spineFkCntrl)
        
        displaySetup= self.spineDict['endFkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        self.endFkCntrl = cntrlCrv(name=cntrlName, obj=self.endGuide,**displaySetup)
        self.endFkCntrl.getParent().setParent(self.midFkCntrl)
        
        #cria controles ik com nomes e setagem de display vindas do spineDict
        displaySetup= self.spineDict['startIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.startIkCntrl = cntrlCrv(name=cntrlName, obj=self.startGuide,**displaySetup)
        self.startIkCntrl.getParent().setParent(self.cogCntrl)
        
        displaySetup= self.spineDict['midIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.midIkCntrl = cntrlCrv(name=cntrlName, obj=self.midGuide,**displaySetup)

        displaySetup= self.spineDict['endIkCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']
        self.endIkCntrl = cntrlCrv(name=cntrlName, obj=self.endGuide,**displaySetup)
        self.endIkCntrl.getParent().setParent(self.cogCntrl)    
            
        #Cria os joints orientados em X down
        start=pm.xform(self.startGuide,q=True,t=True,ws=True)
        startTip=pm.xform(self.startTipGuide,q=True,t=True,ws=True)
        pm.select(cl=True)
        jntName=self.spineDict['startJntSetup']['nameTempl']+self.zeroJxtSulfix
        self.startZeroJnt=pm.joint(p=(0,0,0), n=jntName)
        pm.select(cl=True)
        jntName=self.spineDict['startJntSetup']['nameTempl']+self.jntSulfix
        self.startJnt=pm.joint(p=(0,0,0), n=jntName)
        pm.select(cl=True)
        jntName=self.spineDict['startJntSetup']['nameTempl']+self.tipJxtSulfix
        self.startTipJnt=pm.joint(p=(0,0,0), n=jntName)
     
        A=om.MVector(start)
        B=om.MVector(startTip)
        Z=om.MVector(0,0,1)
        AB=B-A
        
        dot = Z.normal()*AB.normal() #se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        # vai acontecer qnd usarem a guide horizontal
        if abs(dot)>.95:
            Z=om.MVector(0,1,0)
        n=AB^Z

        m= orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)

        pm.xform (self.startZeroJnt, m = m, ws=True) 
        pm.xform (self.startJnt, m = m, ws=True) 
        pm.xform (self.startTipJnt, m = m, ws=True) 
        pm.xform (self.startTipJnt, t= B, ws=True) 
        pm.parent (self.startJnt,self.startZeroJnt)
        pm.parent (self.startTipJnt, self.startJnt)
        
        end=pm.xform(self.endGuide,q=True,t=True,ws=True)
        endTip=pm.xform(self.endTipGuide,q=True,t=True,ws=True)
        pm.select(cl=True)
        jntName=self.spineDict['endJntSetup']['nameTempl']+self.zeroJxtSulfix
        self.endZeroJnt=pm.joint(p=(0,0,0), n=jntName)
        pm.select(cl=True)
        jntName=self.spineDict['endJntSetup']['nameTempl']+self.jntSulfix
        self.endJnt=pm.joint(p=(0,0,0), n=jntName)
        pm.select(cl=True)
        jntName=self.spineDict['endJntSetup']['nameTempl']+self.tipJxtSulfix
        self.endTipJnt=pm.joint(p=(0,0,0), n=jntName)

        A=om.MVector(end)
        B=om.MVector(endTip)
        Z=om.MVector(0,0,1)
        AB=B-A
        
        dot = Z.normal()*AB.normal() #se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot)>.95:
            Z=om.MVector(0,1,0)            
        n=AB^Z
        m= orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
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
 
        spineRibbon = RibbonBezierSimple(name=self.name+'Ribbon_',size=AB.length(), offsetStart=0.05, offsetEnd=0.05)
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
        pm.pointConstraint (self.startIkCntrl, self.endIkCntrl, self.midIkCntrl.getParent(), mo=True)
        pm.orientConstraint (aimTwist.mid, self.midIkCntrl, mo=True)
        self.midIkCntrl.rotate.lock()
        self.midIkCntrl.rotate.setKeyable(0)
        pm.orientConstraint (aimTwist.mid, self.midFkOffsetCntrl, mo=True)
        self.midFkOffsetCntrl.rotate.lock()
        self.midFkOffsetCntrl.rotate.setKeyable(0)
        
        #faz os constraints do ribbon nos controles ik e fk pra fazer blend
        cns1=pm.parentConstraint (self.startFkCntrl, self.startIkCntrl, spineRibbon.startCntrl, mo=True)
        mid=pm.xform(self.midGuide,q=True,t=True,ws=True)
        pm.xform (spineRibbon.midCntrl.getParent(), t=mid, ws=True)
        cns2=pm.parentConstraint (self.midFkOffsetCntrl, self.midIkCntrl, spineRibbon.midCntrl, mo=True)
        cns3=pm.parentConstraint (self.endFkCntrl, self.endIkCntrl, spineRibbon.endCntrl, mo=True)
        
        #parenteia os joints das pontas nos controles do ribbon
        self.startZeroJnt.setParent (spineRibbon.startCntrl.getParent())
        self.endZeroJnt.setParent (spineRibbon.endCntrl.getParent())
        #e cria os constraints point no start joint zero e orient no start joint
        #o joint zero eh necessario para o twist extractor
        pm.pointConstraint (spineRibbon.startCntrl, self.startZeroJnt, mo=True)
        pm.orientConstraint (spineRibbon.startCntrl, self.startJnt, mo=True)
        pm.pointConstraint (spineRibbon.endCntrl, self.endZeroJnt, mo=True)
        pm.orientConstraint (spineRibbon.endCntrl, self.endJnt, mo=True)
        
        
        #e parenteia todo mundo
        pm.parent (twistExtractor1.extractorGrp, twistExtractor2.extractorGrp, spineRibbon.moveall, self.cogCntrl)
        pm.parent (self.midIkCntrl.getParent(),self.cogCntrl.getParent(), self.moveall)


        #conecta os twist extractors nos twists do ribbon
        twistExtractor1.extractor.extractTwist >> spineRibbon.startCntrl.twist
        twistExtractor2.extractor.extractTwist >> spineRibbon.endCntrl.twist
        
        #cria o node tree do blend ikfk
        self.moveall.addAttr ('ikfk', at='float', max=1, min=0, dv=1, k=1)
        ikfkRev = pm.createNode('reverse')
        ikfkCond1 = pm.createNode('condition')
        ikfkCond2 = pm.createNode('condition')
        self.moveall.ikfk >> ikfkCond1.firstTerm
        self.moveall.ikfk >> ikfkCond2.firstTerm
        self.moveall.ikfk >> ikfkRev.inputX
        
        #visibilidade ik fk        
        ikfkCond1.secondTerm.set (0)
        ikfkCond1.operation.set (2)
        ikfkCond1.colorIfTrueR.set (1)
        ikfkCond1.colorIfFalseR.set (0)
        ikfkCond1.outColorR >> self.startIkCntrl.getParent().visibility
        ikfkCond1.outColorR >> self.midIkCntrl.getParent().visibility
        ikfkCond1.outColorR >> self.endIkCntrl.getParent().visibility        
        ikfkCond2.secondTerm.set (1)
        ikfkCond2.operation.set (4)
        ikfkCond2.colorIfTrueR.set (1)
        ikfkCond2.colorIfFalseR.set (0)
        ikfkCond2.outColorR >> self.startFkCntrl.getParent().visibility
        ikfkCond2.outColorR >> self.spineFkCntrl.getParent().visibility
        
        #blend dos constraints         
        weightAttr = cns1.target.connections(p=True, t='parentConstraint') #descobre parametros
        self.moveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns2.target.connections(p=True, t='parentConstraint') #descobre parametros
        self.moveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        weightAttr = cns3.target.connections(p=True, t='parentConstraint') #descobre parametros
        self.moveall.ikfk >> weightAttr[1]
        ikfkRev.outputX >> weightAttr[0]
        
        #IMPLEMENTAR guardar a posicao dos guides
        
class Chain:
    """
        Cria uma cadeia de joints com controles fk
        Parametros: 
            name (string): nome do novo limb            
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
            divNum (int): numero de joints da cadeia
                             
    """  
    ## IMPLEMENTAR:
    #  nomes dos joints
    #  talvez conexoes diretas dos controles?
    #  algum tipo de controle ik para a cadeia
        
    def __init__(self, name='chain', flipAxis=False, divNum=2, axis='X', **kwargs):
        self.axis=axis
        self.flipAxis=flipAxis
        self.name=name 
        self.divNum=divNum
        
        self.guideList=[]
        self.guideMoveall=None
        
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        self.zeroJxtSulfix='Zero_jxt'
        grpSulfix='_grp'
        
        self.chainGuideDict={'moveall':[0,0,0]}
        for i in range (self.divNum):
            self.chainGuideDict['guide'+str(i+1)]=[0+i,0,0]
        #parametros de aparencia dos controles
        self.chainDict={'name':name, 'axis':axis, 'flipAxis':flipAxis}
        self.chainDict['moveAllCntrlSetup']={'nameTempl':self.name+'Moveall', 'icone':'circuloX','size':1.8,'color':(1,1,0) }    
        self.chainDict['fkCntrlSetup'] = {'nameTempl':self.name+'ChainFk', 'icone':'cubo','size':.8,'color':(0,1,0) }    
        self.chainDict['guideSetup'] = {'nameTempl':self.name+'Chain', 'size':.8,'color':(0,1,0) }    
        self.chainDict['jntSetup'] = {'nameTempl':self.name+'Chain', 'icone':'Bone','size':.8 }    

        self.chainDict['guideDict'] = {}
        self.chainDict.update(kwargs) 
        self.chainGuideDict.update(self.chainDict['guideDict']) 
        self.chainDict['guideDict']=self.chainGuideDict.copy()
        
    def doGuide(self, **kwargs):
        self.chainGuideDict = self.chainDict['guideDict'].copy()
        self.chainGuideDict.update(kwargs)
        
        #apaga se existir
        cntrlName=self.chainDict['moveAllCntrlSetup']['nameTempl']+self.guideSulfix
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
        self.guideMoveall=pm.group(n=cntrlName, em=True)

        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')

        self.guideList=[]
        for i in range(len(self.chainGuideDict.keys())-1):
            guideName= self.chainDict['guideSetup']['nameTempl']+str(i)+self.guideSulfix
            guide= pm.spaceLocator (n=guideName,p=(0,0,0))
            self.guideList.append (guide)
            guidePos = self.chainGuideDict['guide'+str(i+1)]
            pm.xform(guide, t=guidePos, ws=True)
            pm.parent(guide, self.guideMoveall)
        self.guideMoveall.translate.set (self.chainGuideDict['moveall'])

    def getGuideFromScene(self):
        cntrlName=self.chainDict['moveAllCntrlSetup']['nameTempl']+self.guideSulfix
        self.guideMoveall=pm.PyNode(cntrlName)

        self.guideList=[]
        for i in range(len(self.chainGuideDict.keys())-1):
            guideName= self.chainDict['guideSetup']['nameTempl']+str(i)+self.guideSulfix
            guide= pm.PyNode(guideName)
            self.guideList.append (guide)

    def mirrorConnectGuide(self,chain):
        if not self.guideMoveall:
            self.doGuide()        
        if not chain.guideMoveall:
            chain.doGuide()
            
        self.mirrorGuide= pm.group (em=True, n=self.name+'MirrorGuide_grp') 
        if not pm.objExists('GUIDES'):
            pm.group ( self.name+'MirrorGuide_grp', n='GUIDES' )
        else:
            pm.parent ( self.name+'MirrorGuide_grp', 'GUIDES')
                   
        self.guideMoveall.setParent (self.mirrorGuide)
        self.mirrorGuide.scaleX.set (-1)
        self.mirrorGuide.template.set (1)

        chain.guideMoveall.translate >>  self.guideMoveall.translate
        chain.guideMoveall.rotate >>  self.guideMoveall.rotate
        chain.guideMoveall.scale >>  self.guideMoveall.scale
        
        for origin,mirror in zip (chain.guideList, self.guideList):
            origin.translate >>  mirror.translate
            origin.rotate >>  mirror.rotate
            origin.scale >>  mirror.scale
        
        if chain.flipAxis:
            self.flipAxis=False
        else:
            self.flipAxis=True            
                               
    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.guideMoveall:
            self.doGuide()
            
        #apagar se ja houver um grupo moveall
        cntrlName=self.chainDict['moveAllCntrlSetup']['nameTempl']                     
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
        self.moveall = pm.group(empty=True, n=cntrlName)
        pos =pm.xform (self.guideMoveall, q=True, ws=True, t=True)
        pm.xform (self.moveall, ws=True, t=pos)
        if not pm.objExists('MOVEALL'):
            pm.group ( self.moveall, n='MOVEALL' )
        else:
            pm.parent (self.moveall, 'MOVEALL') 
        
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
            if abs(dot) < 0.95:
                normal=AB[i]^Z
            else:
                normal=AB[i]^X
            # descobre a matriz de transformacao orientada e desenha os joints     
            m=orientMatrix(AB[i], normal, A[i], self.axis)
            pm.select(cl=True)
            jntName=self.chainDict['jntSetup']['nameTempl']+str(i)+self.jntSulfix        
            jnt = pm.joint(n=jntName)
            self.jntList.append(jnt)
            pm.xform (jnt, m = m, ws=True) 
            pm.makeIdentity (jnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
            if last:
                pm.parent (jnt, last)
            last=jnt
        
        # desenha o ultimo joint (ou o unico)
        pm.select(cl=True)
        if self.divNum==1:
            jntName=self.chainDict['jntSetup']['nameTempl']+self.jntSulfix  
        else:
            jntName=self.chainDict['jntSetup']['nameTempl']+self.tipJxtSulfix      
        jnt = pm.joint(n=jntName)
        self.jntList.append(jnt)
        pm.xform (jnt, m = m, ws=True)
        pm.xform (jnt, t=A[-1], ws=True) 
        pm.makeIdentity (jnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        pm.parent (jnt, last)
        
        pm.parent (self.jntList[0], self.moveall)
        
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
            
        pm.parent (self.cntrlList[0].getParent(), self.moveall)
        
        #IMPLEMENTAR: guardar as posicoes dos locators
               
class Neck:
    """
        Cria um pescoco com um joint de distribuicao de twist
        Parametros: 
            name (string): nome do novo limb            
            flipAxis (boolean): se o eixo eh flipado ao longo do bone
            axis (string:'X','Y' ou 'Z'): eixo ao longo do bone
                             
    """  
        
    def __init__(self, name='neck', flipAxis=False, axis='X', **kwargs):
        self.axis=axis
        self.flipAxis=flipAxis
        self.name=name
        self.guideMoveall=None
        
        self.guideSulfix='_guide'
        self.jntSulfix='_jnt'
        self.jxtSulfix='_jxt'
        self.tipJxtSulfix='Tip_jxt'
        self.zeroJxtSulfix='Zero_jxt'
        grpSulfix='_grp'
        
       #parametros de aparencia dos controles
        self.neckDict={'name':name, 'axis':axis, 'flipAxis':flipAxis}
        self.neckDict['moveAllCntrlSetup'] = {'nameTempl':name+'Moveall', 'icone':'circuloX','size':1,'color':(0,1,0) }
        self.neckDict['startCntrlSetup'] = {'nameTempl':'Neck', 'icone':'circuloY','size':3,'color':(0,1,0) }
        self.neckDict['endCntrlSetup'] = {'nameTempl':'Head', 'icone':'circuloZ', 'size':2, 'color':(0,1,0)}

        self.neckDict['moveAllGuideSetup'] = {'nameTempl':name+'Moveall'}
        self.neckDict['startGuideSetup'] = {'nameTempl':'neck', 'size':1,'color':(0,1,0) }
        self.neckDict['endGuideSetup'] = {'nameTempl':'head', 'size':1, 'color':(0,1,0)}

        self.neckDict['startGuideSetup'] = {'nameTempl':'neck', 'size':1,'color':(0,1,0) }
        self.neckDict['midGuideSetup'] = {'nameTempl':'midNeck', 'size':1, 'color':(0,1,0)}
        self.neckDict['endGuideSetup'] = {'nameTempl':'head', 'size':1, 'color':(0,1,0)}

        self.neckDict['guideDict'] = {}
        self.neckDict.update(kwargs) 
        self.neckGuideDict ={'moveall':[0,0,0],'start':[0,0,0], 'end':[0,2,0]}
        self.neckGuideDict.update(self.neckDict['guideDict']) 
        self.neckDict['guideDict']=self.neckGuideDict.copy()


    def doGuide(self, **kwargs):
        self.neckGuideDict = self.neckDict['guideDict'].copy()
        self.neckGuideDict.update(kwargs)
        
        #apaga se existir
        cntrlName=self.neckDict['moveAllGuideSetup']['nameTempl']+self.guideSulfix
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
        self.guideMoveall=pm.group(n=cntrlName, em=True)

        if not pm.objExists('GUIDES'):
            pm.group ( self.guideMoveall, n='GUIDES' )
        else:
            pm.parent ( self.guideMoveall, 'GUIDES')

        cntrlName=self.neckDict['startGuideSetup']['nameTempl']+self.guideSulfix
        self.startGuide=pm.spaceLocator (p=(0,0,0), n=cntrlName)
        pm.xform (self.startGuide, t=self.neckGuideDict['start'], ws=True)
        
        cntrlName=self.neckDict['endGuideSetup']['nameTempl']+self.guideSulfix
        self.endGuide=pm.spaceLocator (p=(0,0,0),n=cntrlName)
        pm.xform (self.endGuide, t=self.neckGuideDict['end'], ws=True)
        pm.parent (self.startGuide,self.endGuide,self.guideMoveall)
        
        self.guideMoveall.translate.set(self.neckGuideDict['moveall'])

    def getGuideFromScene(self):
        cntrlName=self.neckDict['moveAllGuideSetup']['nameTempl']+self.guideSulfix
        self.guideMoveall=pm.PyNode(cntrlName)

        cntrlName=self.neckDict['startGuideSetup']['nameTempl']+self.guideSulfix
        self.startGuide=pm.PyNode(cntrlName)
        
        cntrlName=self.neckDict['endGuideSetup']['nameTempl']+self.guideSulfix
        self.endGuide=pm.PyNode(cntrlName)    
                       
    def doRig(self):
        # se nao tiver guide faz um padrao
        if not self.guideMoveall:
            self.doGuide()
            
        #apagar se ja houver um grupo moveall
        cntrlName=self.neckDict['moveAllCntrlSetup']['nameTempl']                     
        if pm.objExists(cntrlName):
            pm.delete (cntrlName)
        self.moveall = pm.group(empty=True, n=cntrlName)
        pos =pm.xform (self.guideMoveall, q=True, ws=True, t=True)
        pm.xform (self.moveall, ws=True, t=pos)
        if not pm.objExists('MOVEALL'):
            pm.group ( self.moveall, n='MOVEALL' )
        else:
            pm.parent (self.moveall, 'MOVEALL')
            
        #doRig
        start =pm.xform (self.startGuide, q=True, t=True,ws=True)
        end =pm.xform (self.endGuide, q=True, t=True,ws=True)
        
        A=om.MVector(start)
        B=om.MVector(end)
        Z=om.MVector(0,0,-1) 
        AB=B-A  
        dot = Z.normal()*AB.normal() #se o eixo Z, usado como secundario, for quase paralelo ao vetor do Bone, troca pra eixo Y como secundario
        if abs(dot)>.95:
            Z=om.MVector(0,-1,0)
        
        n=AB^Z
        m= orientMatrix(mvector=AB, normal=n, pos=A, axis=self.axis)
        pm.select (cl=True)
        
        jntName= self.neckDict['startGuideSetup']['nameTempl']+self.jntSulfix
        self.startJnt = pm.joint(n=jntName)
        pm.xform (self.startJnt, m = m, ws=True) 
        pm.makeIdentity (self.startJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)

        jntName= self.neckDict['endGuideSetup']['nameTempl']+self.jntSulfix        
        self.endJnt = pm.joint(n=jntName)
        pm.xform (self.endJnt, m = m, ws=True) 
        pm.xform (self.endJnt, t=B ,ws=True)
        pm.makeIdentity (self.endJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        pm.select (cl=True)

        jntName= self.neckDict['midGuideSetup']['nameTempl']+self.jntSulfix        
        self.midJnt = pm.joint(n=jntName)
        pm.xform (self.midJnt, m = m, ws=True) 
        pm.xform (self.midJnt, t=(0,0,0) ,ws=True)
        pm.makeIdentity (self.midJnt, apply=True, r=1, t=0, s=1, n=0, pn=0)
        
        aimTwist = AimTwistDivider()
        aimTwist.start.setParent (self.startJnt,r=True)
        aimTwist.end.setParent (self.endJnt,r=True)
        aimTwist.mid.setParent (self.moveall)
        self.midJnt.setParent(aimTwist.mid)
        self.midJnt.translate.set(0,0,0)
        self.midJnt.rotate.set(0,0,0)
        
        displaySetup= self.neckDict['startCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']        
        self.startCntrl = cntrlCrv(name=cntrlName, obj=self.startGuide, **displaySetup)
        pm.parentConstraint(self.startCntrl, self.startJnt,mo=True)      
        displaySetup= self.neckDict['endCntrlSetup'].copy()
        cntrlName = displaySetup['nameTempl']                
        self.endCntrl = cntrlCrv(name=cntrlName, obj=self.endGuide,**displaySetup)
        pm.parentConstraint(self.endCntrl, self.endJnt,mo=True)
        self.endCntrl.getParent().setParent(self.startCntrl)
        pm.parent (self.startJnt,self.startCntrl.getParent(),self.moveall)

        #IMPLEMENTAR: guardar as posicoes dos guides ao final
        