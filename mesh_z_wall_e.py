from . import binary_reader
import bpy
import os
import bmesh
import io, struct, collections, math, numpy
from mathutils import Matrix
from mathutils import Vector
from mathutils import Quaternion
from mathutils import Euler
import pathlib
from . import format_helper

rootpath = ""
excludedMeshes = []
bones = []
boneNames = []
meshBoneCrc32s = []
boneTrans = []
boneRot = []
boneTrs = []
globalMeshObjects = []
linkfmt = "DPC"

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
    namecrc32 = str(reader.read_int32())
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
    animation = bpy.data.actions.new(namecrc32)
    
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

def bone_traversal(current):    
    for child in current.children:
        child.translate(current.tail)
        bone_traversal(child)
        
def readSkel_Z(bs):
    bs.seek(0x04)
    link_size = bs.read_uint32()
    bs.seek(0x18)
        # Links
    bs.seek(link_size, 1) # skip links
        
        # Data
    bs.seek(20, 1)
    bone_count = bs.read_uint32()
    for i in range(0, bone_count):
        bs.read_uint32()
        qx = bs.read_float()
        qy = bs.read_float()
        qz = bs.read_float()
        qw = bs.read_float()
        bs.read_float()
        bs.read_float()
        bs.read_float()
        bs.read_uint32()
        x = bs.read_float()
        y = bs.read_float()
        z = bs.read_float()
        bs.read_uint32()
        rot00 = bs.read_float()
        rot01 = bs.read_float()
        rot02 = bs.read_float()
        bs.read_uint32()
        rot10 = bs.read_float()
        rot11 = bs.read_float()
        rot12 = bs.read_float()
        bs.read_uint32()
        rot20 = bs.read_float()
        rot21 = bs.read_float()
        rot22 = bs.read_float()
        bs.seek(68, 1)
        trs = numpy.frombuffer(bs.read_bytes(64), dtype=numpy.float32, count=16)
        trs = trs.reshape((4, 4));
        rotmat = Matrix()
        rotmat[0][0] = trs[0][0]
        rotmat[0][1] = trs[0][1]
        rotmat[0][2] = trs[0][2]
        rotmat[1][0] = trs[1][0]
        rotmat[1][1] = trs[1][1]
        rotmat[1][2] = trs[1][2]
        rotmat[2][0] = trs[2][0]
        rotmat[2][1] = trs[2][1]
        rotmat[2][2] = trs[2][2]
        boneTrs.append(trs)
        boneRot.append(Quaternion((qw, qx, qy, qz)).to_matrix().to_4x4())
        boneTrans.append(Matrix.Translation(Vector((x,y,z))))
        
        bs.seek(1 * 1 * 4, 1)
        parent_index = bs.read_int32()
        bs.seek(1 * 2 * 4, 1)
        boneNames.append(str(bs.read_uint32()))
        bones.append((Matrix(trs), parent_index))
        
    material_crc32_count = bs.read_uint32()
    bs.seek(material_crc32_count * 1 * 4, 1)
        
    mesh_data_crc32_count = bs.read_uint32()
    bs.seek(mesh_data_crc32_count * 1 * 4, 1)
        
    animation_node_names_arrays = bs.read_uint32()
    for i in range(0, animation_node_names_arrays):
        crc32s = bs.read_uint32()
        bs.seek(crc32s * 1 * 4, 1)
        
    some_names_crc32_count = bs.read_uint32()
    bs.seek(some_names_crc32_count * 1 * 4, 1)
        
    sphere_col_bones0_count = bs.read_uint32()
    bs.seek(sphere_col_bones0_count * 7 * 4, 1)
        
    sphere_col_bones1_count = bs.read_uint32()
    bs.seek(sphere_col_bones1_count * 7 * 4, 1)
        
    box_col_bones_count = bs.read_uint32()
    bs.seek(box_col_bones_count * 19 * 4, 1)
    
