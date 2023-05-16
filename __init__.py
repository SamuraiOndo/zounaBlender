import bpy
import bpy_extras.io_utils
from bpy.types import Operator, AddonPreferences
from bpy.props import *
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.utils import register_class
from bpy.utils import unregister_class
from typing import Tuple,List

bl_info = {
    "name": "Skin_Z, Anim_Z Import",
    "author": "Violet and Sabe",
    "version": (0, 2, 0),
    "blender": (2, 80, 0),
    "location": "File > Import",
    "description": "Import Skin_Z, Anim_Z",
    "category": "Import-Export"
}
    

class ImportSkinZ(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.skinz"
    bl_label = "Import Skin_Z"
    bl_description = "Import Skin_Z file"
    bl_options = {'PRESET'}

    filename_ext = ".Skin_Z"
    filter_glob: StringProperty(default="*.Skin_Z", options={'HIDDEN'})

    @staticmethod
    def blender_props() -> List[Tuple[str,str,str]]:
        return [
            ("Ratatouille","Ratatouille","Import Ratatouille Skin_Z"),
            ("Wall-E","Wall-E","Import Wall-E Skin_Z"),
        ]

    gameVersion: EnumProperty(items=blender_props(),  name="Imported File Version", default=0)
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        from . import mesh_z
        result = mesh_z.load(
            self, context, **self.as_keywords(ignore=("filter_glob", "files")))
        if result:
            self.report({'INFO'}, 'Skin_Z has been loaded')
            return {'FINISHED'}
        
        else:
            self.report({'ERROR'}, 'Failed to load Skin_Z')
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return True
class ImportAnimZ(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.animz"
    bl_label = "Import Animation_Z"
    bl_description = "Import Animation_Z file"
    bl_options = {'PRESET'}

    filename_ext = ".Anim_Z"
    filter_glob: StringProperty(default="*.Animation_Z", options={'HIDDEN'})

    @staticmethod
    def blender_props() -> List[Tuple[str,str,str]]:
        return [
            ("Ratatouille","Ratatouille","Import Ratatouille Animation_Z"),
            ("Wall-E","Wall-E","Import Wall-E Animation_Z"),
        ]

    #gameVersion: EnumProperty(items=blender_props(),  name="Imported File Version", default=0)
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):
        from . import anim_z
        result = anim_z.load(
            self, context, **self.as_keywords(ignore=("filter_glob", "files")))
        if result:
            self.report({'INFO'}, 'Animation_Z has been loaded')
            return {'FINISHED'}
        
        else:
            self.report({'ERROR'}, 'Failed to load Animation_Z')
            return {'CANCELLED'}

    @classmethod
    def poll(self, context):
        return True

def menu_func_skinz_import(self, context):
    self.layout.operator(ImportSkinZ.bl_idname, text="Skin_Z (.Skin_Z)")
def menu_func_animz_import(self, context):
    self.layout.operator(ImportAnimZ.bl_idname, text="Animation_Z (.Animation_Z)")


def register():
    bpy.utils.register_class(ImportSkinZ)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_skinz_import)
    bpy.utils.register_class(ImportAnimZ)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_animz_import)


def unregister():
    bpy.utils.unregister_class(ImportSkinZ)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_skinz_import)
    bpy.utils.unregister_class(ImportAnimZ)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_animz_import)


if __name__ == "__main__":
    register()
