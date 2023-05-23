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

rootpath = ""
excludedMeshes = []
bones = []
boneNames = []
meshBoneCrc32s = []
boneTrans = []
boneRot = []
boneTrs = []
globalMeshObjects = []



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
    bs.seek(36, 1)
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
    bs = binary_reader.BinaryReader(open(rootpath + "\\" + (str(skelCrc32) + ".Skel_Z"), "rb").read())

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
    reader.set_endian(True)
    datasize = reader.read_uint32()
    linksize = reader.read_uint32()
    decompressedsize = reader.read_uint32()
    compressedsize = reader.read_uint32()
    classcrc32 = reader.read_uint32()
    namecrc32 = reader.read_uint32()
    name = str(namecrc32)
    linkcrc32 = reader.read_uint32()
    linkCount = reader.read_uint32()
    print("linkCount" + str(linkCount))
    reader.seek(linkCount*4, whence=1)
    reader.seek(126, whence=1)
    matCrc32Count = reader.read_uint32()
    print("matcount" + str(matCrc32Count))
    matCrc32List = []
    matList = []
    addMatIndices = False
    
    if not subsectionMatIndices:
        addMatIndices = True
        
    for i in range(matCrc32Count):
        matCrc32List.append(str(reader.read_uint32()))
        if addMatIndices: subsectionMatIndices.append(i)
    rootpath += "\\"
    for h in matCrc32List:
        try:
            mat = bpy.data.materials.new(name=str(h))
            mat.use_nodes = True
            material_z = (rootpath + str(h) + ".Material_Z")
            fe = open(material_z, "rb")
            reader2 = binary_reader.BinaryReader(fe.read())
            reader2.seek(0x20)
            texturename = reader2.read_uint32()
            strtexturename = str(texturename)
                
            #open bitmap_z's and get dds from those automatically

            bitmap_z = (rootpath + strtexturename + ".Bitmap_Z")
            dds = (rootpath + strtexturename + ".dds")
            bm = open(bitmap_z, "rb")
            tex = open(dds, "wb")
            reader3 = binary_reader.BinaryReader(bm.read())
            reader3.set_endian(True)
            reader3.seek(0x28)
            size3 = reader3.read_uint32()
            reader3.seek(0x34)
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
            mat.blend_method = 'BLEND'
            mat.show_transparent_back = False
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

    vertices = []
    uvs = []
    normals = []

    #read short vertices and basically ignore them
    vertexCount = reader.read_uint32()
    for i in range(vertexCount * 3):
        vertices.append(reader.read_int16())

    uvShortCount = reader.read_uint32()
    for i in range(uvShortCount):
        uvs.append(reader.read_int16())
    
    normalByteCount = reader.read_uint32()
    for i in range(normalByteCount):
        normals.append(reader.read_int8())
    
    meshObjects = []
    blender_norms = []
    blender_uvs = []

    displayListCount = reader.read_uint32()
    for i in range(displayListCount):
        blender_verts = []
        
        bm = bmesh.new()
        uv_layer = bm.loops.layers.uv.new()
        bytes = reader.read_uint32()
        print(str(bytes))
        reader.read_uint32()
        format = reader.read_uint8()
        vertexRefCount = reader.read_uint16()
        counterForFace = 0
        for j in range(vertexRefCount):
            posIndex = reader.read_uint16()
            normalIndex = reader.read_uint16()
            uvIndex = reader.read_uint16()
            if (format & 1):
                reader.read_uint16()

            posX = vertices[posIndex*3]
            posY = vertices[posIndex*3+1]
            posZ = vertices[posIndex*3+2]

            normalX = normals[normalIndex*3]
            normalY = normals[normalIndex*3+1]
            normalZ = normals[normalIndex*3+2]

            uvX = uvs[uvIndex*2]
            uvY = uvs[uvIndex*2+1]

            vert = bm.verts.new((posX/4095,posY/4095,posZ/4095))
            blender_verts.append(vert)
            blender_uvs.append((uvX/1023,uvY/1023))
            blender_norms.append([normalX/63,normalY/63,normalZ/63])

            try:
                if (j >= 2):
                    if (j % 2 != 0):
                        face = bm.faces.new([blender_verts[j-2], blender_verts[j-1], blender_verts[j]])
                    else:
                        face = bm.faces.new([blender_verts[j-2], blender_verts[j], blender_verts[j-1]])
            except:
                continue

        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        def uv_to_blender(uv):
            return (uv[0], 1.0 - uv[1])
        for face in bm.faces:
            for loop in face.loops:
                loop[uv_layer].uv = uv_to_blender(blender_uvs[loop.vert.index])

        newmesh = bpy.data.meshes.new('newmesh')
        bm.to_mesh(newmesh)
        newmesh.create_normals_split()
        newmesh.normals_split_custom_set_from_vertices(blender_norms)

        newobject = bpy.data.objects.new(("Mesh_"+name + "_DispList_" + str(i)), newmesh)
        meshObjects.append(newobject)
        bpy.context.view_layer.active_layer_collection.collection.objects.link(newobject)
        newmesh.auto_smooth_angle = 0
        newmesh.use_auto_smooth = True
        newobject.data.materials.append(bpy.data.materials.get(matCrc32List[subsectionMatIndices[i]]))

        blender_norms.clear()
        blender_uvs.clear()

        stride = 6
        if (format & 1):
            stride = 8
        reader.seek(bytes - 3 - vertexRefCount*stride, whence=1)

    globalMeshObjects.append(meshObjects)


