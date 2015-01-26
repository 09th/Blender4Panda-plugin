import bpy
from .defaults import obj_proc

order = 1
target = 'asset'

def invoke(data_dict, asset, context, fname, flags=None):
    data_dict['name'] = asset.name
    data_dict['type'] = asset.type
    data_dict['class'] = asset.code_class
    if asset.type == 'OBJECT':
        data_dict['data'] = asset.ref_object_name
    obj = bpy.data.objects[asset.ref_object_name]
    if obj.type in obj_proc.keys():
        data_dict.update(obj_proc[obj.type](obj))
    return data_dict
