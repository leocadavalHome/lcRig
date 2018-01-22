"""
larm=Limb(name='L_arm' )
larm.doGuide()
rarm=Limb(name='R_arm')
rarm.mirrorConnectGuide(larm)

lhand=Hand(name='L_hand', fingerNum=4)
lhand.doGuide()
rhand=Hand(name='R_hand', fingerNum=4)
rhand.mirrorConnectGuide(lhand)

lfoot=Foot(name='L_foot')
lfoot.doGuide()
rfoot=Foot(name='R_foot')
rfoot.mirrorConnectGuide(lfoot)

n=Neck(name='neck', guideDict={'moveall':[0,10,0]})
n.doGuide()

s=Spine(name='spine')
s.doGuide()

lclav=Chain(name='L_clavicle', divNum=2, fkCntrlSetup = {'nameTempl':'L_clavicleChainFk', 'icone':'ponteiroX','size':.8,'color':(0,1,0) })
lclav.doGuide()
rclav=Chain(name='R_clavicle', divNum=2, fkCntrlSetup = {'nameTempl':'R_clavicleChainFk', 'icone':'ponteiroMenosX','size':.8,'color':(0,1,0) })
rclav.mirrorConnectGuide(lclav)

lleg=Limb(name='L_leg' ,ikCntrlSetup = {'nameTempl':'L_footIk', 'icone':'grp','size':.8,'color':(1,1,0)} )
lleg.doGuide()
rleg=Limb(name='R_leg' , ikCntrlSetup = {'nameTempl':'R_footIk', 'icone':'grp','size':.8,'color':(1,1,0)})
rleg.mirrorConnectGuide(lleg)

llegShoulder=Chain(name='L_legShoulder')
llegShoulder.doGuide()
rlegShoulder=Chain(name='R_legShoulder')
rlegShoulder.mirrorConnectGuide(llegShoulder)

m=Moveall(name='homem')
m.doGuide()
"""

### 
## guide from scene
larm=Limb(name='L_arm' )
larm.getGuideFromScene()
rarm=Limb(name='R_arm', flipAxis=True)
rarm.getGuideFromScene()

lhand=Hand(name='L_hand', fingerNum=4)
lhand.getGuideFromScene()
rhand=Hand(name='R_hand', fingerNum=4)
rhand.getGuideFromScene()

lfoot=Foot(name='L_foot', )
lfoot.getGuideFromScene()
rfoot=Foot(name='R_foot',flipAxis=True)
rfoot.getGuideFromScene()

n=Neck(name='neck', guideDict={'moveall':[0,10,0]})
n.getGuideFromScene()

s=Spine(name='spine')
s.getGuideFromScene()

lclav=Chain(name='L_clavicle', divNum=2, fkCntrlSetup = {'nameTempl':'L_clavicleFk', 'icone':'circuloX','size':1.2,'color':(0,1,0) })
lclav.getGuideFromScene()
rclav=Chain(name='R_clavicle', divNum=2, fkCntrlSetup = {'nameTempl':'R_clavicleFk', 'icone':'circuloX','size':1.2,'color':(0,1,0) }, flipAxis=True)
rclav.getGuideFromScene()

lleg=Limb(name='L_leg',ikCntrlSetup = {'nameTempl':'L_footIk', 'icone':'grp','size':.8,'color':(1,1,0)}  )
lleg.getGuideFromScene()
rleg=Limb(name='R_leg', ikCntrlSetup = {'nameTempl':'R_footIk', 'icone':'grp','size':.8,'color':(1,1,0)}, flipAxis=True)
rleg.getGuideFromScene()

llegShoulder=Chain(name='L_legShoulder' , fkCntrlSetup = {'nameTempl':'L_legClaviculeFk', 'icone':'dropY','size':.4,'color':(0,1,0) })
llegShoulder.getGuideFromScene()
rlegShoulder=Chain(name='R_legShoulder' , fkCntrlSetup = {'nameTempl':'R_legClaviculeFk', 'icone':'dropMenosY','size':.4,'color':(0,1,0) }, flipAxis=True)
rlegShoulder.getGuideFromScene()

m=Moveall(name='menino')
m.getGuideFromScene()

##Rig
s.doRig()
lclav.doRig()
rclav.doRig()
rhand.doRig()
lhand.doRig()
larm.doRig()
rarm.doRig()
rfoot.doRig()
lfoot.doRig()
n.doRig()
lleg.doRig()
rleg.doRig()
llegShoulder.doRig()
rlegShoulder.doRig()
m.doRig()