def readSkin(f,path):
    #print("new skin, globalMeshes: " + str(globalMeshObjects))
    rootpath = os.path.dirname(path)
    subSectionMaterialIndices = []
    reader = binary_reader.BinaryReader(f.read())
    reader.set_endian(True)
    datasize = reader.read_uint32()
    linksize = reader.read_uint32()
    decompressedsize = reader.read_uint32()
    compressedsize = reader.read_uint32()
    classcrc32 = reader.read_uint32()
    namecrc32 = reader.read_uint32()
    linkCrc32 = reader.read_uint32()
    linkCount = reader.read_uint32()
    reader.seek(4*linkCount,1)
    skelCrc32 = reader.read_uint32()
    if (skelCrc32 != 0):
        rig = execute(skelCrc32,namecrc32,rootpath)
    else:
        ShowMessageBox("Unsupported Skin_Z", "Alert", 'ERROR')
        #print("No skel skin (??) : " + str(namecrc32))
        return

    #print("skel_z is totes: ", skelCrc32)
    reader.seek(16,1)
    reader.seek(74,1)
    meshCrc32Count = reader.read_uint32()
    meshCrc32 = []
    for i in range(meshCrc32Count):
        curMesh = reader.read_uint32();
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
            curMaterial = reader.read_uint32()
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
        meshName = ((rootpath + "\\" + str(meshCrc32[i])) + ".Mesh_Z")
        mf = open(meshName, "rb")
        readMesh_Z(mf,subSectionMaterialIndices,rootpath,meshBoneCrc32s)
        
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
        #animFiles = list(pathlib.Path(rootpath).glob('*.Animation_Z'))
        #print(animFiles)
        
        #for animFilePath in animFiles:
        animFile = open(rootpath+'\\378200382.Animation_Z', "rb")#open(animFilePath, "rb")
        maxFrames = readAnimation_Z(animFile,rig,maxFrames)
        
    rig.rotation_euler = (math.radians(90),math.radians(0),math.radians(180))

    boneNames.clear()
    bones.clear()
    boneTrans.clear()
    boneRot.clear()
    globalMeshObjects.clear()

def loadAll(path):
    curMeshObjs = 0
    
    for file in os.listdir(rootpath):
        
        if file.endswith(".Skin_Z"):
            f = open(os.path.join(rootpath, file), "rb")
            print("loading: " + os.path.join(path, file))
            print('-------------------------------------------------------------')
            readSkin(f,path)
            
    for file in os.listdir(rootpath):
        
        if file.endswith(".Mesh_Z"):
            if (os.path.join(path, file)) in excludedMeshes:
                continue
            f = open(os.path.join(path, file), "rb")
            print("loading: " + os.path.join(path, file))
            print('-------------------------------------------------------------')
            readMesh_Z(f,[],rootpath)
            
def loadOne(path):
    
    if path.endswith(".Skin_Z"):
        f = open(path, "rb")
        print("loading: " + path)
        print('-------------------------------------------------------------')    
        readSkin(f,path)
    elif path.endswith(".Mesh_Z"):
        f = open(path, "rb")
        print("loading: " + path)
        print('-------------------------------------------------------------')    
        readMesh_Z(f,[],rootpath)

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

#Load specific skin/mesh
def load(self, context, filepath, gameVersion):
    pathOne = filepath
    rootpath = os.path.dirname(filepath)
    #if(gameVersion == 'Wall-E'):
    #    from . import mesh_z_wall_e as mesh_z
    #    mesh_z.loadOne

    loadOne(pathOne)
    return True


#FOR MANUAL LOADING (TO TEST ANIMS)
#pathOne = 'D:\\THQ\\Ratatouille\\RatDbg\\DATAS\\P_REMY.DPC.out\\objects\\205305043_NormalSkin.Skin_Z'
#loadOne(pathOne)

#Load all skin/mesh files in directory

#pathAll = 'D:\\THQ\\Ratatouille\\RatDbg\\WORLD\\CT.DPC.out\\objects'
#rootpath = pathAll + '\\'
#loadAll(pathAll)

#def exportMesh()