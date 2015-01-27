''' Part of B4P editor/exporter
'''

import bpy, os

order = 1
target = 'scene'

def invoke(all_data, target_data, context, fname, flags=None):
    target_data['paths'] = {'sounds':'./res',
                         'meshes':'./res',
                         'images':'./res',
                         'materials':'./res'
                          }
    target_data['comment'] = 'Export from Blender ' + bpy.app.version_string
    target_data['b_version'] = bpy.app.version
    
    if context.scene.world:
        target_data['ambient'] = list(context.scene.world.ambient_color)
    else:
        target_data['ambient'] = (0,0,0)
    
    if flags and 'SINGLE_GEOM_MODE' in flags:
        sfname = os.path.split(fname)[-1]
        sfname = os.path.splitext(sfname)[0]
        #sfname = os.path.join(target_data['paths']['meshes'], 
        #                      sfname)
        target_data['scene_mesh'] = sfname
        if 'AUTO_EXPORT_EGG' in flags:
            objects = [obj.name for obj in context.scene.objects if obj.type=='MESH']
            p3d_egg_export(os.path.join(os.path.dirname(fname), sfname+'.egg'), 
                           {}, 0, 0, 0, 1, 'tex', 'BLENDER', 'RAW', {}, 0, 1, 0, objects)
    
    return target_data
