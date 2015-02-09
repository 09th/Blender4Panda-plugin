from .defaults import obj_proc
import imp, sys, os
imp.reload(sys.modules['.'.join(__name__.split('.')[:-1]) + '.defaults'])

order = 1
target = 'object'

def invoke(all_data, target_data, obj, context, fname, flags=None):
    if flags:
        #if 'SINGLE_GEOM_MODE' in flags and obj.type == 'MESH':
        #    return #target_data
        if not 'SINGLE_GEOM_MODE' in flags and 'AUTO_EXPORT_EGG' in flags and obj.type == 'MESH':
            path = os.path.join(os.path.split(fname)[0], 'res', obj.name + '.egg')
            p3d_egg_export(path, {}, 0, 0, 0, 1, 'tex', 'BLENDER', 'RAW', {}, 0, 1, 0, [obj.name,])
    mat = []
    for y in obj.matrix_world.col:
        for x in y[:]:
            mat.append(x)
    target_data['name'] = obj.name
    target_data['mat'] = mat
    if obj.parent:
        target_data['parent'] = obj.parent.name
    if 'asset' in obj:
        target_data['type'] = 'ASSET'
        target_data['ref'] = obj['asset_name']
    elif not 'asset_child' in obj:
        target_data['type'] = obj.type
        if obj.type in obj_proc.keys():
            target_data.update(obj_proc[obj.type](obj))
        
    #return target_data
