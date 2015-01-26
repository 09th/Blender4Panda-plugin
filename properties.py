from bpy.types import PropertyGroup
from bpy.props import FloatProperty, IntProperty, BoolProperty, CollectionProperty, StringProperty
import math, bpy

'''
class SE4P3DActionItem(PropertyGroup):
    name = StringProperty(default="")
    function = StringProperty(default="")
    timer = FloatProperty(description="Repeat time for the task (0 - every frame)",default = 0.0)
    action_type = StringProperty(default="EVENT")
'''
#class SE4P3DTaskItem(SE4P3DActionItem):
#    timer = FloatProperty(description="Repeat time for the task (0 - every frame)",default = 0.0)

class SE4P3DAssetItem(PropertyGroup):
    
    def on_update_name(self, context):
        if 'old_name' not in self:
            self['old_name'] = ''
        #print(self['old_name'], self.name)
        for obj in bpy.data.objects:
            if 'asset_name' in obj and obj['asset_name'] == self['old_name']:
                obj['asset_name'] = self.name
        self['old_name'] = self.name

    
    name = StringProperty(default="", update=on_update_name)
    ref_object_name = StringProperty(default="")
    code_class = StringProperty(default="_static_")
    use_as_canvas =  BoolProperty(description = "Asset can be used as a canvas.", default=False)
    z_offset = FloatProperty(description="Set the Z offset the Assets gets placed from the underground.",default = 0.0,min=-30.0, max=30.0)
    distance = FloatProperty(description="Set the asset distance for each Paint Stroke.",default = 1.0,min=0.0, max=30.0)
    surface_affect = FloatProperty(description="Defines how much the asset is aligned to the surface normal.",default = 1.0,min=0.0, max=1.0,subtype="FACTOR")
    stroke_orient =  BoolProperty(description = "Asset is directing to the stroke direction.",default=False)
    
    rand_rot_x = FloatProperty(description="Set the random rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    rand_rot_y = FloatProperty(description="Set the random rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    rand_rot_z = FloatProperty(description="Set the random rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    
    start_rot_z = FloatProperty(description="Set the start rotation of a placed asset.",default=0,subtype='ANGLE',min=0.0,max=math.radians(360))
    
    rand_scale_x = FloatProperty(description="Set the random scale of a placed asset.",default=1.0,min=0.0)
    rand_scale_y = FloatProperty(description="Set the random scale of a placed asset.",default=1.0,min=0.0)
    rand_scale_z = FloatProperty(description="Set the random scale of a placed asset.",default=1.0,min=0.0)
    
    constraint_rand_scale = BoolProperty(description = "Asset is directing to the stroke direction.",default=True)
    
    make_single_user = BoolProperty(description="Objects gets added as single User Obejcts with its own Mesh Data.",default=False)
    
    scale = FloatProperty(description="Set the scale of your asset",default=1.0,min=0.0)
    type = StringProperty()


class SE4P3D(PropertyGroup):
    
    def on_AL_idx_update(self,context):
        if 'old_idx' not in self:
            self['old_idx'] = 0
        if self['old_idx'] != self.assets_list_index and context.window_manager.se4p3d_assets_placing_enabled:
            old_asset = self.assets_list[self['old_idx']]
            #asset = self.assets_list[self.assets_list_index]
            if old_asset.ref_object_name in context.scene.objects:
                context.scene.objects.unlink(bpy.data.objects[old_asset.ref_object_name])
        self['old_idx'] = self.assets_list_index
        
    assets_list = CollectionProperty(type=SE4P3DAssetItem)
    assets_list_index = IntProperty(update=on_AL_idx_update)

