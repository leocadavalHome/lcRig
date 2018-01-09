import maya.api.OpenMaya as om
import pymel.core as pm
import time
import cPickle as pickle

def doLoc(name, pos):
    loc = pm.spaceLocator(n=name)
    loc.localScaleX.set(0.05)
    loc.localScaleY.set(0.05)
    loc.localScaleZ.set(0.05)        
    pm.xform (loc, t=pos, wd=True)
    return loc    
    
    
def intersectEdgePlane (planePoint,planeNormal, A, B):
    u=B-A
    w=(A-planePoint)*-1
    D=planeNormal * u
    N=planeNormal * w
    if abs (D)<0.001:
        if N==0:
            return None
        else:
            return None
    SI = N/D
    if (SI<0 or SI>1):
        return 0
    I=A + SI *u
    return I

def calcMidPoint(planeLoc, geo):
    
    originalSelect = pm.ls (sl=True)
    sel = om.MSelectionList()
    sel.add(planeLoc)
    dag = sel.getDagPath(0)
    planeTransform = om.MFnTransform(dag)
    planePoint= om.MVector (planeTransform.translation(om.MSpace.kWorld)) 
    planeNormal=om.MVector.kZaxisVector * planeTransform.transformation().asMatrix()
       
    sel = om.MSelectionList()
    sel.add(geo)
    dag = sel.getDagPath(0)
    
    mesh = om.MFnMesh(dag)
    edgeIt = om.MItMeshEdge(dag)
    polygonIt = om.MItMeshPolygon(dag)
    
    intesectList = {}
    while not edgeIt.isDone():
        vtxA = mesh.getPoint(edgeIt.vertexId(0), om.MSpace.kWorld)
        vtxB = mesh.getPoint(edgeIt.vertexId(1), om.MSpace.kWorld)	
        A = om.MVector(vtxA)
        B = om.MVector(vtxB)
        
        result = intersectEdgePlane (planePoint,planeNormal, A, B)
        onBoudary = edgeIt.onBoundary()
       
        if result:
            #doLoc ('center1', result)
            intesectList[edgeIt.index()]=[result,onBoudary]
                        
        edgeIt.next()
    
    if intesectList == {}:
        return
        
    allSortedEdges=[]   
    sortedEdges=[]
    edgeIt.reset()  
    remainedEdges = intesectList.keys()
    count = len (remainedEdges)
    boundary = [x for x in remainedEdges if intesectList[x][1]==True]
    if boundary:
        i=boundary[0]
        isClosed =False
    else:
        i = remainedEdges[0]
        isClosed = True
    
    while not count==0:
        sortedEdges.append(i)    
        remainedEdges.remove(i)
        edgeIt.setIndex(i)    
        connectedFaces = edgeIt.getConnectedFaces()
        nextEdge = []
        for f in connectedFaces:
            polygonIt.setIndex(f) 
            connectedEdges = polygonIt.getEdges()
            a = [x for x in connectedEdges if x in remainedEdges]
            if a:
                i = a[0]
                nextEdge.append(i)
                
        if nextEdge:
            i=nextEdge[0] 
        else:
            allSortedEdges.append([sortedEdges,isClosed])        
            if remainedEdges:
                boundary = [x for x in remainedEdges if intesectList[x][1]==True]
                if boundary:
                    i=boundary[0]
                    isClosed = False
                else:
                    i = remainedEdges[0]
                    isClosed = True
            sortedEdges=[]        
        count -= 1
      
    for loop in allSortedEdges:
        maxD =-100000.0
        minD =100000.0
        minIndex = 0
        maxIndex = 0
        for vtx in loop[0]:
            vtxPoint = om.MVector (intesectList[vtx][0])
            if maxD < vtxPoint.length():
                maxD = vtxPoint.length()
                maxIndex= vtx

            if minD > vtxPoint.length():                
                minD =  vtxPoint.length()
                minIndex= vtx

        p1 =om.MVector(intesectList[maxIndex][0])
        p2 = om.MVector(intesectList[minIndex][0])
        c = (p1+p2)/2                 

        d = om.MVector(planePoint-c)
        
        distTreshold = .5
        
        
        if d.length() < distTreshold:         
            v1 = om.MVector (p1-c)
            v2 = v1^planeNormal
            p3 = c + v2.normal()*v2.length()
            p4 = c - v2.normal()*v2.length()
            crv = pm.curve (n='clipCurve', d=1, p=(p1,p3,p2,p4,p1), k=(0,1,2,3,4))
            loc = doLoc ('center1',c )
            pm.color (crv, rgb = (1,0,0))
            pm.color (loc, rgb = (0,1,0)) 
            pm.select (originalSelect)

