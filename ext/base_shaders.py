import bpy, gpu, os, re, sys, shutil, bpy_extras, math

order = 1
target = 'material'

SHARED_TYPES = {gpu.GPU_DYNAMIC_LAMP_DYNVEC:'vec',
                gpu.GPU_DYNAMIC_LAMP_DYNCO:'co',
                gpu.GPU_DYNAMIC_LAMP_DYNIMAT:'imat',
                gpu.GPU_DYNAMIC_LAMP_DYNPERSMAT:'persmat',
                gpu.GPU_DYNAMIC_LAMP_DYNENERGY:'energy',
                gpu.GPU_DYNAMIC_LAMP_DYNCOL:'col',
                gpu.GPU_DYNAMIC_SAMPLER_2DSHADOW:'shadow_samp',
                'distance':'distance',
                'spot_cutoff': 'cutoff',
                'spot_blend': 'blend'
               }

#import bpy, os, sys, shutil
#import bpy_extras

def safe_var_name(name):
    return re.sub('[^a-z0-9_]+', '_', name, flags=re.IGNORECASE)

def light_name_to_obj_name(l_name):
    # Object and appropriate light can have different names,
    # we find object name by light name
    for obj in bpy.data.objects:
        if obj.type == 'LAMP':
            if obj.data.name == l_name:
                return obj.name

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
                            unf['type'] = '_ignore_'
                            break
                        i += 1

def find_idx_for_texcoord(name):
    # Not sure that this index calculation would be work as expected
    if name == 0:
        return 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for i,uv in enumerate(obj.data.uv_layers):
                if uv.name == name:
                    return i

def replace_attributes(material, sha):
    new_atts = []
    for att in sha['attributes']:
        if att['type'] == gpu.CD_MTFACE:
            #idx = att['number']-1
            new_att_name = 'p3d_MultiTexCoord' + str(find_idx_for_texcoord(att['name']))
        elif att['type'] == gpu.CD_TANGENT:
            new_att_name = 'p3d_Tangent'
        elif att['type'] == gpu.CD_MCOL:
            new_att_name = 'p3d_Color'
        elif att['type'] == gpu.CD_ORCO:
            new_att_name = 'p3d_Vertex' # Not sure that it's what wee need, but I have no another ideas
        else:
            raise Exception('Unknown attribute %s in %s material' % (att['name'], material.name))
        if new_att_name in new_atts:
            print('WARNING: Duplicated attribute', new_att_name)
            #print('(attribute vec[0-9] '+att['varname']+';)')
            sha['vertex'] = re.sub('(attribute vec[0-9] '+att['varname']+';)','//\g<1>', sha['vertex'])

        sha['fragment'] = sha['fragment'].replace(att['varname'], new_att_name)
        sha['vertex'] = sha['vertex'].replace(att['varname'], new_att_name)
        new_atts.append(new_att_name)
            

def replace_common_uniforms(sha):
    #p3d_ModelViewMatrixInverse
    for unf in sha['uniforms']:
        new_unf_name = None
        if unf['type'] == gpu.GPU_DYNAMIC_OBJECT_VIEWMAT:
            new_unf_name = 'p3d_ModelViewMatrix'
        if unf['type'] == gpu.GPU_DYNAMIC_OBJECT_VIEWIMAT:
            new_unf_name = 'p3d_ModelViewMatrixInverse'
        if unf['type'] == gpu.GPU_DYNAMIC_OBJECT_MAT:
            new_unf_name = 'p3d_ModelMatrix'
        if unf['type'] == gpu.GPU_DYNAMIC_OBJECT_IMAT:
            new_unf_name = 'p3d_ModelMatrixInverse'

        if new_unf_name:
            sha['vertex'] = sha['vertex'].replace(unf['varname'], new_unf_name)
            sha['fragment'] = sha['fragment'].replace(unf['varname'], new_unf_name)
            unf['varname'] = new_unf_name
            unf['type'] = '_ignore_'

def find_and_correct_spot_light_uniforms(material, sha):
    # find links to needed lamps
    l_links = {}
    for unfs in re.findall('lamp_visibility_spot_circle\(([a-zA-Z0-9_]+), tmp[0-9]+, (tmp[0-9]+)', sha['fragment']):
        #print('+1+', unfs)
        link_unf,tmp = unfs
        for unf in sha['uniforms']:
            if unf['varname'] == link_unf:
                l_links[tmp] = unf['lamp']
                break
    # find uniforms
    for unfs in re.findall('lamp_visibility_spot\((unf[0-9]+), (unf[0-9]+), (tmp[0-9]+)', sha['fragment']):
        #print('+2+', unfs)
        cutoff, blend, tmp = unfs
        for i, unf in enumerate(sha['uniforms']):
            if unf['varname'] == cutoff:
                sha['uniforms'][i]['value'] = math.cos(l_links[tmp].data.spot_size*0.5)
                #sha['uniforms'][i]['lamp'] = light_name_to_obj_name(l_links[tmp].name)
                sha['uniforms'][i]['lamp'] = l_links[tmp]
                sha['uniforms'][i]['type'] = 'spot_cutoff'
            if unf['varname'] == blend:
                sha['uniforms'][i]['value'] = (1.0-math.cos(l_links[tmp].data.spot_size*0.5))*l_links[tmp].data.spot_blend
                #sha['uniforms'][i]['lamp'] = light_name_to_obj_name(l_links[tmp].name)
                sha['uniforms'][i]['lamp'] = l_links[tmp]
                sha['uniforms'][i]['type'] = 'spot_blend'

