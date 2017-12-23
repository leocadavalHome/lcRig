x = Limb({'name':'teste','flipAxis':False, 'axis':'X'})
x.doRig()

p1=pm.xform (x.limbDict['joint1'], q=True, t=True, ws=True)
p2=pm.xform (x.limbDict['joint2'], q=True, t=True, ws=True)
p3=pm.xform (x.limbDict['joint3'], q=True, t=True, ws=True)
A=om.MVector (p1)
B=om.MVector (p2)
C=om.MVector (p3)
AB= A-B
BC= B-C
L=AB.length()+BC.length()

r1 = RibbonBezier({'name':'ribbonBezier2', 'size':L, 'numJnts':10})
r1.doRig()
r1.connectToLimb(x)