larb= RibbonBezier(name='L_armBezier', size=larm.jointLength,numJnts=10, offsetStart=0.08, offsetEnd=0.1)
larb.doRig()
larb.connectToLimb(larm)
rarb= RibbonBezier(name='R_armBezier', size=rarm.jointLength,numJnts=10, offsetStart=0.1, offsetEnd=0.08)
rarb.doRig()
rarb.connectToLimb(rarm)

llrb= RibbonBezier(name='L_legBezier', size=lleg.jointLength, offsetStart=0.1, offsetEnd=0.1)
llrb.doRig()
llrb.connectToLimb(lleg)
rlrb= RibbonBezier(name='R_legBezier', size=lleg.jointLength ,offsetStart=0.1, offsetEnd=0.1)
rlrb.doRig()
rlrb.connectToLimb(rleg)

"""
pm.parentConstraint (s.endTipJnt, lclav.moveall, mo=True)
pm.parentConstraint (s.endTipJnt, rclav.moveall, mo=True)
pm.parentConstraint (s.endTipJnt, n.moveall, mo=True)
pm.parentConstraint (rclav.jntList[-1], rarm.moveall, mo=True)
pm.parentConstraint (lclav.jntList[-1], larm.moveall, mo=True)
pm.parentConstraint (larm.lastTipJnt, lhand.moveall, mo=True)
pm.parentConstraint (rarm.lastTipJnt, rhand.moveall, mo=True)
pm.parentConstraint (s.startTipJnt, llegShoulder.moveall, mo=True)
pm.parentConstraint (s.startTipJnt, rlegShoulder.moveall, mo=True)
pm.parentConstraint (rlegShoulder.jntList[-1], rleg.moveall, mo=True)
pm.parentConstraint (llegShoulder.jntList[-1], lleg.moveall, mo=True)
pm.parentConstraint (lfoot.limbConnectionCntrl, lleg.ikCntrl, mo=True)
pm.parentConstraint (rfoot.limbConnectionCntrl, rleg.ikCntrl, mo=True)
"""

pm.parent ( lclav.moveall, s.endTipJnt)
pm.parent ( rclav.moveall, s.endTipJnt)
pm.parent ( n.moveall, s.endTipJnt)
pm.parent ( rarm.moveall,rclav.jntList[-1])
pm.parent ( larm.moveall,lclav.jntList[-1])
pm.parent ( lhand.moveall, larm.lastTipJnt)
pm.parent ( rhand.moveall, rarm.lastTipJnt)
pm.parent ( llegShoulder.moveall, s.startTipJnt)
pm.parent ( rlegShoulder.moveall, s.startTipJnt)
pm.parent ( rleg.moveall, rlegShoulder.jntList[-1])
pm.parent ( lleg.moveall, llegShoulder.jntList[-1])
pm.parent ( lleg.ikCntrl.getParent(), lfoot.limbConnectionCntrl)
pm.parent ( rleg.ikCntrl.getParent(), rfoot.limbConnectionCntrl)

pm.parentConstraint ( lleg.startCntrl, lfoot.ankleFkCntrl, mo=True)
pm.parentConstraint ( rleg.startCntrl, rfoot.ankleFkCntrl, mo=True)

s.hipCntrl.addAttr ('L_Arm_IkFk', at='float', dv=1, max=1, min=0, k=1)
s.hipCntrl.addAttr ('R_Arm_IkFk', at='float', dv=1, max=1, min=0, k=1)
s.hipCntrl.addAttr ('L_Leg_IkFk', at='float', dv=1, max=1, min=0, k=1)
s.hipCntrl.addAttr ('R_Leg_IkFk', at='float', dv=1, max=1, min=0, k=1)
s.hipCntrl.addAttr ('Spine_IkFk', at='float', dv=1, max=1, min=0, k=1)