def execute(skelCrc32,skinCrc32,rootpath):
    bs = binary_reader.BinaryReader(open(rootpath + os.sep + (str(skelCrc32) + ".Skel_Z"), "rb").read())

    skel = readSkel_Z(bs)
    
    if (bpy.data.armatures.get("Skin_"+str(skinCrc32)+"_skeleton") != None):
        bpy.data.armatures.remove(bpy.data.armatures.get("Skin_"+str(skinCrc32)+"_skeleton"))
    armature = bpy.data.armatures.new("Skin_"+str(skinCrc32)+"_skeleton")
    armature.display_type = "STICK"
    
    rig = bpy.data.objects.new("Skin_"+str(skinCrc32), armature)
    rig.show_in_front = True
    
    context = bpy.context
    context.view_layer.active_layer_collection.collection.objects.link(rig)
    context.view_layer.objects.active = rig
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    #print(len(bones))
    map_index_to_bone = {}
    bone_index = 0
    bone_mats = {}
    for i in range(0, len(bones)):
        bone = bones[i]
        current_bone = armature.edit_bones.new(str(boneNames[i]))

        trans = boneTrans[i]
        rot = boneRot[i]
        final_mat = trans @ rot
        bone_mats[boneNames[i]] = final_mat

        current_bone.tail = (0.0, 0.001, 0.0)
        if bone[1] > -1:
            current_bone.parent = armature.edit_bones[bone[1]]

    bpy.context.view_layer.objects.active = rig
        
    bpy.ops.object.mode_set(mode='POSE')
    
    for bone in rig.pose.bones:
        bone.matrix_basis.identity()
        bone.matrix = bone_mats[bone.name]

    bpy.ops.pose.armature_apply()
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=3)
    bone_vis = bpy.context.active_object
    bone_vis.data.name = bone_vis.name = "bone_vis"
    bone_vis.use_fake_user = True
    bpy.context.view_layer.active_layer_collection.collection.objects.unlink(
        bone_vis)
    bpy.context.view_layer.objects.active = rig

    maxs = [0, 0, 0]
    mins = [0, 0, 0]

    j = 0
    for bone in armature.bones:
        for i in range(3):
            maxs[i] = max(maxs[i], bone.head_local[i])
            mins[i] = min(mins[i], bone.head_local[i])

    dimensions = []
    for i in range(3):
        dimensions.append(maxs[i] - mins[i])

    length = max(0.0001, (dimensions[0] + dimensions[1] + dimensions[2]) / 600)

    bpy.ops.object.mode_set(mode='EDIT')
    for bone in [armature.edit_bones[boneNames[i]] for i in range(0, len(bones))]:
        bone.tail = bone.head + (bone.tail - bone.head).normalized() * length
        rig.pose.bones[bone.name].custom_shape = bone_vis

    bpy.ops.object.mode_set(mode='OBJECT')

    bpy.context.view_layer.update()

    bpy.ops.object.mode_set(mode='OBJECT')
    
    return rig
    
