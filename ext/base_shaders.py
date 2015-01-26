import bpy, gpu, os, re, sys, shutil, bpy_extras

order = 1
target = 'material'


#import bpy, os, sys, shutil
#import bpy_extras

def convertFileNameToPanda(filename):
  """ (Get from Chicken) Converts Blender filenames to Panda 3D filenames.
  """
  path =  filename.replace('//', './').replace('\\', '/')
  if os.name == 'nt' and path.find(':') != -1:
    path = '/'+ path[0].lower() + path[2:]
  return path

def save_image(img, file_path, text_path):
    if img.filepath:
        oldpath = bpy.path.abspath(img.filepath)
        old_dir, old_f = os.path.split(convertFileNameToPanda(oldpath))       
        f_names = [s.lower() for s in old_f.split('.')]
        if not f_names[-1] in ('jpg', 'png', 'tga', 'tiff', 'dds', 'bmp') and img.is_dirty:
            old_f += ('.' + bpy.context.scene.render.image_settings.file_format.lower())
    else:
        oldpath = ''
        old_dir = ''
        old_f = img.name + '.' + bpy.context.scene.render.image_settings.file_format.lower()
    rel_path = os.path.join(text_path, old_f)
    if os.name == 'nt':
        rel_path = rel_path.replace(r"\\",r"/").replace('\\', '/')
    new_dir, eg_f = os.path.split(file_path)
    new_dir = os.path.abspath(os.path.join(new_dir, text_path))
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    if img.is_dirty or bool(img.packed_file):
        try:
            bpy.context.scene.render.image_settings.color_mode = 'RGBA'
        except:
            bpy.context.scene.render.image_settings.color_mode = 'RGB'
        r_path = os.path.abspath(os.path.join(new_dir, old_f))
        ext = bpy.context.scene.render.image_settings.file_format.lower()
        r_path = os.path.splitext(r_path)[0] + '.' + ext
        rel_path = os.path.splitext(rel_path)[0] + '.' + ext
        img.save_render(r_path)
        print('RENDER IMAGE to %s; rel path: %s' % (r_path, rel_path))
    else:
        newf = os.path.join(new_dir, old_f)
        if oldpath != newf:
            bpy_extras.io_utils.path_reference_copy(((oldpath.replace(r"\\", r"/"), newf),), report = print)
            print('COPY IMAGE %s to %s; rel path %s' % (oldpath, newf, rel_path))
    return rel_path


def replace_sampler_for_textures(material, sha):
    for unf in sha['uniforms']:
        if unf['type'] ==  gpu.GPU_DYNAMIC_SAMPLER_2DIMAGE:
            if 'image' in unf:
                i = 0
                for slot in material.texture_slots:
                    if slot and slot.texture.image and slot.texture.image.source == 'FILE':
                        #if os.path.samefile(slot.texture.image.filepath, unf['image']):
                        if slot.texture.image == unf['image']:
                            new_unf_name = 'p3d_Texture' + str(i)
                            sha['fragment'] = sha['fragment'].replace(unf['varname'], new_unf_name)
                            unf['varname'] = new_unf_name
                            unf['type'] = 'p3d_texture'
                            break
                        i += 1



def replace_attributes(material, sha):
    for att in sha['attributes']:
        if att['type'] == gpu.CD_MTFACE:
            idx = 0
            if type(att['name']) == int:
                idx = att['name']
            new_att_name = 'p3d_MultiTexCoord' + str(idx)
        if att['type'] == gpu.CD_TANGENT:
            new_att_name = 'p3d_Tangent'
        if att['type'] == gpu.CD_MCOL:
            new_att_name = 'p3d_Color'
        sha['fragment'] = sha['fragment'].replace(att['varname'], new_att_name)
        sha['vertex'] = sha['vertex'].replace(att['varname'], new_att_name)



def find_and_correct_spot_light_uniforms(material, sha):
    for unfs in re.findall('lamp_visibility_spot\((unf[0-9]+), (unf[0-9]+)', sha['fragment']):
        circle, blend = unfs
        # temporary to test, empiric values
        for i, unf in enumerate(sha['uniforms']):
            if unf['varname'] == circle:
                #sha['uniforms'][i]['value'] = 0.97 #30
                sha['uniforms'][i]['value'] = 0.8 #75
                sha['uniforms'][i]['value'] = 0.75 #90
            if unf['varname'] == blend:
                #sha['uniforms'][i]['value'] = 0.015 #(0.2:0.0)
                sha['uniforms'][i]['value'] = 0.03

        

def invoke(data_dict, material, context, fname, flags=None):
    # TODO: replace uniforms for object<->world matrices
    # replace shared uniforms (lights, camera)
    dirname = os.path.dirname(fname)
    sha = gpu.export_shader(context.scene, material)
    replace_sampler_for_textures(material, sha)
    replace_attributes(material, sha)
    find_and_correct_spot_light_uniforms(material, sha)
    f = open(os.path.join(dirname, material.name + '.vert'), 'w')
    f.write(sha['vertex'])
    f.close()
    f = open(os.path.join(dirname, material.name + '.frag'), 'w')
    f.write(sha['fragment'])
    f.close()
    data_dict['vert'] = material.name + '.vert'
    data_dict['frag'] = material.name + '.frag'
    data_dict['name'] = material.name
    uniforms = []
    for unf in sha['uniforms']:
        uniform = {}
        for key, val in tuple(unf.items()):
            if key == 'lamp':
                val = val.name
            elif key == 'image':
                saved_img = save_image(val, fname, '')
                val = saved_img
                #val = os.path.split(val.filepath)[1]
            elif key == 'texpixels':
                #val = ''
                fname = material.name + '-' + unf['varname'] + '.dat'
                f = open(os.path.join(dirname, fname), 'wb')
                f.write(val)
                f.close()
                val = fname
            elif key == 'type':
                if val == 16: 
                    # Try to find accordance between unifrom with 
                    # type 16 (light distance) and light
                    uniform['lamp'] = bpy.data.lamps[0].name
                    '''
                    lamps = [l for l in bpy.data.lamps if l.type in ('POINT', 'HEMI')]
                    unfs = [u for u in sha['uniforms'] if u['type']==16]
                    idx = unfs.index(unf)
                    if len(unfs) == len(lamps):
                        uniform['lamp'] = lamps[idx].name
                    else:
                        uniform['lamp'] = lamps[0].name
                        print('WARNING: can\'t find Lamp for uniform', unf)
                    '''
            uniform[key] = val
        uniforms.append(uniform)
    data_dict['uniforms'] = uniforms