def find_material_with_same_unf_name(all_data, unf):
    for mname, material in all_data['materials'].items():
        for cmp_unf in material['uniforms']:
            if cmp_unf['varname'] == unf['varname']:
                return mname

def add_lamp_name_for_unf_type16(sha):
    '''void lamp_falloff_invlinear(float lampdist, float dist, out float visifac)
       void lamp_falloff_invsquare(float lampdist, float dist, out float visifac)
       void lamp_falloff_sliders(float lampdist, float ld1, float ld2, float dist, out float visifac)
       void lamp_falloff_curve(float lampdist, sampler2D curvemap, float dist, out float visifac)
       void lamp_visibility_sphere(float lampdist, float dist, float visifac, out float outvisifac)
    '''
    '''void lamp_visibility_sun_hemi(vec3 lampvec, out vec3 lv, out float dist, out float visifac)
       void lamp_visibility_other(vec3 co, vec3 lampco, out vec3 lv, out float dist, out float visifac)
    '''
    l_links = {}
    for unfs in re.findall('lamp_visibility_other\(varposition, ([a-zA-Z0-9_]+), tmp[0-9]+, (tmp[0-9]+)', sha['fragment']):
        #print('+1+', unfs)
        link_unf,tmp = unfs
        for unf in sha['uniforms']:
            if unf['varname'] == link_unf:
                l_links[tmp] = unf['lamp']
                break
    for re_str in ('lamp_falloff_invsquare\((unf[0-9]+), (tmp[0-9]+)',
                   'lamp_falloff_invlinear\((unf[0-9]+), (tmp[0-9]+)'
                   ):
        for unfs in re.findall(re_str, sha['fragment']):
            #print('+2+', unfs)
            unf16, dist_tmp = unfs
            if dist_tmp in l_links.keys():
                for i, unf in enumerate(sha['uniforms']):
                    if unf['varname'] == unf16:
                        sha['uniforms'][i]['lamp'] = l_links[dist_tmp]
                        sha['uniforms'][i]['type'] = 'distance'


def solve_duplicate_names(sha, name, cnt=0):
    for i, unf in enumerate(sha['uniforms']):
        if unf['varname'] == name:
            return solve_duplicate_names(sha, name+'_'+str(cnt), cnt+1)
    return name

def replace_names_for_shared_uniforms(sha):
    for i, unf in enumerate(sha['uniforms']):
        if unf['type'] in SHARED_TYPES.keys():
            if 'lamp' in unf:
                new_varname = safe_var_name(unf['lamp'].name + '_'\
                              + SHARED_TYPES[unf['type']]\
                              + '_' + str(unf['datatype']))
                new_varname = solve_duplicate_names(sha, new_varname)
                #sha['fragment'] = sha['fragment'].replace(unf['varname'], new_varname)
                sha['fragment'] = re.sub(unf['varname']+'([^a-zA-Z0-9_]+)', new_varname+'\g<1>', sha['fragment'])
                sha['uniforms'][i]['varname'] = new_varname
            else:
                print(unf, 'WARNING: hasn\'t lamp attribute')

def invoke(all_data, target_data, material, context, fname, flags=None):
    dirname = os.path.dirname(fname)
    if 'paths' in all_data['scene']:
        dirname = os.path.join(dirname, all_data['scene']['paths']['materials'])
    sha = gpu.export_shader(context.scene, material)
    add_lamp_name_for_unf_type16(sha)
    find_and_correct_spot_light_uniforms(material, sha)
    replace_names_for_shared_uniforms(sha)
    replace_common_uniforms(sha)
    replace_sampler_for_textures(material, sha)
    replace_attributes(material, sha)
    f = open(os.path.join(dirname, material.name + '.vert'), 'w')
    f.write(sha['vertex'])
    f.close()
    f = open(os.path.join(dirname, material.name + '.frag'), 'w')
    f.write(sha['fragment'])
    f.close()
    target_data['vert'] = material.name + '.vert'
    target_data['frag'] = material.name + '.frag'
    target_data['name'] = material.name
    uniforms = []
    for unf in sha['uniforms']:
        uniform = {}
        for key, val in tuple(unf.items()):
            if key == 'lamp':
                val = val.name
            elif key == 'image':
                if unf['type'] != 'p3d_texture':
                    saved_img = save_image(val, fname, all_data['scene']['paths']['images'])
                    #val = saved_img
                    val = os.path.split(saved_img)[1]
                else:
                    val = ''
                #val = os.path.split(val.filepath)[1]
            elif key == 'texpixels':
                #val = ''
                fname = material.name + '-' + unf['varname'] + '.dat'
                f = open(os.path.join(dirname, fname), 'wb')
                f.write(val)
                f.close()
                #val = os.path.join(all_data['scene']['paths']['materials'], 
                #                   fname).replace('\\','/')
                val = fname


            if not key in uniform.keys():
                uniform[key] = val
        uniforms.append(uniform)
    target_data['uniforms'] = uniforms
