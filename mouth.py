class MouthCorners:
    def __init__(self, name='mouthCorners'):
        self.name=name


def connectToPainel(cntrl,bsNode, param, bsMax, vMax, bsMin='', vMin=None):    
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

mouthCornersGuideDict={'moveall':[0,0,0],'lcorner':[.5, 0 ,0],'rcorner':[-.5, 0,0]}
 


guideMoveall=pm.group (em=True, n='Moveall_guide')
lcornerGuide=pm.spaceLocator(n='LCorner')
lcornerGuide.translate.set (mouthCornersGuideDict['lcorner'])
lcornerGuide.localScale.set(0.1,0.1,0.1)
rcornerGuide=pm.spaceLocator(n='RCorner')
rcornerGuide.translate.set (mouthCornersGuideDict['rcorner'])
rcornerGuide.localScale.set(0.1,0.1,0.1)
pm.parent (lcornerGuide, rcornerGuide, guideMoveall)

lcornerCntrl = cntrCrv (name='LCorner',obj=lcornerGuide)
lcornerCntrl = cntrCrv (name='LCorner',obj=rcornerGuide)

tmp = cmds.ls (cmds.listHistory( obj, future = False ), type = 'blendShape')
if tmp:
    bs=tmp[0]
            
bsNode = pm.PyNode('expressoes')
lcntrl = pm.PyNode('L_teste_cntrl')    
rcntrl = pm.PyNode('R_teste_cntrl') 

bsDict = {

bsNode.L_Narrow
connectToPainel(lcntrl,bsNode,'translateX', 'L_Narrow', 1, 'L_Wide', -1)
connectToPainel(lcntrl,bsNode,'translateY', 'L_Corner_Up', 1, 'L_Corner_Down', -1)
connectToPainel(rcntrl,bsNode,'translateX', 'R_Narrow', 1, 'R_Wide', -1)
connectToPainel(rcntrl,bsNode,'translateY', 'R_Corner_Up', 1, 'R_Corner_Down', -1)
      