def sjobMidPoint():
    cen= pm.ls ('clipCurve*', 'center*')
    pm.delete (cen)
    geos =  ['pSphere1Shape', 'pSphere2Shape']
    for g in geos:
        calcMidPoint('locator1', g)
     
#start_time = time.time()
#sjobMidPoint()
#print("--- %s seconds ---" % (time.time() - start_time))



#jobNum = cmds.scriptJob( attributeChange=['locator1.translate', sjobMidPoint] )
#jobNum1 = cmds.scriptJob( attributeChange=['locator1.rotate', sjobMidPoint] )

#cmds.scriptJob( kill=jobNum, force=True)
#cmds.scriptJob( kill=jobNum1, force=True)
#cmds.scriptJob(  ka=True)


def findSkinCluster(mesh):
    skincluster = None
    for each in pm.listHistory(mesh):  
        if type(each)==pm.nodetypes.SkinCluster:   
            skincluster = each
    return skincluster

def saveSkinning(mesh,path):
    print 'saving...'
    dataDict ={} 
    skincluster = findSkinCluster(mesh)
    if skincluster!=None:     
        for infl in skincluster.getInfluence():
            vtxList =[]
            getData = skincluster.getPointsAffectedByInfluence(infl) 
            if getData[0] and getData[1]: 
                for vtx, wgt in zip (getData[0][0],getData[1]):
                    vtxList.append ((vtx.currentItemIndex(),wgt))                   
                dataDict[infl]= vtxList
    
    with open(path, 'wb') as handle:
        pickle.dump(dataDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print 'saving ok!'
    
def loadSkinning(mesh,path):
    print 'loading ok!'
    skincluster = findSkinCluster(mesh)
    
    with open(path, 'rb') as handle:
        dataDict = pickle.load(handle)
        
    if skincluster!=None:
        skincluster.setNormalizeWeights(0)
        pm.skinPercent(skincluster, mesh, nrm=False, prw=100)
        
        jointDict = {}
        for storedJoint in dataDict :
            jointDict[storedJoint]=skincluster.indexForInfluenceObject(storedJoint)
               
        for infl in dataDict :
            for vtx in dataDict[infl]:
                pm.setAttr (skincluster.name()+'.weightList['+str(vtx[0])+'].weights['+str (jointDict[infl]) +']', vtx[1])
        skincluster.setNormalizeWeights(1)
        print 'loading ok!'    
             
#mesh= 'corpo'
#path = 'C:/Users/vzprojeto/Documents/leo/skin.pickle'
#jnts = pm.ls ('*_jnt', type='joint')
#pm.skinCluster (jnts, mesh)
#loadSkinning(mesh,path)

def saveCntrlsShape():
    userSel = pm.ls (sl=True)
    sel=[x for x in userSel if '_cntrl' in x.name()]    
    filename= 'C:/Users/vzprojeto/Documents/leo/cntrls.shp'
    cntrlShapeDict={}
    for obj in sel:
        tempDict={}
        for shp in obj.getShapes():
            if pm.nodeType (shp)=='nurbsCurve':
                pointList=[]
                for i in range (len (shp.cv)):
                    pointList.append (pm.pointPosition (shp.cv[i], l=True))
                tempDict[shp]=pointList
        cntrlShapeDict[obj.name()]=tempDict 
    print   cntrlShapeDict           
    with open(filename, 'wb') as f:
        pickle.dump(cntrlShapeDict, f)
    print 'save ok'
    
def loadCntrlShape():
    filename= 'C:/Users/vzprojeto/Documents/leo/cntrls.shp'
    cntrlShapeDict={}
    with open(filename,'rb') as f:
        print 'entrou'
        cntrlShapeDict  =  pickle.load(f)
    print    cntrlShapeDict     
    for obj in cntrlShapeDict:
        print obj
        for s in cntrlShapeDict[obj]:
            shp = pm.PyNode(s)
            for i in range (len (shp.cv)):
                pm.xform (shp.cv[i], t=cntrlShapeDict[obj][s][i])
