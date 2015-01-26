import bpy
from mathutils import Matrix

def convert_lamp(obj):
    #lamp = bpy.data.lamps[obj.name]
    lamp = bpy.data.objects[obj.name].data
    data_dict = {}
    data_dict['lamp_type'] = lamp.type
    data_dict['lamp_color'] = list(lamp.color)
    data_dict['energy'] = lamp.energy
    if lamp.type in ['SUN', 'SPOT']:
        if lamp.use_shadow:
            data_dict['shadow_caster'] = lamp.use_shadow
            data_dict['buffer_size'] = lamp.shadow_buffer_size
            data_dict['near'] = lamp.shadow_buffer_clip_start
            data_dict['far'] = lamp.shadow_buffer_clip_end
            if lamp.type == 'SUN':
                data_dict['film_size'] = lamp.shadow_frustum_size
        if lamp.type == 'SPOT':
            data_dict['fov'] = lamp.spot_size
    if lamp.type in ('POINT', 'HEMI', 'SPOT'):
        data_dict['lamp_distance'] = lamp.distance
    return data_dict

def convert_speaker(obj):
    #speaker = bpy.data.speakers[obj.name]
    speaker = bpy.data.objects[obj.name].data
    data_dict = {}
    data_dict['volume'] = speaker.volume
    data_dict['sound'] = speaker.sound.name
    return data_dict

def convert_mesh(obj):
    data_dict = {}
    return data_dict
    
def convert_camera(obj):
    data_dict = {}
    #camera = bpy.data.cameras[obj.name]
    camera = bpy.data.objects[obj.name].data
    data_dict['camera_type'] = camera.type
    data_dict['near'] = camera.clip_start
    data_dict['far'] = camera.clip_end
    if camera.type == 'PERSP':
        data_dict['fov'] = camera.angle
    elif camera.type == 'ORTHO':
        data_dict['scale'] = camera.ortho_scale
    return data_dict


obj_proc = {'LAMP':convert_lamp,
            'SPEAKER':convert_speaker,
            'MESH': convert_mesh,
            'CAMERA': convert_camera
            }