def readMesh_Z(f,subsectionMatIndices,rootpath,meshBoneCrc32s=None):
    
    reader = binary_reader.BinaryReader(f.read())
    datasize = reader.read_uint32()
    linksize = reader.read_uint32()
    decompressedsize = reader.read_uint32()
    compressedsize = reader.read_uint32()
    classcrc32 = reader.read_uint32()
    namecrc32 = reader.read_link(linkfmt)
    name = str(namecrc32)
    print("loading mesh " + name)
    reader.seek(linksize, whence=1)
    reader.read_uint32()
    reader.read_uint32()
    morpherRelatedCount = reader.read_uint32()
    print("morpher related count" + str(morpherRelatedCount))
    reader.seek(morpherRelatedCount*4, whence=1)
    reader.read_uint32()
    reader.read_uint32()
    reader.read_uint32()
    reader.read_uint32()
    matCrc32Count = reader.read_uint32()
    matCrc32List = []
    matList = []
    addMatIndices = False
    
    if not subsectionMatIndices:
        addMatIndices = True
        
    for i in range(matCrc32Count):
        matCrc32List.append(str(reader.read_link(linkfmt)))
        if addMatIndices: subsectionMatIndices.append(i)
    rootpath += os.sep
    for h in matCrc32List:
        try:
            mat = bpy.data.materials.new(name=str(h))
            mat.use_nodes = True
            material_z = (rootpath + str(h) + ".Material_Z")
            fe = open(material_z, "rb")
            reader2 = binary_reader.BinaryReader(fe.read())
            reader2.seek(0x20)
            texturename = reader2.read_link(linkfmt)
            strtexturename = str(texturename)
                
            #open bitmap_z's and get dds from those automatically

            bitmap_z = (rootpath + strtexturename + ".Bitmap_Z")
            dds = (rootpath + strtexturename + ".dds")
            bm = open(bitmap_z, "rb")
            tex = open(dds, "wb")
            reader3 = binary_reader.BinaryReader(bm.read())
            reader3.set_endian(False)
            reader3.seek(0x2d)
            size3 = reader3.read_uint32()
            reader3.seek(0x36)
            tex.write(reader3.read_bytes(size3))
            bm.close()
            tex.close()
            fe.close()
            
            nodes = mat.node_tree.nodes
            bdsf = nodes['Principled BSDF']
            imagetexture = nodes.new('ShaderNodeTexImage')
            imagetexture.location = (-300, 250)
            imagetexture.image = bpy.data.images.load(rootpath + strtexturename + ".dds")
            link = mat.node_tree.links.new
            link(imagetexture.outputs[0], bdsf.inputs[0])
            link(imagetexture.outputs[1], bdsf.inputs[21])
            bdsf.inputs['Specular'].default_value = 0
        except:
            pass

    stuffRelatedToCounts = reader.read_bytes(24)
    spherecolcount = reader.read_uint32()
    if (spherecolcount != 0):
        for i in range(spherecolcount):
            reader.read_bytes(20)
            reader.read_uint32()
    boxcolcount = reader.read_uint32()
    if (boxcolcount != 0):
        for i in range(boxcolcount):
            reader.read_float(16)
            reader.read_uint32()
            reader.read_uint32()
    cylindercolcount = reader.read_uint32()
    if (cylindercolcount != 0):
        for i in range(cylindercolcount):
            reader.read_bytes(40)
            reader.read_uint32()
    AABBColRelatedCount = reader.read_uint32()
    if (AABBColRelatedCount != 0):
        for i in range(AABBColRelatedCount):
            reader.read_uint32(2)
    AABBColCount = reader.read_uint32()
    if (AABBColCount != 0):
        for i in range(AABBColCount):
            reader.read_uint32(8)
    shortvertexcount = reader.read_uint32()
    #setup mesh for creation


    vertices_list = []
    uv_list = []
    normals2 = list()
    faces_list = []
    test = []

    #read short vertices and basically ignore them

    for i in range(shortvertexcount * 3):
        reader.read_uint16()
    unkUintCount = reader.read_uint32()
    if (unkUintCount != 0):
        for i in range(unkUintCount):
            reader.read_uint32()
    one = reader.read_uint32()
    #vertices

    vertexcount = reader.read_uint32()
    print(str(vertexcount))
    vertexSize = reader.read_uint32()
    reader.read_uint32()
    if (vertexSize == 24):
        #print("!!!!!! SKIPPED (24B vertices): " + name + ".Mesh_Z")
        return
    vertexStart = reader.pos()
    reader.seek(vertexcount*vertexSize,1)
    reader.read_uint32()
    faceShortCount = reader.read_uint32()
    reader.read_uint32()
    faceStart = reader.pos()
    print("face start: " + str(faceStart))
    print(str(faceShortCount))
    reader.seek(faceShortCount * 2,1)
    vertexGroupCount = reader.read_uint32()
    print(vertexGroupCount)
    meshObjects = []
    print("Reached vertex groups in mesh: " + name)
    for i in range(vertexGroupCount):
        #print("vertexGroup " + str(i))
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()
        weight_layer = bm.verts.layers.deform.new()

        reader.read_uint32()
        reader.read_uint32()
        reader.read_uint32()
        reader.read_uint32()
        vertexBufferOffset = reader.read_uint16()
        print("vbuffer off " + str(vertexBufferOffset))
        reader.read_uint16()
        vertexCountInBuffer = reader.read_uint32()
        print("vcount" + str(vertexCountInBuffer))
        faceBufferOffset = reader.read_uint32()
        print("ibuffer off " + str(faceBufferOffset))
        faceCountInBuffer = reader.read_uint32()
        print("fcount " + str(faceCountInBuffer))
        reader.read_uint32()
        reader.read_uint32()
        reader.read_uint16()
        reader.read_uint16()
        stay = reader.pos()
        reader.seek(vertexStart + vertexBufferOffset*vertexSize)
        
        for j in range(vertexCountInBuffer):
            
            #print("vertex " + str(j))
            
            x = reader.read_float()
            y = reader.read_float()
            z = reader.read_float()
            unk1 = reader.read_float()
            bnz = reader.read_uint8()
            bny = reader.read_uint8()
            bnx = reader.read_uint8()
            pad = reader.read_int8()
            uvx = reader.read_float()
            uvy = reader.read_float()
            vert = bm.verts.new((x,y,z))
            vertices_list.append(vert)
            uv_list.append((uvx,uvy))
            byteToNormalX = (bnx / 255.0)
            byteToNormalY = (bny / 255.0)
            byteToNormalZ = (bnz / 255.0)
            nx = (((byteToNormalX*2)-1))
            ny = (((byteToNormalY*2)-1))
            nz = (((byteToNormalZ*2)-1))
            normals2.append([nx,nz,ny])
            weightIndices = []
            weights = []
            if vertexSize == 60 and meshBoneCrc32s:
                wI1 = reader.read_float()
                wI2 = reader.read_float()
                wI3 = reader.read_float()
                wI4 = reader.read_float()
                weightIndices.append(wI1)
                weightIndices.append(wI2)
                weightIndices.append(wI3)
                weightIndices.append(wI4)
                weights.append(reader.read_float())
                weights.append(reader.read_float())
                weights.append(reader.read_float())
                weights.append(reader.read_float())
                for k in range(0,len(weightIndices)):
                    if (weights[k] == 0.0):
                        continue
                    
                    curBoneIndex = int(weightIndices[k]//6)
                    
                    curBoneName = meshBoneCrc32s[i][curBoneIndex]

                    if (curBoneName == 4294967295 or curBoneName == 4294967294):
                        curBoneName = meshBoneCrc32s[i-1][curBoneIndex]
                        meshBoneCrc32s[i][curBoneIndex] = curBoneName
                    if (curBoneName == 4294967295 or curBoneName == 4294967294):
                        continue;    
                    vert[weight_layer][boneNames.index(str(curBoneName))] = weights[k]
            elif vertexSize == 48 and meshBoneCrc32s:
                weightIndex = reader.read_float()
                reader.read_float()
                reader.read_float()
                reader.read_float()
                weight = reader.read_float()
                if (weight != 0.0):
                    curBoneIndex = int(weightIndex//6)
                    
                    curBoneName = meshBoneCrc32s[i][curBoneIndex]

                    if (curBoneName == 4294967295 or curBoneName == 4294967294):
                        curBoneName = meshBoneCrc32s[i-1][curBoneIndex]
                        meshBoneCrc32s[i][curBoneIndex] = curBoneName
                        
                    vert[weight_layer][boneNames.index(str(curBoneName))] = weight
            else:
                reader.read_bytes(vertexSize - 28)
        
        reader.seek(faceStart + faceBufferOffset*2)
        
        for k in range(faceCountInBuffer):
            try:
                face = bm.faces.new([vertices_list[reader.read_uint16()] for x in range(3)])
                face.material_index = subsectionMatIndices[i]
            except:
                continue
        
        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        def uv_to_blender(uv):
            return (uv[0], 1.0 - uv[1])
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = uv_to_blender(uv_list[loop.vert.index])
            
        newmesh = bpy.data.meshes.new('newmesh')
        bm.to_mesh(newmesh)
        # newmesh.create_normals_split()
        newmesh.normals_split_custom_set_from_vertices(normals2)
        
        newobject = bpy.data.objects.new(("Mesh_"+name + "_VertGrp_" + str(i)), newmesh)
        print("new mesh object: " + newobject.name)
        meshObjects.append(newobject)
        bpy.context.view_layer.active_layer_collection.collection.objects.link(newobject)
        normals2.clear()
        uv_list.clear()
        # newmesh.auto_smooth_angle = 0
        # newmesh.use_auto_smooth = True
        newobject.data.materials.append(bpy.data.materials.get(matCrc32List[subsectionMatIndices[i]]))
        
        for boneName in boneNames:
            newobject.vertex_groups.new(name=boneName)

        try:
            reader.seek(stay)
        except:
            continue

    globalMeshObjects.append(meshObjects)


def readSkin(f,path):
    #print("new skin, globalMeshes: " + str(globalMeshObjects))
    print(path)
    rootpath = os.path.dirname(path)
    print(rootpath)
    subSectionMaterialIndices = []
    reader = binary_reader.BinaryReader(f.read())
    reader.set_endian(False)
    datasize = reader.read_uint32()
    linksize = reader.read_uint32()
    decompressedsize = reader.read_uint32()
    compressedsize = reader.read_uint32()
    classcrc32 = reader.read_uint32()
    namecrc32 = reader.read_link(linkfmt)
    linkCrc32 = reader.read_uint32()
    linkCount = reader.read_uint32()
    reader.seek(4*linkCount,1)
    skelCrc32 = reader.read_link(linkfmt)
    rig = None
    if skelCrc32 != 0:
        rig = execute(skelCrc32,namecrc32,rootpath)
    else:
        ShowMessageBox("Unsupported Skin_Z!! Skeleton will NOT be loaded", "Alert", 'ERROR')
        #print("No skel skin (??) : " + str(namecrc32))
        # return

    #print("skel_z is totes: ", skelCrc32)
    reader.seek(16,1)
    reader.seek(74,1)
    meshCrc32Count = reader.read_uint32()
    meshCrc32 = []
    for i in range(meshCrc32Count):
        curMesh = reader.read_link(linkfmt);
        meshCrc32.append(curMesh)
        excludedMeshes.append(rootpath + str(curMesh) + ".Mesh_Z")
    for i in range(reader.read_uint32()):
        reader.seek(8,1)
    for i in range(reader.read_uint32()):
        reader.read_uint32()
        for i in range(reader.read_uint32()):
            reader.read_uint16()
            for i in range(reader.read_uint32()):
                reader.seek(8,1)
            for i in range(reader.read_uint32()):
                reader.seek(8,1)
    isClassId = reader.read_uint8()
    if (isClassId != 0):
        for i in range(reader.read_uint32()):
            reader.seek(8,1)
        for i in range(reader.read_uint32()):
            reader.seek(8,1)
    matrixCacheCheck = reader.read_uint32()
    skinSectionCount = reader.read_uint32()
    boneCrc32ForSection = list()
    #print(skinSectionCount)
    
    for i in range(skinSectionCount):
        meshBoneCrc32s = []
        subSectionMaterialIndices = []
        oldMaterial = -1
        curIndex = -1
        skinSubSectionCount = reader.read_uint32()
        for j in range(skinSubSectionCount):
            curMaterial = reader.read_link(linkfmt)
            if (curMaterial != oldMaterial):
                curIndex += 1
            for x in range(7):
                bone = reader.read_uint32()
                boneCrc32ForSection.append(bone)
            reader.seek(8,1)
            morphPacketCount = reader.read_uint32()
            reader.seek(8*morphPacketCount,1)
            subSectionMaterialIndices.append(curIndex)
            oldMaterial = curMaterial;
            meshBoneCrc32s.append(boneCrc32ForSection)
            boneCrc32ForSection = []
        meshName = ((rootpath + os.sep + str(meshCrc32[i])) + ".Mesh_Z")
        mf = open(meshName, "rb")
        readMesh_Z(mf,subSectionMaterialIndices,rootpath,meshBoneCrc32s if rig else [])
    
    if rig:
        for i in range(0, len(globalMeshObjects)):
            for mesh_obj in globalMeshObjects[i]:
                mesh_obj.parent = rig
                modifier = mesh_obj.modifiers.new('Armature Rig', 'ARMATURE')
                modifier.object = rig
                modifier.use_bone_envelopes = False
                modifier.use_vertex_groups = True
            
    # Animation_Z Loading (Remove False in the if and manually set anim name in path to load)
    if False and rig != None:
        maxFrames = 0
        for action in bpy.data.actions:
            bpy.data.actions.remove(action)
        #print(str(bpy.data.actions))
        animFiles = list(pathlib.Path(rootpath).glob('*.Animation_Z'))
        #print(animFiles)
        
        for animFilePath in animFiles:
            #print(rootpath+'\\3658503735.Animation_Z')
            animFile = open(animFilePath, "rb")#open(rootpath+'\\3658503735.Animation_Z', "rb")#
            maxFrames = readAnimation_Z(animFile,rig,maxFrames)
        
    rig.rotation_euler = (math.radians(90),math.radians(0),math.radians(180))

    boneNames.clear()
    bones.clear()
    boneTrans.clear()
    boneRot.clear()
    globalMeshObjects.clear()

def loadAll(path):
    curMeshObjs = 0
    
    for file in os.listdir(globalrootpath):
        
        if file.endswith(".Skin_Z"):
            f = open(os.path.join(globalrootpath, file), "rb")
            print("loading: " + os.path.join(path, file))
            print('-------------------------------------------------------------')
            readSkin(f,os.path.join(path, file))
            
    #for file in os.listdir(globalrootpath):
        
        #if file.endswith(".Mesh_Z"):
           # if (os.path.join(path, file)) in excludedMeshes:
           #     continue
           # f = open(os.path.join(path, file), "rb")
           # print("loading: " + os.path.join(path, file))
           # print('-------------------------------------------------------------')
           # readMesh_Z(f,[])
            
def loadOne(path, link_format="DPC"):
    global linkfmt
    linkfmt = link_format
    if path.endswith(".Skin_Z"):
        f = open(path, "rb")
        print("loading: " + path)
        print('-------------------------------------------------------------')    
        readSkin(f,path)
    elif path.endswith(".Mesh_Z"):
        f = open(path, "rb")
        print("loading: " + path)
        print('-------------------------------------------------------------')    
        readMesh_Z(f,[])

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

#Load specific skin/mesh
def load(self, context, filepath):
    pathOne = filepath
    globalrootpath = os.path.dirname(filepath)
    loadOne(pathOne)
    return True


#FOR MANUAL LOADING (TO TEST ANIMS)
#pathOne = 'D:\\Program Files (x86)\\THQ\\Disney-Pixar\\WALL-E\\WALL-E\\DATAS\\P_WALLE.DPC.out\\objects\\2230209665.Skin_Z'
#loadOne(pathOne)

#Load all skin/mesh files in directory

#pathAll = 'D:\\THQ\\Ratatouille\\RatDbg\\WORLD\\MB_RIVER.DPC.out\\objects'
#globalrootpath = pathAll + '\\'
#loadAll(pathAll)

#def exportMesh()