s.hipCntrl.addAttr ('L_Arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
s.hipCntrl.addAttr ('R_Arm_poleVec', at='float', dv=0, max=1, min=0, k=1)
s.hipCntrl.addAttr ('L_Leg_poleVec', at='float', dv=0, max=1, min=0, k=1)
s.hipCntrl.addAttr ('R_Leg_poleVec', at='float', dv=0, max=1, min=0, k=1)

s.hipCntrl.Spine_IkFk >> s.moveall.ikfk
s.hipCntrl.R_Leg_IkFk >> rleg.moveall.ikfk
s.hipCntrl.L_Leg_IkFk >> lleg.moveall.ikfk
s.hipCntrl.R_Leg_IkFk >> rfoot.moveall.ikfk
s.hipCntrl.L_Leg_IkFk >> lfoot .moveall.ikfk
s.hipCntrl.R_Arm_IkFk >> rarm.moveall.ikfk
s.hipCntrl.L_Arm_IkFk >> larm.moveall.ikfk

s.hipCntrl.R_Arm_poleVec >> rarm.moveall.poleVec
s.hipCntrl.L_Arm_poleVec >> larm.moveall.poleVec
s.hipCntrl.R_Leg_poleVec >> rleg.moveall.poleVec
s.hipCntrl.L_Leg_poleVec >> lleg.moveall.poleVec

lfoot.baseCntrl.addAttr ('pin', at='float',min=0, max=1,dv=0, k=1)
lfoot.baseCntrl.addAttr ('bias', at='float',min=-0.9, max=0.9, k=1)
lfoot.baseCntrl.addAttr ('autoStretch', at='float',min=0, max=1,dv=1, k=1)
lfoot.baseCntrl.addAttr ('manualStretch', at='float',dv=1, k=1)
lfoot.baseCntrl.addAttr ('twist', at='float',dv=0, k=1)
lfoot.baseCntrl.pin >> lleg.ikCntrl.pin 
lfoot.baseCntrl.bias >> lleg.ikCntrl.bias
lfoot.baseCntrl.autoStretch >> lleg.ikCntrl.autoStretch 
lfoot.baseCntrl.manualStretch >> lleg.ikCntrl.manualStretch
lfoot.baseCntrl.twist >> lleg.ikCntrl.twist 

rfoot.baseCntrl.addAttr ('pin', at='float',min=0, max=1,dv=0, k=1)
rfoot.baseCntrl.addAttr ('bias', at='float',min=-0.9, max=0.9, k=1)
rfoot.baseCntrl.addAttr ('autoStretch', at='float',min=0, max=1,dv=1, k=1)
rfoot.baseCntrl.addAttr ('manualStretch', at='float',dv=1, k=1)
rfoot.baseCntrl.addAttr ('twist', at='float',dv=0, k=1)
rfoot.baseCntrl.pin >> rleg.ikCntrl.pin 
rfoot.baseCntrl.bias >> rleg.ikCntrl.bias
rfoot.baseCntrl.autoStretch >> rleg.ikCntrl.autoStretch 
rfoot.baseCntrl.manualStretch >> rleg.ikCntrl.manualStretch
rfoot.baseCntrl.twist >> rleg.ikCntrl.twist 


if pm.objExists ('spaces'):
    pm.delete ('spaces')
    
createSpc (None, 'global')
createSpc (larm.lastJnt, 'lhand')
createSpc (rarm.lastJnt, 'rhand')
createSpc (s.hipCntrl, 'hip')
createSpc (s.endJnt, 'chest')
createSpc (s.startJnt, 'cog')
createSpc (lleg.lastJnt, 'lfoot')
createSpc (rleg.lastJnt, 'rfoot')
createSpc (lclav.jntList[-1], 'lclav')
createSpc (rclav.jntList[-1], 'rclav')
createSpc (n.startJnt, 'neck')
createSpc (n.endJnt, 'head')

addSpc (target=larm.ikCntrl, spaceList=['global','chest','cog','lclav'], switcher=larm.ikCntrl.getParent(), type='parent')
addSpc (target=rarm.ikCntrl, spaceList=['global','chest','cog','rclav'], switcher=rarm.ikCntrl.getParent(), type='parent')
addSpc (target=larm.poleVec, spaceList=['hip','global','chest','cog','lclav'], switcher=larm.poleVec.getParent(), type='parent')
addSpc (target=rarm.poleVec, spaceList=['hip','global','chest','cog','rclav'], switcher=rarm.poleVec.getParent(), type='parent')
addSpc (target=lleg.poleVec, spaceList=['hip','global','chest','cog'], switcher=lleg.poleVec.getParent(), type='parent')
addSpc (target=rleg.poleVec, spaceList=['hip','global','chest','cog'], switcher=rleg.poleVec.getParent(), type='parent')
addSpc (target=s.endIkCntrl, spaceList=['hip', 'global', 'cog'], switcher=s.endIkCntrl.getParent(), type='parent')
addSpc (target=n.endCntrl, spaceList=['global','hip','chest','cog', 'neck'], switcher=n.endCntrl.getParent(), type='orient', posSpc=n.startJnt)
addSpc (target=larm.endCntrl, spaceList=['global','hip','chest','cog', 'lclav'], switcher=larm.endCntrl.getParent(), type='orient', posSpc=lclav.jntList[-1])
addSpc (target=rarm.endCntrl, spaceList=['global','hip','chest','cog', 'rclav'], switcher=rarm.endCntrl.getParent(), type='orient', posSpc=rclav.jntList[-1])
