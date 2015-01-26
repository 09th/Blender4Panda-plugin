bl_info = {
    "name": "Scene editor for Panda3D",
    "author": "Andrey (09th) Arbuzov. Based on AssetScetcher by Andreas and Matthias Esau",
    "version": (0, 1),
    "blender": (2, 7, 0),
    "location": "View 3D > Tools > Scene editor for Panda3D",
    "description": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Game Engine"}

#TODO:
#  work with complex assets. For example contains several meshes and lights and sounds e.t.c.
#  load asset settins with library
#  work with groups
#  enable/disable extensions


import bpy, sys
from bpy.props import IntProperty, CollectionProperty, PointerProperty
#from .AssetSketcher import SketchAssetsList, UI_UL_sketcher_list
from .operators import *
from .properties import *
from .gui import *
from . import ext

def register():
    bpy.utils.register_module(__name__)
    #bpy.types.Scene.se4p3d_assets_list = CollectionProperty(type=SE4P3DAssetItem)
    #bpy.types.Scene.se4p3d_assets_list_index = IntProperty()
    bpy.types.Scene.se4p3d = PointerProperty(type=SE4P3D)
    
def unregister():
    bpy.utils.unregister_module(__name__)

def reload_func():
    print('reload')
    #unregister()
    imp.reload(sys.modules[__name__ + '.operators'])
    imp.reload(sys.modules[__name__ + '.properties'])
    imp.reload(sys.modules[__name__ + '.gui'])
    imp.reload(sys.modules[__name__ + '.utils'])
    imp.reload(sys.modules[__name__ + '.ext'])
    register()

if "bpy" in locals():
    reload_func()

class SE4P3DReloadModules(bpy.types.Operator):
    bl_idname = "se4p3d.reload_modules"
    bl_label = "Reload modules"
    
    def execute(self, context):
        reload_func()
        return {"FINISHED"}

