import bpy
from .defaults import obj_proc

order = 1
target = 'asset'

def invoke(all_data, target_data, asset, context, fname, flags=None):
    target_data['name'] = asset.name
    target_data['type'] = asset.type
    target_data['class'] = asset.code_class
    if asset.type == 'OBJECT':
        target_data['data'] = asset.ref_object_name
    obj = bpy.data.objects[asset.ref_object_name]
    if obj.type in obj_proc.keys():
        target_data.update(obj_proc[obj.type](obj))
    return target_data
