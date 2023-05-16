import binary_reader
import bpy
import os
import bmesh
import io, struct, collections, math, numpy
from mathutils import Matrix
from mathutils import Vector
from mathutils import Quaternion
from mathutils import Euler
import pathlib
def readAnimation_Z(f, rig, maxFrames):
    animName = pathlib.Path(f.name).stem
    reader = binary_reader.BinaryReader(f.read())
    datasize = reader.read_uint32()
    #print(str(datasize))
    linksize = reader.read_uint32()
    #print(str(linksize))
    decompressedsize = reader.read_uint32()
    #print(str(decompressedsize))
    compressedsize = reader.read_uint32()
    #print(str(compressedsize))
    classcrc32 = reader.read_uint32()
    #print(str(classcrc32))
    namecrc32 = str(reader.read_uint32())
    #print(namecrc32)
    reader.read_bytes(linksize)
    durationInSec = reader.read_float()
    #print(str(durationInSec))
    durationInFrames = round(durationInSec*60)
    reader.read_bytes(0x08)
    
    bpy.context.scene.render.fps = 60
    if (durationInFrames > maxFrames):
        maxFrames = durationInFrames
        bpy.context.scene.frame_end = durationInFrames
    animation = bpy.data.actions.new(animName)
    
    #AnimNode
    
    node_rotframe_list = []
    
    rotframeCount = reader.read_uint32()
    #print(str(rotframeCount))
    for i in range (0,rotframeCount):
        time = reader.read_float()
        x = reader.read_int16() / 2000
        y = reader.read_int16() / 2000
        z = reader.read_int16() / 2000
        w = reader.read_int16() / 2000
        node_rotframe_list.append(time)
        node_rotframe_list.append(x)
        node_rotframe_list.append(y)
        node_rotframe_list.append(z)
        node_rotframe_list.append(w)
        
    bezierRotframeCount = reader.read_uint32()
    reader.read_bytes(bezierRotframeCount*36)
        
    node_scaleframe_list = []
    
    reader.read_bytes(2)
    scaleframeCount = reader.read_uint32()
    #print(str(scaleframeCount))
    
    for i in range (0,scaleframeCount):
        time = reader.read_float()
        xVal = reader.read_int16() / 4096
        yVal = reader.read_int16() / 4096
        zVal = reader.read_int16() / 4096
        xTgtIn = reader.read_int16() / 4096
        yTgtIn = reader.read_int16() / 4096
        zTgtIn = reader.read_int16() / 4096
        xTgtOut = reader.read_int16() / 4096
        yTgtOut = reader.read_int16() / 4096
        zTgtOut = reader.read_int16() / 4096
        reader.read_uint16()
        node_scaleframe_list.append(time)
        node_scaleframe_list.append(xVal)
        node_scaleframe_list.append(yVal)
        node_scaleframe_list.append(zVal)
        node_scaleframe_list.append(xTgtIn)
        node_scaleframe_list.append(yTgtIn)
        node_scaleframe_list.append(zTgtIn)
        node_scaleframe_list.append(xTgtOut)
        node_scaleframe_list.append(yTgtOut)
        node_scaleframe_list.append(zTgtOut)

    node_transframe_list = []
    
    reader.read_bytes(2)
    transframeCount = reader.read_uint32()
    #print(str(transframeCount))
    
    for i in range (0,transframeCount):
        time = reader.read_float()
        xVal = reader.read_int16() / 4096
        yVal = reader.read_int16() / 4096
        zVal = reader.read_int16() / 4096
        xTgtIn = reader.read_int16() / 4096
        yTgtIn = reader.read_int16() / 4096
        zTgtIn = reader.read_int16() / 4096
        xTgtOut = reader.read_int16() / 4096
        yTgtOut = reader.read_int16() / 4096
        zTgtOut = reader.read_int16() / 4096
        reader.read_int16()
        node_transframe_list.append(time)
        node_transframe_list.append(xVal)
        node_transframe_list.append(yVal)
        node_transframe_list.append(zVal)
        node_transframe_list.append(xTgtIn)
        node_transframe_list.append(yTgtIn)
        node_transframe_list.append(zTgtIn)
        node_transframe_list.append(xTgtOut)
        node_transframe_list.append(yTgtOut)
        node_transframe_list.append(zTgtOut)
        
    messageframeCount = reader.read_uint32()
    for i in range (0,messageframeCount):
        reader.read_float()
        messageCount = reader.read_uint32()
        reader.read_bytes(messageCount*20)
    
    #AnimMaterial
    
    reader.read_bytes(2)
    floatframeCount0 = reader.read_uint32()
    #print(str(floatframeCount0))
    reader.read_bytes(floatframeCount0*12)
    
    reader.read_bytes(2)
    floatframeCount1 = reader.read_uint32()
    #print(str(floatframeCount1))
    reader.read_bytes(floatframeCount1*12)
    
    reader.read_bytes(2)
    vec3fframeCount0 = reader.read_uint32()
    #print(str(vec3fframeCount0))
    reader.read_bytes(vec3fframeCount0*24)
    
    reader.read_bytes(2)
    vec3fframeCount1 = reader.read_uint32()
    #print(str(vec3fframeCount1))
    reader.read_bytes(vec3fframeCount1*24)
    
    reader.read_uint16()
    floatframeCount2 = reader.read_uint32()
    #print(str(floatframeCount2))
    reader.read_bytes(floatframeCount2*12)
    
    #AnimMesh
    
    reader.read_uint16()
    floatframeCount3 = reader.read_uint32()
    #print(str(floatframeCount3))
    reader.read_bytes(floatframeCount3*12)
    
    #AnimMorph
    
    reader.read_bytes(2)
    floatframeCount4 = reader.read_uint32()
    reader.read_bytes(floatframeCount4*12)
    
    #AnimNodeModifier
    
    animNodeModifierCount = reader.read_uint32()
    animNodeModifierValueList = []
    for i in range (0,animNodeModifierCount):
        animNodeModifierValueList.append(reader.read_uint32())
        animNodeModifierValueList.append(reader.read_uint32())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
        animNodeModifierValueList.append(reader.read_uint16())
    brokenFrames = 0    
    #print(str(animNodeModifierCount))
    for i in range (0,len(rig.pose.bones)):
        curBone = rig.pose.bones[i] 
        try:
            i = animNodeModifierValueList.index(int(curBone.name))
        except ValueError:
            continue
        
        boneNameCrc32 = str(animNodeModifierValueList[i])
        #print(str(rig.data.bones))
        editBone = rig.data.bones[boneNameCrc32]
        #print('bone num' + str(i) + ' = ' + boneNameCrc32)
        
        fCurveTransX = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].location',
                    index=0,
                    action_group=boneNameCrc32,
                )
        fCurveTransY = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].location',
                    index=1,
                    action_group=boneNameCrc32,
                )
        fCurveTransZ = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].location',
                    index=2,
                    action_group=boneNameCrc32,
                )

        fCurveRotX = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].rotation_quaternion',
                    index=1,
                    action_group=boneNameCrc32,
                )
        fCurveRotY = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].rotation_quaternion',
                    index=2,
                    action_group=boneNameCrc32,
                )
        fCurveRotZ = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].rotation_quaternion',
                    index=3,
                    action_group=boneNameCrc32,
                )
        fCurveRotW = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].rotation_quaternion',
                    index=0,
                    action_group=boneNameCrc32,
                )
        fCurveScaleX = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].scale',
                    index=0,
                    action_group=boneNameCrc32,
                )
        fCurveScaleY = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].scale',
                    index=1,
                    action_group=boneNameCrc32,
                )
        fCurveScaleZ = animation.fcurves.new(
                    data_path='pose.bones["' + boneNameCrc32 + '"].scale',
                    index=2,
                    action_group=boneNameCrc32,
                )

        boneTransStartFrame = animNodeModifierValueList[i+2]
        boneTransFrameCount = animNodeModifierValueList[i+3]
        #print(len(node_transframe_list))
        for tIndex in range (boneTransStartFrame,boneTransStartFrame+boneTransFrameCount):
            #print(tIndex*10)
            time = node_transframe_list[(tIndex*10)]
            xVal = node_transframe_list[(tIndex*10)+1]
            yVal = node_transframe_list[(tIndex*10)+2]
            zVal = node_transframe_list[(tIndex*10)+3]
            xTgtIn = node_transframe_list[(tIndex*10)+4]
            yTgtIn = node_transframe_list[(tIndex*10)+5]
            zTgtIn = node_transframe_list[(tIndex*10)+6]
            xTgtOut = node_transframe_list[(tIndex*10)+7]
            yTgtOut = node_transframe_list[(tIndex*10)+8]
            zTgtOut = node_transframe_list[(tIndex*10)+9]
            
            #print('time = ' + str(time))
            
            frame = round(time*60)
            
            #print('frame = ' + str(frame))
            
            vec = Vector([xVal,yVal,zVal])
            #print(str(editBone.matrix.to_4x4().inverted()))
            poseSpaceTranslation = (editBone.matrix_local.inverted() @ editBone.parent.matrix_local @ Matrix.Translation([xVal,yVal,zVal])).translation

            keyframeX = fCurveTransX.keyframe_points.insert(frame, poseSpaceTranslation.x)
            keyframeX.interpolation = 'QUAD'
            if (tIndex != boneTransStartFrame):
                keyframeX.handle_left = (frame,xTgtIn)
            if (tIndex != boneTransStartFrame+boneTransFrameCount-1):
                keyframeX.handle_right = (frame,xTgtOut)
                
                
            keyframeY = fCurveTransY.keyframe_points.insert(frame, poseSpaceTranslation.y)
            keyframeY.interpolation = 'QUAD'
            if (tIndex != boneTransStartFrame):
                keyframeY.handle_left = (frame,yTgtIn)
            if (tIndex != boneTransStartFrame+boneTransFrameCount-1):
                keyframeY.handle_right = (frame,yTgtOut)
                
            keyframeZ = fCurveTransZ.keyframe_points.insert(frame, poseSpaceTranslation.z)
            keyframeZ.interpolation = 'QUAD'
            if (tIndex != boneTransStartFrame):
                keyframeZ.handle_left = (frame,zTgtIn)
            if (tIndex != boneTransStartFrame+boneTransFrameCount-1):
                keyframeZ.handle_right = (frame,zTgtOut)
        
        boneRotStartFrame = animNodeModifierValueList[i+4]
        boneRotFrameCount = animNodeModifierValueList[i+5]
        
        for rIndex in range (boneRotStartFrame,boneRotStartFrame+boneRotFrameCount):
            time = node_rotframe_list[(rIndex*5)]
            x = node_rotframe_list[(rIndex*5)+1]
            y = node_rotframe_list[(rIndex*5)+2]
            z = node_rotframe_list[(rIndex*5)+3]
            w = node_rotframe_list[(rIndex*5)+4]
            
            #print('time = ' + str(time))
            
            frame = round(time*60)
            
            #print('frame = ' + str(frame))
            
            quat = Quaternion((w,x,y,z))
            
            poseSpaceRot = (editBone.matrix_local.to_quaternion().inverted().to_matrix().to_4x4() @ editBone.parent.matrix_local @ quat.to_matrix().to_4x4()).to_quaternion()
            
            if (rIndex < boneRotStartFrame+boneRotFrameCount-1):
                timeNext = node_rotframe_list[((rIndex+1)*5)]
                xNext = node_rotframe_list[((rIndex+1)*5)+1]
                yNext = node_rotframe_list[((rIndex+1)*5)+2]
                zNext = node_rotframe_list[((rIndex+1)*5)+3]
                wNext = node_rotframe_list[((rIndex+1)*5)+4]
                
                frameNext = round(timeNext*60)
                
                quatNext = Quaternion((wNext,xNext,yNext,zNext))
                
                poseSpaceRotNext = (editBone.matrix_local.to_quaternion().inverted().to_matrix().to_4x4() @ editBone.parent.matrix_local @ quatNext.to_matrix().to_4x4()).to_quaternion()
                
                poseSpaceRotInterp = poseSpaceRot.slerp(poseSpaceRotNext,0.5)
                
                xInterp = (poseSpaceRot.x+poseSpaceRotNext.x)/2
                yInterp = (poseSpaceRot.y+poseSpaceRotNext.y)/2
                zInterp = (poseSpaceRot.z+poseSpaceRotNext.z)/2
                wInterp = (poseSpaceRot.w+poseSpaceRotNext.w)/2
                
                if (((xInterp - poseSpaceRotInterp.x > 0.5) or (xInterp - poseSpaceRotInterp.x < -0.5)) or
                    ((yInterp - poseSpaceRotInterp.y > 0.5) or (yInterp - poseSpaceRotInterp.y < -0.5)) or
                    ((zInterp - poseSpaceRotInterp.z > 0.5) or (zInterp - poseSpaceRotInterp.z < -0.5)) or
                    ((wInterp - poseSpaceRotInterp.w > 0.5) or (wInterp - poseSpaceRotInterp.w < -0.5))):
                    print('Info: Different interp in rot frame number: ' + str(rIndex))
                    print('    - bone: ' + boneNameCrc32)
                    print('    - blender frame: ' + str(frame))
                    print('    - quatSlerpInterp: ' + str(poseSpaceRotInterp))
                    print('    - quatLerpInterp: ' + str(Quaternion((wInterp,xInterp,yInterp,zInterp))))
                    print('    - Added custom frame: ' + str(frame+1))
                    print('-------------------------------------------------------------')
                    brokenFrames+=1
                    
                    keyframeXfix = fCurveRotX.keyframe_points.insert(frame+1, poseSpaceRotInterp.x)
                    keyframeXfix.interpolation = 'LINEAR'
                        
                    keyframeYfix = fCurveRotY.keyframe_points.insert(frame+1, poseSpaceRotInterp.y)
                    keyframeYfix.interpolation = 'LINEAR'
                        
                    keyframeZfix = fCurveRotZ.keyframe_points.insert(frame+1, poseSpaceRotInterp.z)
                    keyframeZfix.interpolation = 'LINEAR'
                    
                    keyframeWfix = fCurveRotW.keyframe_points.insert(frame+1, poseSpaceRotInterp.w)
                    keyframeWfix.interpolation = 'LINEAR'
            
            keyframeX = fCurveRotX.keyframe_points.insert(frame, poseSpaceRot.x)
            keyframeX.interpolation = 'LINEAR'
                
            keyframeY = fCurveRotY.keyframe_points.insert(frame, poseSpaceRot.y)
            keyframeY.interpolation = 'LINEAR'
                
            keyframeZ = fCurveRotZ.keyframe_points.insert(frame, poseSpaceRot.z)
            keyframeZ.interpolation = 'LINEAR'
            
            keyframeW = fCurveRotW.keyframe_points.insert(frame, poseSpaceRot.w)
            keyframeW.interpolation = 'LINEAR'

        
        boneScaleStartFrame = animNodeModifierValueList[i+8]
        boneScaleFrameCount = animNodeModifierValueList[i+9]
        
        for sIndex in range (boneScaleStartFrame,boneScaleStartFrame+boneScaleFrameCount):
            time = node_scaleframe_list[(sIndex*10)]
            xVal = node_scaleframe_list[(sIndex*10)+1]
            yVal = node_scaleframe_list[(sIndex*10)+2]
            zVal = node_scaleframe_list[(sIndex*10)+3]
            xTgtIn = node_scaleframe_list[(sIndex*10)+4]
            yTgtIn = node_scaleframe_list[(sIndex*10)+5]
            zTgtIn = node_scaleframe_list[(sIndex*10)+6]
            xTgtOut = node_scaleframe_list[(sIndex*10)+7]
            yTgtOut = node_scaleframe_list[(sIndex*10)+8]
            zTgtOut = node_scaleframe_list[(sIndex*10)+9]
            
            #print('time = ' + str(time))
            
            frame = round(time*60)
            
            #print('frame = ' + str(frame))
            
            vec = Vector([xVal,yVal,zVal])
            #print(str(editBone.matrix.to_4x4().inverted()))
            poseSpaceScale = (editBone.matrix_local.inverted() @ editBone.parent.matrix_local @ Matrix.Diagonal(Vector([xVal,yVal,zVal])).to_4x4()).to_scale()
            
            keyframeX = fCurveScaleX.keyframe_points.insert(frame, poseSpaceScale.x)
            keyframeX.interpolation = 'QUAD'
            if (sIndex != boneScaleStartFrame):
                keyframeX.handle_left = (frame,xTgtIn)
            if (sIndex != boneScaleStartFrame+boneScaleFrameCount-1):
                keyframeX.handle_right = (frame,xTgtOut)
                
                
            keyframeY = fCurveScaleY.keyframe_points.insert(frame, poseSpaceScale.y)
            keyframeY.interpolation = 'QUAD'
            if (sIndex != boneScaleStartFrame):
                keyframeY.handle_left = (frame,yTgtIn)
            if (sIndex != boneScaleStartFrame+boneScaleFrameCount-1):
                keyframeY.handle_right = (frame,yTgtOut)
                
            keyframeZ = fCurveScaleZ.keyframe_points.insert(frame, poseSpaceScale.z)
            keyframeZ.interpolation = 'QUAD'
            if (sIndex != boneScaleStartFrame):
                keyframeZ.handle_left = (frame,zTgtIn)
            if (sIndex != boneScaleStartFrame+boneScaleFrameCount-1):
                keyframeZ.handle_right = (frame,zTgtOut)
    
    #AnimMaterialModifier
    
    animMaterialModifierCount = reader.read_uint32()
    reader.read_bytes(28*animMaterialModifierCount)
    
    #AnimMeshModifier
    
    animMeshModifierCount = reader.read_uint32()
    reader.read_bytes(12*animMeshModifierCount)
    
    #AnimMorphModifier
    
    animMorphModifierCount = reader.read_uint32()
    reader.read_bytes(12*animMorphModifierCount)
    
    if rig.animation_data is None:
        rig.animation_data_create()
    rig.animation_data.action = animation
    
    print('Info: Broken interp frame count: ' + str(brokenFrames))
    return maxFrames
def load(self, context, filepath):
    pathOne = filepath
    rootpath = os.path.dirname(filepath)
    f = open(pathOne,"rb")
    readAnimation_Z(f,bpy.context.active_object,0)
    f.close()
    
    return True