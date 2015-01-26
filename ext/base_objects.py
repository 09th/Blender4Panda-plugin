from .defaults import obj_proc
import imp, sys, os
imp.reload(sys.modules['.'.join(__name__.split('.')[:-1]) + '.defaults'])

order = 1
target = 'object'

def invoke(data_dict, obj, context, fname, flags=None):
    if flags:
        if 'SINGLE_GEOM_MODE' in flags and obj.type == 'MESH':
            return #data_dict
        if 'AUTO_EXPORT_EGG' in flags and obj.type == 'MESH':
            path = os.path.join(os.path.split(fname)[0], 'res', obj.name + '.egg')
            p3d_egg_export(path, {}, 0, 0, 0, 1, 'tex', 'BLENDER', 'RAW', {}, 0, 1, 0, [obj.name,])
    mat = []
    for y in obj.matrix_world.col:
        for x in y[:]:
            mat.append(x)
    data_dict['name'] = obj.name
    data_dict['mat'] = mat
    if obj.parent:
        data_dict['parent'] = obj.parent.name
    if 'asset' in obj:
        data_dict['type'] = 'ASSET'
        data_dict['ref'] = obj['asset_name']
    elif not 'asset_child' in obj:
        data_dict['type'] = obj.type
        if obj.type in obj_proc.keys():
            data_dict.update(obj_proc[obj.type](obj))
        
    #return data_dict
