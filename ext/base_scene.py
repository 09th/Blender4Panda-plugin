''' Part of B4P editor/exporter
'''

import bpy, os

order = 1
target = 'scene'

def invoke(data_dict, context, fname, flags=None):
    data_dict['comment'] = 'Export from Blender ' + bpy.app.version_string
    data_dict['b_version'] = bpy.app.version
    
    if context.scene.world:
        data_dict['ambient'] = list(context.scene.world.ambient_color)
    else:
        data_dict['ambient'] = (0,0,0)
    return data_dict
    
    if flag and 'SINGLE_GEOM_MODE' in flags:
        fname = os.path.split(fname)[-1]
        data_dict['scene_mesh'] = os.path.splitext(fname)[0]
