class MouthCorners:
    def __init__(self, name='mouthCorners', bsDict=None, mesh=None, tgtMesh=None):
        self.name=name
        self.mesh=mesh
        self.tgtMesh=tgtMesh
        self.mouthCornersGuideDict={'moveall':[0,0,0],'lcorner':[.5, 0 ,0],'rcorner':[-.5, 0,0]}
        if bsDict:
            self.bsDict=bsDict
        else:
            self.bsDict = {  'L_up':None            ,'R_up':None, 
                             'L_down':None          ,'R_down':None,
                             'L_narrow':None        ,'R_narrow':None,    
                             'L_wide':None          ,'R_wide':None,    
                             'L_wide_up':None       ,'R_wide_up':None  , 
                             'L_wide_down':None     ,'R_wide_down':None , 
                             'L_narrow_up':None     ,'R_narrow_up':None  , 
                             'L_narrow_down':None   ,'R_narrow_down':None } 
  
    def doGuide(self): 
        if pm.objExists(self.name+'Moveall_guide'):
            pm.delete (self.name+'Moveall_guide')
        self.guideMoveall=pm.group (em=True, n=self.name+'Moveall_guide')
        self.lcornerGuide=pm.spaceLocator(n=self.name+'LCorner_guide')
        self.lcornerGuide.translate.set (self.mouthCornersGuideDict['lcorner'])
        self.lcornerGuide.localScale.set(0.1,0.1,0.1)
        self.rcornerGuide=pm.spaceLocator(n=self.name+'RCorner_guide')
        self.rcornerGuide.translate.set (self.mouthCornersGuideDict['rcorner'])
        self.rcornerGuide.localScale.set(0.1,0.1,0.1)
        pm.parent (self.lcornerGuide, self.rcornerGuide, self.guideMoveall)

    def getGuideFromScene(self): 
        self.guideMoveall=pm.PyNode (self.name+'Moveall_guide')
        self.lcornerGuide=pm.PyNode (self.name+'LCorner_guide')
        self.rcornerGuide=pm.PyNode (self.name+'RCorner_guide')
                    
    def doRig(self, bsDict=None):        
        if not self.guideMoveall:
            self.doGuide()
        
        if pm.objExists(self.name+'Moveall'):
            pm.delete (self.name+'Moveall')
        self.moveall=pm.group (em=True, n=self.name+'Moveall')
        
        if bsDict:
            self.bsDict=bsDict
        
        self.lcornerCntrl = cntrlCrv (name='LCorner',obj=self.lcornerGuide, icone='circuloZ', size=.5)
        self.lcornerCntrl.getParent().scaleX.set(-1)
        self.rcornerCntrl = cntrlCrv (name='RCorner',obj=self.rcornerGuide, icone='circuloZ', size=.5)
        
        pm.parent (self.lcornerCntrl.getParent(), self.rcornerCntrl.getParent(), self.moveall)
        tmp = pm.ls (pm.listHistory( self.mesh, future = False ), type = 'blendShape')
        if tmp:
            bsNode=tmp[0]
        else:
            print 'Nao encontrou blendShape node'            
                               
        self.connectToPainel(self.lcornerCntrl,bsNode,'translateX', self.bsDict['L_narrow'], .3, self.bsDict['L_wide'], -.3)
        self.connectToPainel(self.lcornerCntrl,bsNode,'translateY', self.bsDict['L_up'], .3, self.bsDict['L_down'], -.3)
        self.connectToPainel(self.rcornerCntrl,bsNode,'translateX', self.bsDict['R_narrow'], .3, self.bsDict['R_wide'], -.3)
        self.connectToPainel(self.rcornerCntrl,bsNode,'translateY', self.bsDict['R_up'], .3, self.bsDict['R_down'], -.3)

        for prefix in ['L_','R_']:
            for shpA in ['up', 'down']:
                for shpB in ['wide', 'narrow']:               
                    multi1 = pm.createNode('multDoubleLinear')
                    bsNode.attr(bsDict[prefix+shpA]) >> multi1.input1
                    bsNode.attr(bsDict[prefix+shpB]) >> multi1.input2
                    multi1.output >>  bsNode.attr(self.bsDict[prefix+shpA+'_'+shpB])

    def selToBsDict(self):
        ## funcao para povoar o dicionario com os nomes dos shapes
        ## a selecao deve ser feita na mesma ordem que aparece abaixo
        sel=pm.ls (sl=True)
        if len(sel)==16:
            self.bsDict = {  'L_up':sel[0].name()            ,'R_up':sel[1].name(), 
                             'L_down':sel[2].name()          ,'R_down':sel[3].name(),
                             'L_narrow':sel[4].name()        ,'R_narrow':sel[5].name(),    
                             'L_wide':sel[6].name()          ,'R_wide':sel[7].name(),    
                             'L_up_wide':sel[8].name()      ,'R_up_wide':sel[9].name(), 
                             'L_down_wide':sel[10].name()    ,'R_down_wide':sel[11].name(), 
                             'L_up_narrow':sel[12].name()    ,'R_up_narrow':sel[13].name(), 
                             'L_down_narrow':sel[14].name()  ,'R_down_narrow':sel[15].name() } 
        print self.bsDict
         
    def invertBSBaseWeights(self, obj, bs):   
        #inverte o mapa de influencia de um blendShape.
        #usado pra tirar o blend esquedo e direito
        allWeights = pm.polyEvaluate (obj, v=True)
        for i in range (allWeights):
            x = pm.getAttr (bs+'.inputTarget[0].baseWeights['+str (i)+']')
            pm.setAttr  (bs+'.inputTarget[0].baseWeights['+str (i)+ ']', (1-x))

    def splitShapes (self) : 
        #duplica um objeto q tenha todos os blends aplicados
        #e um mapa de influencia pintado na metade
        #criando versoes para esqueda e direita
        ##IMPLEMENTAR: mapa automatico
        obj=self.tgtMesh
        
        tmp = pm.ls (pm.listHistory( obj, future = False ), type = 'blendShape')
        if tmp:
            bs=tmp[0]
        print bs
        numOfShapes = pm.blendShape( bs, query = True, weightCount = True )
        [ pm.setAttr(bs+'.weight[%d]' % ( i ), 0 ) for i in range( numOfShapes ) ]
        
        for shp in range (numOfShapes):
            pm.setAttr(bs+'.weight[%d]' %  shp, 1)
            name = pm.aliasAttr( '%s.weight[%d]' % ( bs, shp ), query = True )
            
            pm.duplicate (obj, n='R_'+name)
            self.invertBSBaseWeights(obj,bs)
            pm.duplicate (obj, n='L_'+name)    
            self.invertBSBaseWeights(obj,bs)
            pm.setAttr(bs+'.weight[%d]' %  shp, 0)

    def connectToPainel(self,cntrl,bsNode, param, bsMax, vMax, bsMin='', vMin=None):    
        ##funcao que conecta o movimento dos controles aos blendShapes
        sR= pm.createNode ('setRange')
        c = pm.createNode ('clamp')
        sR.maxX.set(1)
        sR.minX.set(0)
        sR.oldMaxX.set(vMax)
        sR.oldMinX.set(0)
        c.maxR.set(1)
        cntrl.attr (param) >> sR.valueX
        sR.outValueX >> c.inputR 
        c.outputR >> bsNode.attr(bsMax)
        if bsMin:
            sR.maxY.set(0)
            sR.minY.set(1)
            sR.oldMaxY.set(0)
            sR.oldMinY.set(vMin)
            c.maxG.set(1)
            cntrl.attr(param) >> sR.valueY
            sR.outValueY >> c.inputG
            c.outputG >> bsNode.attr(bsMin)
            
m= MouthCorners(mesh='corpo1', tgtMesh='BSMesh')
# 
m.getGuideFromScene() 
#m.splitShapes()
#m.selToBsDict()
m.doRig({'L_up_narrow': u'L_Corner_Up___Nar', 'L_down_narrow': u'L_Corner_Down___N', 'L_up_wide': u'L_Corner_Up___Wid', 'R_down_wide': u'R_Corner_Down___W', 'R_up_narrow': u'R_Corner_Up___Nar', 'R_wide': u'R_Wide', 'R_down': u'R_Corner_Down', 'R_narrow': u'R_Narrow', 'R_up_wide': u'R_Corner_Up___Wid', 'R_down_narrow': u'R_Corner_Down___N', 'L_narrow': u'L_Narrow', 'L_down_wide': u'L_Corner_Down___W', 'L_up': u'L_Corner_Up', 'L_wide': u'L_Wide', 'L_down': u'L_Corner_Down', 'R_up': u'R_Corner_Up'})
     